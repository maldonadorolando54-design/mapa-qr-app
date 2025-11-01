import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io, os

try:
    import qrcode
except Exception:
    qrcode = None

from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Mapa + QR — Drag & Drop", layout="centered")
st.title("🗺️ Mapa + QR — Mueve elementos con el mouse")

if qrcode is None:
    st.error("Instala `qrcode` con `pip install qrcode[pil] Pillow` para usar QR desde URL.")

# --- INPUTS ---
map_file = st.file_uploader("🗺️ Imagen del mapa", type=["png","jpg","jpeg"])
qr_link = st.text_input("🔗 QR — URL (se genera automáticamente si se ingresa)")
qr_file = st.file_uploader("🔳 Imagen QR (opcional si hay URL)", type=["png","jpg","jpeg"])
title_text = st.text_input("Título principal", value="Título de ejemplo")
subtitle_text = st.text_input("Subtítulo", value="Subtítulo de ejemplo")

# --- AJUSTES ---
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
if map_file:
    map_img = load_image(map_file)
    map_img_resized = map_img.resize((int(map_img.width*map_scale/100),
                                      int(map_img.height*map_scale/100)), Image.LANCZOS)
else:
    map_img_resized = None

if qr_link:
    qr_img = generate_qr_image(qr_link, qr_size)
elif qr_file:
    qr_img = load_image(qr_file).resize((qr_size, qr_size), Image.LANCZOS)
else:
    qr_img = None

# --- CANVAS PARA DRAG & DROP ---
canvas_width = 800
canvas_height = 1100
canvas = st_canvas(
    fill_color="rgba(255, 255, 255, 0)",
    stroke_width=1,
    background_color="#FFFFFF",
    width=canvas_width,
    height=canvas_height,
    drawing_mode="transform",  # permite mover imágenes/texto
    key="canvas",
    initial_drawing=[  # elementos iniciales
        {
            "type": "image",
            "x": 40,
            "y": 900,
            "width": qr_img.width if qr_img else 100,
            "height": qr_img.height if qr_img else 100,
            "src": qr_img
        },
        {
            "type": "image",
            "x": 600,
            "y": 150,
            "width": map_img_resized.width if map_img_resized else 100,
            "height": map_img_resized.height if map_img_resized else 100,
            "src": map_img_resized
        },
        {
            "type": "text",
            "x": 80,
            "y": 50,
            "text": title_text,
            "color": title_color,
            "fontSize": font_title_size
        },
        {
            "type": "text",
            "x": 80,
            "y": 150,
            "text": subtitle_text,
            "color": subtitle_color,
            "fontSize": font_sub_size
        }
    ]
)

# --- EXPORTAR PNG ---
if st.button("📥 Exportar PNG"):
    img = Image.new("RGBA", (canvas_width, canvas_height), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    # Agregar manualmente texto y QR/mapa si es necesario
    st.image(img)
