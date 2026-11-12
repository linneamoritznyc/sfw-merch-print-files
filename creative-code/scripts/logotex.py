import random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
N=3000; SS=2; cell=12
EB=(55,128,184); NAVY=(26,44,82); PY=(214,226,140); LB=(150,196,232)
r=random.Random(5)
def tex():
    t=Image.new('RGB',(N*SS,N*SS),NAVY); d=ImageDraw.Draw(t)
    for li,col in enumerate([PY,LB]):
        src=Image.new('L',(N,N),0)
        for k in range(4):
            p=Image.open(f'/home/claude/merch/micro/plate_{r.randrange(16)}.png').convert('RGBA').split()[3]
            s=r.randint(1600,2600); p=p.resize((s,s)).rotate(r.choice([0,90,180,270]))
            src.paste(p,(r.randint(-600,N-1200),r.randint(-600,N-1200)),p)
        A=np.asarray(src.filter(ImageFilter.GaussianBlur(5))).astype(float)/255
        off=li*cell/2
        for gy in np.arange(off,N,cell):
            row=A[min(N-1,int(gy))]
            for gx in np.arange(off+(cell/2 if int(gy/cell)%2 else 0),N,cell):
                v=row[min(N-1,int(gx))]
                if v<0.12: continue
                rad=cell*0.48*min(1,v)**0.6
                d.ellipse([(gx-rad)*SS,(gy-rad)*SS,(gx+rad)*SS,(gy+rad)*SS],fill=col)
    return t
lg=Image.open('/home/claude/merch/logos/SFW-logo-flower-colour.png').convert('RGBA').split()[3]
L=2400; m=Image.new('L',(N*SS,N*SS),0)
m.paste(lg.resize((L*SS,L*SS),Image.LANCZOS).point(lambda v:255 if v>127 else 0),((N-L)//2*SS,(N-L)//2*SS))
im=Image.new('RGB',(N*SS,N*SS),EB); im.paste(tex(),(0,0),m)
out=im.resize((N,N),Image.LANCZOS); a=np.asarray(out).astype(float)
g=np.random.default_rng(1).normal(0,1,a.shape[:2])
Image.fromarray((a*(1+0.03*g[...,None])).clip(0,255).astype(np.uint8)).save('SFW-logo-micrograph-blue.png')
