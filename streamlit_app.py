
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io, os

# Librería para generar QR
# instalar con: pip install qrcode[pil]
import qrcode

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mapa + QR (Diseño final)", layout="centered")
st.title("🗺️ Mapa + QR — Estilo Institucional Final")

st.markdown("""
**Genera una hoja A4 profesional con:**
- Título y subtítulo arriba a la izquierda  
- Línea divisoria  
- **QR a la izquierda** (se puede subir imagen o generar desde URL)  
- **Mapa a la derecha**, más abajo  
- Todo contenido en la mitad superior del A4
""")

# Input files / link
col1, col2 = st.columns(2)
with col1:
    qr_link = st.text_input("🔗 QR — URL (si pones aquí, se generará el QR automáticamente)")
    qr_file = st.file_uploader("🔳 (Opcional) Sube la imagen del QR (si no pones URL)", type=["png", "jpg", "jpeg"])
with col2:
    map_file = st.file_uploader("🗺️ Sube la imagen del mapa", type=["png", "jpg", "jpeg"])

default_name = ""
if map_file is not None:
    default_name = os.path.splitext(map_file.name)[0]

name = st.text_input("Título principal", value=default_name)
subtitle = st.text_input("Subtítulo (debajo del título)", value="Cong. Brescia Española")

# Mover ajustes al sidebar para una UI más limpia
with st.sidebar.expander("⚙️ Ajustes opcionales", expanded=True):
    bg_color = st.color_picker("Color de fondo", "#ffffff")
    dpi = st.selectbox("Resolución (A4 DPI)", [150, 200, 300], index=2)
    font_title = st.slider("Tamaño del título (px)", 20, 120, 70)
    font_sub = st.slider("Tamaño del subtítulo (px)", 10, 60, 36)
    qr_size = st.slider("Tamaño final del QR (px)", 100, 600, 250)
    margin = st.slider("Margen lateral (px)", 20, 200, 80)
    extra_space = st.slider("Espacio entre línea y QR (px)", 0, 400, 120)
    map_offset_y = st.slider("Desplazamiento vertical del mapa (px)", 0, 600, 150)
    show_qr_border = st.checkbox("Dibujar borde alrededor del QR", value=True)
    qr_border_px = st.slider("Grosor borde QR (px)", 1, 10, 3)
    qr_error_correction = st.selectbox("Corrección de error QR",
                                       ["LOW (7%)", "MEDIUM (15%)", "QUARTILE (25%)", "HIGH (30%)"],
                                       index=2)

# --- FUNCIONES ---
def load_image(file):
    img = Image.open(file)
    if img.mode not in ("RGBA", "LA"):
        img = img.convert("RGBA")
    return img

