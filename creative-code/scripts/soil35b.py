import math, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
exec(open('soilcase.py').read().split("SOIL=dict(")[0].split("def build(")[0])
LIT=(203,214,150); TOP=(92,109,46); SUB=(47,60,29); PAR=(33,54,30)
PUR=(150,112,190); PURD=(120,86,160); LIL=(200,182,226); PG=(214,226,160); BLUE=(120,170,214); CRM=(244,241,234); TAN=(200,155,123)
def wiggle_root(d,x,y,a,w,depth,rr,dep=0,col=PUR):
    pts=[]
    while w>1.6 and y<depth:
        a+=rr.gauss(0,0.07); a=0.94*a+0.06*(math.pi/2); x+=6*math.cos(a); y+=6*math.sin(a); w*=0.9955; pts.append((x,y,w))
        if rr.random()<0.022 and dep<5: wiggle_root(d,x,y,a+rr.choice([-1,1])*rr.uniform(0.6,1.1),w*0.62,depth,rr,dep+1,col)
    for (px,py,pw) in pts: d.ellipse([(px-pw/2)*SS,(py-pw/2)*SS,(px+pw/2)*SS,(py+pw/2)*SS],fill=col)
def make(name,seed,logo_mode):
    r=random.Random(seed)
    im=Image.new('RGB',(W*SS,H*SS),LIT); d=ImageDraw.Draw(im)
    s1=wave(seed+1,1150,45); s2=wave(seed+2,2000,40); s3=wave(seed+3,2780,40)
    for (a,b,c,dc) in [(s1,s2,TOP,(102,120,52)),(s2,s3,SUB,(56,70,34)),(s3,np.full(W,H+10.0),PAR,(40,63,35))]:
        m=band_mask(a,b); im.paste(Image.new('RGB',im.size,c),(0,0),m); dots(im,m,dc,seed+int(a.mean()),cell=12,dens=0.45,scale=70)
    # soft light line along each boundary
    for s in (s1,s2,s3):
        d.line([(x*SS,(s[x]+2)*SS) for x in range(0,W,6)],fill=(255,255,255),width=0)
    d=ImageDraw.Draw(im)
    # litter: real leaves resting on the surface, layered
    for k in range(40):
        x=r.uniform(-60,W+60); base=s1[int(min(W-1,max(0,x)))]
        y=base-r.uniform(15,170)
        col=r.choice([TOP,(120,138,64),TAN,(160,128,184),(150,166,90)])
        leaf(d,x,y,r.uniform(120,220),r.uniform(-0.35,0.35)+r.choice([0,0,math.pi]),col,LIT)
    # seedlings above
    for px,h in [(560,520),(1240,380)]:
        gy=s1[px]-120
        pts=[(px+14*math.sin(i/30),gy-i*h/80) for i in range(81)]; stroke(d,pts,18,10,(21,104,38))
        for side,ln,yo in [(-1,190,0.6),(1,210,0.82),(-1,150,1.0)]:
            leaf(d,px+side*ln*0.45,gy-h*yo,ln,side*(-0.5),(89,166,108),(21,104,38))
    # aggregates in topsoil
    for k in range(55):
        cx,cy=r.uniform(0,W),r.uniform(s1.mean()+70,s2.mean()-50); rx=r.uniform(12,30); blob(d,cx,cy,rx,rx*0.8,(74,90,36),k,0.2)
    # roots: purple, tapering, from both seedlings
    for j,(px,w0) in enumerate([(560,30),(1240,24)]):
        wiggle_root(d,px,s1[px]-120,math.pi/2,w0,s3.mean()+60,random.Random(seed*10+j))
    # fungal hyphae: fine pale green webs in topsoil around roots
    rr=random.Random(seed+5)
    for cx,cy in [(520,1550),(780,1750),(1250,1450),(1400,1800),(950,1350)]:
        hyphae(d,cx,cy,PG,rr.randint(0,999),22,150)
    # organisms
    nematode(d,1080,1680,360,0.25,LIL,1)
    nematode(d,420,2350,260,-0.5,LIL,2)
    amoeba(d,1450,2250,70,BLUE,SUB,3)
    # ciliate: oval with cilia ring
    cx,cy,rx,ry=330,1350,70,46
    for t in np.linspace(0,6.283,46):
        x0,y0=cx+rx*math.cos(t),cy+ry*math.sin(t); x1,y1=cx+(rx+22)*math.cos(t),cy+(ry+22)*math.sin(t)
        d.line([x0*SS,y0*SS,x1*SS,y1*SS],fill=BLUE,width=3*SS)
    d.ellipse([(cx-rx)*SS,(cy-ry)*SS,(cx+rx)*SS,(cy+ry)*SS],fill=BLUE)
    d.ellipse([(cx-20)*SS,(cy-12)*SS,(cx+20)*SS,(cy+12)*SS],outline=TOP,width=5*SS)
    # pebbles in subsoil
    for k in range(18):
        cx,cy=r.uniform(0,W),r.uniform(s2.mean()+80,s3.mean()-60); rx=r.uniform(16,40); blob(d,cx,cy,rx,rx*0.75,(70,86,42),k+300,0.15)
    # rocks in parent material, rounded with highlight, leaving logo space
    lx,ly=(W//2,H-330) if logo_mode=='bc' else (W-330,H-330)
    placed=0; tries=0
    while placed<11 and tries<400:
        tries+=1; cx,cy=r.uniform(-80,W+80),r.uniform(s3.mean()+150,H+80); rx=r.uniform(110,230)
        if math.hypot(cx-lx,cy-ly)<rx+320: continue
        blob(d,cx,cy,rx,rx*r.uniform(0.62,0.82),(76,92,44),placed,0.1); blob(d,cx-rx*0.18,cy-rx*0.2,rx*0.5,rx*0.26,(104,120,60),placed+60,0.1); placed+=1
    im=im.convert('RGBA')
    w=480; lg=Image.open('/home/claude/merch/logos/SFW-logo-flower-cream.png').convert('RGBA').resize((w*SS,w*SS),Image.LANCZOS)
    im.alpha_composite(lg,((lx-w//2)*SS,(ly-w//2)*SS))
    out=im.resize((W,H),Image.LANCZOS).convert('RGB'); a=np.asarray(out).astype(float)
    g=np.random.default_rng(seed).normal(0,1,a.shape[:2]); out=Image.fromarray((a*(1+0.025*g[...,None])).clip(0,255).astype(np.uint8))
    out.save(f'SFW-case-{name}.png'); return out
a=make('35b-soil-layers-logo-centre',7,'bc'); b=make('35c-soil-layers-logo-corner',11,'br')
s=Image.new('RGB',(2*620+20,1247),(226,222,214)); s.paste(a.resize((600,1227)),(20,10)); s.paste(b.resize((600,1227)),(640,10)); s.save('SFW-case-35-redesign.jpg',quality=90)
