import numpy as np, cv2, glob, random
from PIL import Image
M='/home/claude/merch/micro/'
fs=[f for f in glob.glob(M+'*.jpg')]
def lines(f, s):
    g=cv2.imread(f,0).astype(np.float32)
    g=cv2.resize(g,None,fx=s,fy=s,interpolation=cv2.INTER_AREA)
    bg=cv2.GaussianBlur(g,(0,0),25)
    d=np.abs(g-bg)
    d=cv2.GaussianBlur(d,(0,0),1.2)
    t=np.percentile(d,84)
    return (d>t)
def make(W,H,seed,green=(46,74,58),white=(242,242,236)):
    rnd=random.Random(seed)
    out=np.zeros((H,W),bool)
    # big hand-cut shards: random polygons, each filled with a rotated micrograph texture
    n=26
    pts=np.array([[rnd.uniform(-.1,1.1)*W,rnd.uniform(-.1,1.1)*H] for _ in range(n)])
    yy,xx=np.mgrid[0:H,0:W]
    dist=np.stack([(xx-p[0])**2+(yy-p[1])**2 for p in pts]); lab=dist.argmin(0)
    # rough the borders
    noise=cv2.GaussianBlur(np.random.RandomState(seed).randn(H//8,W//8).astype(np.float32),(0,0),2)
    noise=cv2.resize(noise,(W,H))*40
    lab=np.stack([(xx+noise-p[0])**2+(yy-noise-p[1])**2 for p in pts]).argmin(0)
    for i in range(n):
        f=rnd.choice(fs); L=lines(f,rnd.uniform(.5,1.0)).astype(np.uint8)*255
        ang=rnd.uniform(0,360); h,w=L.shape
        R=cv2.getRotationMatrix2D((w/2,h/2),ang,1)
        L=cv2.warpAffine(L,R,(w,h),borderMode=cv2.BORDER_REFLECT)
        L=cv2.resize(L,(W,H)) if (h<H or w<W) else L[:H,:W]
        m=L>127
        if rnd.random()<.35: m=~m
        out[lab==i]=m[lab==i]
    img=np.zeros((H,W,3),np.uint8); img[:]=green; img[out]=white
    return Image.fromarray(img)
if __name__=='__main__':
    for s in (1,2,3):
        make(1800,1800,s).save(f'camo{s}.png')
