import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
W,H=1392,2220
def fit(src):
    im=Image.open(src).convert('RGB'); w,h=im.size; ch=int(w*H/W); y0=(h-ch)//2
    return im.crop((0,y0,w,y0+ch)).resize((W,H),Image.LANCZOS)
def add_logo(im,logo,bg=None,maxw=420):
    a=np.asarray(im).astype(int)
    if bg is None: bg=a[5,W-5]
    occ=np.abs(a-np.array(bg)).sum(-1)>40
    occ[:640,:660]=True; occ[:70]=occ[-70:]=True; occ[:,:70]=occ[:,-70:]=True
    d=distance_transform_edt(~occ); y,x=np.unravel_index(d.argmax(),d.shape)
    w=int(min(maxw,d.max()*1.7)); lg=Image.open(logo).convert('RGBA').resize((w,w),Image.LANCZOS)
    o=im.convert('RGBA'); o.alpha_composite(lg,(int(x-w/2),int(y-w/2))); return o.convert('RGB'),w
L='/home/claude/merch/logos/'
jobs=[('ikat-deepgreen-sage','SFW-case-16-ikat-deep-green-sage-hyphae-nologo.png',L+'SFW-logo-flower-colour.png'),
      ('ikat-purple-sage','SFW-case-17-ikat-purple-sage-nematode-nologo.png',L+'SFW-logo-flower-colour.png'),
      ('ikat-green-cream','SFW-case-19-ikat-green-cream-ciliate-nologo.png',L+'SFW-logo-flower-colour.png'),
      ('ikat-blue-cream','SFW-case-20-ikat-blue-cream-hyphae-nologo.png',L+'SFW-logo-flower-colour.png')]
out=[]
for n,src,lg in jobs:
    im,w=add_logo(fit(src),lg); im.save(f'SFW-phonecase-tough-{n}.png'); out.append(im); print(n,w)
# microbe collage case
exec(open('tee_organic2.py').read().split("outs=[]")[0])
H_,WW=1110,696
big=jq_fine(organic(51,30,35),[P_BG,P_INK]).resize((1392,2220),Image.NEAREST)
W,H=1392,2220
o=big.convert('RGBA'); lw=420; lg=Image.open(L+'SFW-logo-flower-white-3000.png').convert('RGBA').resize((lw,lw),Image.LANCZOS)
o.alpha_composite(lg,(1392-110-lw,2220-140-lw)); mc=o.convert('RGB'); mc.save('SFW-phonecase-tough-microbe-collage.png'); out.append(mc)
S=Image.new('RGB',(5*420+20,700),(226,222,214))
for i,v in enumerate(out): S.paste(v.resize((400,638)),(20+i*420,30))
S.save('SFW-phonecases-tough-batch.jpg',quality=90)
