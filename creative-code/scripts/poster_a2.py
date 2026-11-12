import math, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
Image.MAX_IMAGE_PIXELS=None
W,H=4961,7016; CELL=30
OLV=(91,107,46); FWG=(21,104,38); LGR=(89,166,108); LIME=(190,214,90)
PUR=(107,76,122); LIL=(200,182,226); PG=(203,214,150); EB=(55,128,184); PY=(214,226,140); LB=(150,196,232)
def texture(base,dots,seed):
    r=random.Random(seed); t=Image.new('RGB',(W,H),base); d=ImageDraw.Draw(t)
    for li,col in enumerate(dots):
        src=Image.new('L',(W,H),0)
        for k in range(4):
            p=Image.open(f'/home/claude/merch/micro/plate_{r.randrange(16)}.png').convert('RGBA').split()[3]
            m=Image.new('L',p.size,0); c=p.width/2; rr=p.width*0.465; ImageDraw.Draw(m).ellipse([c-rr,c-rr,c+rr,c+rr],fill=255)
            p=Image.fromarray(np.minimum(np.asarray(p),np.asarray(m)))
            s=r.randint(3000,4600); p=p.resize((s,s)).rotate(r.choice([0,90,180,270]))
            src.paste(p,(r.randint(-1800,W-2000),r.randint(-1800,H-2000)),p)
        A=np.asarray(src.filter(ImageFilter.GaussianBlur(8))).astype(float)/255
        off=li*CELL/2
        for gy in np.arange(off,H,CELL):
            row=A[min(H-1,int(gy))]
            for gx in np.arange(off+(CELL/2 if int(gy/CELL)%2 else 0),W,CELL):
                v=row[min(W-1,int(gx))]
                if v<0.12: continue
                rad=CELL*0.48*min(1,v)**0.6; d.ellipse([gx-rad,gy-rad,gx+rad,gy+rad],fill=col)
    return t
def blob(cx,cy,R,seed,sy=1.2):
    m=Image.new('L',(W,H),0)
    pts=[(cx+R*(1+0.18*math.sin(3*t+seed)+0.1*math.sin(5*t))*math.cos(t),cy+R*sy*(1+0.15*math.cos(2*t+seed))*math.sin(t)) for t in np.linspace(0,6.283,240)]
    ImageDraw.Draw(m).polygon(pts,fill=255); return m
def hypha(seed,starts):
    rr=random.Random(seed); m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
    def br(x,y,a,w,dep):
        while w>90 and -500<x<W+500 and -500<y<H+500:
            a+=rr.gauss(0,0.035); nx,ny=x+30*math.cos(a),y+30*math.sin(a)
            d.line([x,y,nx,ny],fill=255,width=int(w)); d.ellipse([nx-w/2,ny-w/2,nx+w/2,ny+w/2],fill=255); x,y=nx,ny; w*=0.9985
            if rr.random()<0.0035 and dep<1: br(x,y,a+rr.choice([-1,1])*rr.uniform(0.6,0.9),w*0.68,dep+1)
    for (x,y,a,w) in starts: br(x,y,a,w,0)
    return m.filter(ImageFilter.GaussianBlur(2)).point(lambda v:255 if v>127 else 0)
im=Image.new('RGB',(W,H),OLV)
mb=blob(3300,2000,1650,2,1.15)          # blue, top right
mp=blob(1350,5300,1600,9,1.05)          # purple, bottom left
mh=hypha(6,[(-300,900,0.78,520),(W+300,5200,3.55,330)])
im.paste(texture(EB,[PY,LB],12),(0,0),mb)
im.paste(texture(PUR,[LIL,PG],11),(0,0),mp)
im.paste(texture(FWG,[LGR,LIME],13),(0,0),mh)
# logo bottom right
w=900; lg=Image.open('/home/claude/merch/logos/SFW-logo-flower-cream.png').convert('RGBA').resize((w,w),Image.LANCZOS)
w=750; lg=lg.resize((w,w),Image.LANCZOS)
im=im.convert('RGBA'); im.alpha_composite(lg,(W-300-w,H-300-w)); im=im.convert('RGB')
a=np.asarray(im).astype(float); g=np.random.default_rng(3).normal(0,1,a.shape[:2])
im=Image.fromarray((a*(1+0.03*g[...,None])).clip(0,255).astype(np.uint8))
im.save('SFW-poster-A2-micro-shapes.png'); im.resize((1000,1414),Image.LANCZOS).save('/tmp/a2.png')
