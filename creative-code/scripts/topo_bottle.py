import numpy as np, cv2
from skimage import measure
from PIL import Image, ImageDraw, ImageFont, ImageCms
ICC=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
W,H=2751,1200
g=cv2.imread('/home/claude/merch/micro/Testate amoebae 40x obj Jimena Fuentes.jpg',0).astype(np.float32)
h,w=g.shape; s=max(W/w,H/h)*1.25; g=cv2.resize(g,(int(w*s),int(h*s)))
y0=(g.shape[0]-H)//2+80; x0=(g.shape[1]-W)//2; g=g[y0:y0+H,x0:x0+W]
g=cv2.GaussianBlur(cv2.resize(g,(W//4,H//4)),(0,0),14)
from skimage.exposure import equalize_hist
g=cv2.GaussianBlur(equalize_hist(g).astype(np.float32),(0,0),3)
S=3; im=Image.new('L',(W*S,H*S),0); d=ImageDraw.Draw(im)
for lv in np.linspace(g.min(),g.max(),13)[1:-1]:
    for c in measure.find_contours(g,lv):
        if len(c)<25: continue
        d.line([(x*4*S,y*4*S) for y,x in c],fill=255,width=8*S,joint='curve')
# clear a quiet band for the wordmark on the front (centre of the wrap)
f=ImageFont.truetype('/home/claude/merch/brand/ebg600.ttf',62*S); t='SOIL FOOD WEB'
sp=10*S; tw=sum(d.textlength(ch,font=f) for ch in t)+sp*(len(t)-1); x=(W*S-tw)/2; y=H*S-210*S
d.rectangle([x-50*S,y-30*S,x+tw+50*S,y+100*S],fill=0)
for ch in t: d.text((x,y),ch,font=f,fill=255); x+=d.textlength(ch,font=f)+sp
a=im.resize((W,H),Image.LANCZOS); a=a.point(lambda v:255 if v>110 else 0)
out=Image.new('RGBA',(W,H),(255,255,255,0)); out.putalpha(a)
out.save('SFW-topo-bottle-wrap.png',icc_profile=ICC,dpi=(300,300))
for name,bg in (('black',(28,28,28)),('navy',(30,40,70))):
    p=Image.new('RGB',(W,H),bg); p.paste(out,(0,0),out); p.resize((W//3,H//3)).save(f'/tmp/bottle-{name}.jpg')
