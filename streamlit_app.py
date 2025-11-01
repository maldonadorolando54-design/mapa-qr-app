import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io, os

# Intentar importar qrcode; si falta, mostrar instrucción al usuario
try:
    import qrcode
except Exception:
    qrcode = None

# --- INFORMACIÓN / REQUERIMIENTOS ---
st.set_page_config(page_title="Mapa + QR (Diseño final)", layout="centered")
st.title("🗺️ Mapa + QR — Estilo Institucional Final")

st.markdown("""
**Genera una hoja A4 profesional con:**
- Título y subtítulo arriba a la izquierda  
- Línea divisoria  
- **QR a la izquierda** (sube imagen o pon URL)  
- **Mapa a la derecha**, más abajo  
- Vista previa con guías; exporta sin guías excepto la línea de corte.
""")

if qrcode is None:
    st.error(
        "La librería `qrcode` no está instalada en este entorno.\n\n"
        "Instálala localmente con `pip install qrcode[pil] Pillow` o agrega `qrcode[pil]` y `Pillow` a tu `requirements.txt` si estás en Streamlit Cloud."
    )

# --- INPUTS ---
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

# --- SIDEBAR: ajustes ---
with st.sidebar.expander("⚙️ Ajustes opcionales", expanded=True):
    bg_color = st.color_picker("Color de fondo", "#ffffff")
    dpi = st.selectbox("Resolución (A4 DPI)", [150, 200, 300], index=2)
    font_title = st.slider("Tamaño del título (px)", 20, 120, 70)
    font_sub = st.slider("Tamaño del subtítulo (px)", 10, 60, 36)
    qr_size = st.slider("Tamaño final del QR (px)", 100, 600, 250)
    margin = st.slider("Margen lateral (px)", 20, 200, 80)
    extra_space = st.slider("Espacio entre línea y QR (px)", 0, 400, 120)
    map_offset_y = st.slider("Desplazamiento vertical del mapa (px)", 0, 600, 150)
    show_qr_border = st.checkbox("Dibujar borde alrededor del QR (solo preview)", value=True)
    qr_border_px = st.slider("Grosor borde QR (px)", 1, 10, 3)
    qr_error_correction = st.selectbox("Corrección de error QR",
                                       ["LOW (7%)", "MEDIUM (15%)", "QUARTILE (25%)", "HIGH (30%)"],
                                       index=2)
    show_guides = st.checkbox("🧭 Mostrar guías en la previsualización (bordes, márgenes, centro, corte)", value=True)
    export_cut_line = st.checkbox("📐 Incluir línea de corte (mitad superior) en la exportación (PNG/PDF)", value=True)

# --- UTILIDADES ---
def load_image(file):
    img = Image.open(file)
    if img.mode not in ("RGBA", "LA"):
        img = img.convert("RGBA")
    return img

