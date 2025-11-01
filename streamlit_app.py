import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io, os, re

try:
    import qrcode
except Exception:
    qrcode = None

st.set_page_config(page_title="Mapa + QR — Layout absoluto", layout="centered")
st.title("🗺️ Mapa + QR — sliders y números sincronizados")

if qrcode is None:
    st.error("Instala `qrcode` con `pip install qrcode[pil] Pillow` para usar QR desde URL.")

# ---------- Valores por defecto ----------
defaults = {
    "map_scale_slider": 157, "map_scale_num": 157,
    "map_x_slider": 580, "map_x_num": 580,
    "map_y_slider": 600, "map_y_num": 600,
    "qr_size_slider": 250, "qr_size_num": 250,
    "qr_x_slider": 30, "qr_x_num": 30,
    "qr_y_slider": 950, "qr_y_num": 950,
    "font_title_slider": 48, "font_title_num": 48,
    "font_sub_slider": 28, "font_sub_num": 28,
    "title_x_slider": 30, "title_x_num": 30,
    "title_y_slider": 50, "title_y_num": 50,
    "subtitle_x_slider": 0, "subtitle_x_num": 0,
    "subtitle_y_slider": 0, "subtitle_y_num": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------- Sincronización ----------
def sync(from_key, to_key):
    st.session_state[to_key] = st.session_state[from_key]

# ---------- Entradas principales ----------
col1, col2 = st.columns(2)
with col1:
    qr_link = st.text_input("🔗 URL para generar QR (automático si se ingresa)")
    qr_file = st.file_uploader("🔳 Imagen QR (opcional si ya hay URL)", type=["png","jpg","jpeg"])
with col2:
    map_file = st.file_uploader("🗺️ Imagen del mapa", type=["png","jpg","jpeg"])

# Título por defecto
default_name = os.path.splitext(map_file.name)[0] if map_file else ""
title_text = st.text_input("Título principal", value=default_name)
subtitle_text = st.text_input("Subtítulo", value="Cong. Brescia Española")

# ---------- Controles sincronizados ----------
with st.sidebar.expander("🗺️ Mapa"):
    map_scale = st.slider("Escala mapa (%)", 10, 300, st.session_state["map_scale_slider"],
                          key="map_scale_slider", on_change=sync, args=("map_scale_slider","map_scale_num"))
    map_scale_num = st.number_input("Escala mapa (%)", 10, 300, st.session_state["map_scale_num"],
                                    key="map_scale_num", on_change=sync, args=("map_scale_num","map_scale_slider"))
    map_x = st.slider("Mapa X (px)", 0, 2400, st.session_state["map_x_slider"],
                      key="map_x_slider", on_change=sync, args=("map_x_slider","map_x_num"))
    map_x_num = st.number_input("Mapa X (px)", 0, 2400, st.session_state["map_x_num"],
                                key="map_x_num", on_change=sync, args=("map_x_num","map_x_slider"))
    map_y = st.slider("Mapa Y (px)", 0, 2400, st.session_state["map_y_slider"],
                      key="map_y_slider", on_change=sync, args=("map_y_slider","map_y_num"))
    map_y_num = st.number_input("Mapa Y (px)", 0, 2400, st.session_state["map_y_num"],
                                key="map_y_num", on_change=sync, args=("map_y_num","map_y_slider"))

with st.sidebar.expander("🔳 Código QR"):
    qr_size = st.slider("Tamaño QR (px)", 50, 800, st.session_state["qr_size_slider"],
                        key="qr_size_slider", on_change=sync, args=("qr_size_slider","qr_size_num"))
    qr_size_num = st.number_input("Tamaño QR (px)", 50, 800, st.session_state["qr_size_num"],
                                  key="qr_size_num", on_change=sync, args=("qr_size_num","qr_size_slider"))
    qr_x = st.slider("QR X (px)", 0, 2400, st.session_state["qr_x_slider"],
                     key="qr_x_slider", on_change=sync, args=("qr_x_slider","qr_x_num"))
    qr_x_num = st.number_input("QR X (px)", 0, 2400, st.session_state["qr_x_num"],
                               key="qr_x_num", on_change=sync, args=("qr_x_num","qr_x_slider"))
    qr_y = st.slider("QR Y (px)", 0, 2400, st.session_state["qr_y_slider"],
                     key="qr_y_slider", on_change=sync, args=("qr_y_slider","qr_y_num"))
    qr_y_num = st.number_input("QR Y (px)", 0, 2400, st.session_state["qr_y_num"],
                               key="qr_y_num", on_change=sync, args=("qr_y_num","qr_y_slider"))

with st.sidebar.expander("📝 Título y Subtítulo"):
    font_title = st.slider("Tamaño título (px)", 10, 200, st.session_state["font_title_slider"],
                           key="font_title_slider", on_change=sync, args=("font_title_slider","font_title_num"))
    font_title_num = st.number_input("Tamaño título (px)", 10, 200, st.session_state["font_title_num"],
                                     key="font_title_num", on_change=sync, args=("font_title_num","font_title_slider"))
    font_sub = st.slider("Tamaño subtítulo (px)", 10, 100, st.session_state["font_sub_slider"],
                         key="font_sub_slider", on_change=sync, args=("font_sub_slider","font_sub_num"))
    font_sub_num = st.number_input("Tamaño subtítulo (px)", 10, 100, st.session_state["font_sub_num"],
                                   key="font_sub_num", on_change=sync, args=("font_sub_num","font_sub_slider"))

    spacing_title_sub = st.slider("Espaciado título-subtítulo (px)", 0, 200, 8)
    title_x = st.slider("Título X (px)", 0, 2400, st.session_state["title_x_slider"],
                        key="title_x_slider", on_change=sync, args=("title_x_slider","title_x_num"))
    title_x_num = st.number_input("Título X (px)", 0, 2400, st.session_state["title_x_num"],
                                  key="title_x_num", on_change=sync, args=("title_x_num","title_x_slider"))
    title_y = st.slider("Título Y (px)", 0, 2400, st.session_state["title_y_slider"],
                        key="title_y_slider", on_change=sync, args=("title_y_slider","title_y_num"))
    title_y_num = st.number_input("Título Y (px)", 0, 2400, st.session_state["title_y_num"],
                                  key="title_y_num", on_change=sync, args=("title_y_num","title_y_slider"))

    subtitle_x = st.slider("Subtítulo X (px)", 0, 2400, st.session_state["subtitle_x_slider"],
                           key="subtitle_x_slider", on_change=sync, args=("subtitle_x_slider","subtitle_x_num"))
    subtitle_x_num = st.number_input("Subtítulo X (px)", 0, 2400, st.session_state["subtitle_x_num"],
                                     key="subtitle_x_num", on_change=sync, args=("subtitle_x_num","subtitle_x_slider"))
    subtitle_y = st.slider("Subtítulo Y (px)", 0, 2400, st.session_state["subtitle_y_slider"],
                           key="subtitle_y_slider", on_change=sync, args=("subtitle_y_slider","subtitle_y_num"))
    subtitle_y_num = st.number_input("Subtítulo Y (px)", 0, 2400, st.session_state["subtitle_y_num"],
                                     key="subtitle_y_num", on_change=sync, args=("subtitle_y_num","subtitle_y_slider"))

    title_color = st.color_picker("Color del título", "#000000")
    subtitle_color = st.color_picker("Color del subtítulo", "#555555")

with st.sidebar.expander("⚙️ Opciones generales"):
    bg_color = st.color_picker("Color de fondo", "#ffffff")
    dpi = st.selectbox("Resolución de salida (DPI)", [150, 200, 300], index=2)
    show_guides = st.checkbox("Mostrar guías de margen", True)
    export_cut_line = st.checkbox("Incluir línea de corte (mitad superior)", True)
    qr_error_correction = st.selectbox(
        "Corrección de error QR",
        ["LOW (7%)", "MEDIUM (15%)", "QUARTILE (25%)", "HIGH (30%)"], index=2
    )

# ---------- Funciones ----------
def sanitize_filename(name: str) -> str:
    return re.sub(r"[^\w\-_. ]", "_", name).strip() or "export"

def load_image(file):
    img = Image.open(file)
    return img.convert("RGBA")

def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    lv = len(hex_color)
    return tuple(int(hex_color[i:i + lv//3], 16) for i in range(0, lv, lv//3))

def generate_qr_image(url, qr_px, error_level="QUARTILE"):
    ec_map = {
        "LOW": qrcode.constants.ERROR_CORRECT_L,
        "MEDIUM": qrcode.constants.ERROR_CORRECT_M,
        "QUARTILE": qrcode.constants.ERROR_CORRECT_Q,
        "HIGH": qrcode.constants.ERROR_CORRECT_H
    }
    level = error_level.split()[0]
    qr = qrcode.QRCode(error_correction=ec_map.get(level, qrcode.constants.ERROR_CORRECT_Q),
                       box_size=10, border=4)
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
    a4_w, a4_h = int(8.27 * dpi), int(11.69 * dpi)
    canvas = Image.new("RGBA", (a4_w, a4_h), hex_to_rgb(bg_color) + (255,))
    draw = ImageDraw.Draw(canvas)
    try:
        font_b = ImageFont.truetype("DejaVuSans-Bold.ttf", font_title)
        font_s = ImageFont.truetype("DejaVuSans.ttf", font_sub)
    except:
        font_b = font_s = ImageFont.load_default()

    if show_guides:
        draw.rectangle([(0,0),(a4_w-1,a4_h-1)], outline=(0,100,255), width=3)
        draw.line([(0,a4_h//2),(a4_w,a4_h//2)], fill=(255,0,0), width=2)

    if export_cut_line:
        dash_len, gap = 12, 8
        y = a4_h//2 + 3
        for x in range(0, a4_w, dash_len + gap):
            draw.line([(x,y),(min(x+dash_len,a4_w),y)], fill=(0,0,0), width=1)

    draw.text(title_pos, title, fill=title_color, font=font_b)
    title_bbox = draw.textbbox(title_pos, title, font=font_b)
    sx = subtitle_pos[0] if subtitle_pos[0] != 0 else title_pos[0]
    sy = subtitle_pos[1] if subtitle_pos[1] != 0 else title_bbox[3] + spacing_title_sub
    draw.text((sx, sy), subtitle, fill=subtitle_color, font=font_s)

    if qr_img:
        qr_resized = qr_img.resize((qr_size, qr_size), Image.LANCZOS)
        canvas.paste(qr_resized, qr_pos, qr_resized)

    if map_img:
        w = int(map_img.width * map_scale / 100)
        h = int(map_img.height * map_scale / 100)
        resized = map_img.resize((w, h), Image.LANCZOS)
        canvas.paste(resized, map_pos, resized)

    return canvas.convert("RGB")

# ---------- Generar ----------
if map_file and (qr_link or qr_file):
    map_img = load_image(map_file)
    qr_img = generate_qr_image(qr_link, st.session_state["qr_size_num"], qr_error_correction) if qr_link else load_image(qr_file)
    final_img = compose_layout(
        title_text, subtitle_text, map_img, qr_img,
        dpi=dpi, font_title=st.session_state["font_title_num"],
        font_sub=st.session_state["font_sub_num"],
        title_color=title_color, subtitle_color=subtitle_color,
        spacing_title_sub=spacing_title_sub,
        title_pos=(st.session_state["title_x_num"], st.session_state["title_y_num"]),
        subtitle_pos=(st.session_state["subtitle_x_num"], st.session_state["subtitle_y_num"]),
        qr_pos=(st.session_state["qr_x_num"], st.session_state["qr_y_num"]),
        qr_size=st.session_state["qr_size_num"],
        map_pos=(st.session_state["map_x_num"], st.session_state["map_y_num"]),
        map_scale=st.session_state["map_scale_num"],
        bg_color=bg_color, show_guides=show_guides,
        export_cut_line=export_cut_line
    )
    st.subheader("🖼️ Previsualización A4")
    st.image(final_img, use_column_width=True)

    safe_name = sanitize_filename(title_text or default_name or "map_qr")
    buf = io.BytesIO(); final_img.save(buf, format="PNG", dpi=(dpi, dpi)); buf.seek(0)
    st.download_button("📥 Descargar PNG", buf, f"{safe_name}_A4.png", "image/png")
    buf_pdf = io.BytesIO(); final_img.save(buf_pdf, format="PDF", dpi=(dpi, dpi)); buf_pdf.seek(0)
    st.download_button("📄 Descargar PDF", buf_pdf, f"{safe_name}_A4.pdf", "application/pdf")
else:
    st.info("Sube imagen del mapa y proporciona URL o imagen QR para generar el diseño.")
