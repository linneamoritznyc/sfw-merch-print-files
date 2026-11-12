import numpy as np, random
from PIL import Image, ImageDraw, ImageFilter
L='/home/claude/merch/logos/'
def hx(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
CRM=hx('F4F1EA')
# 1) logo on cream circle, for die-cut sticker + magnet
N=1800; im=Image.new('RGBA',(N,N),(0,0,0,0)); ImageDraw.Draw(im).ellipse([20,20,N-21,N-21],fill=CRM+(255,))
lg=Image.open(L+'SFW-logo-flower-colour.png').convert('RGBA').resize((1420,1420),Image.LANCZOS); im.alpha_composite(lg,((N-1420)//2,(N-1420)//2))
big=im.resize((N*2,N*2),Image.LANCZOS); im=big.resize((N,N),Image.LANCZOS); im.save('SFW-sticker-logo-circle.png')
# 2) sticker sheet: 10 microbe discs + 2 logo circles
def plate(i,size,rot):
    p=Image.open(f'/home/claude/merch/micro/plate_{i}.png').convert('RGBA').split()[3].rotate(rot)
    p=p.resize((size,size),Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))
    return np.asarray(p)>107
PAIRS=[(hx('6B4C7A'),(176,176,146)),(hx('156826'),CRM),(hx('1A2C52'),hx('96C4E8')),(hx('22371F'),hx('BED65A')),
       (hx('C8B6E2'),hx('6B4C7A')),(hx('3780B8'),CRM),(CRM,hx('156826')),(hx('5B6B2E'),hx('CBD696')),(hx('6B4C7A'),hx('C8B6E2')),(hx('1A2C52'),hx('BED65A'))]
W,H=1750,2482; sheet=Image.new('RGBA',(W,H),(0,0,0,0))
cols,rows=3,4; cw,ch=W/cols,H/rows; D=int(min(cw,ch)-70)
cells=[(c,r) for r in range(rows) for c in range(cols)]
logo_cells={(1,0),(1,3)}
r=random.Random(3); order=[5,1,10,2,4,11,0,3,15,1]; k=0
for (c,rw) in cells:
    cx,cy=int((c+0.5)*cw),int((rw+0.5)*ch)
    if (c,rw) in logo_cells:
        s=im.resize((D,D),Image.LANCZOS); sheet.alpha_composite(s,(cx-D//2,cy-D//2)); continue
    bg,ink=PAIRS[k%len(PAIRS)]
    m=plate(order[k],int(D*1.25),r.choice([0,90,180,270])); o=(m.shape[0]-D)//2; m=m[o:o+D,o:o+D]
    a=np.zeros((D,D,4),np.uint8); a[...,:3]=bg; a[m,:3]=ink; a[...,3]=255
    yy,xx=np.mgrid[0:D,0:D]; a[((xx-D/2)**2+(yy-D/2)**2)>(D/2-2)**2,3]=0
    t=Image.fromarray(a,'RGBA'); sheet.alpha_composite(t,(cx-D//2,cy-D//2)); k+=1
sheet.save('SFW-sticker-sheet-microbes.png')
prev=Image.new('RGB',(W+40,H+40),(226,222,214)); prev.paste(sheet,(20,20),sheet); prev.resize((700,990)).save('/tmp/ss.png')
