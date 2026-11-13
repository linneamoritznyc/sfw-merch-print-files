import numpy as np, sys, glob
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageCms
from scipy.ndimage import gaussian_filter
ICC=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
M='/home/claude/merch/micro/'; B='/home/claude/merch/brand/'
W,H=1650,2550
def blob(cx,cy,r,seed,k=5,amp=0.35,stretch=(1,1),rot=0):
    rng=np.random.default_rng(seed); t=np.linspace(0,2*np.pi,240,endpoint=False)
    rr=np.ones_like(t)
    for f in range(2,k+2): rr+=amp/f*rng.normal()*np.cos(f*t+rng.uniform(0,6.3))
    x=r*rr*np.cos(t)*stretch[0]; y=r*rr*np.sin(t)*stretch[1]
    c,s=np.cos(rot),np.sin(rot)
    return list(zip(cx+c*x-s*y,cy+s*x+c*y))
def cut(cx,cy,r,seed,n=7,stretch=(1,1),rot=0):
    # scissor-cut paper: a few corners, edges either straight or gently bowed
    rng=np.random.default_rng(seed); ang=np.sort(rng.uniform(0,2*np.pi,n)); rad=r*rng.uniform(0.55,1.15,n)
    P=[(rad[i]*np.cos(ang[i])*stretch[0],rad[i]*np.sin(ang[i])*stretch[1]) for i in range(n)]
    out=[]
    for i in range(n):
        a=np.array(P[i]); b=np.array(P[(i+1)%n]); bow=rng.choice([0,0,0.18,0.3,-0.1])
        mid=(a+b)/2; nrm=np.array([-(b-a)[1],(b-a)[0]]); mid2=mid+nrm*bow
        for t in np.linspace(0,1,14,endpoint=False):
            out.append(tuple((1-t)**2*a+2*(1-t)*t*mid2+t*t*b))
    c,s_=np.cos(rot),np.sin(rot)
    return [(cx+c*x-s_*y,cy+s_*x+c*y) for x,y in out]
def ink(src,cx,cy,cw,size,thr=60):
    im=ImageOps.grayscale(Image.open(src).convert('RGB')); iw,ih=im.size
    box=(int((cx-cw/2)*iw),int(cy*ih-cw*iw/2),int((cx+cw/2)*iw),int(cy*ih+cw*iw/2))
    g=np.asarray(im.crop(box).resize((size,size),Image.LANCZOS)).astype(np.float32)
    loc=g-gaussian_filter(g,size/12); t=gaussian_filter(-loc,2.2)
    m=(t>np.percentile(t,thr))|(gaussian_filter(g,2)<np.percentile(g,12))
    # fade to nothing toward the edge so it reads as a drawn organism, not a square
    yy,xx=np.mgrid[0:size,0:size]; rad=np.hypot(xx-size/2,yy-size/2)/(size/2)
    keep=rad<0.9
    m&=keep
    from scipy.ndimage import label, binary_closing
    lab,n=label(binary_closing(m,iterations=2)); 
    if n:
        areas=np.bincount(lab.ravel()); areas[0]=0; keepl=np.argsort(areas)[::-1][:6]
        m&=np.isin(lab,keepl[areas[keepl]>size*size*0.002])
    return Image.fromarray((gaussian_filter(m.astype(np.float32),0.8)>0.5).astype(np.uint8)*255)
def cover(name,bg,shapes,organism,dots,word):
    im=Image.new('RGB',(W,H),bg); d=ImageDraw.Draw(im)
    for col,pts in shapes: d.polygon(pts,fill=col)
    rng=np.random.default_rng(9)
    for (x0,y0,x1,y1,n,col) in dots:
        for _ in range(n):
            x=rng.uniform(x0,x1); y=rng.uniform(y0,y1); a=rng.uniform(-0.5,0.5); L=rng.uniform(30,48); w=L*0.42
            pts=[(x+L*np.cos(t)*np.cos(a)-w*np.sin(t)*np.sin(a), y+L*np.cos(t)*np.sin(a)+w*np.sin(t)*np.cos(a)) for t in np.linspace(0,2*np.pi,30)]
            d.polygon(pts,fill=col)
    src,cx,cy,cw,size,pos=organism
    m=ink(src,cx,cy,cw,size); im.paste(Image.new('RGB',m.size,(18,18,16)),pos,m)
    d.text((150,160),word,font=ImageFont.truetype(B+'ebg600.ttf',92),fill=(240,236,222))
    im.save(name+'.png',icc_profile=ICC,dpi=(300,300)); return im
OL=(78,88,48); LAV=(190,176,234); RUST=(222,92,46); CR=(238,233,216); LIME=(204,222,110); PURP=(88,66,150); GR=(30,64,44)
cil=[f for f in glob.glob(M+'*.jpg') if 'Ciliates (stalked)' in f][0]
tes=[f for f in glob.glob(M+'*.jpg') if 'Testate amoebae 40x' in f][0]
a=cover('SFW-notebook-ciliate',OL,
  [(LAV,cut(1050,1250,520,1,stretch=(1,1.3),rot=.4)),(RUST,cut(420,1750,330,4,stretch=(1.4,0.8),rot=-.3)),
   (CR,cut(1350,2150,380,7,stretch=(1.2,0.9))),(LAV,cut(250,700,240,11))],
  (cil,0.55,0.42,0.5,1250,(250,760)),[(980,250,1550,800,26,CR)],'SOIL FOOD WEB')
b=cover('SFW-notebook-testate',GR,
  [(LIME,cut(500,1100,560,21,stretch=(1.2,1.1),rot=-.2)),(RUST,cut(1300,1700,420,24,rot=.9)),
   (LAV,cut(1200,600,300,27,stretch=(1.5,0.9))),(CR,cut(350,2200,300,29,stretch=(1.6,0.8)))],
  (tes,0.36,0.64,0.32,1150,(280,780)),[(150,1900,900,2400,30,CR)],'SOIL FOOD WEB')
sheet=Image.new('RGB',(W*2+300,H+200),(236,226,206)); sheet.paste(a,(100,100)); sheet.paste(b,(W+200,100))
sheet.resize((sheet.width//3,sheet.height//3),Image.LANCZOS).save('/tmp/nb.jpg',quality=90)
