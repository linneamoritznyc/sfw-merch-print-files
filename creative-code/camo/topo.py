import numpy as np, cv2
from skimage import measure
from PIL import Image, ImageDraw
M='/home/claude/merch/micro/'
def topo(f,W=1800,H=2100,levels=9,blur=40,col=(200,200,195),bg=(14,14,14),lw=5,out='t.png'):
    g=cv2.imread(M+f,0).astype(np.float32)
    h,w=g.shape; s=max(W/w,H/h); g=cv2.resize(g,(int(w*s)+1,int(h*s)+1))[:H,:W]
    g=cv2.GaussianBlur(g,(0,0),blur)
    im=Image.new('RGB',(W*2,H*2),bg); d=ImageDraw.Draw(im)
    for lv in np.linspace(g.min(),g.max(),levels+2)[1:-1]:
        for c in measure.find_contours(g,lv):
            if len(c)<60: continue
            d.line([(x*2,y*2) for y,x in c[::2]],fill=col,width=lw*2,joint='curve')
    im.resize((W,H),Image.LANCZOS).save(out)
topo('Nematode (molting) 40x obj Cameron Radman.jpg',out='topo-nematode.png')
topo('Testate amoebae 40x obj Jimena Fuentes.jpg',out='topo-testate.png',blur=30)
topo('Ciliates (stalked) 40x obj Sid Jensen.jpg',out='topo-ciliate.png',blur=22,levels=8)
