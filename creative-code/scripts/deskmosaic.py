import numpy as np, random, glob, os
from PIL import Image, ImageFilter, ImageOps
from scipy.ndimage import gaussian_filter
def hx(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
CRM=hx('F4F1EA')
PAIRS=[(hx('6B4C7A'),(176,176,146)),(hx('156826'),CRM),(hx('1A2C52'),hx('96C4E8')),(hx('22371F'),hx('BED65A')),
       (hx('C8B6E2'),hx('6B4C7A')),(hx('3780B8'),CRM),(CRM,hx('156826')),(hx('5B6B2E'),hx('CBD696')),(hx('6B4C7A'),hx('C8B6E2')),(hx('1A2C52'),hx('BED65A')),
       (hx('96C4E8'),hx('1A2C52')),(hx('BED65A'),hx('22371F'))]
fs=sorted(f for f in glob.glob('/home/claude/merch/micro/*.jpg'))
W,H=5610,3839; C,R=5,4; cw=W/C; ch=H/R
r=random.Random(11); pick=r.sample(fs,len(fs))+r.sample(fs,C*R-len(fs))
out=Image.new('RGB',(W,H))
for k,f in enumerate(pick):
    c,rw=k%C,k//C; x0,y0=int(c*cw),int(rw*ch); x1,y1=int((c+1)*cw),int((rw+1)*ch); w,h=x1-x0,y1-y0
    g=ImageOps.grayscale(Image.open(f)); s=min(g.size); z=r.uniform(0.55,0.8); s2=int(s*z)
    ox=(g.width-s2)//2+r.randint(-s//10,s//10); oy=(g.height-s2)//2+r.randint(-s//10,s//10)
    ox=max(0,min(g.width-s2,ox)); oy=max(0,min(g.height-s2,oy))
    g=g.crop((ox,oy,ox+s2,oy+s2)).resize((max(w,h),max(w,h)),Image.LANCZOS).crop((0,0,w,h))
    a=np.asarray(g).astype(np.float32); bgl=gaussian_filter(a,max(w,h)/8); d=a-bgl
    d=gaussian_filter(d,1.5); m=d< -np.std(d)*0.35
    bg,ink=PAIRS[(k*5)%len(PAIRS)]
    t=np.zeros((h,w,3),np.uint8); t[:]=bg; t[m]=ink
    out.paste(Image.fromarray(t),(x0,y0))
out.save('SFW-deskmat-mosaic-nologo.png')
o=out.convert('RGBA'); S=900
lg=Image.open('/home/claude/merch/logos/SFW-logo-flower-colour.png').convert('RGBA').resize((S,S),Image.LANCZOS)
# cream square tile behind logo at centre so it reads
from PIL import ImageDraw
T=int(cw*1.0); cx,cy=W//2,H//2
ImageDraw.Draw(o).rectangle([cx-T//2,cy-T//2,cx+T//2,cy+T//2],fill=CRM+(255,))
o.alpha_composite(lg,(cx-S//2,cy-S//2)); o.convert('RGB').save('SFW-deskmat-mosaic-logo.png')
p=Image.new('RGB',(1900,1330),(230,228,222))
for i,f in enumerate(['SFW-deskmat-mosaic-nologo.png','SFW-deskmat-mosaic-logo.png']):
    im=Image.open(f); im.thumbnail((1880,640)); p.paste(im,(10,10+i*660))
p.save('SFW-deskmat-mosaic-preview.jpg',quality=88)
