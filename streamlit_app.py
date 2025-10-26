import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io, os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Mapa + QR (Diseño institucional)", layout="centered")
st.title("🗺️ Mapa + QR — Estilo Institucional (mitad superior A4)")

st.markdown("""
Crea una hoja **A4 vertical** con el formato profesional:
- **Título grande** arriba a la izquierda  
- **Subtítulo pequeño** debajo  
- **Línea divisoria**  
- **QR a la izquierda**  
- **Mapa grande a la derecha**  
Todo en la **mitad superior de la página**.
""")

col1, col2 = st.columns(2)
with col1:
    map_file = st.file_uploader("🗺️ Sube la imagen del mapa", type=["png", "jpg", "jpeg"])
with col2:
    qr_file = st.file_uploader("🔳 Sube la imagen del QR", type=["png", "jpg", "jpeg"])

default_name = ""
if map_file is not None:
    default_name = os.path.splitext(map_file.name)[0]

name = st.text_input("Título (arriba)", value=default_name)
subtitle = st.text_input("Subtítulo (debajo del título)", value="Cong. Brescia Española")

with st.expander("⚙️ Ajustes opcionales"):
    bg_color = st.color_picker("Color de fondo", "#ffffff")
    dpi = st.selectbox("Resolución (A4)", [150, 200, 300], index=2)
    font_title = st.slider("Tamaño del título", 20, 120, 70)
    font_sub = st.slider("Tamaño del subtítulo", 10, 60, 36)
    qr_size = st.slider("Tamaño del QR (px)", 100, 600, 250)
    margin = st.slider("Margen (px)", 20, 200, 80)

# --- FUNCIONES ---
def load_image(file):
    return Image.open(file).convert("RGBA")

def compose_institutional_layout(map_img, qr_img, title, subtitle,
                                 bg="#ffffff", font_title=70, font_sub=36,
                                 qr_px=250, margin_px=80, dpi=300):
    """Diseño tipo institucional: título + subtítulo + línea + QR izq + mapa der."""
    a4_w_px = int(8.27 * dpi)
    a4_h_px = int(11.69 * dpi)

    # Lienzo
    canvas = Image.new("RGBA", (a4_w_px, a4_h_px), bg)
    draw = ImageDraw.Draw(canvas)

    # Fuentes
    try:
        font_bold = ImageFont.truetype("DejaVuSans-Bold.ttf", font_title)
        font_subt = ImageFont.truetype("DejaVuSans.ttf", font_sub)
    except:
        font_bold = ImageFont.load_default()
        font_subt = ImageFont.load_default()

    # Cálculo de texto
    dummy = Image.new("RGBA", (10,10))
    d = ImageDraw.Draw(dummy)
    try:
        tb = d.textbbox((0,0), title, font=font_bold)
        sb = d.textbbox((0,0), subtitle, font=font_subt)
        title_w, title_h = tb[2]-tb[0], tb[3]-tb[1]
        sub_w, sub_h = sb[2]-sb[0], sb[3]-sb[1]
    except:
        title_w, title_h = d.textsize(title, font=font_bold)
        sub_w, sub_h = d.textsize(subtitle, font=font_subt)

    # Redimensionar QR
    qr_img = qr_img.resize((qr_px, qr_px), Image.LANCZOS)

    # Redimensionar mapa (grande)
    max_map_w = int(a4_w_px * 0.55)
    max_map_h = int(a4_h_px * 0.45)
    mw, mh = map_img.size
    ratio = min(max_map_w/mw, max_map_h/mh)
    map_img = map_img.resize((int(mw*ratio), int(mh*ratio)), Image.LANCZOS)

    # Coordenadas base
    content_top = int(a4_h_px * 0.1)
    left_x = margin_px
    right_x = left_x + qr_px + margin_px

    # Título
    draw.text((left_x, content_top), title, fill=(0,0,0), font=font_bold)
    subtitle_y = content_top + title_h + 10
    draw.text((left_x, subtitle_y), subtitle, fill=(80,80,80), font=font_subt)

    # Línea divisoria
    line_y = subtitle_y + sub_h + 20
    draw.line((left_x, line_y, a4_w_px - margin_px, line_y), fill=(180,180,180), width=3)

    # QR debajo de la línea
    qr_y = line_y + 20
    canvas.paste(qr_img, (left_x, qr_y), qr_img)

    # Mapa grande a la derecha
    map_y = content_top
    canvas.paste(map_img, (right_x, map_y), map_img)

    # Convertir a RGB
    final = Image.new("RGB", canvas.size, bg)
    final.paste(canvas, mask=canvas.split()[3] if canvas.mode == "RGBA" else None)
    return final

# --- PROCESO ---
if map_file and qr_file:
    map_img = load_image(map_file)
    qr_img = load_image(qr_file)

    final_img = compose_institutional_layout(
        map_img=map_img,
        qr_img=qr_img,
        title=name,
        subtitle=subtitle,
        bg=bg_color,
        font_title=font_title,
        font_sub=font_sub,
        qr_px=qr_size,
        margin_px=margin,
        dpi=dpi
    )

    st.subheader("🖼️ Previsualización:")
    st.image(final_img, use_column_width=True)

    buf = io.BytesIO()
    final_img.save(buf, format="PNG")
    buf.seek(0)
    st.download_button("📥 Descargar PNG", buf, f"{name}_A4_institucional.png", "image/png")

    buf_pdf = io.BytesIO()
    final_img.save(buf_pdf, format="PDF")
    buf_pdf.seek(0)
    st.download_button("📄 Descargar PDF", buf_pdf, f"{name}_A4_institucional.pdf", "application/pdf")
else:
    st.info("Sube el mapa y el QR para generar el diseño institucional.")
