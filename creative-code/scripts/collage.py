import numpy as np, cv2, glob
from PIL import Image, ImageDraw, ImageCms, ImageFilter
from scipy.ndimage import gaussian_filter
ICC=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
M='/home/claude/merch/micro/'
def camo(W,H,seed):
    r=np.random.default_rng(seed); s=4
    a=gaussian_filter(r.random((H//s,W//s)),W/s/30); b=gaussian_filter(r.random((H//s,W//s)),W/s/22)
    a=(a-a.mean())/a.std(); b=(b-b.mean())/b.std()
    out=np.zeros((H//s,W//s,3),np.float32); out[:]=(224,215,158)
    blue=np.clip((b-0.35)*2.2,0,1)[...,None]; white=np.clip((a-0.7)*2.2,0,1)[...,None]
    out=out*(1-blue)+np.array((150,166,238))*blue
    out=out*(1-white)+np.array((242,241,232))*white
    out=cv2.resize(out,(W,H),interpolation=cv2.INTER_CUBIC)
    return out
def micro_patch(f,w,h,seed):
    g=cv2.imread(f)[:,:,::-1].astype(np.float32); gh,gw=g.shape[:2]
    r=np.random.default_rng(seed); x=int(r.uniform(0,gw-gw*0.6)); y=int(r.uniform(0,gh-gh*0.6))
    g=g[y:y+int(gh*0.6),x:x+int(gw*0.6)]; g=cv2.resize(g,(w,h))
    l=cv2.cvtColor(g.astype(np.uint8),cv2.COLOR_RGB2GRAY).astype(np.float32)/255
    l=(l-l.min())/(l.max()-l.min()+1e-6)
    tint=np.array((214,208,170))*l[...,None]+np.array((70,86,40))*(1-l[...,None])  # warm sepia-green
    return tint
def pinked(cx,cy,R,seed,teeth=(0.2,0.55),start=0):
    # circle whose edge is partly cut with pinking shears
    r=np.random.default_rng(seed); t=np.linspace(0,2*np.pi,1400,endpoint=False)
    rr=np.full_like(t,R); a0=r.uniform(0,2*np.pi); span=r.uniform(*teeth)*2*np.pi
    inz=((t-a0)%(2*np.pi))<span
    k=np.where(inz,(np.abs(((t*R/70)%1)-0.5)*2),0)
    rr=rr*(1-0.06*k)
    return list(zip(cx+rr*np.cos(t),cy+rr*np.sin(t)))
def make(W,H,bg,seed,out):
    r=np.random.default_rng(seed)
    base=np.zeros((H,W,3),np.float32); base[:]=bg
    fill=camo(W,H,seed)
    fs=glob.glob(M+'*.jpg')
    for i in range(5):
        w=int(W*r.uniform(0.18,0.32)); h=int(w*r.uniform(0.6,1.1)); x=int(r.uniform(0,W-w)); y=int(r.uniform(0,H-h))
        p=micro_patch(r.choice(fs),w,h,seed+i)
        fill[y:y+h,x:x+w]=fill[y:y+h,x:x+w]*0.25+p*0.75
    mk=Image.new('L',(W,H),0); d=ImageDraw.Draw(mk)
    for i in range(r.integers(4,6)):
        R=W*r.uniform(0.22,0.38); d.polygon(pinked(r.uniform(-0.05,1.05)*W,r.uniform(-0.05,1.05)*H,R,seed*10+i),fill=255)
    m=np.asarray(mk)[...,None]/255.0
    img=base*(1-m)+fill*m
    # a few thin dotted hand lines, like pencil arcs
    im=Image.fromarray(img.clip(0,255).astype(np.uint8)); dd=ImageDraw.Draw(im)
    for i in range(2):
        cx,cy,R=r.uniform(0,W),r.uniform(0,H),W*r.uniform(0.4,0.7); a0=r.uniform(0,6.3)
        for t in np.linspace(a0,a0+1.2,700):
            x,y=cx+R*np.cos(t),cy+R*np.sin(t)
            for j in range(3):
                xx=x+r.normal(0,W*0.002); yy=y+r.normal(0,W*0.002); s=W*0.0012
                dd.ellipse([xx-s,yy-s,xx+s,yy+s],fill=(40,40,36))
    im.save(out,icc_profile=ICC,dpi=(150,150)); return im
if __name__=='__main__':
    ims=[make(1200,1200,c,s,f'/tmp/col{s}.png') for c,s in (((120,58,48),1),((30,56,34),2),((120,58,48),3),((56,38,96),4))]
    sh=Image.new('RGB',(4*1200+5*40,1280),(236,236,232))
    for i,a in enumerate(ims): sh.paste(a,(40+i*1240,40))
    sh.resize((sh.width//3,sh.height//3)).save('/tmp/col.jpg')
