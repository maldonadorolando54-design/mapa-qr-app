import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io, os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Mapa + QR (Mitad A4 Izquierda)", layout="centered")
st.title("🗺️ Mapa + QR — Diseño tipo folleto (mitad superior A4)")

st.markdown("""
Genera una hoja **A4 vertical**, con:
- **Título arriba a la izquierda**
- **QR debajo del título**
- **Mapa grande a la derecha**
- Todo contenido en la **mitad superior de la hoja**.
""")

col1, col2 = st.columns(2)
with col1:
    map_file = st.file_uploader("🗺️ Sube la imagen del mapa", type=["png", "jpg", "jpeg"])
with col2:
    qr_file = st.file_uploader("🔳 Sube la imagen del QR", type=["png", "jpg", "jpeg"])

default_name = ""
if map_file is not None:
    default_name = os.path.splitext(map_file.name)[0]

name = st.text_input("Nombre que aparecerá arriba", value=default_name)

with st.expander("⚙️ Ajustes (opcional)"):
    canvas_bg = st.color_picker("Color de fondo", "#ffffff")
    dpi = st.selectbox("Resolución (A4)", [150, 200, 300], index=2)
    font_size = st.slider("Tamaño de título", 20, 120, 64)
    qr_size = st.slider("Tamaño QR (px)", 100, 600, 250)
    margin = st.slider("Margen (px)", 10, 200, 80)

# --- FUNCIONES ---

def load_image(file):
    return Image.open(file).convert("RGBA")

def compose_left_qr_right_map(map_img, qr_img, title_text, bg_hex="#ffffff",
                              font_size=64, qr_px=250, margin_px=80, dpi=300):
    """Diseño: título + QR a la izquierda, mapa grande a la derecha (mitad superior A4)."""
    # Tamaño A4
    a4_w_px = int(8.27 * dpi)
    a4_h_px = int(11.69 * dpi)

    # Lienzo base
    canvas = Image.new("RGBA", (a4_w_px, a4_h_px), bg_hex)
    draw = ImageDraw.Draw(canvas)

    # Fuente
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Texto
    dummy = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(dummy)
    try:
        bbox = d.textbbox((0, 0), title_text, font=font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except:
        text_w, text_h = d.textsize(title_text, font=font)

    # Redimensionar QR
    qr_img = qr_img.resize((qr_px, qr_px), Image.LANCZOS)

    # Redimensionar mapa
    map_max_width = int(a4_w_px * 0.55)
    map_max_height = int(a4_h_px * 0.45)
    mw, mh = map_img.size
    ratio = min(map_max_width / mw, map_max_height / mh)
    map_img = map_img.resize((int(mw * ratio), int(mh * ratio)), Image.LANCZOS)

    # Posiciones
    content_top = int(a4_h_px * 0.1)
    left_col_x = margin_px
    right_col_x = left_col_x + qr_px + margin_px

    # Título (izquierda arriba)
    draw.text((left_col_x, content_top), title_text, fill=(0, 0, 0), font=font)

    # QR (debajo del título)
    qr_y = content_top + text_h + margin_px // 2
    canvas.paste(qr_img, (left_col_x, qr_y), qr_img)

    # Mapa (derecha)
    map_x = right_col_x
    map_y = content_top
    canvas.paste(map_img, (map_x, map_y), map_img)

    # Convertir a RGB
    final = Image.new("RGB", canvas.size, bg_hex)
    final.paste(canvas, mask=canvas.split()[3] if canvas.mode == "RGBA" else None)
    return final

# --- PROCESO ---
if map_file and qr_file:
    map_img = load_image(map_file)
    qr_img = load_image(qr_file)

    final_img = compose_left_qr_right_map(
        map_img, qr_img, name,
        bg_hex=canvas_bg,
        font_size=font_size,
        qr_px=qr_size,
        margin_px=margin,
        dpi=dpi
    )

    st.subheader("🖼️ Previsualización:")
    st.image(final_img, use_column_width=True)

    buf = io.BytesIO()
    final_img.save(buf, format="PNG")
    buf.seek(0)
    st.download_button("📥 Descargar PNG", buf, f"{name}_A4_layout.png", "image/png")

    buf_pdf = io.BytesIO()
    final_img.save(buf_pdf, format="PDF")
    buf_pdf.seek(0)
    st.download_button("📄 Descargar PDF", buf_pdf, f"{name}_A4_layout.pdf", "application/pdf")
else:
    st.info("Sube el mapa y el QR para generar el diseño.")
