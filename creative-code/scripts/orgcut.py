import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, sobel, label, binary_fill_holes, binary_closing, binary_opening, binary_erosion
M='/home/claude/merch/micro/'
def cut(nm, pick, mode='edge', N=1600, erodef=0.03):
    im=Image.open(M+f'circ_{nm}.png').convert('RGBA')
    g=np.asarray(im.convert('L').resize((N,N))).astype(float)
    A=binary_erosion(np.asarray(im.split()[3].resize((N,N)))>200,iterations=int(N*erodef))
    if mode=='edge':
        dev=np.abs(g-gaussian_filter(g,N/30)); e=gaussian_filter(np.hypot(sobel(g,0),sobel(g,1)),3)
        s=(gaussian_filter(dev,3)>np.percentile(dev[A],80))|(e>np.percentile(e[A],85))
    else:
        s=gaussian_filter(g,4)<np.percentile(g[A],mode)
    s&=A; s=binary_closing(s,iterations=6); s=binary_opening(s,iterations=4); s=binary_fill_holes(s)
    lab,_=label(s); px,py=int(pick[0]*N),int(pick[1]*N); k=lab[py,px]
    if k==0:
        ys,xs=np.nonzero(lab); i=((xs-px)**2+(ys-py)**2).argmin(); k=lab[ys[i],xs[i]]
    body=gaussian_filter((lab==k).astype(float),3)>0.5
    # interior detail, two-tone like the collage
    loc=g-gaussian_filter(g,N/60); det=gaussian_filter(loc,1.2)>0
    ys,xs=np.nonzero(body); y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    return body[y0:y1,x0:x1], det[y0:y1,x0:x1]
