import math, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
exec(open('cases4.py').read().split("specs=[")[0])
T=1200  # seamless tile size
def tile_bands(seed,n=3):
    r=random.Random(seed); m=Image.new('L',(T*3,T*3),0); d=ImageDraw.Draw(m)
    for k in range(n):
        x,y=r.uniform(0,T)+T,r.uniform(0,T)+T; a=r.uniform(0,6.28); w=r.uniform(90,150)
        pts=[];ws=[]
        for i in range(260):
            a+=r.gauss(0,0.05); x+=6*math.cos(a); y+=6*math.sin(a); pts.append((x,y)); ws.append(w)
            if r.random()<0.01:
                bx,by,ba,bw=x,y,a+r.choice([-1,1])*0.8,w*0.6
                for j in range(80): ba+=r.gauss(0,0.05); bx+=6*math.cos(ba); by+=6*math.sin(ba); pts.append((bx,by)); ws.append(bw)
        for (px,py),pw in zip(pts,ws):
            for ox in (-T,0,T):
                for oy in (-T,0,T): d.ellipse([px+ox-pw/2,py+oy-pw/2,px+ox+pw/2,py+oy+pw/2],fill=255)
    A=np.asarray(m)[T:2*T,T:2*T]
    # fold the wrapped parts in
    big=np.asarray(m); A=np.zeros((T,T),bool)
    for i in range(3):
        for j in range(3): A|=big[i*T:(i+1)*T,j*T:(j+1)*T]>127
    return A
def ikat_tile(A,seed,amp=5):
    r=np.random.default_rng(seed); off=np.zeros(T,int); y=0
    while y<T: run=r.integers(2,8); off[y:y+run]=r.integers(-amp,amp+1); y+=run
    B=np.array([np.roll(A[y],off[y]) for y in range(T)])
    L=B&~np.roll(B,-1,1); R=~B&np.roll(B,-1,1); ys,xs=np.nonzero(L|R)
    idx=r.choice(len(ys),min(700,len(ys)),replace=False)
    for k in idx:
        y,x=ys[k],xs[k]; ln=int(r.integers(10,80)); th=int(r.integers(1,4)); right=L[y,x]
        seg=np.arange(ln); keep=r.random(ln)>np.linspace(0,0.9,ln); cols=((x+1+seg) if right else (x-seg))[keep]%T
        B[y:y+th,cols]=True
    return B
def colour(B,fg,bg,seed):
    img=np.empty((T,T,3),float); img[:]=bg; img[B]=fg
    n=np.random.default_rng(seed).normal(0,1,(T,T)); img=img*(1+0.05*n[...,None]); return Image.fromarray(img.clip(0,255).astype(np.uint8))
tiles={'ikat-deepgreen-sage':(DG,SAGE,3),'ikat-purple-sage':(PUR,SAGE,5),'ikat-blue-cream':(EB,CRM,7),'ikat-green-cream':(FWG,CRM,9)}
out={}
for k,(fg,bg,s) in tiles.items():
    out[k]=colour(ikat_tile(tile_bands(s),s),fg,bg,s); out[k].save(f'SFW-aop-tile-{k}.png')
disc=Image.open('SFW-aop-tile-discs-deepgreen.png'); out['discs-deepgreen']=disc
# garment mockups: flat shapes filled with the tiled pattern
def fill(pattern,size,scale):
    t=pattern.resize((int(pattern.width*scale),int(pattern.height*scale)),Image.LANCZOS); W_,H_=size; c=Image.new('RGB',size)
    for x in range(0,W_,t.width):
        for y in range(0,H_,t.height): c.paste(t,(x,y))
    return c
def tee(pattern):
    W_,H_=900,960; m=Image.new('L',(W_,H_),0); d=ImageDraw.Draw(m)
    d.polygon([(250,40),(340,20),(380,70),(520,70),(560,20),(650,40),(880,230),(780,360),(700,290),(700,940),(200,940),(200,290),(120,360),(20,230)],fill=255)
    d.ellipse([360,0,540,90],fill=0)
    bg=Image.new('RGB',(W_,H_),(235,232,226)); bg.paste(fill(pattern,(W_,H_),0.42),(0,0),m)
    ImageDraw.Draw(bg).line([(380,70),(450,95),(520,70)],fill=(40,40,40),width=3); return bg
def shirt(pattern):
    W_,H_=900,1000; m=Image.new('L',(W_,H_),0); d=ImageDraw.Draw(m)
    d.polygon([(280,40),(380,30),(450,80),(520,30),(620,40),(860,300),(820,700),(740,700),(700,360),(700,980),(200,980),(200,360),(160,700),(80,700),(40,300)],fill=255)
    bg=Image.new('RGB',(W_,H_),(235,232,226)); bg.paste(fill(pattern,(W_,H_),0.42),(0,0),m); dd=ImageDraw.Draw(bg)
    dd.line([(450,80),(450,980)],fill=(30,30,30),width=3); dd.polygon([(380,30),(450,80),(410,150)],outline=(30,30,30),width=3); dd.polygon([(520,30),(450,80),(490,150)],outline=(30,30,30),width=3)
    for y in range(180,960,110): dd.ellipse([440,y,460,y+20],fill=(240,236,226))
    return bg
def track(pattern):
    W_,H_=900,1000; m=Image.new('L',(W_,H_),0); d=ImageDraw.Draw(m)
    d.polygon([(280,40),(380,20),(520,20),(620,40),(860,300),(840,760),(760,760),(700,360),(700,940),(200,940),(200,360),(140,760),(60,760),(40,300)],fill=255)
    bg=Image.new('RGB',(W_,H_),(235,232,226)); bg.paste(fill(pattern,(W_,H_),0.42),(0,0),m); dd=ImageDraw.Draw(bg)
    dd.rectangle([380,10,520,45],fill=(34,55,31)); dd.line([(450,45),(450,940)],fill=(200,200,200),width=6)
    dd.rectangle([200,900,700,945],fill=(34,55,31)); dd.rectangle([60,730,140,765],fill=(34,55,31)); dd.rectangle([760,730,840,765],fill=(34,55,31))
    return bg
rows=[('ikat-deepgreen-sage',shirt),('ikat-purple-sage',tee),('ikat-blue-cream',track),('discs-deepgreen',shirt),('ikat-green-cream',tee),('discs-deepgreen',track)]
S=Image.new('RGB',(3*920+20,2*1020+20),(226,222,214))
for i,(k,fn) in enumerate(rows):
    g=fn(out[k]).resize((900,1000)); S.paste(g,(20+(i%3)*920,20+(i//3)*1020))
S.save('SFW-aop-fashion-mockups.jpg',quality=90)
