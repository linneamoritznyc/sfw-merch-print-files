import glob, numpy as np
from PIL import Image, ImageDraw, ImageOps, ImageCms
from scipy.ndimage import gaussian_filter, label, binary_fill_holes, binary_closing
Image.MAX_IMAGE_PIXELS=None
M='/home/claude/merch/micro/'; ICC=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
COLS=[(70,167,112),(186,160,226),(178,214,72)]
def mask_from_photo(path,R,crop):
    im=ImageOps.grayscale(Image.open(path)); w,h=im.size; s=int(min(w,h)*crop[2])
    x=int(np.clip(crop[0]*w-s/2,0,w-s)); y=int(np.clip(crop[1]*h-s/2,0,h-s))
    g=np.asarray(im.crop((x,y,x+s,y+s)).resize((R,R),Image.LANCZOS)).astype(float)
    hp=g-gaussian_filter(g,R/40); a=np.abs(gaussian_filter(hp,1.0))
    return a>np.percentile(a,78)
def tile(a,R):
    c=binary_closing(a,iterations=int(R/180)); lab,n=label(c); sz=np.bincount(lab.ravel()); sz[0]=0
    out=np.zeros((R,R,3),np.uint8)
    yy,xx=np.mgrid[0:R,0:R]; inside=np.hypot(xx-R/2,yy-R/2)<R/2-6
    for j,k in enumerate(np.argsort(sz)[::-1][:3]): out[binary_fill_holes(lab==k)&inside]=COLS[j]
    out[a]=(255,255,255)
    im=Image.fromarray(out); m=Image.new('L',(R,R),0); ImageDraw.Draw(m).ellipse([3,3,R-4,R-4],fill=255)
    bg=Image.new('RGB',(R,R),(0,0,0)); bg.paste(im,(0,0),m); ImageDraw.Draw(bg).ellipse([3,3,R-4,R-4],outline=(255,255,255),width=max(3,R//400))
    return bg
