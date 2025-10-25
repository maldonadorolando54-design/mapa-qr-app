import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mapa + QR Composer", layout="centered")
st.title("🗺️ Mapa + QR — Composición centrada en A4")

st.markdown("""
Sube **el mapa** (imagen) y **el QR** (imagen).  
Esta versión coloca ambos **centrados dentro de una hoja A4** (210 × 297 mm).  
""")

# --- INTERFAZ DE CARGA ---
col1, col2 = st.columns([1, 1])
with col1:
    map_file = st.file_uploader("🗺️ Sube la imagen del mapa", type=["png", "jpg", "jpeg"])
with col2:
    qr_file = st.file_uploader("🔳 Sube la imagen del QR", type=["png", "jpg", "jpeg"])

default_name = ""
if map_file is not None:
    try:
        default_name = os.path.splitext(map_file.name)[0]
    except Exception:
        default_name = ""

name = st.text_input("Nombre que aparecerá arriba", value=default_name)

with st.expander("⚙️ Ajustes (opcional)"):
    canvas_bg = st.color_picker("Color de fondo del lienzo", value="#ffffff")
    map_max_width = st.number_input("Máx ancho del mapa (px)", min_value=200, max_value=2000, value=900)
    qr_size = st.number_input("Tamaño QR (px)", min_value=50, max_value=600, value=200)
    margin = st.number_input("Margen interno (px)", min_value=0, max_value=200, value=40)
    font_size = st.slider("Tamaño del texto del título", 20, 100, 40)
    dpi = st.selectbox("Resolución del lienzo", [150, 200, 300], index=2)

# --- FUNCIONES AUXILIARES ---

def load_image(file):
    img = Image.open(file).convert("RGBA")
    return img

def compose_centered_A4(map_img, qr_img, title_text, bg_hex="#ffffff", map_max_w=900,
                        qr_px=200, margin_px=40, font_size=40, dpi=300):
    """Compone mapa + QR + título centrados en un lienzo A4."""
    # Tamaño A4 a la resolución elegida
    a4_w_px = int(8.27 * dpi)  # 210 mm
    a4_h_px = int(11.69 * dpi)  # 297 mm

    # Redimensionar mapa si es necesario
    map_w, map_h = map_img.size
    if map_w > map_max_w:
        ratio = map_max_w / float(map_w)
        map_img = map_img.resize((int(map_w * ratio), int(map_h * ratio)), Image.LANCZOS)
        map_w, map_h = map_img.size

    # Redimensionar QR
    qr_img = qr_img.resize((qr_px, qr_px), Image.LANCZOS)

    # Fuente
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    # Calcular tamaño del texto
    dummy = Image.new("RGBA", (10, 10))
    draw = ImageDraw.Draw(dummy)
    try:
        bbox = draw.textbbox((0, 0), title_text, font=font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        text_w, text_h = draw.textsize(title_text, font=font)

    # Crear lienzo A4
    canvas = Image.new("RGBA", (a4_w_px, a4_h_px), bg_hex)
    draw = ImageDraw.Draw(canvas)

    # Calcular bloque total (título + QR + mapa)
    block_w = max(map_w, qr_px, text_w) + 2 * margin_px
    block_h = text_h + qr_px + map_h + 4 * margin_px

    # Posición superior izquierda del bloque centrado
    start_x = (a4_w_px - block_w) // 2
    start_y = (a4_h_px - block_h) // 2

    # Dibujar título
    title_x = start_x + (block_w - text_w) // 2
    title_y = start_y + margin_px
    draw.text((title_x, title_y), title_text, fill=(0, 0, 0), font=font)

    # Dibujar QR debajo del título
    qr_x = start_x + (block_w - qr_px) // 2
    qr_y = title_y + text_h + margin_px
    canvas.paste(qr_img, (qr_x, qr_y), qr_img)

    # Dibujar mapa debajo del QR
    map_x = start_x + (block_w - map_w) // 2
    map_y = qr_y + qr_px + margin_px
    canvas.paste(map_img, (map_x, map_y), map_img)

    # Convertir a RGB final
    final = Image.new("RGB", canvas.size, bg_hex)
    final.paste(canvas, mask=canvas.split()[3] if canvas.mode == "RGBA" else None)
    return final

# --- PROCESO PRINCIPAL ---
if map_file is not None and qr_file is not None:
    try:
        map_img = load_image(map_file)
        qr_img = load_image(qr_file)
    except Exception as e:
        st.error(f"No se pudieron leer las imágenes: {e}")
        st.stop()

    if name.strip() == "":
        name = os.path.splitext(map_file.name)[0] if map_file else "Sin nombre"

    final_img = compose_centered_A4(
        map_img=map_img,
        qr_img=qr_img,
        title_text=name,
        bg_hex=canvas_bg,
        map_max_w=map_max_width,
        qr_px=qr_size,
        margin_px=margin,
        font_size=font_size,
        dpi=dpi
    )

    st.subheader("🖼️ Previsualización (centrado en hoja A4):")
    st.image(final_img, use_column_width=True)

    # Descargar PNG
    buf = io.BytesIO()
    final_img.save(buf, format="PNG")
    buf.seek(0)
    st.download_button(
        "📥 Descargar PNG",
        data=buf,
        file_name=f"{name}_A4.png",
        mime="image/png"
    )

    # Descargar PDF
    buf_pdf = io.BytesIO()
    final_img.save(buf_pdf, format="PDF")
    buf_pdf.seek(0)
    st.download_button(
        "📄 Descargar PDF (A4)",
        data=buf_pdf,
        file_name=f"{name}_A4.pdf",
        mime="application/pdf"
    )
else:
    st.info("Sube ambos archivos (mapa y QR) para generar la composición centrada en una hoja A4.")

