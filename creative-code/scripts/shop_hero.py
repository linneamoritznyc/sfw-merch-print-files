import numpy as np, cv2
from PIL import Image, ImageDraw, ImageChops
M='/home/claude/merch/micro/'
W,H=2880,1280
GREEN=(28,58,40); PURP=(98,74,160); LAV=(196,182,232); LIME=(206,226,110); BROWN=(122,70,36); MID=(62,128,80)
im=Image.new('RGB',(W,H),GREEN); d=ImageDraw.Draw(im)
for x in range(0,W,160): d.line([(x,0),(x,H)],fill=(40,74,52),width=2)
for y in range(0,H,160): d.line([(0,y),(W,y)],fill=(40,74,52),width=2)
def duo(f,size,c0,c1,zoom=1.0,cx=.5,cy=.5,seed=0):
    g=cv2.imread(M+f,0).astype(np.float32); h,w=g.shape; c=int(min(h,w)/zoom)
    x0=int(min(max(cx*w-c/2,0),w-c)); y0=int(min(max(cy*h-c/2,0),h-c))
    g=cv2.resize(g[y0:y0+c,x0:x0+c],(size,size),interpolation=cv2.INTER_CUBIC)
    g=cv2.equalizeHist(g.astype(np.uint8)).astype(np.float32)/255
    g=np.clip(g+np.random.default_rng(seed).normal(0,0.05,g.shape),0,1)
    a=np.array(c0,np.float32); b=np.array(c1,np.float32)
    return Image.fromarray((a+(b-a)*g[...,None]).astype(np.uint8))
def circ(img,D,pos):
    m=Image.new('L',(D,D),0); ImageDraw.Draw(m).ellipse([0,0,D-1,D-1],fill=255); im.paste(img,pos,m)
# big purple testate circle, right side
D=1120; circ(duo('Testate amoebae 40x obj Jimena Fuentes.jpg',D,(40,26,80),LAV,zoom=1.5,cx=.3,cy=.62),D,(1480,80))
# lime ciliates circle overlapping
D2=760; circ(duo('Ciliates (stalked) 40x obj Sid Jensen.jpg',D2,GREEN,LIME,zoom=1.2,cx=.45,cy=.4,seed=1),D2,(2260,480))
# brown leaf
lw,lh=360,600; m=Image.new('L',(lw,lh),0); ImageDraw.Draw(m).ellipse([-lw*0.9,0,lw*0.9,lh],fill=255)
m2=Image.new('L',(lw,lh),0); ImageDraw.Draw(m2).ellipse([lw*0.1,0,lw*1.9,lh],fill=255)
m=ImageChops.multiply(m,m2); im.paste(Image.new('RGB',(lw,lh),BROWN),(2180,180),m)
# small mid green dot
d.ellipse([1400,980,1600,1180],fill=MID)
im.save('sfw-hero.jpg',quality=90)
im.resize((W//4,H//4)).save('/tmp/hero_prev.jpg')
lg=Image.open('/home/claude/sfw-merch-print-files/logos/SFW-logo-colour-transparent-3000px.png'); lg=lg.crop(lg.getbbox()); lg.thumbnail((600,600)); lg.save('sfw-logo.png')
