from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import inch


def build_interior_pdf(story, imgs, trim_size=8.625):
    """يبني الـ interior PDF كامل بالصور والنصوص، مقاس مربع افتراضي 8.625x8.625 (مقاس شائع لكتب أطفال KDP)"""
    W = trim_size * inch
    H = trim_size * inch
    out = "/tmp/interior.pdf"
    c = canvas.Canvas(out, pagesize=(W, H))
    pages = story.get('pages', [])
    for i, pg in enumerate(pages):
        img = imgs[i] if i < len(imgs) else None
        if img:
            try:
                c.drawImage(img, 0, 0, W, H)
            except Exception:
                pass
        c.setFillColorRGB(1, 1, 1)
        c.setFillAlpha(0.85)
        c.rect(0, 0.25 * inch, W, 0.7 * inch, fill=1, stroke=0)
        c.setFillAlpha(1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(W / 2, 0.45 * inch, pg.get('text', '')[:70])
        c.showPage()
    c.save()
    return out
