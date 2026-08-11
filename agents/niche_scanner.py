"""
بيدور على أفضل نيتشات كتب أطفال بالبحث الفعلي في صفحات Best Sellers بتاعة أمازون
(كتب أطفال Kindle + ورقي، إنجليزي أولًا لأن السوق الإنجليزي أكبر وأربح لـ KDP)
لو أمازون حظرت الطلب (بتحصل كتير مع سيرفرات زي Railway) بيرجع لتحليل موسمي احتياطي
وبيقول للمستخدم صراحة إن دي بيانات احتياطية مش لايف.
"""
import re
import requests
from collections import Counter
from bs4 import BeautifulSoup
from .seasonal_hunter import get_seasonal

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# أهم صفحات Best Sellers الخاصة بكتب الأطفال على أمازون (إنجليزي = أولوية)
AMAZON_URLS = [
    "https://www.amazon.com/Best-Sellers-Kindle-Store-Childrens-eBooks/zgbs/digital-text/6157140011",
    "https://www.amazon.com/best-sellers-books-Amazon/zgbs/books/4",
]

# قاموس كلمات مفتاحية بيربط كلمات العناوين بنيتشات معروفة نافعة لـ KDP
NICHE_KEYWORDS = {
    "Emotional Regulation / Big Feelings": ["feelings", "emotions", "calm", "big feelings", "meltdown"],
    "Anxiety / Worry": ["anxiety", "worry", "worries", "nervous"],
    "Anger Management": ["anger", "angry", "mad", "temper"],
    "Bedtime / Sleep": ["bedtime", "sleep", "goodnight", "night"],
    "Potty Training": ["potty", "toilet training"],
    "Starting School": ["first day", "school", "kindergarten"],
    "Sibling / New Baby": ["sibling", "new baby", "big brother", "big sister"],
    "Grief / Loss": ["grief", "loss", "goodbye", "miss you", "passed away"],
    "Divorce / Family Change": ["divorce", "separated families"],
    "Courage / Bravery": ["brave", "courage", "fear", "scared"],
    "Kindness / Empathy": ["kind", "kindness", "empathy", "friend"],
    "Growth Mindset": ["mindset", "try again", "mistakes", "persistence"],
    "Counting / ABC": ["counting", "numbers", "alphabet", "abc"],
    "Diversity / Adoption": ["adoption", "diverse", "different family"],
    "Gratitude / Mindfulness": ["gratitude", "mindful", "thankful"],
}


def _fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    if r.status_code != 200 or "captcha" in r.text.lower() or "api-services-support@amazon.com" in r.text:
        return None
    return r.text


def _extract_titles(html):
    soup = BeautifulSoup(html, "html.parser")
    titles = []
    # أمازون بتغيّر الـ class names باستمرار، فبندور بأكتر من طريقة
    for sel in ["div._cDEzb_p13n-sc-css-line-clamp-1_1Fn1y", "span.zg-text-center-align",
                "div.p13n-sc-truncate-desktop-type2", "img[alt]"]:
        for el in soup.select(sel):
            txt = el.get("alt") if el.name == "img" else el.get_text(strip=True)
            if txt and len(txt) > 4:
                titles.append(txt)
    return titles


def _bucket_titles(titles):
    counts = Counter()
    for title in titles:
        low = title.lower()
        for niche, keywords in NICHE_KEYWORDS.items():
            if any(k in low for k in keywords):
                counts[niche] += 1
    return counts


def get_hot_niches(limit=6):
    """
    بيرجع (list_of_niches, is_live)
    is_live=True يعني البيانات فعلاً من أمازون دلوقتي
    is_live=False يعني رجعنا للـ fallback الموسمي عشان أمازون حظرت الطلب
    """
    all_titles = []
    got_any_live_page = False
    for url in AMAZON_URLS:
        try:
            html = _fetch(url)
            if html:
                got_any_live_page = True
                all_titles.extend(_extract_titles(html))
        except requests.RequestException:
            continue

    if got_any_live_page and all_titles:
        counts = _bucket_titles(all_titles)
        if counts:
            ranked = [n for n, _ in counts.most_common(limit)]
            if ranked:
                return ranked, True

    # Fallback: موسمي + قايمة ثابتة من أقوى نيتشات KDP معروفة
    fallback = list(dict.fromkeys(get_seasonal() + [
        "Emotional Regulation / Big Feelings",
        "Anxiety / Worry",
        "Bedtime / Sleep",
        "Starting School",
        "Sibling / New Baby",
        "Growth Mindset",
    ]))[:limit]
    return fallback, False
