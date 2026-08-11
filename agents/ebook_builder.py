import uuid
from ebooklib import epub


def build_epub(story, imgs, cover_jpg_path):
    """يبني ملف EPUB3 كامل (نسخة Kindle) بالصور مدمجة جوه كل صفحة"""
    book = epub.EpubBook()
    book.set_identifier(str(uuid.uuid4()))
    book.set_title(story.get("title", "My Book"))
    book.set_language("en")
    book.add_author("KDP Author")

    if cover_jpg_path:
        with open(cover_jpg_path, "rb") as f:
            book.set_cover("cover.jpg", f.read())

    chapters = []
    for i, pg in enumerate(story.get("pages", [])):
        img_tag = ""
        img_path = imgs[i] if i < len(imgs) else None
        if img_path:
            img_name = f"images/page_{i}.jpg"
            with open(img_path, "rb") as f:
                book.add_item(epub.EpubItem(uid=f"img_{i}", file_name=img_name, media_type="image/jpeg", content=f.read()))
            img_tag = f'<img src="{img_name}" style="max-width:100%;"/>'

        c = epub.EpubHtml(title=f"Page {i+1}", file_name=f"page_{i}.xhtml", lang="en")
        c.content = f"<html><body>{img_tag}<p style='text-align:center;font-size:1.4em;'>{pg.get('text','')}</p></body></html>"
        book.add_item(c)
        chapters.append(c)

    book.toc = tuple(chapters)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + chapters

    out = "/tmp/ebook.epub"
    epub.write_epub(out, book)
    return out
