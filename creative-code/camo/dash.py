import numpy as np, cv2, sys
from skimage import measure
from PIL import Image, ImageDraw, ImageCms
ICC=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
def dashed(f,W,H,out,blur=55,levels=12,zoom=1.0,bg=(20,21,19),col=(214,214,206),lw=7,dash=46,gap=26):
    g=cv2.imread('/home/claude/merch/micro/'+f,0).astype(np.float32)
    h,w=g.shape; s=max(W/w,H/h)*zoom; g=cv2.resize(g,(int(w*s)+2,int(h*s)+2))
    y0=(g.shape[0]-H)//2; x0=(g.shape[1]-W)//2; g=g[y0:y0+H,x0:x0+W]
    g=cv2.GaussianBlur(cv2.resize(g,(W//4,H//4)),(0,0),blur/4)
    im=Image.new('RGB',(W,H),bg); d=ImageDraw.Draw(im)
    for lv in np.linspace(g.min(),g.max(),levels+2)[1:-1]:
        for c in measure.find_contours(g,lv):
            if len(c)<25: continue
            p=c[:,::-1]*4; seg=np.r_[0,np.cumsum(np.hypot(*np.diff(p,axis=0).T))]
            per=dash+gap; on=(seg%per)<dash
            run=[]
            for pt,o in zip(p,on):
                if o: run.append(tuple(pt))
                elif run:
                    if len(run)>1: d.line(run,fill=col,width=lw,joint='curve')
                    run=[]
            if len(run)>1: d.line(run,fill=col,width=lw,joint='curve')
    im.save(out,icc_profile=ICC)
dashed('Testate amoebae 40x obj Jimena Fuentes.jpg',6600,6900,'SFW-topo-dashed-jacket.png',blur=120,levels=8,lw=13,dash=95,gap=55)
