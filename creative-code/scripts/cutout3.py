import random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
def hx(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
C=dict(navy=hx('1A2C52'),blue=hx('3780B8'),lblue=hx('96C4E8'),purple=hx('6B4C7A'),lil=hx('C8B6E2'),dg=hx('22371F'),fwg=hx('156826'),lg=hx('59A66C'),lime=hx('BED65A'),pg=hx('CBD696'),cream=hx('F4F1EA'))
def shape(i,blur=6,minfrac=0.002):
    p=Image.open(f'/home/claude/merch/micro/plate_{i}.png').convert('RGBA').split()[3]
    n=p.width; m=Image.new('L',p.size,0); ImageDraw.Draw(m).ellipse([n*0.08,n*0.08,n*0.92,n*0.92],fill=255)
    a=np.minimum(np.asarray(p),np.asarray(m)).astype(float)
    a=ndi.gaussian_filter(a,blur)>100
    a=ndi.binary_opening(a,iterations=2)
    lab,k=ndi.label(a); sizes=ndi.sum(a,lab,range(1,k+1)); keep=np.isin(lab,1+np.nonzero(sizes>minfrac*a.size)[0])
    m=Image.fromarray((keep*255).astype(np.uint8)).resize((n*3,n*3),Image.BICUBIC).filter(ImageFilter.GaussianBlur(4))
    return m.point(lambda v:255 if v>127 else 0)
SH={i:shape(i) for i in range(16)}
def compose(W,H,seed,bg,cols,name,n=11):
    r=random.Random(seed); im=Image.new('RGB',(W,H),C[bg]); order=list(range(16)); r.shuffle(order)
    for k in range(n):
        m=SH[order[k%16]].rotate(r.choice([0,90,180,270]),expand=True); s=int(r.uniform(0.55,1.15)*H)
        m=m.resize((s,s),Image.LANCZOS).point(lambda v:255 if v>127 else 0)
        x=int(r.uniform(-0.25,1.0)*W-s*0.25); y=int(r.uniform(-0.4,0.6)*H)
        im.paste(C[cols[k%len(cols)]],(x,y),m)
    im.save(name); return im
P1=['purple','lblue','fwg','lime','blue','lil','lg','navy','pg']
P2=['lime','lil','blue','lg','pg','lblue','purple','fwg']
P3=['fwg','purple','lblue','lime','navy','lil','blue','pg']
a=compose(2400,1300,4,'cream',P1,'SFW-micro-cutout-a.png')
b=compose(2400,1300,7,'navy',P2,'SFW-micro-cutout-b.png')
c=compose(2400,1300,9,'lil',P3,'SFW-micro-cutout-c.png')
S=Image.new('RGB',(1240,3*670+20),(226,222,214))
for i,v in enumerate([a,b,c]): S.paste(v.resize((1200,650),Image.LANCZOS),(20,20+i*670))
S.save('SFW-micro-cutout-preview.jpg',quality=90)
