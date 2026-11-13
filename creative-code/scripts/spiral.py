import numpy as np, cv2
from PIL import Image, ImageDraw, ImageCms
from scipy.ndimage import gaussian_filter
ICC=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
M='/home/claude/merch/micro/'
W,H=2250,2700
def make(photo,c0,c1,seed,out,zoom=1.0,cx=.5,cy=.5,turns=2.7):
    rng=np.random.default_rng(seed)
    g=cv2.imread(M+photo,0).astype(np.float32); h,w=g.shape; s=max(W/w,H/h)*zoom
    g=cv2.resize(g,(int(w*s)+2,int(h*s)+2)); y0=int((g.shape[0]-H)*cy); x0=int((g.shape[1]-W)*cx); g=g[y0:y0+H,x0:x0+W]
    g=cv2.equalizeHist(g.astype(np.uint8)).astype(np.float32)/255
    a=np.array(c0,np.float32); b=np.array(c1,np.float32); rgb=(a+(b-a)*g[...,None])
    # hand-cut outer shape: wobbly rounded rectangle-ish blob
    t=np.linspace(0,2*np.pi,400,endpoint=False); r=np.ones_like(t)
    for f in range(2,9): r+=0.16/f*rng.normal()*np.cos(f*t+rng.uniform(0,6.3))
    sq=np.abs(np.cos(t))**0.6*np.sign(np.cos(t)), np.abs(np.sin(t))**0.6*np.sign(np.sin(t))
    pts=list(zip(W/2+0.47*W*r*sq[0], H/2+0.47*H*r*sq[1]))
    mk=Image.new('L',(W,H),0); d=ImageDraw.Draw(mk); d.polygon(pts,fill=255)
    # spiral cut, drawn like by hand: radius grows unevenly, line weight changes
    n=2000; th=np.linspace(1.2,turns*2*np.pi,n)
    wob=gaussian_filter(rng.normal(0,1,n),25)*110
    rad=(th/(turns*2*np.pi))*0.42*W*1.0+wob
    xs=W/2+rad*np.cos(th)*1.0; ys=H/2+rad*np.sin(th)*1.15
    lw=(230+gaussian_filter(rng.normal(0,1,n),40)*260).clip(150,320)
    for i in range(0,n-1):
        d.line([(xs[i],ys[i]),(xs[i+1],ys[i+1])],fill=0,width=int(lw[i]))
        d.ellipse([xs[i]-lw[i]/2,ys[i]-lw[i]/2,xs[i]+lw[i]/2,ys[i]+lw[i]/2],fill=0)
    m=np.asarray(mk.filter(__import__('PIL.ImageFilter',fromlist=['x']).GaussianBlur(1.2)))>127
    out_im=np.zeros((H,W,4),np.uint8); out_im[...,:3]=rgb.astype(np.uint8); out_im[...,3]=m*255
    Image.fromarray(out_im).save(out,icc_profile=ICC,dpi=(300,300))
make('Fungal hyphae 40x obj Tanja Dekker.jpg',(24,52,34),(170,206,140),5,'SFW-spiral-hyphae-back.png',zoom=1.1)
make('Testate amoebae 40x obj Jimena Fuentes.jpg',(52,34,96),(200,186,236),8,'SFW-spiral-testate-back.png',zoom=1.3,cx=.3,cy=.6)
for f,bg in (('SFW-spiral-hyphae-back.png',(24,24,24)),('SFW-spiral-testate-back.png',(150,150,148))):
    im=Image.open(f); c=Image.new('RGB',im.size,bg); c.paste(im,(0,0),im); c.resize((W//4,H//4)).save('/tmp/'+f.replace('.png','.jpg'))
