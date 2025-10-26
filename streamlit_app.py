import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io, os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mapa + QR (Diseño Limpio)", layout="centered")
st.title("🗺️ Mapa + QR — Versión Profesional Limpia")

st.markdown("""
Genera una hoja **A4 limpia y profesional**, con:
- **Título arriba a la izquierda**
- **QR debajo del título, bien separado**
- **Mapa grande a la derecha**, un poco más abajo  
- Todo contenido en la **mitad superior de la hoja A4**.
""")

# Archivos
col1, col2 = st.columns(2)
with col1:
    qr_file = st.file_uploader("🔳 Sube la imagen del QR", type=["png", "jpg", "jpeg"])
with col2:
    map_file = st.file_uploader("🗺️ Sube la imagen del mapa", type=["png", "jpg", "jpeg"])

default_name = ""
if map_file:
    default_name = os.path.splitext(map_file.name)[0]

name = st.text_input("Título principal", value=default_name)

# Ajustes
with st.expander("⚙️ Ajustes opcionales"):
    bg_color = st.color_picker("Color de fondo", "#ffffff")
    dpi = st.selectbox("Resolución (A4)", [150, 200, 300], index=2)
    font_size = st.slider("Tamaño de título", 30, 120, 80)
    qr_size = st.slider("Tamaño QR (px)", 150, 600, 250)
    margin = st.slider("Margen lateral (px)", 20, 200, 100)
    qr_gap = st.slider("Distancia del QR desde el título (px)", 50, 600, 180)
    map_offset_y = st.slider("Altura vertical del mapa (px)", 0, 600, 180)

# --- FUNCIONES ---
def load_image(file):
    return Image.open(file).convert("RGBA")

def compose_clean(map_img, qr_img, title_text, bg="#ffffff",
                  font_size=80, qr_px=250, margin_px=100,
                  qr_gap=180, map_offset_y=180, dpi=300):
    """Diseño limpio, sin sombras, QR a la izquierda, mapa a la derecha."""
    # Tamaño A4
    a4_w_px = int(8.27 * dpi)
    a4_h_px = int(11.69 * dpi)
    canvas = Image.new("RGBA", (a4_w_px, a4_h_px), bg)
    draw = ImageDraw.Draw(canvas)

    # Fuente
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Título arriba izquierda
    title_x = margin_px
    title_y = int(a4_h_px * 0.1)
    draw.text((title_x, title_y), title_text, fill=(0,0,0), font=font)

    # QR más abajo
    qr_img = qr_img.resize((qr_px, qr_px), Image.LANCZOS)
    qr_x = margin_px
    qr_y = title_y + font_size + qr_gap
    canvas.paste(qr_img, (qr_x, qr_y), qr_img)

    # Mapa grande a la derecha
    map_max_width = int(a4_w_px * 0.55)
    map_max_height = int(a4_h_px * 0.45)
    mw, mh = map_img.size
    ratio = min(map_max_width/mw, map_max_height/mh)
    map_img = map_img.resize((int(mw*ratio), int(mh*ratio)), Image.LANCZOS)

    map_x = qr_x + qr_px + margin_px
    map_y = title_y + map_offset_y
    canvas.paste(map_img, (map_x, map_y), map_img)

    # Convertir a RGB final
    final = Image.new("RGB", canvas.size, bg)
    final.paste(canvas, mask=canvas.split()[3] if canvas.mode == "RGBA" else None)
    return final

# --- PROCESO ---
if map_file and qr_file:
    map_img = load_image(map_file)
    qr_img = load_image(qr_file)

    final_img = compose_clean(
        map_img=map_img,
        qr_img=qr_img,
        title_text=name,
        bg=bg_color,
        font_size=font_size,
        qr_px=qr_size,
        margin_px=margin,
        qr_gap=qr_gap,
        map_offset_y=map_offset_y,
        dpi=dpi
    )

    st.subheader("🖼️ Vista previa:")
    st.image(final_img, use_column_width=True)

    buf = io.BytesIO()
    final_img.save(buf, format="PNG")
    buf.seek(0)
    st.download_button("📥 Descargar PNG", buf, f"{name}_A4_limpio.png", "image/png")

    buf_pdf = io.BytesIO()
    final_img.save(buf_pdf, format="PDF")
    buf_pdf.seek(0)
    st.download_button("📄 Descargar PDF", buf_pdf, f"{name}_A4_limpio.pdf", "application/pdf")
else:
    st.info("Sube el QR y el mapa para generar la composición.")
