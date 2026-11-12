import math, random, numpy as np
from PIL import Image, ImageDraw
exec(open('webposter.py').read().split("def root(")[0])
def root2(m,seed,x0,w0,depth):
    rr=random.Random(seed); d=ImageDraw.Draw(m)
    def br(x,y,a,w,dep):
        while w>5 and y<depth and -200<x<W+200:
            a+=rr.gauss(0,0.06); a=0.97*a+0.03*(math.pi/2); nx,ny=x+14*math.cos(a),y+14*math.sin(a)
            d.line([x,y,nx,ny],fill=255,width=int(w)); d.ellipse([nx-w/2,ny-w/2,nx+w/2,ny+w/2],fill=255); x,y=nx,ny; w*=0.993
            if rr.random()<0.012*(dep+1) and dep<5: br(x,y,a+rr.choice([-1,1])*rr.uniform(0.7,1.3),w*0.6,dep+1)
    for k,a in enumerate([1.25,1.45,1.6,1.75,1.95]): br(x0+(k-2)*20,200,a,w0*(1 if k==2 else 0.65),0)
    d.polygon([(x0-w0*0.6,-100),(x0+w0*0.6,-100),(x0+w0*0.45,230),(x0-w0*0.45,230)],fill=255)
def build(name,bg,logo,seed=1):
    im=Image.new('RGB',(W,H),bg)
    mr=Image.new('L',(W,H),0); root2(mr,seed,W*0.48,150,H*0.93)
    mw=Image.new('L',(W,H),0)
    O=[('blob',PUR,[LIL,PG],(1250,2300,520),3),('nema',EB,[PY,LB],(3500,3200,1.1),0),('cil',OLV,[LIME,PG],(3700,1250,0.4),0),
       ('blob',EB,[PY,LB],(1200,4700,380),9),('nema',PUR,[LIL,PG],(1300,6100,-0.3),0),('blob',(89,166,108),[PG,LIME],(3800,5200,300),12),
       ('cil',PUR,[LIL,PG],(3600,6200,-0.2),0),('blob',(91,107,46),[LIME,LIL],(800,1100,260),14)]
    pts=[]
    for k,(kind,base,dots,p,s) in enumerate(O):
        m=Image.new('L',(W,H),0)
        if kind=='blob': org_blob(m,p[0],p[1],p[2],s,6,0.45); pts.append(p[:2])
        elif kind=='nema': nema(m,p[0],p[1],1500 if k<3 else 1100,p[2],230 if k<3 else 180); pts.append(p[:2])
        else: cil(m,p[0],p[1],380 if k<3 else 300,240 if k<3 else 190,p[2]); pts.append(p[:2])
        O[k]=(m,base,dots)
    links=[(pts[i],(int(W*0.48)+random.Random(i).randint(-300,300),pts[i][1]+random.Random(i).randint(-500,500)),random.Random(i).randint(35,60)) for i in range(len(pts))]
    links+=[(pts[0],pts[7],40),(pts[1],pts[5],45),(pts[3],pts[4],40),(pts[2],pts[1],40),(pts[5],pts[6],40),(pts[0],(-200,3300),40),(pts[1],(W+200,2500),40)]
    web(mw,links,seed+3)
    im.paste(texture(FWG,[LGR,LIME],13),(0,0),mw)
    im.paste(texture((89,166,108),[PG,LIME],22),(0,0),mr)
    for (m,base,dots),k in zip(O,range(9)): im.paste(texture(base,dots,40+k),(0,0),m)
    w=750; lg=Image.open('/home/claude/merch/logos/'+logo).convert('RGBA').resize((w,w),Image.LANCZOS)
    im=im.convert('RGBA'); im.alpha_composite(lg,(W-260-w,H-260-w)); im=im.convert('RGB')
    a=np.asarray(im).astype(float); g=np.random.default_rng(3).normal(0,1,a.shape[:2])
    im=Image.fromarray((a*(1+0.03*g[...,None])).clip(0,255).astype(np.uint8)); im.save(f'SFW-poster-A2-rhizosphere-{name}.png'); return im
ims=[build('deepgreen',(34,55,31),'SFW-logo-flower-cream.png'),build('sage',(168,180,154),'SFW-logo-flower-deepgreen.png')]
S=Image.new('RGB',(2*730+30,1030),(226,222,214))
for i,v in enumerate(ims): S.paste(v.resize((700,990),Image.LANCZOS),(30+i*730,20))
S.save('SFW-posters-A2-rhizosphere.jpg',quality=90)
