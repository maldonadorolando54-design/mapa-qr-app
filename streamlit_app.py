import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io, os, re

try:
    import qrcode
except Exception:
    qrcode = None

st.set_page_config(page_title="Mapa + QR — Layout absoluto", layout="centered")
st.title("🗺️ Mapa + QR + URL + Posiciones absolutas (entrada numérica de px)")

if qrcode is None:
    st.error("Instala `qrcode` con `pip install qrcode[pil] Pillow` para usar QR desde URL.")

# --- ENTRADAS PRINCIPALES ---
col1, col2 = st.columns(2)
with col1:
    qr_link = st.text_input("🔗 URL para generar QR (automático si se ingresa)")
    qr_file = st.file_uploader("🔳 Imagen QR (opcional si ya hay URL)", type=["png","jpg","jpeg"])
    custom_font_file = st.file_uploader("🔤 Fuente TTF (opcional)", type=["ttf"])
with col2:
    map_file = st.file_uploader("🗺️ Imagen del mapa", type=["png","jpg","jpeg"])

# Título por defecto: usa el nombre del archivo del mapa
default_name = ""
if map_file is not None:
    try:
        default_name = os.path.splitext(map_file.name)[0]
    except Exception:
        default_name = ""

title_text = st.text_input("Título principal", value=default_name)
subtitle_text = st.text_input("Subtítulo", value="Cong. Brescia Española")

# --- CONTROLES DE POSICIÓN Y TAMAÑO ---
with st.sidebar.expander("🗺️ Mapa"):
    map_scale = st.slider("Escala mapa (%)", 10, 300, 157)
    # ahora permiten escribir el valor en px
    map_x = st.number_input("Posición X mapa (px)", min_value=0, max_value=2400, value=580, step=1)
    map_y = st.number_input("Posición Y mapa (px)", min_value=0, max_value=2400, value=600, step=1)

with st.sidebar.expander("🔳 Código QR"):
    qr_size = st.slider("Tamaño QR (px)", 50, 800, 250)
    qr_x = st.number_input("Posición X QR (px)", min_value=0, max_value=2400, value=30, step=1)
    qr_y = st.number_input("Posición Y QR (px)", min_value=0, max_value=2400, value=950, step=1)

with st.sidebar.expander("📝 Título y Subtítulo"):
    font_title = st.slider("Tamaño título (px)", 10, 200, 48)
    font_sub = st.slider("Tamaño subtítulo (px)", 10, 100, 28)
    spacing_title_sub = st.slider("Espaciado entre título y subtítulo (px)", 0, 200, 8)
    title_x = st.number_input("Título — posición X (px)", min_value=0, max_value=2400, value=30, step=1)
    title_y = st.number_input("Título — posición Y (px)", min_value=0, max_value=2400, value=50, step=1)
    subtitle_x = st.number_input("Subtítulo — posición X (0 = igual al título)", min_value=0, max_value=2400, value=0, step=1)
    subtitle_y = st.number_input("Subtítulo — posición Y (0 = debajo del título)", min_value=0, max_value=2400, value=0, step=1)

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

# --- FUNCIONES AUXILIARES ---
def sanitize_filename(name: str) -> str:
    """Limpia el nombre del archivo para evitar caracteres inválidos."""
    name = re.sub(r"[^\w\-_. ]", "_", name)
    return name.strip() or "export"

def load_image(file):
    """Carga imagen en modo RGBA."""
    img = Image.open(file)
    return img.convert("RGBA")

