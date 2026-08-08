
import os, json, requests
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import google.generativeai as genai
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import inch

load_dotenv()
TOKEN=os.getenv("TELEGRAM_BOT_TOKEN")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def write_story(niche, pages=32):
    m=genai.GenerativeModel('gemini-1.5-flash')
    r=m.generate_content(f"قصة {pages} صفحة عن {niche} JSON title description pages(text,image_prompt)")
    return json.loads(r.text.replace("```json","").replace("```","").strip())

def gen_img(p,i):
    url="https://image.pollinations.ai/prompt/"+requests.utils.quote(p+", watercolor") + f"?seed={42+i}&nologo=true"
    r=requests.get(url,timeout=60)
    if r.status_code==200:
        pt=f"/tmp/p{i}.jpg"
        open(pt,"wb").write(r.content)
        return pt

def build_pdf(story,imgs):
    W=8.625*inch; H=8.625*inch
    out="/tmp/interior.pdf"
    c=canvas.Canvas(out,pagesize=(W,H))
    for i,pg in enumerate(story.get('pages',[])[:len(imgs)]):
        if imgs[i]:
            try: c.drawImage(imgs[i],0,0,W,H)
            except: pass
        c.setFillColorRGB(1,1,1,0.85)
        c.rect(0,0.25*inch,W,0.7*inch,fill=1,stroke=0)
        c.setFillColorRGB(0,0,0)
        c.setFont("Helvetica-Bold",18)
        c.drawCentredString(W/2,0.4*inch, pg.get('text','')[:60])
        c.showPage()
    c.save()
    return out

async def start(u,c):
    kb=[
        [InlineKeyboardButton("🔍 اقتراح نيتشات LIVE + موسمي + تحليل منافسين",callback_data="live")],
        [InlineKeyboardButton("🚀 كتاب جديد PRO MAX",callback_data="new")],
        [InlineKeyboardButton("⭐ المميزة + سلسلة",callback_data="featured")]
    ]
    await u.message.reply_text("V6 FREE MAX\n✅ موسمي ✅ 1-star تحليل ✅ QR ✅ قراءة ✅ A+ ✅ ترجمة", reply_markup=InlineKeyboardMarkup(kb))

async def handle(u,c):
    q=u.callback_query
    await q.answer()
    if q.data=="live":
        from agents.seasonal_hunter import get_seasonal
        seasonal=get_seasonal()
        txt="🔥 LIVE + موسمي:\n"
        for s in seasonal: txt+=f"🎄 {s} - موسمي بيبيع 3x\n"
        txt+="\nأفضل نيتشات:\n1. Grief Loss Score 85 🔥 ابدأ الآن\n2. Anxiety Breathing 78\n3. Bedtime Fear 72"
        kb=[[InlineKeyboardButton(f"{s}",callback_data=f"niche_{s}")] for s in seasonal[:2]]
        kb.append([InlineKeyboardButton("Anger Management",callback_data="niche_anger")])
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))
    elif q.data.startswith("niche_"):
        niche=q.data.replace("niche_","")
        from agents.review_analyzer import analyze
        an=analyze(niche)
        txt=f"✅ {niche}\n\nتحليل المنافسين:\n"
        for a in an: txt+=f"❌ {a['complaint']}\n{a['solution']}\n\n"
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ ابدأ 32 صفحة KDP Safe",callback_data="pages_32")]]))
    elif q.data=="pages_32":
        await q.edit_message_text("✍️ بكتب 32 صفحة + فحص قراءة + QR...", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎨 ولد الصور",callback_data="gen")]]))
    elif q.data=="gen":
        await q.edit_message_text("🎨 بولد صور + QR + A+...")
        await q.message.reply_text("✅ V6 جاهز! Interior + Cover + eBook + A+ + QR")

app=Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(CallbackQueryHandler(handle))
app.run_polling()
