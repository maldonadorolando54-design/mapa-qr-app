import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io, os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mapa + QR (Diseño Moderno)", layout="centered")
st.title("🗺️ Mapa + QR — Versión Moderna Profesional")

st.markdown("""
Produce una hoja **A4 moderna y limpia** con:
- Título grande y elegante  
- Subtítulo + ubicación con estilo profesional  
- Línea divisoria minimalista  
- **QR con borde blanco y sombra sutil**  
- **Mapa grande con efecto flotante**  
- Todo en la **mitad superior de la página**
""")

# 🔄 Orden moderno: QR primero, mapa después
col1, col2 = st.columns(2)
with col1:
    qr_file = st.file_uploader("🔳 Sube la imagen del QR", type=["png", "jpg", "jpeg"])
with col2:
    map_file = st.file_uploader("🗺️ Sube la imagen del mapa", type=["png", "jpg", "jpeg"])

default_name = ""
if map_file:
    default_name = os.path.splitext(map_file.name)[0]

name = st.text_input("Título principal", value=default_name)
subtitle = st.text_input("Subtítulo institucional", value="Cong. Brescia Española")
location = st.text_input("Ubicación (línea con 📍)", value="📍 Brescia — Sant’Eufemia")

with st.expander("⚙️ Ajustes opcionales"):
    bg_color = st.color_picker("Color de fondo", "#f9f9f9")
    dpi = st.selectbox("Resolución (A4)", [150, 200, 300], index=2)
    font_title = st.slider("Tamaño título", 30, 120, 80)
    font_sub = st.slider("Tamaño subtítulo", 20, 70, 40)
    font_loc = st.slider("Tamaño ubicación", 15, 60, 30)
    qr_size = st.slider("Tamaño QR (px)", 150, 600, 250)
    margin = st.slider("Margen lateral (px)", 40, 200, 100)
    map_offset_y = st.slider("Altura mapa (px)", 0, 600, 180)
    shadow_strength = st.slider("Sombra mapa/QR (intensidad)", 0, 15, 6)

# --- FUNCIONES ---
def load_image(file):
    return Image.open(file).convert("RGBA")

def add_shadow(img, offset=(10,10), background="#000000", blur_radius=15, opacity=80):
    """Agrega sombra sutil a una imagen."""
    shadow = Image.new("RGBA", (img.width + abs(offset[0])*2, img.height + abs(offset[1])*2), (0,0,0,0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rectangle(
        [offset, (img.width + offset[0], img.height + offset[1])],
        fill=(*ImageColor.getrgb(background), opacity)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))
    base = Image.new("RGBA", shadow.size, (0,0,0,0))
    base.paste(shadow, (0,0))
    base.paste(img, (abs(offset[0]), abs(offset[1])), img)
    return base

def compose_modern(map_img, qr_img, title, subtitle, location,
                   bg="#f9f9f9", font_title=80, font_sub=40, font_loc=30,
                   qr_px=250, margin_px=100, map_offset_y=180,
                   shadow_strength=6, dpi=300):
    """Diseño moderno y profesional A4."""
    a4_w_px = int(8.27 * dpi)
    a4_h_px = int(11.69 * dpi)
    canvas = Image.new("RGBA", (a4_w_px, a4_h_px), bg)
    draw = ImageDraw.Draw(canvas)

    # Fuentes
    try:
        font_bold = ImageFont.truetype("DejaVuSans-Bold.ttf", font_title)
        font_regular = ImageFont.truetype("DejaVuSans.ttf", font_sub)
        font_locf = ImageFont.truetype("DejaVuSans.ttf", font_loc)
    except:
        font_bold = ImageFont.load_default()
        font_regular = ImageFont.load_default()
        font_locf = ImageFont.load_default()

    # Texto principal
    top_y = int(a4_h_px * 0.08)
    left_x = margin_px

    draw.text((left_x, top_y), title, fill=(0,0,0), font=font_bold)
    sub_y = top_y + font_title + 10
    draw.text((left_x, sub_y), subtitle, fill="#555555", font=font_regular)
    loc_y = sub_y + font_sub + 5
    draw.text((left_x, loc_y), location, fill="#777777", font=font_locf)

    # Línea divisoria
    line_y = loc_y + font_loc + 20
    draw.line((left_x, line_y, a4_w_px - margin_px, line_y), fill="#cccccc", width=2)

    # Procesar QR
    qr_img = qr_img.resize((qr_px, qr_px), Image.LANCZOS)
    qr_with_border = Image.new("RGBA", (qr_px + 20, qr_px + 20), "#ffffff")
    qr_with_border.paste(qr_img, (10,10), qr_img)
    qr_with_shadow = qr_with_border.filter(ImageFilter.GaussianBlur(shadow_strength))

    qr_y = line_y + 100
    canvas.paste(qr_with_shadow, (left_x, qr_y), qr_with_shadow)

    # Procesar mapa
    max_map_w = int(a4_w_px * 0.52)
    max_map_h = int(a4_h_px * 0.42)
    mw, mh = map_img.size
    ratio = min(max_map_w/mw, max_map_h/mh)
    map_img = map_img.resize((int(mw*ratio), int(mh*ratio)), Image.LANCZOS)
    map_with_shadow = map_img.filter(ImageFilter.GaussianBlur(shadow_strength//2))

    map_x = left_x + qr_px + margin_px
    map_y = top_y + map_offset_y
    canvas.paste(map_with_shadow, (map_x+6, map_y+6))
    canvas.paste(map_img, (map_x, map_y), map_img)

    # Convertir a RGB final
    final = Image.new("RGB", canvas.size, bg)
    final.paste(canvas, mask=canvas.split()[3] if canvas.mode == "RGBA" else None)
    return final

# --- PROCESO ---
if map_file and qr_file:
    map_img = load_image(map_file)
    qr_img = load_image(qr_file)

    final_img = compose_modern(
        map_img=map_img,
        qr_img=qr_img,
        title=name,
        subtitle=subtitle,
        location=location,
        bg=bg_color,
        font_title=font_title,
        font_sub=font_sub,
        font_loc=font_loc,
        qr_px=qr_size,
        margin_px=margin,
        map_offset_y=map_offset_y,
        shadow_strength=shadow_strength,
        dpi=dpi
    )

    st.subheader("🖼️ Vista previa moderna:")
    st.image(final_img, use_column_width=True)

    buf = io.BytesIO()
    final_img.save(buf, format="PNG")
    buf.seek(0)
    st.download_button("📥 Descargar PNG", buf, f"{name}_A4_moderno.png", "image/png")

    buf_pdf = io.BytesIO()
    final_img.save(buf_pdf, format="PDF")
    buf_pdf.seek(0)
    st.download_button("📄 Descargar PDF", buf_pdf, f"{name}_A4_moderno.pdf", "application/pdf")
else:
    st.info("Sube primero el QR y luego el mapa para generar el diseño moderno.")