def hex_to_rgb(hex_color: str):
    """Convierte color HEX a tupla RGB."""
    hex_color = hex_color.lstrip("#")
    lv = len(hex_color)
    return tuple(int(hex_color[i:i + lv//3], 16) for i in range(0, lv, lv//3))

def generate_qr_image(url, qr_px, error_level="QUARTILE"):
    """Genera imagen QR con nivel de corrección elegido."""
    if qrcode is None:
        raise RuntimeError("qrcode no está instalado")
    ec_map = {
        "LOW": qrcode.constants.ERROR_CORRECT_L,
        "MEDIUM": qrcode.constants.ERROR_CORRECT_M,
        "QUARTILE": qrcode.constants.ERROR_CORRECT_Q,
        "HIGH": qrcode.constants.ERROR_CORRECT_H
    }
    chosen = error_level.split()[0]
    qr = qrcode.QRCode(error_correction=ec_map.get(chosen, qrcode.constants.ERROR_CORRECT_Q),
                       box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    return img.resize((qr_px, qr_px), Image.LANCZOS)

def load_font(font_file, size):
    """Carga fuente personalizada o usa DejaVu como respaldo."""
    try:
        if font_file is not None:
            font_bytes = font_file.read()
            return ImageFont.truetype(io.BytesIO(font_bytes), size)
    except Exception:
        pass
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except Exception:
        return ImageFont.load_default()

def compose_layout(title, subtitle, map_img, qr_img,
                   dpi=300, font_title=70, font_sub=36,
                   title_color="#000", subtitle_color="#555", spacing_title_sub=10,
                   title_pos=(0,0), subtitle_pos=(0,0),
                   qr_pos=(0,0), qr_size=250,
                   map_pos=(0,0), map_scale=100,
                   bg_color="#fff", show_guides=True, export_cut_line=True,
                   font_file=None):
    """Crea la composición final sobre hoja A4."""
    a4_w = int(8.27 * dpi)
    a4_h = int(11.69 * dpi)
    canvas = Image.new("RGBA", (a4_w, a4_h), hex_to_rgb(bg_color) + (255,))
    draw = ImageDraw.Draw(canvas)

    # Fuentes
    font_b = load_font(font_file, font_title)
    font_s = load_font(font_file, font_sub)

    # Guías
    if show_guides:
        draw.rectangle([(0, 0), (a4_w-1, a4_h-1)], outline=(0, 100, 255, 255), width=3)
        draw.line([(0, a4_h//2), (a4_w, a4_h//2)], fill=(255, 0, 0, 255), width=2)

    # Línea de corte
    if export_cut_line:
        dash_len, gap = 12, 8
        x = 0
        y = a4_h // 2 + 3
        while x < a4_w:
            draw.line([(x, y), (min(x + dash_len, a4_w), y)], fill=(0, 0, 0), width=1)
            x += dash_len + gap

    # Texto principal
    tx, ty = title_pos
    draw.text((tx, ty), title, fill=title_color, font=font_b)

    # Subtítulo: si el usuario deja 0 lo colocamos debajo del título con spacing
    title_bbox = draw.textbbox((tx, ty), title, font=font_b)
    title_bottom = title_bbox[3]
    sx = subtitle_pos[0] if subtitle_pos[0] != 0 else tx
    sy = subtitle_pos[1] if subtitle_pos[1] != 0 else title_bottom + spacing_title_sub
    draw.text((sx, sy), subtitle, fill=subtitle_color, font=font_s)

    # Código QR
    if qr_img:
        qr_resized = qr_img.resize((qr_size, qr_size), Image.LANCZOS)
        qr_x_safe = max(0, min(qr_pos[0], a4_w - qr_resized.width))
        qr_y_safe = max(0, min(qr_pos[1], a4_h - qr_resized.height))
        canvas.paste(qr_resized, (qr_x_safe, qr_y_safe), qr_resized)

    # Mapa
    if map_img:
        new_w = int(map_img.width * map_scale / 100)
        new_h = int(map_img.height * map_scale / 100)
        map_resized = map_img.resize((new_w, new_h), Image.LANCZOS)
        map_x_safe = max(0, min(map_pos[0], a4_w - map_resized.width))
        map_y_safe = max(0, min(map_pos[1], a4_h - map_resized.height))
        canvas.paste(map_resized, (map_x_safe, map_y_safe), map_resized)

    return canvas.convert("RGB")

# --- GENERACIÓN FINAL ---
if map_file and (qr_link or qr_file):
    map_img = load_image(map_file)

    # Muestra el mapa original
    st.subheader("🖼️ Vista previa del mapa original")
    st.image(map_img, width=300)

    # Genera o carga el QR
    qr_img = None
    if qr_link:
        qr_img = generate_qr_image(qr_link, qr_size, qr_error_correction)
    elif qr_file:
        qr_img = load_image(qr_file)

    if qr_img:
        st.subheader("🔳 Vista previa del QR")
        st.image(qr_img, width=150)

        # Composición final
        final_img = compose_layout(
            title_text, subtitle_text, map_img, qr_img,
            dpi=dpi, font_title=font_title, font_sub=font_sub,
            title_color=title_color, subtitle_color=subtitle_color,
            spacing_title_sub=spacing_title_sub,
            title_pos=(int(title_x), int(title_y)),
            subtitle_pos=(int(subtitle_x), int(subtitle_y)),
            qr_pos=(int(qr_x), int(qr_y)), qr_size=int(qr_size),
            map_pos=(int(map_x), int(map_y)), map_scale=int(map_scale),
            bg_color=bg_color, show_guides=show_guides,
            export_cut_line=export_cut_line,
            font_file=custom_font_file
        )

        st.subheader("🖼️ Previsualización A4")
        st.image(final_img, use_column_width=True)

        # Descargas
        safe_name = sanitize_filename(title_text or default_name or "map_qr")

        buf = io.BytesIO()
        final_img.save(buf, format="PNG", dpi=(dpi, dpi))
        buf.seek(0)
        st.download_button("📥 Descargar PNG", buf, f"{safe_name}_A4.png", "image/png")

        buf_pdf = io.BytesIO()
        final_img.save(buf_pdf, format="PDF", dpi=(dpi, dpi))
        buf_pdf.seek(0)
        st.download_button("📄 Descargar PDF", buf_pdf, f"{safe_name}_A4.pdf", "application/pdf")
    else:
        st.warning("Proporciona una URL o una imagen QR válida.")
else:
    st.info("Sube una imagen del mapa y una URL o QR para generar el diseño.")
