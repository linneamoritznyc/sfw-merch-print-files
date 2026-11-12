import math, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
def hx(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
C=dict(navy=hx('1A2C52'),blue=hx('3780B8'),lblue=hx('96C4E8'),purple=hx('6B4C7A'),lil=hx('C8B6E2'),dg=hx('22371F'),fwg=hx('156826'),lg=hx('59A66C'),lime=hx('BED65A'),pg=hx('CBD696'),olive=hx('5B6B2E'),cream=hx('F4F1EA'),sage=hx('A8B49A'))
def plate_mask(i,size,rot,blur):
    p=Image.open(f'/home/claude/merch/micro/plate_{i}.png').convert('RGBA').split()[3]
    m=Image.new('L',p.size,0); c=p.width/2; r=p.width*0.42; ImageDraw.Draw(m).ellipse([c-r,c-r,c+r,c+r],fill=255)
    p=Image.fromarray(np.minimum(np.asarray(p),np.asarray(m))).rotate(rot).resize((size,size),Image.LANCZOS)
    return p.filter(ImageFilter.GaussianBlur(blur)).point(lambda v:255 if v>110 else 0).filter(ImageFilter.GaussianBlur(2)).point(lambda v:255 if v>127 else 0)
def blob(d,cx,cy,R,seed,lobes=6,amp=0.35,sy=1.0,col=(0,0,0)):
    r=random.Random(seed); L=[(r.uniform(0,6.28),r.uniform(0.15,amp),r.uniform(0.25,0.5)) for _ in range(lobes)]
    pts=[]
    for t in np.linspace(0,6.283,500):
        k=1
        for a,am,wd in L: dd=math.atan2(math.sin(t-a),math.cos(t-a)); k+=am*math.exp(-(dd/wd)**2)
        pts.append((cx+R*k*math.cos(t),cy+R*sy*k*math.sin(t)))
    d.polygon(pts,fill=col)
def stroke(d,pts,ws,col):
    for (x,y),w in zip(pts,ws): d.ellipse([x-w/2,y-w/2,x+w/2,y+w/2],fill=col)
def hypha(d,x,y,a,w,col,rr,n=420,dep=0):
    pts=[];ws=[]
    for i in range(n):
        a+=rr.gauss(0,0.03); x+=9*math.cos(a); y+=9*math.sin(a); w*=0.998; pts.append((x,y)); ws.append(w)
        if rr.random()<0.006 and dep<2: hypha(d,x,y,a+rr.choice([-1,1])*rr.uniform(0.5,0.9),w*0.6,col,rr,int(n*0.6),dep+1)
    stroke(d,pts,ws,col)
def nematode(d,cx,cy,L,a,wid,col,ph=0):
    pts=[];ws=[]
    for i in range(500):
        t=i/499; s=(t-0.5)*L; o=0.12*L*math.sin(t*2*math.pi*1.3+ph)
        pts.append((cx+s*math.cos(a)-o*math.sin(a),cy+s*math.sin(a)+o*math.cos(a))); ws.append(wid*min(1,(t/0.1)**0.6,((1-t)/0.25)**0.8)+3)
    stroke(d,pts,ws,col)
def ciliate(d,cx,cy,rx,ry,rot,col,cil=True):
    ca,sa=math.cos(rot),math.sin(rot); P=lambda x,y:(cx+x*ca-y*sa,cy+x*sa+y*ca)
    d.polygon([P(rx*math.cos(t),ry*math.sin(t)) for t in np.linspace(0,6.283,300)],fill=col)
    if cil:
        for t in np.linspace(0,6.283,90): d.line([P(rx*math.cos(t),ry*math.sin(t)),P((rx+40)*math.cos(t),(ry+40)*math.sin(t))],fill=col,width=7)
def frond(d,x,y,a,L,col,rr):
    # flagellate / leaf-like fan of fronds like the reference
    for k in range(7):
        b=a+(k-3)*0.22; w=L*0.12
        pts=[];ws=[]
        xx,yy=x,y
        for i in range(160):
            t=i/159; b+=0.004*(k-3); xx+=L/160*math.cos(b); yy+=L/160*math.sin(b); pts.append((xx,yy)); ws.append(w*math.sin(math.pi*min(1,t*1.1)) +2)
        stroke(d,pts,ws,col)
def compose(W,H,seed,bg,P,name):
    r=random.Random(seed); im=Image.new('RGB',(W,H),C[bg]); d=ImageDraw.Draw(im); S=W/2400
    # big background blobs
    blob(d,W*0.18,H*0.35,420*S,seed+1,6,0.4,1.1,C[P[0]])
    blob(d,W*0.78,H*0.62,520*S,seed+2,7,0.45,0.9,C[P[1]])
    blob(d,W*0.52,H*0.15,300*S,seed+3,5,0.35,1,C[P[2]])
    # micrograph silhouettes as flat cut-outs
    for k,(i,sz,x,y,col) in enumerate([(4,900,0.33,0.62,P[3]),(14,800,0.88,0.22,P[4]),(8,700,0.06,0.9,P[5])]):
        m=plate_mask(i,int(sz*S),r.choice([0,90,180,270]),int(10*S)); im.paste(C[col],(int(W*x-m.width/2),int(H*y-m.height/2)),m)
    d=ImageDraw.Draw(im)
    rr=random.Random(seed+9)
    hypha(d,-50,H*0.95,-0.6,60*S,C[P[6]],rr); hypha(d,W+50,H*0.05,2.6,48*S,C[P[7]],rr)
    nematode(d,W*0.62,H*0.42,900*S,-0.25,70*S,C[P[8]])
    ciliate(d,W*0.42,H*0.80,120*S,80*S,0.5,C[P[9]])
    ciliate(d,W*0.92,H*0.86,90*S,60*S,-0.4,C[P[4]])
    frond(d,W*0.70,H*0.98,-1.9,700*S,C[P[10]],rr)
    blob(d,W*0.24,H*0.12,70*S,seed+20,5,0.5,1,C[P[9]])
    blob(d,W*0.58,H*0.62,55*S,seed+21,5,0.5,1,C[P[2]])
    im.save(name); return im
# weekender ratio ~ 24x13 -> preview 2400x1300
a=compose(2400,1300,1,'cream',['lblue','purple','pg','fwg','navy','lil','dg','blue','purple','lime','lg'],'SFW-cutout-a.png')
b=compose(2400,1300,2,'navy',['fwg','purple','blue','lime','lil','lg','pg','lblue','lime','lil','lg'],'SFW-cutout-b.png')
c=compose(2400,1300,3,'lil',['blue','fwg','pg','purple','navy','lime','dg','lg','navy','lime','fwg'],'SFW-cutout-c.png')
S=Image.new('RGB',(1240,3*670+20),(226,222,214))
for i,v in enumerate([a,b,c]): S.paste(v.resize((1200,650)),(20,20+i*670))
S.save('SFW-cutout-preview.jpg',quality=90)
