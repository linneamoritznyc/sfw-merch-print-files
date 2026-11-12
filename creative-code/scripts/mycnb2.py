import math, random, numpy as np
from PIL import Image, ImageDraw
def hx(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def grow(W,H,seed,bg,ink,origins,mode,SS=2):
    r=random.Random(seed); base=Image.new('RGB',(W*SS,H*SS),bg)
    layer=Image.new('RGBA',(W*SS,H*SS),(0,0,0,0)); d=ImageDraw.Draw(layer)
    segs=[]
    def walk(x,y,a,w,gen,life,bias):
        for i in range(life):
            if bias is not None: a=a*0.97+bias*0.03 if abs(a-bias)<math.pi else a
            a+=r.gauss(0,0.09+0.03*gen); L=r.uniform(4,7)
            nx,ny=x+L*math.cos(a),y+L*math.sin(a)
            segs.append((x,y,nx,ny,w,gen)); x,y=nx,ny; w=max(0.6,w*0.996)
            if not(-40<x<W+40 and -40<y<H+40): return
            if gen<5 and r.random()<0.022/(1+gen*0.3):
                walk(x,y,a+r.choice([-1,1])*r.uniform(0.35,0.9),w*0.62,gen+1,int(life*r.uniform(0.35,0.7)),None)
    for (ox,oy,n) in origins:
        for k in range(n):
            a=r.uniform(0,6.283); bias=None
            if mode=='rising': a=-math.pi/2+r.gauss(0,0.7); bias=-math.pi/2
            walk(ox*W,oy*H,a,r.uniform(5,8),0,r.randint(260,420),bias)
    for (x,y,nx,ny,w,gen) in segs:
        al=int(255*[1.0,0.75,0.5,0.35,0.22,0.15][min(gen,5)])
        d.line([(x*SS,y*SS),(nx*SS,ny*SS)],fill=ink+(al,),width=max(1,int(w*SS)))
    base=base.convert('RGBA'); base.alpha_composite(layer); out=base.convert('RGB').resize((W,H),Image.LANCZOS)
    a=np.asarray(out).astype(float); g=np.random.default_rng(seed).normal(0,1,a.shape[:2])
    return Image.fromarray((a*(1+0.02*g[...,None])).clip(0,255).astype(np.uint8))
W,H=1800,3000
V=[('spore-navy',hx('1A2C52'),hx('F4F1EA'),[(0.55,0.5,9)],'spore'),
   ('colonies-cream',hx('F4F1EA'),hx('4A2030'),[(0.3,0.25,4),(0.75,0.55,4),(0.4,0.85,4)],'colonies'),
   ('rising-deepgreen',hx('22371F'),hx('CBD696'),[(0.3,1.0,5),(0.7,1.0,5)],'rising'),
   ('spore-lilac',hx('C8B6E2'),hx('2E1B3A'),[(0.5,0.45,9)],'spore'),
   ('spore-sage',hx('A8B49A'),hx('22371F'),[(0.4,0.4,8)],'spore'),
   ('colonies-soil',hx('4F3433'),hx('E0B38A'),[(0.3,0.3,4),(0.7,0.6,4),(0.45,0.9,4)],'colonies'),
   ('rising-cream',hx('F4F1EA'),hx('1A2C52'),[(0.25,1.0,5),(0.6,1.0,5),(0.9,1.0,4)],'rising'),
   ('spore-purple',hx('6B4C7A'),hx('F4F1EA'),[(0.5,0.55,9)],'spore')]
S=Image.new('RGB',(4*380+20,2*680+20),(40,40,40))
for i,(n,bg,ink,o,m) in enumerate(V):
    im=grow(W,H,i+21,bg,ink,o,m); im.resize((900,1500),Image.LANCZOS).save(f'SFW-journalbook-myc2-{n}.png'); S.paste(im.resize((360,600)),(20+(i%4)*380,30+(i//4)*680))
S.save('SFW-journalbook-myc2-preview.jpg',quality=90)
