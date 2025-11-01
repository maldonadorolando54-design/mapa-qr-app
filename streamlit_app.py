import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io, os

try:
    import qrcode
except Exception:
    qrcode = None

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Mapa + QR (Diseño final)", layout="centered")
st.title("🗺️ Mapa + QR — Estilo Institucional Final")

st.markdown("""
**Versión mejorada:**
- Control total del título y subtítulo (color, posición, alineación, espaciado)  
- Línea divisoria eliminada  
- QR y mapa con misma lógica y guías opcionales
""")

if qrcode is None:
    st.error(
        "Falta la librería `qrcode`. Instálala con:\n"
        "`pip install qrcode[pil] Pillow`"
    )

# --- ENTRADAS ---
col1, col2 = st.columns(2)
with col1:
    qr_link = st.text_input("🔗 QR — URL (se genera automáticamente si se ingresa)")
    qr_file = st.file_uploader("🔳 (Opcional) Imagen del QR", type=["png", "jpg", "jpeg"])
with col2:
    map_file = st.file_uploader("🗺️ Imagen del mapa", type=["png", "jpg", "jpeg"])

default_name = ""
if map_file:
    default_name = os.path.splitext(map_file.name)[0]

name = st.text_input("Título principal", value=default_name)
subtitle = st.text_input("Subtítulo", value="Cong. Brescia Española")

# --- AJUSTES ---
with st.sidebar.expander("⚙️ Ajustes generales", expanded=True):
    bg_color = st.color_picker("Color de fondo", "#ffffff")
    dpi = st.selectbox("Resolución (A4 DPI)", [150, 200, 300], index=2)
    qr_size = st.slider("Tamaño QR (px)", 100, 600, 250)
    margin = st.slider("Margen lateral (px)", 20, 200, 80)
    extra_space = st.slider("Espacio vertical entre título y QR (px)", 0, 400, 120)
    map_offset_y = st.slider("Desplazamiento vertical del mapa (px)", 0, 600, 150)
    show_guides = st.checkbox("🧭 Mostrar guías en previsualización", value=True)
    export_cut_line = st.checkbox("📐 Incluir línea de corte (mitad superior) en exportación", value=True)

with st.sidebar.expander("🎨 Estilo del texto", expanded=True):
    font_title = st.slider("Tamaño título (px)", 20, 120, 70)
    font_sub = st.slider("Tamaño subtítulo (px)", 10, 60, 36)
    title_color = st.color_picker("Color del título", "#000000")
    subtitle_color = st.color_picker("Color del subtítulo", "#555555")
    spacing_title_sub = st.slider("Espacio entre título y subtítulo (px)", 0, 100, 10)
    title_offset_y = st.slider("Ajuste vertical del bloque de texto (px)", -200, 400, 0)
    text_align = st.selectbox("Alineación del texto", ["izquierda", "centro", "derecha"], index=0)

with st.sidebar.expander("🔳 QR — Opciones avanzadas"):
    qr_error_correction = st.selectbox("Corrección de error QR",
                                       ["LOW (7%)", "MEDIUM (15%)", "QUARTILE (25%)", "HIGH (30%)"],
                                       index=2)

# --- FUNCIONES ---
def load_image(file):
    img = Image.open(file)
    return img.convert("RGBA") if img.mode != "RGBA" else img

