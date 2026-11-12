import math, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
exec(open('cutout3.py').read().split("def shape(")[0])
def organism(i):
    p=Image.open(f'/home/claude/merch/micro/plate_{i}.png').convert('RGBA').split()[3]
    n=p.width; m=Image.new('L',p.size,0); ImageDraw.Draw(m).ellipse([n*0.08,n*0.08,n*0.92,n*0.92],fill=255)
    a=np.minimum(np.asarray(p),np.asarray(m)).astype(float)
    b=ndi.gaussian_filter(a,8)>80; b=ndi.binary_closing(b,iterations=10); b=ndi.binary_fill_holes(b)
    lab,k=ndi.label(b)
    if k==0: return None
    sizes=ndi.sum(b,lab,range(1,k+1)); body=lab==(1+np.argmax(sizes))
    if body.sum()<0.02*b.size: return None
    body=ndi.binary_opening(body,iterations=6)
    ys,xs=np.nonzero(body); y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1; body=body[y0:y1,x0:x1]
    hull_area=(y1-y0)*(x1-x0); solidity=body.sum()/hull_area
    if solidity<0.35: return None
    core=ndi.binary_erosion(body,iterations=int(min(body.shape)*0.28))
    up=lambda z:Image.fromarray((z*255).astype(np.uint8)).resize(((x1-x0)*3,(y1-y0)*3),Image.BICUBIC).filter(ImageFilter.GaussianBlur(9)).point(lambda v:255 if v>127 else 0)
    return up(body),up(core)
ORG=[o for o in (organism(i) for i in range(16)) if o]; print('organisms',len(ORG))
def leaf(d,cx,cy,L,rot,col,w=0.34,asym=0.08):
    ca,sa=math.cos(rot),math.sin(rot); P=lambda x,y:(cx+x*ca-y*sa,cy+x*sa+y*ca)
    ts=np.linspace(0,1,160)
    up=[P(t*L,L*w*math.sin(math.pi*t)**0.75*(1.1-0.35*t)*(1+asym)) for t in ts]
    dn=[P(t*L,-L*w*math.sin(math.pi*t)**0.75*(1.1-0.35*t)*(1-asym)) for t in ts[::-1]]
    d.polygon(up+dn,fill=col)
    pts=[P(-L*0.25*t,L*0.03*math.sin(t*3)) for t in np.linspace(0,1,40)]
    for x,y in pts: q=max(4,L*0.018); d.ellipse([x-q,y-q,x+q,y+q],fill=col)
def frond(d,x0,y0,L,rot,col,n=9):
    ca,sa=math.cos(rot),math.sin(rot)
    for k in range(int(L/8)):
        t=k/(L/8); x=x0+t*L*ca+math.sin(t*2)*L*0.04*-sa; y=y0+t*L*sa+math.sin(t*2)*L*0.04*ca; q=max(3,L*0.012*(1-t)); d.ellipse([x-q,y-q,x+q,y+q],fill=col)
    for k in range(n):
        t=0.18+0.78*k/n; x=x0+t*L*ca; y=y0+t*L*sa; s=L*0.32*(1-t*0.7)
        for side in (1,-1): leaf(d,x,y,s,rot+side*1.0,col,0.3,0)
def mushroom(d,cx,cy,H,col,stemcol):
    w=H*0.22; d.polygon([(cx-w*0.45,cy),(cx+w*0.45,cy),(cx+w*0.3,cy-H*0.75),(cx-w*0.3,cy-H*0.75)],fill=stemcol)
    d.chord([cx-H*0.55,cy-H*1.15,cx+H*0.55,cy-H*0.45],180,360,fill=col)
    d.ellipse([cx-H*0.55,cy-H*0.86,cx+H*0.55,cy-H*0.74],fill=col)
def hypha(d,x,y,a,w,col,rr,n=400,dep=0):
    for i in range(n):
        a+=rr.gauss(0,0.025); x+=8*math.cos(a); y+=8*math.sin(a); w=max(5,w*0.9985); d.ellipse([x-w/2,y-w/2,x+w/2,y+w/2],fill=col)
        if rr.random()<0.005 and dep<2: hypha(d,x,y,a+rr.choice([-1,1])*rr.uniform(0.5,0.9),w*0.65,col,rr,int(n*0.5),dep+1)
