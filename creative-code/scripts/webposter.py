import math, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
exec(open('poster_a2.py').read().split("def blob(")[0])
BR=(79,52,51); TAN=(200,155,123)
def new(): return Image.new('L',(W,H),0)
def org_blob(m,cx,cy,R,seed,lobes=5,amp=0.35):
    r=random.Random(seed); L=[(r.uniform(0,6.28),r.uniform(0.2,amp),r.uniform(0.25,0.45)) for _ in range(lobes)]
    pts=[]
    for t in np.linspace(0,6.283,400):
        k=1+0.06*math.sin(3*t+seed)
        for a,am,wd in L: dd=math.atan2(math.sin(t-a),math.cos(t-a)); k+=am*math.exp(-(dd/wd)**2)
        pts.append((cx+R*k*math.cos(t),cy+R*k*math.sin(t)))
    ImageDraw.Draw(m).polygon(pts,fill=255)
def nema(m,cx,cy,L,a,wid):
    d=ImageDraw.Draw(m)
    for i in range(600):
        t=i/599; s=(t-0.5)*L; o=0.13*L*math.sin(t*2*math.pi*1.4)
        x=cx+s*math.cos(a)-o*math.sin(a); y=cy+s*math.sin(a)+o*math.cos(a)
        w=wid*min(1,(t/0.12)**0.6,((1-t)/0.3)**0.8)+4; d.ellipse([x-w/2,y-w/2,x+w/2,y+w/2],fill=255)
def cil(m,cx,cy,rx,ry,rot):
    d=ImageDraw.Draw(m); ca,sa=math.cos(rot),math.sin(rot)
    P=lambda x,y:(cx+x*ca-y*sa,cy+x*sa+y*ca)
    d.polygon([P(rx*math.cos(t),ry*math.sin(t)) for t in np.linspace(0,6.283,200)],fill=255)
    for t in np.linspace(0,6.283,70):
        d.line([P(rx*math.cos(t),ry*math.sin(t)),P((rx+90)*math.cos(t),(ry+90)*math.sin(t))],fill=255,width=16)
def web(m,nodes,seed):
    # hyphae: tapering wandering strands between organisms, with side branches
    rr=random.Random(seed); d=ImageDraw.Draw(m)
    def strand(x0,y0,x1,y1,w0):
        n=int(math.hypot(x1-x0,y1-y0)/20); ang=math.atan2(y1-y0,x1-x0); x,y=x0,y0
        for i in range(n):
            tgt=math.atan2(y1-y,x1-x); ang+=0.25*math.atan2(math.sin(tgt-ang),math.cos(tgt-ang))+rr.gauss(0,0.12)
            w=w0*(0.65+0.35*abs(0.5-i/n)*2); nx,ny=x+20*math.cos(ang),y+20*math.sin(ang)
            d.line([x,y,nx,ny],fill=255,width=int(w)); d.ellipse([nx-w/2,ny-w/2,nx+w/2,ny+w/2],fill=255); x,y=nx,ny
            if rr.random()<0.025: side(x,y,ang+rr.choice([-1,1])*rr.uniform(0.6,1.2),w*0.55)
    def side(x,y,a,w):
        for i in range(rr.randint(15,45)):
            a+=rr.gauss(0,0.12); nx,ny=x+18*math.cos(a),y+18*math.sin(a); d.line([x,y,nx,ny],fill=255,width=max(4,int(w))); x,y=nx,ny; w*=0.97
    for (a,b,w) in nodes: strand(*a,*b,w)
def root(m,seed):
    rr=random.Random(seed); d=ImageDraw.Draw(m)
    def br(x,y,a,w,dep):
        while w>10 and y<H*0.62:
            a+=rr.gauss(0,0.06); a=0.95*a+0.05*(math.pi/2); nx,ny=x+16*math.cos(a),y+16*math.sin(a)
            d.line([x,y,nx,ny],fill=255,width=int(w)); d.ellipse([nx-w/2,ny-w/2,nx+w/2,ny+w/2],fill=255); x,y=nx,ny; w*=0.994
            if rr.random()<0.02 and dep<3: br(x,y,a+rr.choice([-1,1])*rr.uniform(0.6,1.0),w*0.6,dep+1)
    br(2300,-100,math.pi/2,300,0)
def build(name,bg,logo):
    im=Image.new('RGB',(W,H),bg)
    # soil aggregates bottom band
    ma=new(); r=random.Random(4)
    for k in range(26):
        cx,cy=r.uniform(-200,W+200),r.uniform(H*0.80,H+300); R=r.uniform(220,420)
        if math.hypot(cx-(W-675),cy-(H-675))<R*1.5+520: continue
        org_blob(ma,cx,cy,R,k,4,0.15)
    mr=new(); root(mr,3)
    org={'amoeba':(1150,2650,560,PUR,[LIL,PG]),'nema':(3500,3350,0,EB,[PY,LB]),'cil':(3550,1150,0,(91,107,46),[LIME,PG]),'amoeba2':(1450,5150,380,EB,[PY,LB])}
    mo={k:new() for k in org}
    org_blob(mo['amoeba'],1150,2650,560,7,6,0.45); nema(mo['nema'],3450,3500,2100,1.0,320); cil(mo['cil'],3600,1300,520,330,0.4); org_blob(mo['amoeba2'],1450,5150,380,9,5,0.4)
    mw=new(); web(mw,[((1150,2650),(3600,1300),70),((1150,2650),(3450,3500),60),((3600,1300),(2300,600),55),((3450,3500),(1450,5150),60),((1150,2650),(-200,1800),55),((3450,3500),(W+200,4600),50),((1450,5150),(2600,6400),45),((2300,2400),(3200,2300),40)],5)
    im.paste(texture(BR,[TAN,(120,86,80)],21),(0,0),ma)
    im.paste(texture(FWG,[LGR,LIME],13),(0,0),mw)
    im.paste(texture((89,166,108),[PG,LIME],22),(0,0),mr)
    for k,(cx,cy,R,base,dots) in org.items(): im.paste(texture(base,dots,hash(k)%97),(0,0),mo[k])
    w=750; lg=Image.open('/home/claude/merch/logos/'+logo).convert('RGBA').resize((w,w),Image.LANCZOS)
    im=im.convert('RGBA'); im.alpha_composite(lg,(W-300-w,H-300-w)); im=im.convert('RGB')
    a=np.asarray(im).astype(float); g=np.random.default_rng(3).normal(0,1,a.shape[:2])
    im=Image.fromarray((a*(1+0.03*g[...,None])).clip(0,255).astype(np.uint8)); im.save(f'SFW-poster-A2-foodweb-{name}.png'); return im
ims=[build('sage',(168,180,154),'SFW-logo-flower-deepgreen.png'),build('cream',(244,241,234),'SFW-logo-flower-colour.png'),build('deepgreen',(34,55,31),'SFW-logo-flower-cream.png')]
S=Image.new('RGB',(3*730+30,1030),(226,222,214))
for i,v in enumerate(ims): S.paste(v.resize((700,990),Image.LANCZOS),(30+i*730,20))
S.save('SFW-posters-A2-foodweb.jpg',quality=90)
