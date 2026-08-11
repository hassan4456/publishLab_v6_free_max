def fix(pages):
    fixed=[]
    for p in pages:
        txt=p.get('text','')
        if len(txt.split())>12:
            txt=' '.join(txt.split()[:12])+'.'
        p['text']=txt
        fixed.append(p)
    return fixed