def place_org(im,o,x,y,size,rot,col,core):
    b,c=o; b=b.rotate(rot,expand=True); c=c.rotate(rot,expand=True); s=size/max(b.size)
    sz=(int(b.width*s),int(b.height*s)); b=b.resize(sz,Image.LANCZOS); c=c.resize(sz,Image.LANCZOS)
    im.paste(C[col],(int(x-sz[0]/2),int(y-sz[1]/2)),b)
    if core: im.paste(C[core],(int(x-sz[0]/2),int(y-sz[1]/2)),c)
def compose(W,H,seed,bg,pal,name):
    r=random.Random(seed); im=Image.new('RGB',(W,H),C[bg]); d=ImageDraw.Draw(im)
    rr=random.Random(seed+5)
    hypha(d,-60,H*0.75,-0.25,26,C[pal['hy']],rr); hypha(d,W+60,H*0.25,2.95,22,C[pal['hy']],rr)
    # big leaves anchoring corners
    leaf(d,W*0.03,H*1.05,H*0.95,-1.05,C[pal['l1']],0.36,0.1)
    leaf(d,W*0.12,H*1.08,H*0.7,-1.45,C[pal['l2']],0.3,-0.1)
    frond(d,W*0.98,H*-0.05,H*1.05,2.2,C[pal['l3']])
    leaf(d,W*0.70,H*1.06,H*0.6,-1.8,C[pal['l2']],0.33,0.05)
    # organisms
    o=list(range(len(ORG))); r.shuffle(o)
    spots=[(0.30,0.32,0.42),(0.52,0.62,0.48),(0.78,0.55,0.36),(0.42,0.10,0.22),(0.63,0.22,0.24),(0.92,0.86,0.2),(0.20,0.62,0.18)]
    for k,(x,y,s) in enumerate(spots):
        col,core=pal['org'][k%len(pal['org'])]; place_org(im,ORG[o[k%len(o)]],W*x,H*y,H*s*1.6,r.choice([0,90,180,270]),col,core)
    d=ImageDraw.Draw(im)
    mushroom(d,W*0.88,H*0.98,H*0.32,C[pal['mu']],C[pal['ms']]); mushroom(d,W*0.94,H*0.98,H*0.2,C[pal['mu2']],C[pal['ms']])
    for k in range(14):
        x,y=r.uniform(0,W),r.uniform(0,H); q=r.uniform(7,16); d.ellipse([x-q,y-q,x+q,y+q],fill=C[r.choice(pal['dots'])])
    im.save(name); return im
PA=dict(hy='lime',l1='fwg',l2='lg',l3='fwg',mu='purple',mu2='lil',ms='pg',org=[('lblue','blue'),('purple','lil'),('lime',None),('blue','lblue'),('lil','purple'),('pg','lg'),('lblue',None)],dots=['purple','blue','lime'])
PB=dict(hy='lg',l1='fwg',l2='lg',l3='lime',mu='lil',mu2='lblue',ms='pg',org=[('lil','purple'),('blue','lblue'),('lime','fwg'),('lblue',None),('purple','lil'),('pg',None),('lime',None)],dots=['lil','lime','lblue'])
PC=dict(hy='fwg',l1='fwg',l2='lime',l3='fwg',mu='navy',mu2='blue',ms='cream',org=[('blue','lblue'),('purple','cream'),('lime','fwg'),('navy',None),('cream','purple'),('lblue',None),('purple',None)],dots=['navy','fwg','cream'])
a=compose(2400,1300,4,'cream',PA,'SFW-micro-cutout-a.png'); b=compose(2400,1300,7,'navy',PB,'SFW-micro-cutout-b.png'); c=compose(2400,1300,9,'lil',PC,'SFW-micro-cutout-c.png')
S=Image.new('RGB',(1240,3*670+20),(226,222,214))
for i,v in enumerate([a,b,c]): S.paste(v.resize((1200,650),Image.LANCZOS),(20,20+i*670))
S.save('SFW-micro-cutout-preview.jpg',quality=90)
