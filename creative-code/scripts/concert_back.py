import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageCms
from scipy.ndimage import gaussian_filter
B='/home/claude/merch/brand/'; M='/home/claude/merch/micro/'
ICC=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
INK=(110,40,46); W,H=3600,4800
def mono(src,cx,cy,ch,w,h):
    im=ImageOps.grayscale(Image.open(src).convert('RGB')); iw,ih=im.size
    cw=ch*ih*w/h/iw
    box=(int((cx-cw/2)*iw),int((cy-ch/2)*ih),int((cx+cw/2)*iw),int((cy+ch/2)*ih))
    g=np.asarray(im.crop(box).resize((w,h),Image.LANCZOS)).astype(np.float32)
    t=gaussian_filter(-(g-gaussian_filter(g,w/10)),1.6)
    m=(t>np.percentile(t,60))|(gaussian_filter(g,2)<np.percentile(g,20))
    return gaussian_filter(m.astype(np.float32),1.2)>0.5
P=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(P)
def spaced(y,t,f,sp):
    tw=sum(d.textlength(c,font=f) for c in t)+sp*(len(t)-1); x=(W-tw)/2
    for c in t: d.text((x,y),c,font=f,fill=INK+(255,)); x+=d.textlength(c,font=f)+sp
fT=ImageFont.truetype(B+'ebg600.ttf',560); fU=ImageFont.truetype(B+'ebg600.ttf',400)
spaced(0,'THE',fT,40); spaced(600,'UNDERGROUND',fU,0)
bx,by,bw,bh=200,1330,3200,2900
import glob
org=mono([f for f in glob.glob(M+'*.jpg') if 'Ciliates (stalked)' in f][0],0.66,0.50,0.62,bw,bh)
blk=np.zeros((H,W),bool); blk[by:by+bh,bx:bx+bw]=~org
a=np.asarray(P.split()[3]).copy(); a[blk]=255
rgb=np.zeros((H,W,3),np.uint8); rgb[:]=INK
P=Image.fromarray(np.dstack([rgb,a])); d=ImageDraw.Draw(P)
spaced(by+bh+130,'STALKED CILIATE  ·  40X  ·  ON TOUR 2027',ImageFont.truetype(B+'ebg500.ttf',120),26)
P=P.crop(P.getbbox()); P.save(B+'SFW-concert-tee-back.png',icc_profile=ICC,dpi=(300,300))
M2=Image.new('RGB',(1400,1600),(232,232,232)); d=ImageDraw.Draw(M2)
d.polygon([(380,120),(560,80),(840,80),(1020,120),(1330,330),(1220,560),(1080,480),(1080,1520),(320,1520),(320,480),(180,560),(70,330)],fill=(178,178,176))
d.polygon([(560,80),(840,80),(780,120),(620,120)],fill=(160,160,158))
pw=640; p=P.resize((pw,int(pw*P.height/P.width)),Image.LANCZOS); M2.paste(p,((1400-pw)//2,230),p)
F=Image.open(B+'SFW-concert-tee-preview.jpg').convert('RGB')
both=Image.new('RGB',(2800,1600),(232,232,232)); both.paste(F,(0,0)); both.paste(M2,(1400,0))
both.save(B+'SFW-concert-tee-front-back.jpg',quality=90)
