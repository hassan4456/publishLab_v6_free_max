import os, asyncio, logging
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from agents.niche_scanner import get_hot_niches
from agents.review_analyzer import analyze
from agents.readability import fix as fix_readability
from agents.qr_generator import gen_qr
from agents.story_writer import write_story
from agents.image_gen import gen_img
from agents.interior_builder import build_interior_pdf
from agents.covers import build_print_cover_pdf, build_ebook_cover_jpg
from agents.ebook_builder import build_epub
from agents.aplus_generator import build_aplus_images

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("publishlab")

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")


# ---------------- Telegram handlers ----------------

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    c.user_data.clear()
    kb = [[InlineKeyboardButton("🔍 ابحث عن أفضل نيتشات (Amazon Live)", callback_data="live")]]
    await u.message.reply_text(
        "📚 PublishLab V7\n✅ نيتشات لايف من أمازون ✅ قصة كاملة ✅ صور ✅ Interior PDF\n"
        "✅ غلاف طباعة ✅ غلاف eBook ✅ ملف EPUB ✅ A+ Content ✅ QR\n\nدوس تبدأ:",
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def handle(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query
    await q.answer()
    data = q.data

    try:
        if data == "live":
            await _handle_live(q, c)
        elif data.startswith("niche_idx_"):
            await _handle_niche(q, c, int(data.replace("niche_idx_", "")))
        elif data == "pages_32":
            await _handle_write_story(q, c)
        elif data == "gen":
            await _handle_generate_all(q, c)
        elif data == "restart":
            c.user_data.clear()
            kb = [[InlineKeyboardButton("🔍 ابحث عن أفضل نيتشات (Amazon Live)", callback_data="live")]]
            await q.edit_message_text("🔄 يلا كتاب جديد! دوس تبدأ:", reply_markup=InlineKeyboardMarkup(kb))
        else:
            await q.edit_message_text("⚠️ الزرار ده مش متعرف، ابدأ من /start")
    except Exception as e:
        log.exception("handler failed for %s", data)
        await q.message.reply_text(f"⚠️ حصل خطأ: {e}\nجرب تاني أو ابدأ من /start")


async def _handle_live(q, c):
    await q.edit_message_text("🔍 بدور على أفضل نيتشات في أمازون دلوقتي...")
    niches, is_live = await asyncio.to_thread(get_hot_niches, 6)
    c.user_data["niches"] = niches

    status = "✅ بيانات LIVE من أمازون دلوقتي" if is_live else "⚠️ أمازون حظرت الطلب حاليًا - دي بيانات احتياطية (موسمي + أقوى نيتشات KDP معروفة)، مش لايف 100%"
    txt = f"{status}\n\nأفضل نيتشات كتب أطفال:\n"
    for i, n in enumerate(niches):
        txt += f"{i+1}. {n}\n"

    kb = [[InlineKeyboardButton(n[:40], callback_data=f"niche_idx_{i}")] for i, n in enumerate(niches)]
    await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))


async def _handle_niche(q, c, idx):
    niches = c.user_data.get("niches", [])
    if idx >= len(niches):
        await q.edit_message_text("⚠️ اختيار غير موجود، ابدأ من /start")
        return
    niche = niches[idx]
    c.user_data["niche"] = niche
    an = analyze(niche)
    txt = f"✅ النيتش: {niche}\n\nتحليل شكاوى المنافسين (1-star reviews):\n"
    for a in an:
        txt += f"❌ {a['complaint']}\n{a['solution']}\n\n"
    await q.edit_message_text(
        txt,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ ابدأ 32 صفحة KDP Safe", callback_data="pages_32")]])
    )


