import math, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
W,H=1800,3680; SS=2
def hx(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
LOGO='/home/claude/merch/logos/'
def wave(seed,base,amp=45):
    r=np.random.default_rng(seed); x=np.linspace(0,1,W)
    return base+sum(amp/(k+1)*np.sin(2*math.pi*(k+1)*x*r.uniform(0.7,1.3)+r.uniform(0,6)) for k in range(4))
def band_mask(top,bot):
    yy=np.arange(H)[:,None]; m=((yy>=top[None,:])&(yy<bot[None,:])).astype(np.uint8)*255
    return Image.fromarray(m).resize((W*SS,H*SS),Image.BILINEAR)
def dots(im,mask,col,seed,cell=14,dens=0.35,scale=90):
    # halftone grain inside a mask, driven by smooth noise
    r=np.random.default_rng(seed); n=r.random((H//scale+3,W//scale+3))
    N=np.asarray(Image.fromarray((n*255).astype(np.uint8)).resize((W,H),Image.BICUBIC)).astype(float)/255
    M=np.asarray(mask.resize((W,H)))>127
    d=ImageDraw.Draw(im)
    for gy in np.arange(0,H,cell):
        off=cell/2 if int(gy/cell)%2 else 0
        for gx in np.arange(off,W,cell):
            y,x=min(H-1,int(gy)),min(W-1,int(gx))
            if not M[y,x]: continue
            v=(N[y,x]-(1-dens))/dens
            if v<=0.05: continue
            rad=cell*0.45*min(1,v)**0.7; d.ellipse([(gx-rad)*SS,(gy-rad)*SS,(gx+rad)*SS,(gy+rad)*SS],fill=col)
def blob(d,cx,cy,rx,ry,col,seed,k=0.15):
    r=random.Random(seed); ph=[r.uniform(0,6) for _ in range(3)]
    pts=[(cx+rx*(1+k*math.sin(2*t+ph[0])+k*0.6*math.sin(3*t+ph[1]))*math.cos(t),cy+ry*(1+k*math.sin(2*t+ph[2]))*math.sin(t)) for t in np.linspace(0,6.283,90)]
    d.polygon([(x*SS,y*SS) for x,y in pts],fill=col)
def leaf(d,cx,cy,L,a,col,vein):
    pts=[]
    for t in np.linspace(0,2*math.pi,60):
        px=L/2*math.cos(t); py=L*0.22*math.sin(t)*(1-0.25*math.cos(t))
        pts.append(((cx+px*math.cos(a)-py*math.sin(a))*SS,(cy+px*math.sin(a)+py*math.cos(a))*SS))
    d.polygon(pts,fill=col)
    d.line([((cx-L/2*math.cos(a))*SS,(cy-L/2*math.sin(a))*SS),((cx+L/2*math.cos(a))*SS,(cy+L/2*math.sin(a))*SS)],fill=vein,width=4*SS)
def stroke(d,pts,w0,w1,col):
    n=len(pts)
    for i,(x,y) in enumerate(pts):
        w=w0+(w1-w0)*i/max(1,n-1); d.ellipse([(x-w/2)*SS,(y-w/2)*SS,(x+w/2)*SS,(y+w/2)*SS],fill=col)
def roots(d,x0,y0,col,seed,depth_max,w0=26):
    rr=random.Random(seed); tips=[]
    def br(x,y,a,w,dep,ln):
        pts=[]
        for i in range(ln):
            a+=rr.gauss(0,0.08); a=0.93*a+0.07*(math.pi/2)
            x+=7*math.cos(a); y+=7*math.sin(a); pts.append((x,y))
            if y>depth_max: break
            if rr.random()<0.025 and dep<4: br(x,y,a+rr.choice([-1,1])*rr.uniform(0.6,1.1),w*0.6,dep+1,int(ln*0.55))
        if pts: stroke(d,pts,w,max(2,w*0.25),col); tips.append(pts[-1])
    br(x0,y0,math.pi/2,w0,0,260); return tips
def hyphae(d,cx,cy,col,seed,n=40,R=160):
    rr=random.Random(seed)
    for k in range(n):
        x,y=cx+rr.gauss(0,R*0.4),cy+rr.gauss(0,R*0.4); a=rr.uniform(0,6.28)
        pts=[]
        for i in range(rr.randint(20,45)):
            a+=rr.gauss(0,0.25); x+=6*math.cos(a); y+=6*math.sin(a); pts.append((x*SS,y*SS))
        d.line(pts,fill=col,width=2*SS)
def nematode(d,cx,cy,L,a,col,seed):
    pts=[]
    for i in range(140):
        t=i/139; s=(t-0.5)*L
        x=cx+s*math.cos(a)+0.12*L*math.sin(t*2*math.pi*1.3)*(-math.sin(a)); y=cy+s*math.sin(a)+0.12*L*math.sin(t*2*math.pi*1.3)*math.cos(a)
        pts.append((x,y))
    n=len(pts)
    for i,(x,y) in enumerate(pts):
        t=i/(n-1); w=L*0.075*min(1,(t/0.15)**0.6,((1-t)/0.3)**0.8)+2
        d.ellipse([(x-w/2)*SS,(y-w/2)*SS,(x+w/2)*SS,(y+w/2)*SS],fill=col)
def amoeba(d,cx,cy,R,col,inner,seed):
    blob(d,cx,cy,R,R*0.85,col,seed,0.28)
    d.ellipse([(cx-R*0.25)*SS,(cy-R*0.22)*SS,(cx+R*0.25)*SS,(cy+R*0.22)*SS],outline=inner,width=5*SS)
def worm(d,cx,cy,L,col,band,seed):
    pts=[(cx+i*L/120,cy+40*math.sin(i/120*2*math.pi*1.2)) for i in range(121)]
    stroke(d,pts,58,40,col)
    x,y=pts[40]; d.ellipse([(x-34)*SS,(y-34)*SS,(x+34)*SS,(y+34)*SS],fill=band)
def build(name,P,seed=1):
    r=random.Random(seed)
    im=Image.new('RGB',(W*SS,H*SS),P['sky']); d=ImageDraw.Draw(im)
    s0=wave(seed,640,30); s1=wave(seed+1,980); s2=wave(seed+2,2050); s3=wave(seed+3,2880)
    bands=[(s0,s1,'O'),(s1,s2,'A'),(s2,s3,'B'),(s3,np.full(W,H+10.0),'C')]
    for (a,b,k) in bands:
        m=band_mask(a,b); im.paste(Image.new('RGB',im.size,P[k]),(0,0),m); dots(im,m,P[k+'d'],seed+ord(k),dens=0.4)
    d=ImageDraw.Draw(im)
    # C: rocks
    for k in range(13):
        cx,cy=r.uniform(-60,W+60),r.uniform(s3.mean()+120,H+60); rx=r.uniform(110,240)
        blob(d,cx,cy,rx,rx*r.uniform(0.6,0.85),P['rock'],k,0.12); blob(d,cx-rx*0.15,cy-rx*0.18,rx*0.55,rx*0.3,P['rockhi'],k+50,0.1)
    # B: pebbles
    for k in range(22):
        cx,cy=r.uniform(0,W),r.uniform(s2.mean()+80,s3.mean()-60); rx=r.uniform(18,46)
        blob(d,cx,cy,rx,rx*0.75,P['pebble'],k+100,0.15)
    # A: crumbs / aggregates
    for k in range(70):
        cx,cy=r.uniform(0,W),r.uniform(s1.mean()+60,s2.mean()-40); rx=r.uniform(14,34)
        blob(d,cx,cy,rx,rx*0.8,P['crumb'],k+200,0.2)
    # O: litter leaves
    for k in range(26):
        cx,cy=r.uniform(-40,W+40),r.uniform(s0.mean()+40,s1.mean()-40)
        leaf(d,cx,cy,r.uniform(110,200),r.uniform(-0.5,0.5)+r.choice([0,math.pi/2*0.3]),r.choice(P['leaves']),P['O'])
    # roots from two plants
    plants=P.get('plants',(620,1300))
    tips=[]
    for j,px in enumerate(plants):
        tips+=roots(d,px,s0[int(px)]-5,P['root'],seed*10+j,s3.mean()-80,28-j*4)
    # fungal hyphae around root tips in topsoil/subsoil
    for k,(x,y) in enumerate(tips[:18]):
        if y<s2.mean()+200: hyphae(d,x,y,P['hypha'],k,14,120)
    # organisms in topsoil
    nematode(d,1180,1500,330,0.35,P['org1'],1)
    amoeba(d,420,1720,85,P['org2'],P['A'],3)
    worm(d,880,1880,520,P['worm'],P['wormband'],2)
    nematode(d,1450,2420,240,-0.6,P['org1'],4)
    amoeba(d,350,2500,60,P['org2'],P['B'],5)
    # plants above ground
    for j,px in enumerate(plants):
        gy=s0[int(px)]; h=r.uniform(330,430) if j==0 else r.uniform(240,320)
        pts=[(px+18*math.sin(i/40),gy-i*h/80) for i in range(81)]; stroke(d,pts,22,12,P['stem'])
        tx,ty=pts[-1]
        for side,ln,yo in [(-1,170,0.55),(1,190,0.75),(-1,140,0.95),(1,120,1.0)]:
            yy=gy-h*yo; leaf(d,px+side*ln*0.45,yy,ln,side*(-0.55),P['plant'],P['stem'])
    # logo top right in the sky
    lg=Image.open(LOGO+P['logo']).convert('RGBA').resize((440*SS,440*SS),Image.LANCZOS)
    im=im.convert('RGBA'); im.alpha_composite(lg,((W-90-440)*SS,(70)*SS))
    out=im.resize((W,H),Image.LANCZOS).convert('RGB'); a=np.asarray(out).astype(float)
    g=np.random.default_rng(seed).normal(0,1,a.shape[:2]); out=Image.fromarray((a*(1+0.025*g[...,None])).clip(0,255).astype(np.uint8))
    out.save(f'SFW-case-{name}.png'); return out
SOIL=dict(sky=hx('E4E9D5'),O=hx('4F3433'),Od=hx('5E4140'),A=hx('3A2624'),Ad=hx('4A3331'),B=hx('7A5A48'),Bd=hx('8A6A56'),C=hx('A49A86'),Cd=hx('B3AA97'),
  rock=hx('8B8270'),rockhi=hx('BDB5A2'),pebble=hx('A8927E'),crumb=hx('2C1C1B'),leaves=[hx('5B6B2E'),hx('8A9A4E'),hx('C89B7B'),hx('6B4C7A')],
  root=hx('F4F1EA'),hypha=hx('CBD696'),org1=hx('B6A0D6'),org2=hx('9CC4E8'),worm=hx('C98F86'),wormband=hx('B07870'),stem=hx('156826'),plant=hx('59A66C'),logo='SFW-logo-flower-colour.png')
BRAND=dict(sky=hx('F4F1EA'),O=hx('5B6B2E'),Od=hx('6B7B3A'),A=hx('22371F'),Ad=hx('2E4528'),B=hx('6B4C7A'),Bd=hx('7A5A8A'),C=hx('3780B8'),Cd=hx('4A90C4'),
  rock=hx('2A5F8C'),rockhi=hx('9CC4E8'),pebble=hx('C8B6E2'),crumb=hx('17271A'),leaves=[hx('59A66C'),hx('A8B49A'),hx('CBD696'),hx('C89B7B')],
  root=hx('F4F1EA'),hypha=hx('CBD696'),org1=hx('C8B6E2'),org2=hx('9CC4E8'),worm=hx('C98F86'),wormband=hx('B07870'),stem=hx('156826'),plant=hx('59A66C'),logo='SFW-logo-flower-colour.png')
a=build('64-soil-profile-real',SOIL,1); b=build('65-soil-profile-brand',BRAND,2)
s=Image.new('RGB',(2*620+20,1247),(226,222,214)); s.paste(a.resize((600,1227)),(20,10)); s.paste(b.resize((600,1227)),(640,10)); s.save('SFW-cases-soil-profile-v3.jpg',quality=90)
