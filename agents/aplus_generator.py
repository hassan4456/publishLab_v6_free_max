from PIL import Image, ImageDraw, ImageFont

W, H = 1464, 600  # مقاس موديول A+ القياسي على أمازون


def _font(size, bold=True):
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textbbox((0, 0), test, font=font)[2] <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _hero_module(title, description, cover_img_path):
    img = Image.new("RGB", (W, H), (255, 247, 235))
    draw = ImageDraw.Draw(img)
    if cover_img_path:
        try:
            cover = Image.open(cover_img_path).convert("RGB")
            cw, ch = int(H * 0.75), H  # عمودي
            cover = cover.resize((cw, ch))
            img.paste(cover, (60, 0))
        except Exception:
            pass
    text_x = 60 + int(H * 0.75) + 40
    draw.text((text_x, 80), title[:30], font=_font(46), fill=(30, 30, 30))
    for i, line in enumerate(_wrap(draw, description, _font(28, bold=False), W - text_x - 60)):
        draw.text((text_x, 170 + i * 40), line, font=_font(28, bold=False), fill=(70, 70, 70))
    out = "/tmp/aplus_1_hero.jpg"
    img.save(out, quality=92)
    return out


def _bullets_module(bullets):
    img = Image.new("RGB", (W, H), (235, 245, 250))
    draw = ImageDraw.Draw(img)
    draw.text((50, 40), "Why parents & kids love this book", font=_font(38), fill=(20, 20, 20))
    y = 130
    for b in bullets[:3]:
        draw.ellipse((50, y + 8, 74, y + 32), fill=(40, 130, 90))
        for i, line in enumerate(_wrap(draw, b, _font(30, bold=False), W - 140)):
            draw.text((90, y + i * 38), line, font=_font(30, bold=False), fill=(40, 40, 40))
        y += 130
    out = "/tmp/aplus_2_bullets.jpg"
    img.save(out, quality=92)
    return out


def _interior_preview_module(sample_img_path, title):
    img = Image.new("RGB", (W, H), (250, 250, 245))
    draw = ImageDraw.Draw(img)
    draw.text((50, 40), "A peek inside", font=_font(38), fill=(20, 20, 20))
    if sample_img_path:
        try:
            sample = Image.open(sample_img_path).convert("RGB")
            sample = sample.resize((420, 420))
            img.paste(sample, (60, 130))
            img.paste(sample, (520, 130))
            img.paste(sample, (980, 130))
        except Exception:
            pass
    out = "/tmp/aplus_3_preview.jpg"
    img.save(out, quality=92)
    return out


def build_aplus_images(story, imgs, cover_img_path):
    """يبني 3 صور A+ Content: Hero + Bullets + Interior Preview. يرجع list بمسارات الصور"""
    title = story.get("title", "My Book")
    description = story.get("description") or "A heartwarming story for kids."
    bullets = story.get("aplus_bullets") or [
        "Beautiful illustrations on every page",
        "Simple, age-appropriate language",
        "A great bedtime or classroom read",
    ]
    sample = imgs[0] if imgs else None
    return [
        _hero_module(title, description, cover_img_path),
        _bullets_module(bullets),
        _interior_preview_module(sample, title),
    ]
