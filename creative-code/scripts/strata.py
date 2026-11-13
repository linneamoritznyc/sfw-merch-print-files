import numpy as np
from PIL import Image, ImageDraw, ImageCms
from scipy.ndimage import gaussian_filter1d
ICC=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
W=H=3000; r=np.random.default_rng(11)
INK=(26,24,20); CR=(238,228,200); GRN=(110,150,52); BRN=(122,96,72); TAUPE=(160,140,118); DK=(64,48,36)
im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
xs=np.linspace(-20,W+20,300)
def edge(y,amp,seed,smooth=18):
    rr=np.random.default_rng(seed); return y+gaussian_filter1d(rr.normal(0,1,len(xs)),smooth)*amp*9
tops=[edge(y,a,i) for i,(y,a) in enumerate([(820,10),(960,12),(1200,14),(1450,12),(1700,16),(1990,14),(2300,18),(2640,14)])]
bottom=np.full_like(xs,H+20)
def band(i,col):
    top=tops[i]; bot=tops[i+1] if i+1<len(tops) else bottom
    d.polygon(list(zip(xs,top))+list(zip(xs[::-1],bot[::-1])),fill=col)
    return top,bot
def inside(top,bot,x,y): yt=np.interp(x,xs,top); yb=np.interp(x,xs,bot); return yt+12<y<yb-12
def wob(pts,a=2.5): return [(x+r.normal(0,a),y+r.normal(0,a)) for x,y in pts]
# 0: grass line + litter (cream ground, short black dashes)
t,b=band(0,CR)
for _ in range(900):
    x=r.uniform(0,W); y=r.uniform(t.min(),b.max())
    if inside(t,b,x,y):
        L=r.uniform(18,46); a=r.normal(0,0.15); d.line(wob([(x,y),(x+L*np.cos(a),y+L*np.sin(a))]),fill=INK,width=int(r.uniform(5,9)))
d.line(wob(list(zip(xs,tops[0])),1.5),fill=GRN,width=34)
for _ in range(220):  # grass blades
    x=r.uniform(0,W); y=np.interp(x,xs,tops[0])-8; h=r.uniform(20,110)*(0.4+abs(np.sin(x/170))); lean=r.normal(0,14)
    d.line([(x,y),(x+lean,y-h)],fill=GRN,width=7)
# 1: dark brown with cream crumbs (aggregates)
t,b=band(1,DK)
for _ in range(1400):
    x=r.uniform(0,W); y=r.uniform(t.min(),b.max())
    if inside(t,b,x,y):
        s=r.uniform(5,14); d.ellipse([x-s*1.3,y-s,x+s*1.3,y+s],fill=CR)
# 2: taupe with little rings (soil aggregates)
t,b=band(2,TAUPE)
for _ in range(700):
    x=r.uniform(0,W); y=r.uniform(t.min(),b.max())
    if inside(t,b,x,y):
        s=r.uniform(9,20); d.ellipse([x-s,y-s*0.8,x+s,y+s*0.8],outline=INK,width=5)
# 3: black with cream fungal hyphae threads
t,b=band(3,INK)
for _ in range(70):
    x0=r.uniform(-100,W); y0=r.uniform(t.min(),b.max()); pts=[]; x,y=x0,y0; a=r.normal(0,0.4)
    for k in range(60):
        a+=r.normal(0,0.18); x+=9*np.cos(a); y+=9*np.sin(a)
        if not inside(t,b,x,y): break
        pts.append((x,y))
    if len(pts)>4: d.line(pts,fill=CR,width=5,joint='curve')
# 4: cream with black seed dots in rows
t,b=band(4,CR)
for _ in range(1500):
    x=r.uniform(0,W); y=r.uniform(t.min(),b.max())
    if inside(t,b,x,y):
        s=r.uniform(6,12); a=r.normal(0,0.3); d.ellipse([x-s*1.6,y-s,x+s*1.6,y+s],fill=INK)
# 5: brown with vertical hatch, uneven
t,b=band(5,BRN)
for x in np.arange(0,W,26):
    x=x+r.normal(0,4); yt=np.interp(x,xs,t)+10; yb=np.interp(x,xs,b)-10
    d.line(wob([(x,yt),(x+r.normal(0,10),yb)],2),fill=INK,width=6)
# 6: black bedrock with cream stones
t,b=band(6,INK)
for _ in range(16):
    x=r.uniform(80,W-80); y=r.uniform(t.min()+60,b.max()-40)
    if inside(t,b,x,y):
        s=r.uniform(40,110); ang=np.linspace(0,2*np.pi,30)
        rr=s*(1+gaussian_filter1d(r.normal(0,0.25,30),2,mode='wrap'))
        d.polygon(list(zip(x+rr*np.cos(ang)*1.4,y+rr*np.sin(ang)*0.8)),fill=CR)
# 7: deepest band, taupe dashes
t,b=band(7,TAUPE)
for _ in range(500):
    x=r.uniform(0,W); y=r.uniform(t.min(),b.max())
    if inside(t,b,x,y): d.line([(x,y),(x+r.uniform(20,50),y+r.normal(0,4))],fill=INK,width=6)
# a root diving down through the layers, with fine root hairs
def root(x,y,a,L,w,depth):
    pts=[(x,y)]
    for k in range(int(L/12)):
        a+=r.normal(0,0.11); a+=(np.pi/2-a)*0.04; x+=12*np.cos(a); y+=12*np.sin(a); pts.append((x,y))
        if depth<3 and r.random()<0.045: root(x,y,a+r.choice([-0.8,0.8]),L*0.45,max(4,w*0.55),depth+1)
        if r.random()<0.25:
            aa=a+r.choice([-1.3,1.3]); d.line([(x,y),(x+28*np.cos(aa),y+28*np.sin(aa))],fill=GRN,width=4)
    d.line(pts,fill=CR,width=int(w)+10,joint='curve'); d.line(pts,fill=INK,width=int(w),joint='curve')
root(1700,tops[0][150]-30,np.pi/2+0.05,1700,26,0)
# logo, small, in the empty sky
lg=Image.open('/home/claude/merch/logos/SFW-logo-flower-colour.png').convert('RGBA'); lg.thumbnail((420,420),Image.LANCZOS)
im.alpha_composite(lg,((W-lg.width)//2,260))
im.save('SFW-soil-strata-tote.png',icc_profile=ICC,dpi=(300,300))
for n,bg in (('oyster',(232,226,210)),('black',(30,30,30))):
    p=Image.new('RGB',(W,H),bg); p.paste(im,(0,0),im); p.resize((750,750),Image.LANCZOS).save(f'/tmp/tote-{n}.jpg')
