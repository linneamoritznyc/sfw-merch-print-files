import random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter, zoom
Image.MAX_IMAGE_PIXELS=None
P_BG=(100,85,104); P_INK=(176,176,146)
def plate(i):
    p=Image.open(f'/home/claude/merch/micro/plate_{i}.png').convert('RGBA').split()[3]
    m=Image.new('L',p.size,0); c=p.width/2; r=p.width*0.465; ImageDraw.Draw(m).ellipse([c-r,c-r,c+r,c+r],fill=255)
    return Image.fromarray(np.minimum(np.asarray(p),np.asarray(m)))
PL=[plate(i) for i in range(16)]
def field(seed,W,H,n,warp):
    r=random.Random(seed); g=np.random.default_rng(seed)
    sw,sh=W//8,H//8
    up=lambda a: np.array(Image.fromarray(a.astype(np.float32)).resize((W,H),Image.BILINEAR))
    wx=up(gaussian_filter(g.normal(0,1,(sh,sw)),8)); wy=up(gaussian_filter(g.normal(0,1,(sh,sw)),8))
    wx*=warp/wx.std(); wy*=warp/wy.std()
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32); X=xx+wx; Y=yy+wy; del xx,yy
    pts=[(r.uniform(0,W),r.uniform(0,H)) for _ in range(n)]
    best=np.full((H,W),np.inf,np.float32); reg=np.zeros((H,W),np.int16)
    for k,(x,y) in enumerate(pts):
        d=(X-x)**2+(Y-y)**2; m=d<best; best[m]=d[m]; reg[m]=k
    del X,Y,best
    L=np.zeros((H,W),np.uint8); order=list(range(16))
    for k in range(n):
        m=reg==k
        if not m.any(): continue
        ys,xs=np.nonzero(m); y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1; h,w=y1-y0,x1-x0
        s=int(max(h,w)*1.25)+10
        p=PL[r.randrange(16)].rotate(r.choice([0,90,180,270])).resize((s,s),Image.LANCZOS).filter(ImageFilter.GaussianBlur(max(1,s/600)))
        A=np.asarray(p).astype(np.float32)/255; oy=(s-h)//2; ox=(s-w)//2; A=A[oy:oy+h,ox:ox+w]
        inv=r.random()<0.5; t=((A>0.42)!=inv).astype(np.uint8)
        sub=L[y0:y1,x0:x1]; mm=m[y0:y1,x0:x1]; sub[mm]=t[mm]
    return L
def stitch(L,cw,ch):
    H,W=L.shape; im=Image.new('RGB',(W,H),P_BG); d=ImageDraw.Draw(im); cols=[P_BG,P_INK]
    dark=[tuple(int(c*0.86) for c in col) for col in cols]
    for y in range(0,H,ch):
        for x in range(0,W,cw):
            v=L[min(H-1,y+ch//2),min(W-1,x+cw//2)]; c=cols[v]; dk=dark[v]
            d.polygon([(x,y),(x+cw/2,y+ch*0.2),(x+cw/2,y+ch),(x,y+ch*0.8)],fill=c)
            d.polygon([(x+cw/2,y+ch*0.2),(x+cw,y),(x+cw,y+ch*0.8),(x+cw/2,y+ch)],fill=dk)
    return im
def panel(seed,W,H,n):
    L=field(seed,W//2,H//2,n,60*1.0)
    L=np.kron(L,np.ones((2,2),np.uint8))[:H,:W]
    return stitch(L,14,18)
import sys
which=sys.argv[1]
if which=='front':
    im=panel(41,5250,6750,110)
    lg=Image.open('/home/claude/merch/logos/SFW-logo-flower-white-3000.png').convert('RGBA').resize((760,760),Image.LANCZOS)
    o=im.convert('RGBA'); o.alpha_composite(lg,(int(5250*0.66)-380,int(6750*0.43)-380)); o.convert('RGB').save('SFW-aop-tee-microbes-front.png')
elif which=='back': panel(42,5250,6750,110).save('SFW-aop-tee-microbes-back.png')
elif which=='sl': panel(43,5250,3000,45).save('SFW-aop-tee-microbes-sleeve-left.png')
else: panel(44,5250,3000,45).save('SFW-aop-tee-microbes-sleeve-right.png')
