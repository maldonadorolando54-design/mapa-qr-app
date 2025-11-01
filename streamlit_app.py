import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io, os

try:
    import qrcode
except Exception:
    qrcode = None

st.set_page_config(page_title="Mapa + QR — Layout inicial", layout="centered")
st.title("🗺️ Mapa + QR — Layout inicial preconfigurado")

if qrcode is None:
    st.error("Instala `qrcode` con `pip install qrcode[pil] Pillow` para usar QR desde URL.")

# --- INPUTS ---
col1, col2 = st.columns(2)
with col1:
    qr_link = st.text_input("🔗 QR — URL (se genera automáticamente si se ingresa)")
    qr_file = st.file_uploader("🔳 Imagen QR (opcional si hay URL)", type=["png","jpg","jpeg"])
with col2:
    map_file = st.file_uploader("🗺️ Imagen del mapa", type=["png","jpg","jpeg"])

default_name = os.path.splitext(map_file.name)[0] if map_file else ""
title_text = st.text_input("Título principal", value=default_name)
subtitle_text = st.text_input("Subtítulo", value="Cong. Brescia Española")

# --- AJUSTES ---
with st.sidebar.expander("📝 Título y Subtítulo"):
    font_title = st.number_input("Tamaño título (px)", 10, 200, 70)
    font_sub = st.number_input("Tamaño subtítulo (px)", 10, 100, 36)
    title_color = st.color_picker("Color título", "#000000")
    subtitle_color = st.color_picker("Color subtítulo", "#555555")
    spacing_title_sub = st.number_input("Espacio entre título y subtítulo (px)", 0, 100, 10)
    title_x = st.number_input("Título X (px)", -500, 1000, 0)
    title_y = st.number_input("Título Y (px)", -500, 1000, 0)
    subtitle_x = st.number_input("Subtítulo X (px)", -500, 1000, 0)
    subtitle_y = st.number_input("Subtítulo Y (px)", -500, 1000, 50)

with st.sidebar.expander("🔳 QR"):
    qr_size = st.number_input("Tamaño QR (px)", 50, 800, 250)
    qr_x = st.number_input("QR X (px)", -500, 1000, 50)
    qr_y = st.number_input("QR Y (px)", -500, 1000, 600)

with st.sidebar.expander("🗺️ Mapa"):
    map_scale = st.number_input("Escala mapa (%)", 10, 300, 70)
    map_x = st.number_input("Mapa X (px)", -500, 1000, 400)
    map_y = st.number_input("Mapa Y (px)", -500, 1000, 150)

with st.sidebar.expander("Opciones generales"):
    bg_color = st.color_picker("Color de fondo", "#ffffff")
    dpi = st.selectbox("Resolución A4 (DPI)", [150,200,300], index=2)
    margin_px = st.number_input("Margen lateral (px)", 0, 200, 80)
    show_guides = st.checkbox("Mostrar guías", True)
    export_cut_line = st.checkbox("Incluir línea de corte (mitad superior)", True)
    qr_error_correction = st.selectbox("Corrección de error QR",
                                       ["LOW (7%)","MEDIUM (15%)","QUARTILE (25%)","HIGH (30%)"], index=2)

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
    qr = qrcode.QRCode(error_correction=ec_map.get(error_level, qrcode.constants.ERROR_CORRECT_Q), box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    return img.resize((qr_px, qr_px), Image.LANCZOS)

def compose_layout(title, subtitle, map_img, qr_img,
                   dpi=300, font_title=70, font_sub=36,
                   title_color="#000", subtitle_color="#555", spacing_title_sub=10,
                   title_pos=(0,0), subtitle_pos=(0,0),
                   qr_pos=(0,0), qr_size=250,
                   map_pos=(0,0), map_scale=100,
                   bg_color="#fff", show_guides=True, export_cut_line=True):

    a4_w = int(8.27*dpi)
    a4_h = int(11.69*dpi)
    canvas = Image.new("RGBA",(a4_w,a4_h),bg_color)
    draw = ImageDraw.Draw(canvas)

    # Guías
    if show_guides:
        draw.rectangle([(0,0),(a4_w-1,a4_h-1)], outline=(0,100,255), width=3)
        mid_y = a4_h//2
        draw.line([(0, mid_y),(a4_w, mid_y)], fill=(255,0,0), width=2)

    if export_cut_line:
        dash_len, gap = 12, 8
        x=0
        dash_y = a4_h//2 + 3
        while x<a4_w:
            draw.line([(x,dash_y),(min(x+dash_len,a4_w),dash_y)], fill=(0,0,0), width=1)
            x+=dash_len+gap

    # Fuentes
    try:
        font_b = ImageFont.truetype("DejaVuSans-Bold.ttf", font_title)
        font_s = ImageFont.truetype("DejaVuSans.ttf", font_sub)
    except:
        font_b, font_s = ImageFont.load_default(), ImageFont.load_default()

    # Título y subtítulo
    draw.text(title_pos, title, fill=title_color, font=font_b)
    draw.text(subtitle_pos, subtitle, fill=subtitle_color, font=font_s)

    # QR
    if qr_img:
        qr_img_resized = qr_img.resize((qr_size, qr_size), Image.LANCZOS)
        canvas.paste(qr_img_resized, qr_pos, qr_img_resized)

    # Mapa
    if map_img:
        map_img_resized = map_img.resize((int(map_img.width*map_scale/100), int(map_img.height*map_scale/100)), Image.LANCZOS)
        canvas.paste(map_img_resized, map_pos, map_img_resized)

    return canvas.convert("RGB")

# --- GENERACIÓN ---
if map_file and (qr_link or qr_file):
    map_img = load_image(map_file)
    if qr_link:
        qr_img = generate_qr_image(qr_link, qr_size, qr_error_correction.split()[0])
    elif qr_file:
        qr_img = load_image(qr_file)
    else:
        st.warning("Proporciona URL o imagen QR")
        qr_img = None

    if qr_img:
        final_img = compose_layout(
            title_text, subtitle_text, map_img, qr_img,
            dpi=dpi, font_title=font_title, font_sub=font_sub,
            title_color=title_color, subtitle_color=subtitle_color, spacing_title_sub=spacing_title_sub,
            title_pos=(title_x, title_y), subtitle_pos=(subtitle_x, subtitle_y),
            qr_pos=(qr_x, qr_y), qr_size=qr_size,
            map_pos=(map_x, map_y), map_scale=map_scale,
            bg_color=bg_color, show_guides=show_guides, export_cut_line=export_cut_line
        )

        st.subheader("🖼️ Previsualización")
        st.image(final_img, use_column_width=True)

        buf = io.BytesIO()
        final_img.save(buf, format="PNG")
        buf.seek(0)
        st.download_button("📥 Descargar PNG", buf, f"{title_text}_A4.png", "image/png")

        buf_pdf = io.BytesIO()
        final_img.save(buf_pdf, format="PDF")
        buf_pdf.seek(0)
        st.download_button("📄 Descargar PDF", buf_pdf, f"{title_text}_A4.pdf", "application/pdf")
else:
    st.info("Sube mapa y proporciona QR (URL o imagen) para generar el diseño.")
