import numpy as np, math
from PIL import Image, ImageDraw, ImageFilter
exec(open('cases2.py').read().split("CAM=")[0])
W,H=1800,3680
src=Image.open('passion/src.png').convert('RGB')
def prep(scale,cx,cy,rot=0):
    # place flower on a W x H field; return float RGB + flower mask
    s=src.rotate(rot,resample=Image.BICUBIC) if rot else src
    w=int(s.width*scale); h=int(s.height*scale)
    s=s.resize((w,h),Image.LANCZOS)
    f=Image.new('RGB',(W,H),(0,0,0)); f.paste(s,(cx-w//2,cy-h//2))
    a=np.asarray(f).astype(float)/255
    r,g,b=a[...,0],a[...,1],a[...,2]; lum=0.3*r+0.59*g+0.11*b
    leaf=(g>r+0.04)&(g>b+0.02)&(lum<0.45)        # dark green leaves
    m=np.clip((lum-0.18)/0.5,0,1); m[leaf]=0
    return a,lum,m
def halftone(bg,pal,scale,cx,cy,rot=0,cell=14,seed=0,mono=None):
    a,lum,m=prep(scale,cx,cy,rot)
    im=Image.new('RGB',(W*SS,H*SS),bg); d=ImageDraw.Draw(im)
    P=np.array(pal[1],float)/255; T=np.array(pal[0],float)/255   # target colours -> dot colours
    for gy in np.arange(0,H,cell):
        off=cell/2 if int(gy/cell)%2 else 0
        for gx in np.arange(off,W,cell):
            y,x=min(H-1,int(gy)),min(W-1,int(gx)); v=m[y,x]
            if v<0.08: continue
            c=a[y,x]
            if mono: col=mono
            else: col=tuple(pal[1][int(np.argmin(((T-c)**2).sum(1)))])
            rad=cell*0.5*v**0.55
            d.ellipse([(gx-rad)*SS,(gy-rad)*SS,(gx+rad)*SS,(gy+rad)*SS],fill=col)
    out=im.resize((W,H),Image.LANCZOS); o=np.asarray(out).astype(float)
    g=np.random.default_rng(seed).normal(0,1,o.shape[:2])
    return Image.fromarray((o*(1+0.03*g[...,None])).clip(0,255).astype(np.uint8))
# source colour -> dot colour mapping: (lilac petal, deep violet ring, white filament, pale green stamen, mauve centre)
SRCC=[(165,160,205),(70,40,140),(235,235,245),(225,230,160),(150,90,110)]
DO=(34,48,26); PURB=(58,34,74); EB=(55,128,184); OLV=(91,107,46)
specs={
 'passion-1-olive-full':(DO,[SRCC,[(190,170,230),(120,70,170),(240,236,248),(214,226,140),(150,96,150)]],5.0,900,1840,0),
 'passion-2-purple-crop':(PURB,[SRCC,[(196,176,232),(30,16,44),(246,240,252),(214,226,140),(170,110,170)]],9.5,1500,2700,20),
 'passion-3-olive-mono':(DO,[SRCC,SRCC],7.0,700,1500,-15,'mono'),
 'passion-4-blue':(EB,[SRCC,[(214,226,140),(26,44,82),(240,244,250),(214,226,140),(150,196,232)]],6.2,1100,2300,35),
}
arts={}
for i,(n,sp) in enumerate(specs.items()):
    bg,pal,sc,cx,cy,rot=sp[:6]; mono=(203,214,150) if len(sp)>6 else None
    arts[n]=halftone(bg,pal,sc,cx,cy,rot,seed=i,mono=mono); arts[n].save(f'SFW-case-{n}.png')
exec(open('cases2.py').read().split("# mockups")[1].split("ms=[")[0])
ms=[mock(v.convert('RGBA')) for v in arts.values()]
sheet=Image.new('RGB',(len(ms)*1000+80,2040),(226,222,214)); x=50
for mm in ms: sheet.paste(mm,(x,80),mm); x+=1000
sheet.convert('RGB').save('SFW-phone-cases-passionflower-preview.jpg',quality=90)
