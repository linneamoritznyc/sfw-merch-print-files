import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import uniform_filter
exec(open('cases2.py').read().split("CAM=")[0])
PUR=(107,76,122); LIL=(200,182,226)
LOGO=LG_CR='/home/claude/merch/logos/SFW-logo-flower-cream.png'
def macro(bg,ink,pi,size,ox,oy,rot=0,logo_w=760,seed=0):
    im=canvas(bg); p=plate(pi,ink,size)
    if rot: p=p.rotate(rot)
    im.alpha_composite(p,(ox*SS,oy*SS))
    # find the emptiest spot for the logo
    a=np.asarray(im.resize((W//10,H//10)).convert('RGB')).astype(float); dif=np.abs(a-np.array(bg)).sum(-1)>40
    dens=uniform_filter(dif.astype(float),size=logo_w//10)
    yy,xx=np.mgrid[0:H//10,0:W//10]; r=logo_w//20+6
    ok=(xx>r)&(xx<W//10-r)&(yy>950//10)&(yy<3050//10)&~((xx<85)&(yy<85))
    dens=np.where(ok,dens+0.002*np.abs(xx-W//20),9); y,x=np.unravel_index(dens.argmin(),dens.shape); cx,cy=x*10,y*10
    R=int(logo_w*0.62); ImageDraw.Draw(im).ellipse([(cx-R)*SS,(cy-R)*SS,(cx+R)*SS,(cy+R)*SS],fill=bg+(255,))
    lg=Image.open(LOGO).convert('RGBA').resize((logo_w*SS,logo_w*SS),Image.LANCZOS); im.alpha_composite(lg,((cx-logo_w//2)*SS,(cy-logo_w//2)*SS))
    out=im.resize((W,H),Image.LANCZOS).convert('RGB'); a=np.asarray(out).astype(float); g=np.random.default_rng(seed).normal(0,1,a.shape[:2])
    return Image.fromarray((a*(1+0.05*g[...,None])).clip(0,255).astype(np.uint8))
specs=[('43-macro-olive-palegreen-cell',DO,PG,4,3400,-900,-200,0),
       ('44-macro-olive-palegreen-hypha',OL,PG,11,3800,-1300,-500,0),
       ('45-macro-purple-lilac',PUR,LIL,14,3600,-700,300,90),
       ('46-macro-olive-purple',DO,PU2,8,3900,-1500,-900,0)]
arts={}
for i,(n,bg,ink,pi,sz,ox,oy,rot) in enumerate(specs):
    a=macro(bg,ink,pi,sz,ox,oy,rot,seed=i); a.save(f'SFW-case-{n}.png'); arts[n]=a
exec(open('cases2.py').read().split("# mockups")[1].split("ms=[")[0])
ms=[mock(v.convert('RGBA')) for v in arts.values()]
sheet=Image.new('RGB',(len(ms)*1000+80,2040),(226,222,214)); x=50
for mm in ms: sheet.paste(mm,(x,80),mm); x+=1000
sheet.save('SFW-phone-cases-macro-preview.png'); sheet.resize((sheet.width//2,sheet.height//2)).save('/tmp/mac.png')
