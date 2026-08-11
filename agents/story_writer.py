import json
import google.generativeai as genai


def write_story(niche, pages=32):
    """يكتب قصة أطفال كاملة (عنوان + وصف + صفحات) عن طريق Gemini، يرجع dict"""
    m = genai.GenerativeModel('gemini-1.5-flash')
    prompt = (
        f"Write a children's picture book story, {pages} pages, about: {niche}. "
        "Return ONLY valid JSON, no explanation, no markdown fences, in this exact shape: "
        '{"title": "string", "subtitle": "string", "description": '
        '"2-3 sentence back-cover style description for Amazon KDP", '
        '"pages": [{"text": "short kid-friendly sentence for this page", '
        '"image_prompt": "detailed visual description for an illustrator"}], '
        '"aplus_bullets": ["3 short marketing bullet points about why parents will love this book"]}'
    )
    r = m.generate_content(prompt)
    raw = r.text.replace("```json", "").replace("```", "").strip()
    data = json.loads(raw)
    if "pages" not in data or not data["pages"]:
        raise ValueError("Gemini رجّع بيانات ناقصة، جرب تاني")
    data.setdefault("subtitle", "")
    data.setdefault("description", "")
    data.setdefault("aplus_bullets", [])
    return data
