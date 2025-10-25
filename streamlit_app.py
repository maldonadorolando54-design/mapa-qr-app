import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mapa + QR Composer", layout="centered")
st.title("🗺️ Mapa + QR — Diseño uniforme (mitad superior A4)")

st.markdown("""
Esta versión genera una hoja **A4 vertical**, colocando el **nombre, QR y mapa**
en la **mitad superior**, con proporciones uniformes y visualmente equilibradas.
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
    dpi = st.selectbox("Resolución del lienzo (A4)", [150, 200, 300], index=2)
    font_size = st.slider("Tamaño del texto del título", 24, 120, 72)

# --- FUNCIONES AUXILIARES ---

def load_image(file):
    """Carga y convierte una imagen a RGBA."""
    return Image.open(file).convert("RGBA")

def compose_balanced_A4(map_img, qr_img, title_text, bg_hex="#ffffff", font_size=72, dpi=300):
    """
    Crea una hoja A4 vertical con título, QR mediano y mapa grande,
    todo centrado en la mitad superior.
    """
    # Tamaño A4 en píxeles
    a4_w_px = int(8.27 * dpi)
    a4_h_px = int(11.69 * dpi)

    # --- Redimensionar mapa (grande) ---
    max_map_width = int(a4_w_px * 0.7)    # 70% del ancho de la página
    max_map_height = int(a4_h_px * 0.35)  # ocupa aprox. 35% del alto
    map_w, map_h = map_img.size
    ratio = min(max_map_width / map_w, max_map_height / map_h)
    map_img = map_img.resize((int(map_w * ratio), int(map_h * ratio)), Image.LANCZOS)

    # --- Redimensionar QR (mediano visible) ---
    qr_size = int(a4_w_px * 0.18)  # 18% del ancho de la hoja
    qr_img = qr_img.resize((qr_size, qr_size), Image.LANCZOS)

    # --- Fuente ---
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    # --- Calcular tamaño de texto ---
    dummy = Image.new("RGBA", (10, 10))
    draw = ImageDraw.Draw(dummy)
    try:
        bbox = draw.textbbox((0, 0), title_text, font=font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        text_w, text_h = draw.textsize(title_text, font=font)

    # --- Crear lienzo A4 ---
    canvas = Image.new("RGBA", (a4_w_px, a4_h_px), bg_hex)
    draw = ImageDraw.Draw(canvas)

    # --- Posiciones base ---
    top_margin = int(a4_h_px * 0.07)   # margen superior
    spacing = int(a4_h_px * 0.03)      # espacio entre secciones

    # --- Título ---
    title_x = (a4_w_px - text_w) // 2
    title_y = top_margin
    draw.text((title_x, title_y), title_text, fill=(0, 0, 0), font=font)

    # --- QR debajo del título ---
    qr_x = (a4_w_px - qr_size) // 2
    qr_y = title_y + text_h + spacing
    canvas.paste(qr_img, (qr_x, qr_y), qr_img)

    # --- Mapa grande debajo del QR ---
    map_x = (a4_w_px - map_img.width) // 2
    map_y = qr_y + qr_size + spacing
    canvas.paste(map_img, (map_x, map_y), map_img)

    # --- Convertir a RGB final ---
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

    final_img = compose_balanced_A4(
        map_img=map_img,
        qr_img=qr_img,
        title_text=name,
        bg_hex=canvas_bg,
        font_size=font_size,
        dpi=dpi
    )

    st.subheader("🖼️ Previsualización (mitad superior, diseño equilibrado):")
    st.image(final_img, use_column_width=True)

    # Descargar PNG
    buf = io.BytesIO()
    final_img.save(buf, format="PNG")
    buf.seek(0)
    st.download_button(
        "📥 Descargar PNG",
        data=buf,
        file_name=f"{name}_A4_balanced.png",
        mime="image/png"
    )

    # Descargar PDF
    buf_pdf = io.BytesIO()
    final_img.save(buf_pdf, format="PDF")
    buf_pdf.seek(0)
    st.download_button(
        "📄 Descargar PDF (A4 mitad superior uniforme)",
        data=buf_pdf,
        file_name=f"{name}_A4_balanced.pdf",
        mime="application/pdf"
    )
else:
    st.info("Sube ambos archivos (mapa y QR) para generar la composición equilibrada en la mitad superior de una hoja A4.")
