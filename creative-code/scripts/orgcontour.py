import math, random, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import distance_transform_edt as edt, gaussian_filter
from skimage import measure
W,H=1800,3680; h=2  # field at half res
w2,h2=W//h,H//h; SS=2; K=SS*h   # field px -> canvas px
DO=(46,58,28); PG=(203,214,150); PU2=(150,112,190)
def blank(): return Image.new('L',(w2,h2),0)
def noise(seed,scale=160):
    r=np.random.default_rng(seed); n=r.normal(0,1,(h2//8+2,w2//8+2)); n=gaussian_filter(n,scale/8/3)
    return np.asarray(Image.fromarray(n.astype(np.float32)).resize((w2,h2),Image.BICUBIC))/ (n.std()+1e-9)
def contours(d,field,levels,col,width,clip=None):
    for lv in levels:
        for c in measure.find_contours(field,lv):
            pts=[(x*K,y*K) for y,x in c]
            if clip is not None:
                # split where outside clip
                seg=[]
                for (y,x),p in zip(c,pts):
                    yi,xi=min(h2-1,int(y)),min(w2-1,int(x))
                    if clip[yi,xi]: seg.append(p)
                    else:
                        if len(seg)>1: d.line(seg,fill=col+(255,),width=width*SS,joint='curve')
                        seg=[]
                if len(seg)>1: d.line(seg,fill=col+(255,),width=width*SS,joint='curve')
            elif len(pts)>1: d.line(pts,fill=col+(255,),width=width*SS,joint='curve')
def render(body,organelles,purple,seed,logo_xy,spacing=34,logo_w=660):
    B=np.asarray(body)>127
    im=Image.new('RGBA',(W*SS,H*SS),DO+(255,)); d=ImageDraw.Draw(im)
    dout=edt(~B); n=noise(seed)
    f=dout+n*np.clip((dout-40)/400,0,1)*30
    lv=[3]+[3+spacing*k*(1+0.015*k) for k in range(1,60)]
    contours(d,f,lv[1:],PG,3)
    contours(d,dout,[3],PG,6)
    din=edt(B); contours(d,din,[14],PG,2)
    inner=din>8
    for o in organelles:
        O=np.asarray(o)>127; do=edt(~O)
        contours(d,do,[0.5,9,18],PG,2,clip=inner)
    P=np.asarray(purple)>127
    pm=Image.fromarray((P*255).astype(np.uint8)).resize((W*SS,H*SS),Image.BILINEAR).point(lambda v:255 if v>127 else 0)
    im.paste(Image.new('RGBA',im.size,PU2+(255,)),(0,0),pm)
    lx,ly=logo_xy; r=int(logo_w*0.62); d.ellipse([(lx-r)*SS,(ly-r)*SS,(lx+r)*SS,(ly+r)*SS],fill=DO+(255,)); d.ellipse([(lx-r)*SS,(ly-r)*SS,(lx+r)*SS,(ly+r)*SS],outline=PG+(255,),width=3*SS)
    lg=Image.open('/home/claude/merch/logos/SFW-logo-flower-cream.png').convert('RGBA').resize((logo_w*SS,logo_w*SS),Image.LANCZOS); im.alpha_composite(lg,((lx-logo_w//2)*SS,(ly-logo_w//2)*SS))
    out=im.resize((W,H),Image.LANCZOS).convert('RGB')
    a=np.asarray(out).astype(float); g=np.random.default_rng(seed).normal(0,1,a.shape[:2]); return Image.fromarray((a*(1+0.05*g[...,None])).clip(0,255).astype(np.uint8))
def S(*v): return v
# ---------- Vorticella: bell + coiled stalk
def vorticella():
    b=blank(); d=ImageDraw.Draw(b)
    cx,top=470,560; lipw,belh=300,460
    bell=[]
    for t in np.linspace(0,1,80):  # right side, top->bottom
        y=top+t*belh; wdt=lipw*(1-0.82*t**1.6)*(1+0.12*math.sin(t*math.pi)); bell.append((cx+wdt,y))
    left=[(2*cx-x,y) for x,y in bell[::-1]]
    d.polygon(bell+left,fill=255)
    d.ellipse([cx-lipw-22,top-55,cx+lipw+22,top+55],fill=255)  # peristome lip
    # stalk with coil
    pts=[]; y=top+belh-10
    for i in range(400):
        t=i/399; yy=y+t*(h2+60-y); xx=cx+20*math.sin(t*40)+50*math.sin(t*3)
        pts.append((xx,yy))
    d.line(pts,fill=255,width=16)
    nuc=blank(); dn=ImageDraw.Draw(nuc)
    dn.arc([cx-170,top+40,cx+150,top+330],200,520-40,fill=255,width=48)  # horseshoe macronucleus
    vacs=[]
    for (x,y,r) in [(cx+150,top+120,34),(cx+90,top+260,28),(cx-150,top+80,26),(cx+20,top+380,24),(cx-60,top+170,22)]:
        v=blank(); ImageDraw.Draw(v).ellipse([x-r,y-r,x+r,y+r],fill=255); vacs.append(v)
    cv=blank(); ImageDraw.Draw(cv).ellipse([cx-200-30,top+20-30,cx-200+30,top+20+30],fill=255)  # contractile vacuole
    return b,[nuc,cv]+vacs,nuc
# ---------- Nematode: tapered S-body
def nematode():
    b=blank(); d=ImageDraw.Draw(b); pts=[]
    N=500
    for i in range(N):
        t=i/(N-1); y=380+t*1350; x=470+230*math.sin(t*math.pi*1.7+0.4)
        w=78*min(1,(t/0.06)**0.5,((1-t)/0.3)**0.8)+4; pts.append((x,y,w))
    for x,y,w in pts: d.ellipse([x-w/2,y-w/2,x+w/2,y+w/2],fill=255)
    def at(t): i=int(t*(N-1)); return pts[i]
    org=[]
    bx,by,_=at(0.13); bulb=blank(); ImageDraw.Draw(bulb).ellipse([bx-26,by-30,bx+26,by+30],fill=255)
    phar=blank(); dp=ImageDraw.Draw(phar); dp.line([(at(t)[0],at(t)[1]) for t in np.linspace(0.02,0.12,20)],fill=255,width=12)
    org+=[bulb,phar]
    for t in np.linspace(0.2,0.68,11):
        x,y,w=at(t); g=blank(); ImageDraw.Draw(g).ellipse([x-13,y-11,x+13,y+11],fill=255); org.append(g)
    return b,org,bulb
# ---------- Arcella-like testate amoeba: dome test with aperture + pseudopods
def testate():
    b=blank(); d=ImageDraw.Draw(b); cx,cy,R=470,960,330
    d.ellipse([cx-R,cy-R,cx+R,cy+R],fill=255)
    for a,L,w in [(1.25,330,70),(1.75,280,58),(2.2,210,48)]:
        pts=[(cx+ (R-40+L*t)*math.cos(a+0.25*math.sin(t*3)), cy+(R-40+L*t)*math.sin(a+0.25*math.sin(t*3))) for t in np.linspace(0,1,60)]
        for i,(x,y) in enumerate(pts):
            ww=w*(1-0.5*i/60); d.ellipse([x-ww/2,y-ww/2,x+ww/2,y+ww/2],fill=255)
    ap=blank(); ImageDraw.Draw(ap).ellipse([cx-110,cy-110,cx+110,cy+110],fill=255)   # aperture
    ring_=blank(); ImageDraw.Draw(ring_).ellipse([cx-R+45,cy-R+45,cx+R-45,cy+R-45],outline=255,width=10)
    nucl=blank(); ImageDraw.Draw(nucl).ellipse([cx+120,cy-200,cx+210,cy-110],fill=255)
    nucl2=blank(); ImageDraw.Draw(nucl2).ellipse([cx-215,cy-150,cx-140,cy-75],fill=255)
    vac=[]
    for (x,y,r) in [(cx+170,cy+150,26),(cx-180,cy+130,22),(cx+40,cy-230,18)]:
        v=blank(); ImageDraw.Draw(v).ellipse([x-r,y-r,x+r,y+r],fill=255); vac.append(v)
    return b,[ap,ring_,nucl,nucl2]+vac,nucl
specs=[('40-organism-contour-vorticella',vorticella,(1330,2650),11),
       ('41-organism-contour-nematode',nematode,(560,1900),12),
       ('42-organism-contour-arcella',testate,(1290,640),13)]
arts={}
for name,fn,lxy,seed in specs:
    body,org,pur=fn(); a=render(body,org,pur,seed,lxy); a.save(f'SFW-case-{name}.png'); arts[name]=a; print(name)
exec(open('cases2.py').read().split("# mockups")[1].split("ms=[")[0])
from PIL import ImageFilter
ms=[mock(v.convert('RGBA')) for v in arts.values()]
sheet=Image.new('RGB',(len(ms)*1000+80,2040),(226,222,214)); x=50
for mm in ms: sheet.paste(mm,(x,80),mm); x+=1000
sheet.save('SFW-phone-cases-organism-contours-preview.png'); sheet.resize((sheet.width//2,sheet.height//2)).save('/tmp/oc.png')
