import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os

st.set_page_config(page_title="Mapa + QR Composer", layout="wide")
st.title("🗺️ Mapa + QR — Composición automática")

st.markdown("""
Sube **el mapa** (imagen) y **el QR** (imagen).  
La app colocará automáticamente:
- el **nombre arriba a la izquierda** (toma por defecto el nombre del archivo del mapa),
- el **QR a la izquierda debajo del título**,
- el **mapa a la derecha**,
- y generará una imagen final lista para descargar.
""")

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
    map_max_width = st.number_input("Máx ancho del mapa (px)", min_value=200, max_value=3000, value=900)
    qr_size = st.number_input("Tamaño QR (px)", min_value=50, max_value=600, value=200)
    margin = st.number_input("Margen (px)", min_value=0, max_value=200, value=24)
    font_size = st.slider("Tamaño del texto del título", 20, 100, 36)


# --- Funciones auxiliares ---

def load_image(file):
    """Carga una imagen y la convierte a RGBA."""
    img = Image.open(file).convert("RGBA")
    return img


def compose(map_img, qr_img, title_text, bg_hex="#ffffff", map_max_w=900, qr_px=200, margin_px=24, font_size=36):
    """Compone el mapa + QR + título en una sola imagen."""
    map_w, map_h = map_img.size
    if map_w > map_max_w:
        ratio = map_max_w / float(map_w)
        new_map_w = int(map_w * ratio)
        new_map_h = int(map_h * ratio)
        map_img = map_img.resize((new_map_w, new_map_h), Image.LANCZOS)
        map_w, map_h = map_img.size

    qr_img = qr_img.resize((qr_px, qr_px), Image.LANCZOS)
    qr_w, qr_h = qr_img.size

    # Intentar cargar una fuente adecuada
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    dummy = Image.new("RGBA", (10, 10))
    draw = ImageDraw.Draw(dummy)

    # Compatibilidad: Pillow >=10 usa textbbox, versiones antiguas usan textsize
    try:
        bbox = draw.textbbox((0, 0), title_text, font=font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        text_w, text_h = draw.textsize(title_text, font=font)

    # Dimensiones del lienzo
    left_col_w = max(qr_w, text_w) + 2 * margin_px
    canvas_w = left_col_w + map_w + 2 * margin_px
    left_col_height = text_h + margin_px + qr_h + margin_px
    canvas_h = max(left_col_height, map_h) + 2 * margin_px

    # Crear lienzo
    canvas = Image.new("RGBA", (canvas_w, canvas_h), bg_hex)
    draw = ImageDraw.Draw(canvas)

    # Posiciones
    title_x = margin_px
    title_y = margin_px
    draw.text((title_x, title_y), title_text, fill=(0, 0, 0), font=font)

    qr_x = margin_px
    qr_y = title_y + text_h + margin_px // 2
    canvas.paste(qr_img, (qr_x, qr_y), qr_img if qr_img.mode == "RGBA" else None)

    map_x = left_col_w + margin_px // 2
    map_y = margin_px
    available_h = canvas_h - 2 * margin_px
    if map_h < available_h:
        map_y = margin_px + (available_h - map_h) // 2

    canvas.paste(map_img, (map_x, map_y), map_img if map_img.mode == "RGBA" else None)

    # Convertir a RGB final
    final = Image.new("RGB", canvas.size, bg_hex)
    final.paste(canvas, mask=canvas.split()[3] if canvas.mode == "RGBA" else None)
    return final


# --- Ejecución principal ---
if map_file is not None and qr_file is not None:
    try:
        map_img = load_image(map_file)
        qr_img = load_image(qr_file)
    except Exception as e:
        st.error(f"No se pudieron leer las imágenes: {e}")
        st.stop()

    if name.strip() == "":
        try:
            name = os.path.splitext(map_file.name)[0]
        except Exception:
            name = "Sin nombre"

    final_img = compose(
        map_img=map_img,
        qr_img=qr_img,
        title_text=name,
        bg_hex=canvas_bg,
        map_max_w=map_max_width,
        qr_px=qr_size,
        margin_px=margin,
        font_size=font_size
    )

    st.subheader("🖼️ Previsualización:")
    st.image(final_img, use_column_width=True)

    # Descargar PNG
    buf = io.BytesIO()
    final_img.save(buf, format="PNG")
    buf.seek(0)
    st.download_button(
        "📥 Descargar PNG",
        data=buf,
        file_name=f"{name}_map_qr.png",
        mime="image/png"
    )

    # Descargar PDF
    buf_pdf = io.BytesIO()
    final_img.save(buf_pdf, format="PDF")
    buf_pdf.seek(0)
    st.download_button(
        "📄 Descargar PDF",
        data=buf_pdf,
        file_name=f"{name}_map_qr.pdf",
        mime="application/pdf"
    )

else:
    st.info("Sube ambos archivos (mapa y QR) para generar la composición automáticamente.")
