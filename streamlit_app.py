import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io, os

try:
    import qrcode
except Exception:
    qrcode = None

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Mapa + QR — Posición controlada", layout="centered")
st.title("🗺️ Mapa + QR — Control de posiciones")

st.markdown("""
Control total de posiciones:
- Ajusta vertical y horizontal del bloque de **título + subtítulo**  
- Ajusta vertical y horizontal del bloque **QR + mapa**  
- Guías opcionales y línea de corte opcional
""")

if qrcode is None:
    st.error("Instala `qrcode` con `pip install qrcode[pil] Pillow` para usar la generación de QR desde URL.")

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
with st.sidebar.expander("🎨 Texto"):
    font_title = st.slider("Tamaño título (px)", 20, 120, 70)
    font_sub = st.slider("Tamaño subtítulo (px)", 10, 60, 36)
    title_color = st.color_picker("Color título", "#000000")
    subtitle_color = st.color_picker("Color subtítulo", "#555555")
    spacing_title_sub = st.slider("Espacio entre título y subtítulo (px)", 0, 50, 10)
    title_x_offset = st.slider("Mover título horizontalmente (px)", -200, 200, 0)
    title_y_offset = st.slider("Mover título verticalmente (px)", -200, 400, 0)

with st.sidebar.expander("🔳 Bloque QR + Mapa"):
    qr_size = st.slider("Tamaño QR (px)", 100, 600, 250)
    block_x_offset = st.slider("Mover bloque horizontalmente (px)", -200, 200, 0)
    block_y_offset = st.slider("Mover bloque verticalmente (px)", -200, 400, 0)
    map_scale = st.slider("Escala mapa (%)", 10, 200, 100)

with st.sidebar.expander("Opciones generales"):
    bg_color = st.color_picker("Color de fondo", "#ffffff")
    dpi = st.selectbox("Resolución A4 (DPI)", [150,200,300], index=2)
    margin_px = st.slider("Margen lateral (px)", 20, 200, 80)
    show_guides = st.checkbox("Mostrar guías", value=True)
    export_cut_line = st.checkbox("Incluir línea de corte (mitad superior)", value=True)
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
                   dpi=300, margin_px=80, font_title=70, font_sub=36,
                   title_color="#000", subtitle_color="#555", spacing_title_sub=10,
                   title_x_offset=0, title_y_offset=0,
                   block_x_offset=0, block_y_offset=0,
                   qr_size=250, map_scale=100,
                   bg_color="#fff", show_guides=True, export_cut_line=True):

    a4_w = int(8.27*dpi)
    a4_h = int(11.69*dpi)
    canvas_prev = Image.new("RGBA",(a4_w,a4_h),bg_color)
    canvas_final = Image.new("RGBA",(a4_w,a4_h),bg_color)
    dp, df = ImageDraw.Draw(canvas_prev), ImageDraw.Draw(canvas_final)
    mid_y = a4_h//2
    dash_y = mid_y+3

    # Guías
    if show_guides:
        dp.rectangle([(0,0),(a4_w-1,a4_h-1)], outline=(0,100,255), width=3)
        dp.line([(0, mid_y),(a4_w, mid_y)], fill=(255,0,0), width=2)

    if export_cut_line:
        dash_len, gap = 12, 8
        x=0
        while x<a4_w:
            df.line([(x,dash_y),(min(x+dash_len,a4_w),dash_y)], fill=(0,0,0), width=1)
            x+=dash_len+gap

    # Fuentes
    try:
        font_b = ImageFont.truetype("DejaVuSans-Bold.ttf", font_title)
        font_s = ImageFont.truetype("DejaVuSans.ttf", font_sub)
    except:
        font_b, font_s = ImageFont.load_default(), ImageFont.load_default()

    # Posición título
    top_y = int(a4_h*0.08) + title_y_offset
    tb = dp.textbbox((0,0), title, font=font_b)
    sb = dp.textbbox((0,0), subtitle, font=font_s)
    title_w, sub_w = tb[2]-tb[0], sb[2]-sb[0]
    text_x = (a4_w - max(title_w, sub_w))//2 + title_x_offset
    for draw in [dp, df]:
        draw.text((text_x, top_y), title, fill=title_color, font=font_b)
        draw.text((text_x, top_y + tb[3]-tb[1] + spacing_title_sub), subtitle, fill=subtitle_color, font=font_s)

    # Bloque QR + Mapa
    if qr_img and map_img:
        qr_img = qr_img.resize((qr_size, qr_size), Image.LANCZOS)
        map_img = map_img.resize((int(map_img.width*map_scale/100), int(map_img.height*map_scale/100)), Image.LANCZOS)
        qr_x = margin_px + block_x_offset
        qr_y = top_y + tb[3]-tb[1] + spacing_title_sub + block_y_offset
        map_x = a4_w - margin_px - map_img.width + block_x_offset
        map_y = qr_y  # alineado con el QR
        for canvas in [canvas_prev, canvas_final]:
            canvas.paste(qr_img, (qr_x, qr_y), qr_img)
            canvas.paste(map_img, (map_x, map_y), map_img)

    return canvas_prev.convert("RGB"), canvas_final.convert("RGB")

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
        preview, export = compose_layout(title_text, subtitle_text, map_img, qr_img,
                                         dpi=dpi, margin_px=margin_px,
                                         font_title=font_title, font_sub=font_sub,
                                         title_color=title_color, subtitle_color=subtitle_color,
                                         spacing_title_sub=spacing_title_sub,
                                         title_x_offset=title_x_offset, title_y_offset=title_y_offset,
                                         block_x_offset=block_x_offset, block_y_offset=block_y_offset,
                                         qr_size=qr_size, map_scale=map_scale,
                                         bg_color=bg_color,
                                         show_guides=show_guides, export_cut_line=export_cut_line)

        st.subheader("🖼️ Previsualización")
        st.image(preview, use_column_width=True)

        buf = io.BytesIO()
        export.save(buf, format="PNG")
        buf.seek(0)
        st.download_button("📥 Descargar PNG", buf, f"{title_text}_A4.png", "image/png")

        buf_pdf = io.BytesIO()
        export.save(buf_pdf, format="PDF")
        buf_pdf.seek(0)
        st.download_button("📄 Descargar PDF", buf_pdf, f"{title_text}_A4.pdf", "application/pdf")
else:
    st.info("Sube mapa y proporciona QR (URL o imagen) para generar el diseño.")