def generate_qr_image_from_link(url, qr_px=250, error_level="QUARTILE"):
    if qrcode is None:
        raise RuntimeError("qrcode no está instalado")
    ec_map = {
        "LOW": qrcode.constants.ERROR_CORRECT_L,
        "MEDIUM": qrcode.constants.ERROR_CORRECT_M,
        "QUARTILE": qrcode.constants.ERROR_CORRECT_Q,
        "HIGH": qrcode.constants.ERROR_CORRECT_H,
    }
    ec = ec_map.get(error_level, qrcode.constants.ERROR_CORRECT_Q)
    qr = qrcode.QRCode(error_correction=ec, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    return img.resize((qr_px, qr_px), Image.LANCZOS)

def compose_layout(map_img, qr_img, title, subtitle,
                   bg="#ffffff", font_title=70, font_sub=36,
                   qr_px=250, margin_px=80, extra_space=120, map_offset_y=150,
                   title_color="#000000", subtitle_color="#555555",
                   spacing_title_sub=10, title_offset_y=0, text_align="izquierda",
                   dpi=300, show_guides=False, export_cut_line=False):

    a4_w = int(8.27 * dpi)
    a4_h = int(11.69 * dpi)
    canvas_prev = Image.new("RGBA", (a4_w, a4_h), bg)
    canvas_final = Image.new("RGBA", (a4_w, a4_h), bg)
    dp, df = ImageDraw.Draw(canvas_prev), ImageDraw.Draw(canvas_final)
    mid_y = a4_h // 2
    dash_y = mid_y + 3

    # Guías en preview
    if show_guides:
        dp.rectangle([(0,0),(a4_w-1,a4_h-1)], outline=(0,100,255), width=3)
        dp.line([(0, mid_y),(a4_w, mid_y)], fill=(255,0,0), width=2)
        dash_len, gap = 12, 8
        x=0
        while x<a4_w:
            dp.line([(x, dash_y),(min(x+dash_len,a4_w),dash_y)], fill=(160,32,240), width=2)
            x += dash_len+gap

    # Línea de corte en exportación
    if export_cut_line:
        dash_len, gap = 12, 8
        x=0
        while x<a4_w:
            df.line([(x,dash_y),(min(x+dash_len,a4_w),dash_y)], fill=(0,0,0), width=1)
            x += dash_len+gap

    # Fuentes
    try:
        font_bold = ImageFont.truetype("DejaVuSans-Bold.ttf", font_title)
        font_subt = ImageFont.truetype("DejaVuSans.ttf", font_sub)
    except:
        font_bold = ImageFont.load_default()
        font_subt = ImageFont.load_default()

    # Medidas texto
    tb = dp.textbbox((0,0), title, font=font_bold)
    sb = dp.textbbox((0,0), subtitle, font=font_subt)
    title_w, title_h = tb[2]-tb[0], tb[3]-tb[1]
    sub_w, sub_h = sb[2]-sb[0], sb[3]-sb[1]

    # Alineación
    if text_align == "izquierda":
        text_x = margin_px
    elif text_align == "centro":
        text_x = (a4_w - max(title_w, sub_w)) // 2
    else:
        text_x = a4_w - margin_px - max(title_w, sub_w)

    # Posición Y
    top_y = int(a4_h * 0.08) + title_offset_y

    # Escribir texto
    for draw in [dp, df]:
        draw.text((text_x, top_y), title, fill=title_color, font=font_bold)
        draw.text((text_x, top_y + title_h + spacing_title_sub),
                  subtitle, fill=subtitle_color, font=font_subt)

    # QR y mapa
    qr_y = top_y + title_h + sub_h + extra_space
    qr_img = qr_img.resize((qr_px, qr_px), Image.LANCZOS)
    mw, mh = map_img.size
    ratio = min((a4_w*0.55)/mw, (a4_h*0.45)/mh)
    map_img = map_img.resize((int(mw*ratio), int(mh*ratio)), Image.LANCZOS)
    qr_x = margin_px
    map_x = a4_w - margin_px - map_img.width
    map_y = top_y + map_offset_y
    canvas_prev.paste(qr_img, (qr_x, qr_y), qr_img)
    canvas_final.paste(qr_img, (qr_x, qr_y), qr_img)
    canvas_prev.paste(map_img, (map_x, map_y), map_img)
    canvas_final.paste(map_img, (map_x, map_y), map_img)

    # Convertir a RGB
    final_prev = Image.new("RGB", canvas_prev.size, bg)
    final_prev.paste(canvas_prev, mask=canvas_prev.split()[3])
    final_exp = Image.new("RGB", canvas_final.size, bg)
    final_exp.paste(canvas_final, mask=canvas_final.split()[3])
    return final_prev, final_exp


# --- GENERACIÓN ---
if map_file and (qr_link or qr_file):
    map_img = load_image(map_file)
    if qr_link:
        ec_map = {"LOW (7%)": "LOW", "MEDIUM (15%)": "MEDIUM", "QUARTILE (25%)": "QUARTILE", "HIGH (30%)": "HIGH"}
        ec = ec_map.get(qr_error_correction, "QUARTILE")
        qr_img = generate_qr_image_from_link(qr_link, qr_px=qr_size, error_level=ec)
    else:
        qr_img = load_image(qr_file)

    preview, export = compose_layout(
        map_img, qr_img, name, subtitle,
        bg=bg_color, font_title=font_title, font_sub=font_sub,
        qr_px=qr_size, margin_px=margin, extra_space=extra_space, map_offset_y=map_offset_y,
        title_color=title_color, subtitle_color=subtitle_color,
        spacing_title_sub=spacing_title_sub, title_offset_y=title_offset_y, text_align=text_align,
        dpi=dpi, show_guides=show_guides, export_cut_line=export_cut_line
    )

    st.subheader("🖼️ Previsualización:")
    st.image(preview, use_column_width=True)

    buf = io.BytesIO()
    export.save(buf, format="PNG")
    buf.seek(0)
    st.download_button("📥 Descargar PNG", buf, f"{name}_A4_institucional.png", "image/png")

    buf_pdf = io.BytesIO()
    export.save(buf_pdf, format="PDF")
    buf_pdf.seek(0)
    st.download_button("📄 Descargar PDF", buf_pdf, f"{name}_A4_institucional.pdf", "application/pdf")
else:
    st.info("Sube el mapa y proporciona una URL o imagen de QR para generar el diseño.")