def generate_qr_image_from_link(url, qr_px=250, error_level="QUARTILE"):
    """Genera un PIL Image RGBA del QR desde una URL.
       error_level: 'LOW'|'MEDIUM'|'QUARTILE'|'HIGH'
    """
    # Mapear el nivel de corrección
    ec_map = {
        "LOW": qrcode.constants.ERROR_CORRECT_L,
        "MEDIUM": qrcode.constants.ERROR_CORRECT_M,
        "QUARTILE": qrcode.constants.ERROR_CORRECT_Q,
        "HIGH": qrcode.constants.ERROR_CORRECT_H,
    }
    ec = ec_map.get(error_level, qrcode.constants.ERROR_CORRECT_Q)

    # Generador QR: parametrizado para obtener buena resolución luego del resize
    qr = qrcode.QRCode(
        version=None,
        error_correction=ec,
        box_size=10,  # caja grande para densidad; luego redimensionamos
        border=4
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    # Redimensionar al tamaño deseado (mantener nitidez con LANCZOS)
    img = img.resize((qr_px, qr_px), Image.LANCZOS)
    return img

def compose_institutional_layout(map_img, qr_img, title, subtitle,
                                 bg="#ffffff", font_title=70, font_sub=36,
                                 qr_px=250, margin_px=80, extra_space=120,
                                 map_offset_y=150, dpi=300,
                                 show_qr_border=True, qr_border_px=3):
    """Diseño institucional con QR a la izquierda y mapa a la derecha."""

    # A4 en pulgadas: 8.27 x 11.69
    a4_w_px = int(8.27 * dpi)
    a4_h_px = int(11.69 * dpi)

    # Lienzo base RGBA
    canvas = Image.new("RGBA", (a4_w_px, a4_h_px), bg)
    draw = ImageDraw.Draw(canvas)

    # Fuentes: intentamos cargar DejaVu (común en muchas instalaciones)
    try:
        font_bold = ImageFont.truetype("DejaVuSans-Bold.ttf", font_title)
        font_subt = ImageFont.truetype("DejaVuSans.ttf", font_sub)
    except Exception:
        font_bold = ImageFont.load_default()
        font_subt = ImageFont.load_default()

    # calcular bounding boxes de texto
    try:
        tb = draw.textbbox((0,0), title, font=font_bold)
        sb = draw.textbbox((0,0), subtitle, font=font_subt)
        title_w, title_h = tb[2]-tb[0], tb[3]-tb[1]
        sub_w, sub_h = sb[2]-sb[0], sb[3]-sb[1]
    except Exception:
        title_w, title_h = draw.textsize(title, font=font_bold)
        sub_w, sub_h = draw.textsize(subtitle, font=font_subt)

    # Asegurar QR al tamaño solicitado (si vino de archivo y es distinto)
    qr_img = qr_img.resize((qr_px, qr_px), Image.LANCZOS)

    # Redimensionar mapa para caber en área derecha
    max_map_w = int(a4_w_px * 0.55)
    max_map_h = int(a4_h_px * 0.45)
    mw, mh = map_img.size
    ratio = min(max_map_w/mw, max_map_h/mh, 1.0)  # evitamos upscaling
    map_resized = map_img.resize((int(mw*ratio), int(mh*ratio)), Image.LANCZOS)

    # Coordenadas base
    content_top = int(a4_h_px * 0.08)  # espacio arriba
    left_x = margin_px
    # Map aligned right
    right_x = a4_w_px - margin_px - map_resized.width

    # Título y subtítulo (arriba izquierda)
    draw.text((left_x, content_top), title, fill=(0,0,0), font=font_bold)
    subtitle_y = content_top + title_h + 8
    draw.text((left_x, subtitle_y), subtitle, fill=(80,80,80), font=font_subt)

    # Línea divisoria (anchura completa menos márgenes)
    line_y = subtitle_y + sub_h + 14
    draw.line((left_x, line_y, a4_w_px - margin_px, line_y), fill=(180,180,180), width=3)

    # Coordenadas para QR
    qr_y = line_y + extra_space
    qr_x = left_x

    # Dibujar fondo/borde del QR si se desea
    if show_qr_border:
        pad = 8
        box = (qr_x - pad, qr_y - pad, qr_x + qr_img.width + pad, qr_y + qr_img.height + pad)
        draw.rectangle(box, outline=(150,150,150), width=qr_border_px, fill=(255,255,255,0))

    # Pegar QR (usar la máscara alpha solo si la imagen la tiene)
    if qr_img.mode == "RGBA":
        canvas.paste(qr_img, (qr_x, qr_y), qr_img.split()[3])
    else:
        canvas.paste(qr_img, (qr_x, qr_y))

    # Pegar mapa (a la derecha, más abajo)
    map_y = content_top + map_offset_y
    if map_resized.mode == "RGBA":
        canvas.paste(map_resized, (right_x, map_y), map_resized.split()[3])
    else:
        canvas.paste(map_resized, (right_x, map_y))

    # Convertir a RGB final para exportar (PDF, PNG)
    final = Image.new("RGB", canvas.size, bg)
    final.paste(canvas, mask=canvas.split()[3] if canvas.mode == "RGBA" else None)
    return final, {"a4_px": (a4_w_px, a4_h_px), "qr_pos": (qr_x, qr_y), "map_pos": (right_x, map_y)}

# --- PROCESO ---
if map_file is not None and (qr_link.strip() or qr_file is not None):
    # Cargar mapa
    map_img = load_image(map_file)

    # Preparar QR: priorizamos la URL si viene, si no usamos archivo subido
    if qr_link.strip():
        # generar
        # Mapear seleccion de correccion de error
        ec_choice = {"LOW (7%)": "LOW", "MEDIUM (15%)": "MEDIUM", "QUARTILE (25%)": "QUARTILE", "HIGH (30%)": "HIGH"}
        ec_key = ec_choice.get(qr_error_correction, "QUARTILE")
        qr_img = generate_qr_image_from_link(qr_link.strip(), qr_px=qr_size, error_level=ec_key)
    else:
        qr_img = load_image(qr_file)

    final_img, meta = compose_institutional_layout(
        map_img=map_img,
        qr_img=qr_img,
        title=name or "Título",
        subtitle=subtitle or "",
        bg=bg_color,
        font_title=font_title,
        font_sub=font_sub,
        qr_px=qr_size,
        margin_px=margin,
        extra_space=extra_space,
        map_offset_y=map_offset_y,
        dpi=dpi,
        show_qr_border=show_qr_border,
        qr_border_px=qr_border_px
    )

    st.subheader("🖼️ Previsualización:")
    st.image(final_img, use_column_width=True)

    # Preparar buffers para descarga
    buf = io.BytesIO()
    final_img.save(buf, format="PNG", dpi=(dpi, dpi))
    buf.seek(0)
    st.download_button("📥 Descargar PNG", data=buf, file_name=f"{name}_A4_institucional.png", mime="image/png")

    buf_pdf = io.BytesIO()
    final_img.save(buf_pdf, format="PDF", resolution=dpi)
    buf_pdf.seek(0)
    st.download_button("📄 Descargar PDF", data=buf_pdf, file_name=f"{name}_A4_institucional.pdf", mime="application/pdf")

    st.caption(f"A4 pixels (a {dpi} DPI): {meta['a4_px'][0]} × {meta['a4_px'][1]} px — QR en {meta['qr_pos']} — Mapa en {meta['map_pos']}")

else:
    st.info("Sube el mapa y proporciona una URL para el QR (o sube una imagen de QR) para generar el diseño.")
