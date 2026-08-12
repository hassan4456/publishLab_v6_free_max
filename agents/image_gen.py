import requests


def gen_img(prompt, i, style="watercolor, children book illustration"):
    """يولد صورة مجانية عن طريق Pollinations ويحفظها محليًا، يرجع المسار أو None"""
    url = (
        "https://image.pollinations.ai/prompt/"
        + requests.utils.quote(f"{prompt}, {style}")
        + f"?seed={42 + i}&nologo=true&width=1024&height=1024"
    )
    for attempt in range(2):
        try:
            r = requests.get(url, timeout=35)
            if r.status_code == 200 and r.content and len(r.content) > 500:
                pt = f"/tmp/p{i}.jpg"
                with open(pt, "wb") as f:
                    f.write(r.content)
                return pt
        except requests.RequestException:
            pass
    return None
