import math, numpy as np
from PIL import Image, ImageDraw
src=open('macro.py').read()
exec(src.split("specs=[")[0])
def plate_clean(i,col,size,rot):
    p=Image.open(f'/home/claude/merch/micro/plate_{i}.png').convert('RGBA').split()[3]
    m=Image.new('L',p.size,0); r=p.width*0.465; c=p.width/2
    ImageDraw.Draw(m).ellipse([c-r,c-r,c+r,c+r],fill=255)          # drop the field-of-view ring
    a=Image.fromarray(np.minimum(np.asarray(p),np.asarray(m)))
    if rot: a=a.rotate(rot)
    a=a.resize((size*SS,size*SS),Image.LANCZOS)
    o=Image.new('RGBA',a.size,col+(255,)); o.putalpha(a); return o
def place(u,v,px,py,size):
    # plate point (u,v) -> case point (px,py), keeping the whole case inside the plate circle
    dx=px-W/2-(u-0.5)*size; dy=py-H/2-(v-0.5)*size
    lim=size*0.465-math.hypot(W/2,H/2)-20; mag=math.hypot(dx,dy)
    if mag>lim: dx,dy=dx*lim/mag,dy*lim/mag
    return int(W/2+dx-size/2),int(H/2+dy-size/2)
plate=lambda i,col,size: PL[0]
specs=[('43-macro-olive-palegreen-cell',DO,PG,4,5600,(0.45,0.55),(900,1500),0),
       ('44-macro-olive-palegreen-hypha',OL,PG,11,5600,(0.5,0.45),(900,1700),0),
       ('45-macro-purple-lilac',PUR,LIL,14,5600,(0.55,0.4),(900,1500),90),
       ('46-macro-olive-purple',DO,PU2,8,5600,(0.4,0.52),(800,1300),0)]
arts={}
for k,(n,bg,ink,pi,sz,uv,pp,rot) in enumerate(specs):
    PL=[plate_clean(pi,ink,sz,rot)]; ox,oy=place(*uv,*pp,sz)
    a=macro(bg,ink,pi,sz,ox,oy,0,seed=k); a.save(f'SFW-case-{n}.png'); arts[n]=a
s=Image.new('RGB',(4*620+20,1247),(226,222,214))
for i,v in enumerate(arts.values()): s.paste(v.resize((600,1227)),(20+i*620,10))
s.save('/tmp/mac2.png')
