from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import inch
from PIL import Image, ImageDraw, ImageFont


def build_print_cover_pdf(title, image_path, trim_size=8.625):
    """
    غلاف مبدئي (front cover فقط - بدون spine/back الرسمي).
    ملحوظة: ده مش الغلاف النهائي اللي يترفع على KDP - KDP محتاج full wrap
    (front+spine+back) بحساب دقيق لعدد الصفحات. استخدم KDP Cover Creator
    أو Canva لعمل الـ wrap الكامل باستخدام الصورة دي كنقطة بداية.
    """
    out = "/tmp/cover_front_only.pdf"
    W = trim_size * inch
    H = trim_size * inch
    c = canvas.Canvas(out, pagesize=(W, H))
    if image_path:
        try:
            c.drawImage(image_path, 0, 0, W, H)
        except Exception:
            pass
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, H * 0.38, W, H * 0.24, fill=1, stroke=0)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(W / 2, H / 2, title[:40])
    c.save()
    return out


def build_ebook_cover_jpg(title, subtitle, image_path):
    """
    غلاف eBook بمقاس Amazon القياسي (نسبة 1.6:1) - 1600x2560 بكسل.
    ده الغلاف اللي بيترفع لنسخة Kindle.
    """
    W, H = 1600, 2560
    if image_path:
        try:
            base = Image.open(image_path).convert("RGB").resize((W, H))
        except Exception:
            base = Image.new("RGB", (W, H), (250, 240, 220))
    else:
        base = Image.new("RGB", (W, H), (250, 240, 220))

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    band_top = int(H * 0.62)
    band_h = int(H * 0.22)
    draw.rectangle([0, band_top, W, band_top + band_h], fill=(255, 255, 255, 235))

    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    def center_text(text, y, font, fill):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) / 2, y), text, font=font, fill=fill)

    center_text(title[:36], band_top + 20, font_title, (20, 20, 20, 255))
    if subtitle:
        center_text(subtitle[:50], band_top + band_h - 70, font_sub, (60, 60, 60, 255))

    final = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    out = "/tmp/ebook_cover.jpg"
    final.save(out, quality=92)
    return out
