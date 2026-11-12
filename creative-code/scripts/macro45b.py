import numpy as np
from PIL import Image, ImageFilter
exec(open('macro45.py').read().split("n,bg,ink")[0])
LOGOP='/home/claude/merch/logos/SFW-logo-flower-cream.png'
def macro_nodisc(bg,ink,pi,size,ox,oy,cx,cy,lw,seed=0):
    im=canvas(bg); im.alpha_composite(PL[0],(ox*SS,oy*SS))
    lg=Image.open(LOGOP).convert('RGBA').resize((lw*SS,lw*SS),Image.LANCZOS)
    halo=lg.split()[3].filter(ImageFilter.MaxFilter(61)).filter(ImageFilter.GaussianBlur(6)).point(lambda v:255 if v>100 else 0)
    flat=Image.new('RGBA',lg.size,bg+(255,)); im.paste(flat,((cx-lw//2)*SS,(cy-lw//2)*SS),halo)
    im.alpha_composite(lg,((cx-lw//2)*SS,(cy-lw//2)*SS))
    out=im.resize((W,H),Image.LANCZOS).convert('RGB'); a=np.asarray(out).astype(float); g=np.random.default_rng(seed).normal(0,1,a.shape[:2])
    return Image.fromarray((a*(1+0.05*g[...,None])).clip(0,255).astype(np.uint8))
n,bg,ink,pi,sz,uv,pp='45-macro-purple-lilac',PUR,LIL,5,4800,(0.5,0.38),(900,1500)
PL=[plate_clean(pi,ink,sz,0)]; ox,oy=place(*uv,*pp,sz)
a=macro_nodisc(bg,ink,pi,sz,ox,oy,900,3050,700,seed=2); a.save(f'SFW-case-{n}.png'); a.resize((900,1840)).save('SFW-case-45-fixed-preview.png')
