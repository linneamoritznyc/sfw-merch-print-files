import numpy as np, cv2, random, sys
sys.path.insert(0,'.')
from camo import lines, fs
from PIL import Image
import topo
def camo_big(W,H,seed,green=(46,74,58),white=(242,242,236)):
    w,h=W//2,H//2; rnd=random.Random(seed); n=22
    pts=np.array([[rnd.uniform(-.1,1.1)*w,rnd.uniform(-.1,1.1)*h] for _ in range(n)])
    ys,xs=np.mgrid[0:h//4,0:w//4]*4
    nz=cv2.resize(cv2.GaussianBlur(np.random.RandomState(seed).randn(h//32+1,w//32+1).astype(np.float32),(0,0),2),(w//4+ (w//4==0),h//4))*40
    nz=cv2.resize(nz,(xs.shape[1],xs.shape[0]))
    lab=np.stack([(xs+nz-p[0])**2+(ys-nz-p[1])**2 for p in pts]).argmin(0).astype(np.uint8)
    lab=cv2.resize(lab,(w,h),interpolation=cv2.INTER_NEAREST)
    out=np.zeros((h,w),np.float32)
    for i in range(n):
        L=lines(rnd.choice(fs),rnd.uniform(.6,1.1)).astype(np.uint8)*255
        hh,ww=L.shape; R=cv2.getRotationMatrix2D((ww/2,hh/2),rnd.uniform(0,360),1)
        L=cv2.warpAffine(L,R,(ww,hh),borderMode=cv2.BORDER_REFLECT)
        L=cv2.resize(L,(w,h)) if (hh<h or ww<w) else L[:h,:w]
        m=(L>127).astype(np.float32)
        if rnd.random()<.35: m=1-m
        out[lab==i]=m[lab==i]
    out=cv2.resize(cv2.GaussianBlur(out,(0,0),0.8),(W,H),interpolation=cv2.INTER_CUBIC)>0.5
    img=np.zeros((H,W,3),np.uint8); img[:]=green; img[out]=white
    return Image.fromarray(img)
