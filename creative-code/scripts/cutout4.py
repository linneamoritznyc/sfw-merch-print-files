import random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
exec(open('cutout3.py').read().split("def shape(")[0])
def organism(i):
    p=Image.open(f'/home/claude/merch/micro/plate_{i}.png').convert('RGBA').split()[3]
    n=p.width; m=Image.new('L',p.size,0); ImageDraw.Draw(m).ellipse([n*0.08,n*0.08,n*0.92,n*0.92],fill=255)
    a=np.minimum(np.asarray(p),np.asarray(m)).astype(float)
    b=ndi.gaussian_filter(a,5)>90; b=ndi.binary_closing(b,iterations=6); b=ndi.binary_fill_holes(b)
    lab,k=ndi.label(b)
    if k==0: return None
    sizes=ndi.sum(b,lab,range(1,k+1)); body=lab==(1+np.argmax(sizes))
    if body.sum()<0.01*b.size: return None
    ys,xs=np.nonzero(body); y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    body=body[y0:y1,x0:x1]
    inner=(ndi.gaussian_filter(a,3)>140)[y0:y1,x0:x1]&ndi.binary_erosion(body,iterations=8)
    inner=ndi.binary_opening(inner,iterations=2)
    up=lambda z:Image.fromarray((z*255).astype(np.uint8)).resize(((x1-x0)*3,(y1-y0)*3),Image.BICUBIC).filter(ImageFilter.GaussianBlur(5)).point(lambda v:255 if v>127 else 0)
    return up(body),up(~inner&body)
ORG=[o for o in (organism(i) for i in range(16)) if o]
print(len(ORG))
def compose(W,H,seed,bg,pairs,name,cols=5,rows=3):
    r=random.Random(seed); im=Image.new('RGB',(W,H),C[bg]); order=list(range(len(ORG))); r.shuffle(order); k=0
    cells=[(c,rw) for rw in range(rows) for c in range(cols)]; r.shuffle(cells)
    for (c,rw) in cells:
        b,ho=ORG[order[k%len(ORG)]]; rot=r.choice([0,90,180,270])
        b=b.rotate(rot,expand=True); ho=ho.rotate(rot,expand=True)
        cw,ch=W/cols,H/rows; s=r.uniform(1.1,1.6)*max(cw,ch)/max(b.size)
        sz=(int(b.width*s),int(b.height*s)); b=b.resize(sz,Image.LANCZOS); ho=ho.resize(sz,Image.LANCZOS)
        x=int((c+0.5)*cw+r.uniform(-0.25,0.25)*cw-sz[0]/2); y=int((rw+0.5)*ch+r.uniform(-0.25,0.25)*ch-sz[1]/2)
        f,inn=pairs[k%len(pairs)]
        im.paste(C[inn],(x,y),b); im.paste(C[f],(x,y),ho); k+=1
    im.save(name); return im
P1=[('purple','lil'),('lblue','blue'),('fwg','lime'),('lime','fwg'),('blue','lblue'),('lil','purple'),('lg','pg'),('navy','lblue')]
P2=[('lime','fwg'),('lil','purple'),('blue','lblue'),('lg','pg'),('pg','lg'),('lblue','blue'),('purple','lil'),('fwg','lime')]
P3=[('fwg','lime'),('purple','lil'),('lblue','blue'),('lime','fwg'),('navy','lblue'),('blue','pg'),('pg','fwg')]
a=compose(2400,1300,4,'cream',P1,'SFW-micro-cutout-a.png')
b=compose(2400,1300,7,'navy',P2,'SFW-micro-cutout-b.png')
c=compose(2400,1300,9,'lil',P3,'SFW-micro-cutout-c.png')
S=Image.new('RGB',(1240,3*670+20),(226,222,214))
for i,v in enumerate([a,b,c]): S.paste(v.resize((1200,650),Image.LANCZOS),(20,20+i*670))
S.save('SFW-micro-cutout-preview.jpg',quality=90)