async def _handle_write_story(q, c):
    niche = c.user_data.get("niche", "emotional regulation for kids")
    await q.edit_message_text("✍️ بكتب القصة كاملة (عنوان + وصف + 32 صفحة)... استنى شوية")
    story = await asyncio.to_thread(write_story, niche, 32)
    story["pages"] = fix_readability(story["pages"])
    c.user_data["story"] = story
    await q.message.reply_text(
        f"✅ القصة جاهزة: {story.get('title','')}\n{story.get('description','')}\nعدد الصفحات: {len(story['pages'])}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎨 ولّد كل حاجة (صور + PDF + eBook + A+)", callback_data="gen")]])
    )


async def _handle_generate_all(q, c):
    story = c.user_data.get("story")
    if not story:
        await q.edit_message_text("⚠️ مفيش قصة محفوظة، ابدأ من الأول بـ /start")
        return

    await q.edit_message_text("🎨 بولد الصور... (ممكن ياخد دقيقة لدقيقتين)")
    pages = story["pages"]
    imgs = []
    for i, pg in enumerate(pages):
        prompt = pg.get("image_prompt") or pg.get("text", "children book scene")
        path = await asyncio.to_thread(gen_img, prompt, i)
        imgs.append(path)

    await q.message.reply_text("📄 بجمع Interior PDF...")
    interior_path = await asyncio.to_thread(build_interior_pdf, story, imgs)

    await q.message.reply_text("🎨 بعمل غلاف الطباعة وغلاف الـ eBook...")
    cover_source = imgs[0] if imgs else None
    print_cover_path = await asyncio.to_thread(build_print_cover_pdf, story.get("title", "My Book"), cover_source)
    ebook_cover_path = await asyncio.to_thread(build_ebook_cover_jpg, story.get("title", "My Book"), story.get("subtitle", ""), cover_source)

    await q.message.reply_text("📱 بجمع ملف الـ eBook (EPUB)...")
    epub_path = await asyncio.to_thread(build_epub, story, imgs, ebook_cover_path)

    await q.message.reply_text("🖼️ بولد صور A+ Content...")
    aplus_paths = await asyncio.to_thread(build_aplus_images, story, imgs, ebook_cover_path)

    qr_path = await asyncio.to_thread(gen_qr, story.get("title", "My Book"))

    # إرسال كل الملفات
    await q.message.reply_document(document=open(interior_path, "rb"), filename="interior.pdf", caption="📖 Interior PDF (جاهز للرفع على KDP - راجع الهوامش)")
    await q.message.reply_document(document=open(print_cover_path, "rb"), filename="print_cover_front_only.pdf", caption="🎨 غلاف الطباعة (Front فقط - محتاج تعمله Full Wrap في KDP Cover Creator)")
    await q.message.reply_photo(photo=open(ebook_cover_path, "rb"), caption="📱 غلاف الـ eBook (جاهز لرفع نسخة Kindle)")
    await q.message.reply_document(document=open(epub_path, "rb"), filename="ebook.epub", caption="📚 ملف الـ eBook (EPUB) - افتحه في Kindle Previewer قبل الرفع")
    for i, p in enumerate(aplus_paths):
        await q.message.reply_photo(photo=open(p, "rb"), caption=f"🖼️ A+ Content - موديول {i+1}/{len(aplus_paths)}")
    await q.message.reply_photo(photo=open(qr_path, "rb"), caption="🔗 QR Code للبونص")

    await q.message.reply_text(
        "✅ خلصنا! كل الملفات جاهزة.\n\n"
        "⚠️ قبل الرفع على KDP لازم تراجع:\n"
        "- الغلاف (Front فقط - محتاج Full Wrap بمقاسات دقيقة)\n"
        "- ملف الـ EPUB (افتحه في Kindle Previewer المجاني للتأكد إنه سليم)\n"
        "- A+ Content بتترفع من صفحة الكتاب في KDP بعد النشر مباشرة، مش أثناء الرفع",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 كتاب جديد", callback_data="restart")]])
    )


def main():
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN مش موجود في الـ environment variables")
    if not GEMINI_KEY:
        raise RuntimeError("GEMINI_API_KEY مش موجود في الـ environment variables")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle))
    app.run_polling()


if __name__ == "__main__":
    main()
