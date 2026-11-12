import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter, zoom
Image.MAX_IMAGE_PIXELS=None
W,H=7200,10800                      # 24x36 in @300dpi
CR=(244,241,234); NV=(26,40,78); NV2=(70,92,140); SKY=(176,196,224)
SEP=[(238,233,222),(196,190,160),(122,112,74),(58,48,40)]
src=Image.open('/mnt/user-data/uploads/1cd60aff-image.png').convert('RGB'); src=src.crop((8,8,src.width-8,src.height-8))
m=520; gap=170; pw=W-2*m; ph=int(pw*src.height/src.width)        # panel size
top_y=m; 
print(pw,ph, 3*ph+2*gap+m)
# smooth upscale of tone field, then threshold -> razor sharp edges
g=np.asarray(ImageOps.grayscale(src)).astype(np.float32)/255
bgv=np.percentile(g,85); d0=np.clip((bgv-g)/(bgv-g.min()),0,1)
d0=gaussian_filter(d0,0.9)
d=np.asarray(Image.fromarray((d0*65535).astype(np.uint16)).resize((pw,ph),Image.BICUBIC)).astype(np.float32)/65535
d=gaussian_filter(d,2.0)
def tones(levels,cols):
    o=np.zeros((ph,pw,3),np.uint8); e=[-1]+levels+[2]
    for i,c in enumerate(cols): o[(d>=e[i])&(d<e[i+1])]=c
    return Image.fromarray(o)
P1=tones([0.12,0.35,0.6],SEP)
P2=tones([0.12,0.35,0.6],[CR,SKY,NV2,NV])
# line screen: horizontal lines, thickness = tone, supersampled
pitch=20; ds=gaussian_filter(d,1.2)
yy=np.arange(ph)[:,None]%pitch; half=(np.clip(ds*1.15,0,1)**0.85*pitch*0.5)            # half-thickness per pixel
mask=np.abs(yy-pitch/2)<half
bgmask=ds<0.04
o=np.zeros((ph,pw,3),np.uint8); o[:]=CR; o[mask]=NV
# faint light-grey where nothing (as in approved version: grey ground lines)
light=(~mask)&(np.abs(yy-pitch/2)<1.0)&(ds>=0.0)&(ds<0.12)
o[light]=(214,214,214)
P3=Image.fromarray(o)
Pst=Image.new('RGB',(W,H),CR)
y=m
for p in (P1,P2,P3): Pst.paste(p,(m,y)); y+=ph+gap
lg=Image.open('/home/claude/merch/logos/SFW-logo-flower-colour.png').convert('RGBA')
s=int((H-y+gap-m)*0.0)+560; lg=lg.resize((s,s),Image.LANCZOS)
ly=y-gap+((H-(y-gap))-s)//2
Pst=Pst.convert('RGBA'); Pst.alpha_composite(lg,((W-s)//2,ly)); Pst=Pst.convert('RGB')
Pst.save('SFW-poster-archival-triptych-24x36.png',dpi=(300,300))
pv=Pst.copy(); pv.thumbnail((900,1350)); pv.save('SFW-poster-archival-preview.jpg',quality=90)
Pst.crop((2600,7400,4200,8600)).save('SFW-poster-archival-detail.jpg',quality=92)
