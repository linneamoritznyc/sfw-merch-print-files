import numpy as np, cv2, sys
from skimage import measure
from skimage.exposure import equalize_hist
from PIL import Image, ImageDraw, ImageFont, ImageCms
ICC=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
W,H=2751,1200; SRC='/home/claude/merch/micro/Testate amoebae 40x obj Jimena Fuentes.jpg'
G0=cv2.imread(SRC,0).astype(np.float32)
def field(zoom,fx,fy):
    h,w=G0.shape; s=max(W/w,H/h)*zoom; g=cv2.resize(G0,(int(w*s),int(h*s)))
    y0=int((g.shape[0]-H)*fy); x0=int((g.shape[1]-W)*fx); g=g[y0:y0+H,x0:x0+W]
    g=cv2.GaussianBlur(cv2.resize(g,(W//4,H//4)),(0,0),14)
    return cv2.GaussianBlur(equalize_hist(g).astype(np.float32),(0,0),3)
LV=8
def draw(g,S,lw):
    im=Image.new('L',(int(W*S),int(H*S)),0)
    d=ImageDraw.Draw(im)
    for lv in np.linspace(g.min(),g.max(),LV)[1:-1]:
        for c in measure.find_contours(g,lv):
            if len(c)<25: continue
            d.line([(x*4*S,y*4*S) for y,x in c],fill=255,width=max(1,int(lw*S)),joint='curve')
    return im,d
f1=ImageFont.truetype('/home/claude/merch/brand/ebg600.ttf',62)
t='SOIL FOOD WEB'; sp=10
tw=int(sum(f1.getlength(ch) for ch in t)+sp*(len(t)-1)); th=70; pad=30
best=None
for zoom in (1.0,1.15,1.3,1.5):
  for fx in np.linspace(0,1,9):
    for fy in np.linspace(0,1,7):
        g=field(zoom,fx,fy); im,_=draw(g,0.25,8); a=np.asarray(im)>0
        for yy in range(int(H*0.55/4), int((H-th-pad-80)/4), 3):
          for xx in range(int(W*0.08/4), int((W*0.92-tw)/4), 4):
            win=a[yy-pad//4:yy+(th+pad)//4, xx-pad//4:xx+(tw+pad)//4]
            if not win.any():
                sc=yy-abs(xx*4+tw/2-W/2)/20
                if best is None or sc>best[4]: best=(zoom,fx,fy,yy,sc,xx)
print(best)
zoom,fx,fy,yy,_,xx=best
g=field(zoom,fx,fy); S=3; im,d=draw(g,S,8)
f=ImageFont.truetype('/home/claude/merch/brand/ebg600.ttf',62*S); x=xx*4*S; y=yy*4*S
for ch in t: d.text((x,y),ch,font=f,fill=255); x+=d.textlength(ch,font=f)+sp*S
a=im.resize((W,H),Image.LANCZOS).point(lambda v:255 if v>110 else 0)
out=Image.new('RGBA',(W,H),(255,255,255,0)); out.putalpha(a)
out.save('SFW-topo-bottle-wrap.png',icc_profile=ICC,dpi=(300,300))
p=Image.new('RGB',(W,H),(28,28,28)); p.paste(out,(0,0),out); p.resize((W//3,H//3)).save('/tmp/bottle-black.jpg')
