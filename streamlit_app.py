def compose_institutional_layout(map_img, qr_img, title, subtitle,
                                 bg="#ffffff", font_title=70, font_sub=36,
                                 qr_px=250, margin_px=80, extra_space=120,
                                 map_offset_y=150, dpi=300,
                                 show_qr_border=True, qr_border_px=3,
                                 show_guides=False):
    """Diseño institucional con QR a la izquierda y mapa a la derecha, con guías opcionales.
       Dibuja: borde azul, línea roja central (sólida) y línea punteada que marca la 
       'mitad superior' (punteada y 3 px debajo de la línea central para distinguir)."""

    # A4 en pulgadas: 8.27 x 11.69
    a4_w_px = int(8.27 * dpi)
    a4_h_px = int(11.69 * dpi)

    # Lienzo base RGBA
    canvas = Image.new("RGBA", (a4_w_px, a4_h_px), bg)
    draw = ImageDraw.Draw(canvas)

    # --- GUÍAS (opcional) ---
    if show_guides:
        # Borde azul
        draw.rectangle([(0, 0), (a4_w_px - 1, a4_h_px - 1)], outline=(0, 100, 255), width=3)

        # Línea roja mitad horizontal (sólida)
        mid_y = a4_h_px // 2
        draw.line([(0, mid_y), (a4_w_px, mid_y)], fill=(255, 0, 0), width=2)

        # Línea punteada marcando "final de la mitad superior" (3 px debajo para distinguir)
        dash_y = mid_y + 3
        dash_len = 12
        gap = 8
        x = 0
        while x < a4_w_px:
            x_end = min(x + dash_len, a4_w_px)
            draw.line([(x, dash_y), (x_end, dash_y)], fill=(160, 32, 240), width=2)  # púrpura punteada
            x += dash_len + gap

        # Líneas verdes de márgenes (según margin_px)
        draw.line([(margin_px, 0), (margin_px, a4_h_px)], fill=(0, 200, 0), width=2)
        draw.line([(a4_w_px - margin_px, 0), (a4_w_px - margin_px, a4_h_px)], fill=(0, 200, 0), width=2)

        # Pequeñas etiquetas de texto en píxeles (opcionalmente visibles)
        try:
            small_font = ImageFont.truetype("DejaVuSans.ttf", 12)
        except Exception:
            small_font = ImageFont.load_default()
        draw.text((margin_px + 5, 5), f"margin {margin_px}px", fill=(0,0,0), font=small_font)
        draw.text((5, mid_y + 8), f"centro (y={mid_y}px)", fill=(255,0,0), font=small_font)
        draw.text((5, dash_y + 8), f"fin mitad superior (y={dash_y}px)", fill=(160,32,240), font=small_font)

    # --- Fuentes ---
    try:
        font_bold = ImageFont.truetype("DejaVuSans-Bold.ttf", font_title)
        font_subt = ImageFont.truetype("DejaVuSans.ttf", font_sub)
    except Exception:
        font_bold = ImageFont.load_default()
        font_subt = ImageFont.load_default()

    # Calcular tamaños de texto
    try:
        tb = draw.textbbox((0,0), title, font=font_bold)
        sb = draw.textbbox((0,0), subtitle, font=font_subt)
        title_w, title_h = tb[2]-tb[0], tb[3]-tb[1]
        sub_w, sub_h = sb[2]-sb[0], sb[3]-sb[1]
    except Exception:
        title_w, title_h = draw.textsize(title, font=font_bold)
        sub_w, sub_h = draw.textsize(subtitle, font=font_subt)

    # Ajuste de imágenes
    qr_img = qr_img.resize((qr_px, qr_px), Image.LANCZOS)
    max_map_w = int(a4_w_px * 0.55)
    max_map_h = int(a4_h_px * 0.45)
    mw, mh = map_img.size
    ratio = min(max_map_w/mw, max_map_h/mh, 1.0)
    map_resized = map_img.resize((int(mw*ratio), int(mh*ratio)), Image.LANCZOS)

    # Posiciones base
    content_top = int(a4_h_px * 0.08)
    left_x = margin_px
    right_x = a4_w_px - margin_px - map_resized.width

    # Título + subtítulo
    draw.text((left_x, content_top), title, fill=(0,0,0), font=font_bold)
    subtitle_y = content_top + title_h + 8
    draw.text((left_x, subtitle_y), subtitle, fill=(80,80,80), font=font_subt)

    # Línea divisoria
    line_y = subtitle_y + sub_h + 14
    draw.line((left_x, line_y, a4_w_px - margin_px, line_y), fill=(180,180,180), width=3)

    # QR
    qr_y = line_y + extra_space
    qr_x = left_x
    if show_qr_border:
        pad = 8
        box = (qr_x - pad, qr_y - pad, qr_x + qr_img.width + pad, qr_y + qr_img.height + pad)
        draw.rectangle(box, outline=(150,150,150), width=qr_border_px, fill=(255,255,255,0))
    canvas.paste(qr_img, (qr_x, qr_y), qr_img.split()[3] if qr_img.mode == "RGBA" else None)

    # Mapa
    map_y = content_top + map_offset_y
    canvas.paste(map_resized, (right_x, map_y), map_resized.split()[3] if map_resized.mode == "RGBA" else None)

    # Final RGB
    final = Image.new("RGB", canvas.size, bg)
    final.paste(canvas, mask=canvas.split()[3] if canvas.mode == "RGBA" else None)
    return final, {"a4_px": (a4_w_px, a4_h_px), "qr_pos": (qr_x, qr_y), "map_pos": (right_x, map_y)}
