import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io, base64
try:
    import qrcode
except:
    qrcode = None

from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Mapa + QR — Drag & Drop", layout="centered")
st.title("🗺️ Mapa + QR — Mueve elementos con el mouse")

# --- Función para convertir PIL a base64 ---
def pil_to_base64(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

# --- INPUTS ---
map_file = st.file_uploader("🗺️ Imagen del mapa", type=["png","jpg","jpeg"])
qr_link = st.text_input("🔗 QR — URL (se genera automáticamente si se ingresa)")
qr_file = st.file_uploader("🔳 Imagen QR (opcional si hay URL)", type=["png","jpg","jpeg"])
title_text = st.text_input("Título principal", value="Título de ejemplo")
subtitle_text = st.text_input("Subtítulo", value="Subtítulo de ejemplo")

font_title_size = st.slider("Tamaño título (px)", 10, 200, 150)
font_sub_size = st.slider("Tamaño subtítulo (px)", 10, 100, 50)
title_color = st.color_picker("Color título", "#000000")
subtitle_color = st.color_picker("Color subtítulo", "#555555")
qr_size = st.slider("Tamaño QR (px)", 50, 800, 600)
map_scale = st.slider("Escala mapa (%)", 10, 300, 157)

# --- FUNCIONES ---
def load_image(file):
    img = Image.open(file)
    return img.convert("RGBA") if img.mode != "RGBA" else img

def generate_qr_image(url, qr_px, error_level="QUARTILE"):
    if qrcode is None:
        raise RuntimeError("qrcode no está instalado")
    ec_map = {"LOW": qrcode.constants.ERROR_CORRECT_L,
              "MEDIUM": qrcode.constants.ERROR_CORRECT_M,
              "QUARTILE": qrcode.constants.ERROR_CORRECT_Q,
              "HIGH": qrcode.constants.ERROR_CORRECT_H}
    qr = qrcode.QRCode(error_correction=ec_map.get(error_level, qrcode.constants.ERROR_CORRECT_Q),
                       box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    return img.resize((qr_px, qr_px), Image.LANCZOS)

# --- CARGA DE IMÁGENES ---
map_img_resized = None
if map_file:
    map_img = load_image(map_file)
    map_img_resized = map_img.resize((int(map_img.width*map_scale/100),
                                      int(map_img.height*map_scale/100)), Image.LANCZOS)

qr_img = None
if qr_link:
    qr_img = generate_qr_image(qr_link, qr_size)
elif qr_file:
    qr_img = load_image(qr_file).resize((qr_size, qr_size), Image.LANCZOS)

# --- PREPARAR ELEMENTOS PARA EL CANVAS ---
initial_drawing = []

if qr_img:
    initial_drawing.append({
        "type": "image",
        "x": 40,
        "y": 900,
        "width": qr_img.width,
        "height": qr_img.height,
        "src": pil_to_base64(qr_img)
    })

if map_img_resized:
    initial_drawing.append({
        "type": "image",
        "x": 600,
        "y": 150,
        "width": map_img_resized.width,
        "height": map_img_resized.height,
        "src": pil_to_base64(map_img_resized)
    })

initial_drawing.append({
    "type": "text",
    "x": 80,
    "y": 50,
    "text": title_text,
    "color": title_color,
    "fontSize": font_title_size
})

initial_drawing.append({
    "type": "text",
    "x": 80,
    "y": 150,
    "text": subtitle_text,
    "color": subtitle_color,
    "fontSize": font_sub_size
})

# --- CANVAS ---
canvas_width = 800
canvas_height = 1100
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0)",
    stroke_width=1,
    background_color="#FFFFFF",
    width=canvas_width,
    height=canvas_height,
    drawing_mode="transform",
    key="canvas",
    initial_drawing=initial_drawing
)

# --- EXPORTAR PNG ---
if st.button("📥 Exportar PNG"):
    final_img = Image.new("RGBA", (canvas_width, canvas_height), "#FFFFFF")
    draw = ImageDraw.Draw(final_img)

    # Dibujar manualmente los elementos para PNG final
    for el in initial_drawing:
        if el["type"] == "text":
            try:
                font = ImageFont.truetype("DejaVuSans-Bold.ttf", el["fontSize"])
            except:
                font = ImageFont.load_default()
            draw.text((el["x"], el["y"]), el["text"], fill=el["color"], font=font)
        elif el["type"] == "image":
            # Convertir base64 a PIL
            header, encoded = el["src"].split(",",1)
            img_bytes = base64.b64decode(encoded)
            img = Image.open(io.BytesIO(img_bytes))
            img_resized = img.resize((el["width"], el["height"]))
            final_img.paste(img_resized, (el["x"], el["y"]), img_resized)

    buf = io.BytesIO()
    final_img.save(buf, format="PNG")
    buf.seek(0)
    st.download_button("📥 Descargar PNG final", buf, f"{title_text}_A4.png", "image/png")