def generate_qr_image_from_link(url, qr_px=250, error_level="QUARTILE"):
    """Genera un PIL Image RGBA del QR desde una URL.
       error_level: 'LOW'|'MEDIUM'|'QUARTILE'|'HIGH'
    """
    if qrcode is None:
        raise RuntimeError("qrcode library not installed")

    ec_map = {
        "LOW": qrcode.constants.ERROR_CORRECT_L,
        "MEDIUM": qrcode.constants.ERROR_CORRECT_M,
        "QUARTILE": qrcode.constants.ERROR_CORRECT_Q,
        "HIGH": qrcode.constants.ERROR_CORRECT_H,
    }
    ec = ec_map.get(error_level, qrcode.constants.ERROR_CORRECT_Q)

    qr = qrcode.QRCode(
        version=None,
        error_correction=ec,
        box_size=10,
        border=4
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    img = img.resize((qr_px, qr_px), Image.LANCZOS)
    return img

def compose_institutional_layout(map_img, qr_img, title, subtitle,
                                 bg="#ffffff", font_title=70, font_sub=36,
                                 qr_px=250, margin_px=80, extra_space=120,
                                 map_offset_y=150, dpi=300,
                                 show_qr_border=True, qr_border_px=3,
                                 show_guides_preview=False,
                                 export_cut_line=False):
    """
    Devuelve (preview_img, final_img, meta).
    - preview_img: imagen con TODAS las guías (borde, márgenes, centro, línea punteada).
    - final_img: imagen para exportar (sin guías), pero si export_cut_line=True
                 añade la línea punteada de la mitad como referencia de corte.
    """

    # Tamaño A4 en px
    a4_w_px = int(8.27 * dpi)
    a4_h_px = int(11.69 * dpi)

    # Lienzos RGBA
    canvas_preview = Image.new("RGBA", (a4_w_px, a4_h_px), bg)
    draw_preview = ImageDraw.Draw(canvas_preview)

    canvas_final = Image.new("RGBA", (a4_w_px, a4_h_px), bg)
    draw_final = ImageDraw.Draw(canvas_final)

    # Posiciones de corte/mitad
    mid_y = a4_h_px // 2
    dash_y = mid_y + 3

    # --- GUÍAS EN PREVIEW ---
    if show_guides_preview:
        draw_preview.rectangle([(0, 0), (a4_w_px - 1, a4_h_px - 1)], outline=(0, 100, 255), width=3)
        draw_preview.line([(0, mid_y), (a4_w_px, mid_y)], fill=(255, 0, 0), width=2)

        dash_len = 12
        gap = 8
        x = 0
        while x < a4_w_px:
            x_end = min(x + dash_len, a4_w_px)
            draw_preview.line([(x, dash_y), (x_end, dash_y)], fill=(160, 32, 240), width=2)
            x += dash_len + gap

        draw_preview.line([(margin_px, 0), (margin_px, a4_h_px)], fill=(0, 200, 0), width=2)
        draw_preview.line([(a4_w_px - margin_px, 0), (a4_w_px - margin_px, a4_h_px)], fill=(0, 200, 0), width=2)

        try:
            small_font = ImageFont.truetype("DejaVuSans.ttf", 12)
        except Exception:
            small_font = ImageFont.load_default()
        draw_preview.text((margin_px + 5, 5), f"margin {margin_px}px", fill=(0,0,0), font=small_font)
        draw_preview.text((5, mid_y + 8), f"centro (y={mid_y}px)", fill=(255,0,0), font=small_font)
        draw_preview.text((5, dash_y + 8), f"fin mitad superior (y={dash_y}px)", fill=(160,32,240), font=small_font)

    # --- LÍNEA DE CORTE EN FINAL (opcional) ---
    if export_cut_line:
        dash_len = 12
        gap = 8
        x = 0
        while x < a4_w_px:
            x_end = min(x + dash_len, a4_w_px)
            draw_final.line([(x, dash_y), (x_end, dash_y)], fill=(0, 0, 0), width=1)
            x += dash_len + gap
        try:
            small_font = ImageFont.truetype("DejaVuSans.ttf", 11)
        except Exception:
            small_font = ImageFont.load_default()
        draw_final.text((5, dash_y + 6), f"fin mitad superior (y={dash_y}px)", fill=(0,0,0), font=small_font)

    # --- FUENTES ---
    try:
        font_bold = ImageFont.truetype("DejaVuSans-Bold.ttf", font_title)
        font_subt = ImageFont.truetype("DejaVuSans.ttf", font_sub)
    except Exception:
        font_bold = ImageFont.load_default()
        font_subt = ImageFont.load_default()

    # Calcular tamaños usando draw_preview como referencia
    try:
        tb = draw_preview.textbbox((0,0), title, font=font_bold)
        sb = draw_preview.textbbox((0,0), subtitle, font=font_subt)
        title_w, title_h = tb[2]-tb[0], tb[3]-tb[1]
        sub_w, sub_h = sb[2]-sb[0], sb[3]-sb[1]
    except Exception:
        title_w, title_h = draw_preview.textsize(title, font=font_bold)
        sub_w, sub_h = draw_preview.textsize(subtitle, font=font_subt)

    # Preparar imágenes: QR y mapa
    qr_resized = qr_img.resize((qr_px, qr_px), Image.LANCZOS)
    max_map_w = int(a4_w_px * 0.55)
    max_map_h = int(a4_h_px * 0.45)
    mw, mh = map_img.size
    ratio = min(max_map_w/mw, max_map_h/mh, 1.0)
    map_resized = map_img.resize((int(mw*ratio), int(mh*ratio)), Image.LANCZOS)

    # Posiciones base
    content_top = int(a4_h_px * 0.08)
    left_x = margin_px
    right_x = a4_w_px - margin_px - map_resized.width

    # Título/subtítulo en ambos canvases
    draw_preview.text((left_x, content_top), title, fill=(0,0,0), font=font_bold)
    draw_preview.text((left_x, content_top + title_h + 8), subtitle, fill=(80,80,80), font=font_subt)
    draw_final.text((left_x, content_top), title, fill=(0,0,0), font=font_bold)
    draw_final.text((left_x, content_top + title_h + 8), subtitle, fill=(80,80,80), font=font_subt)

    # Línea divisoria (preview y final)
    subtitle_y = content_top + title_h + 8
    line_y = subtitle_y + sub_h + 14
    draw_preview.line((left_x, line_y, a4_w_px - margin_px, line_y), fill=(180,180,180), width=3)
    draw_final.line((left_x, line_y, a4_w_px - margin_px, line_y), fill=(180,180,180), width=3)

    # QR: en preview con recuadro guía si corresponde; en final solo el QR
    qr_y = line_y + extra_space
    qr_x = left_x
    if show_qr_border:
        pad = 8
        box = (qr_x - pad, qr_y - pad, qr_x + qr_resized.width + pad, qr_y + qr_resized.height + pad)
        draw_preview.rectangle(box, outline=(150,150,150), width=qr_border_px, fill=(255,255,255,0))
    canvas_preview.paste(qr_resized, (qr_x, qr_y), qr_resized.split()[3] if qr_resized.mode == "RGBA" else None)
    canvas_final.paste(qr_resized, (qr_x, qr_y), qr_resized.split()[3] if qr_resized.mode == "RGBA" else None)

    # Mapa: en ambos
    map_y = content_top + map_offset_y
    canvas_preview.paste(map_resized, (right_x, map_y), map_resized.split()[3] if map_resized.mode == "RGBA" else None)
    canvas_final.paste(map_resized, (right_x, map_y), map_resized.split()[3] if map_resized.mode == "RGBA" else None)

    # Convertir a RGB
    final_preview = Image.new("RGB", canvas_preview.size, bg)
    final_preview.paste(canvas_preview, mask=canvas_preview.split()[3] if canvas_preview.mode == "RGBA" else None)

    final_export = Image.new("RGB", canvas_final.size, bg)
    final_export.paste(canvas_final, mask=canvas_final.split()[3] if canvas_final.mode == "RGBA" else None)

    meta = {"a4_px": (a4_w_px, a4_h_px), "qr_pos": (qr_x, qr_y), "map_pos": (right_x, map_y), "mid_y": mid_y, "dash_y": dash_y}
    return final_preview, final_export, meta

# --- PROCESO PRINCIPAL ---
if map_file is not None and (qr_link.strip() or qr_file is not None):
    # Cargar mapa
    map_img = load_image(map_file)

    # Preparar QR (url tiene prioridad)
    if qr_link.strip():
        # mapear corrección de error
        ec_choice = {"LOW (7%)": "LOW", "MEDIUM (15%)": "MEDIUM", "QUARTILE (25%)": "QUARTILE", "HIGH (30%)": "HIGH"}
        ec_key = ec_choice.get(qr_error_correction, "QUARTILE")
        try:
            qr_img = generate_qr_image_from_link(qr_link.strip(), qr_px=qr_size, error_level=ec_key)
        except Exception as e:
            st.error(f"Error al generar QR desde URL: {e}")
            st.stop()
    else:
        qr_img = load_image(qr_file)

    # Generar preview y final (export)
    preview_img, final_img, meta = compose_institutional_layout(
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
        qr_border_px=qr_border_px,
        show_guides_preview=show_guides,
        export_cut_line=export_cut_line
    )

    st.subheader("🖼️ Previsualización (guías visibles en pantalla):")
    st.image(preview_img, use_column_width=True)

    # Descargas (usar final_img)
    buf = io.BytesIO()
    final_img.save(buf, format="PNG", dpi=(dpi, dpi))
    buf.seek(0)
    st.download_button("📥 Descargar PNG", data=buf, file_name=f"{name}_A4_institucional.png", mime="image/png")

    buf_pdf = io.BytesIO()
    final_img.save(buf_pdf, format="PDF", resolution=dpi)
    buf_pdf.seek(0)
    st.download_button("📄 Descargar PDF", data=buf_pdf, file_name=f"{name}_A4_institucional.pdf", mime="application/pdf")

    st.caption(
        f"A4 px @ {dpi} DPI: {meta['a4_px'][0]}×{meta['a4_px'][1]} — QR en {meta['qr_pos']} — Mapa en {meta['map_pos']} — "
        f"mitad y corte en y={meta['dash_y']} px"
    )

else:
    st.info("Sube el mapa y proporciona una URL para el QR (o sube una imagen de QR) para generar el diseño.")
