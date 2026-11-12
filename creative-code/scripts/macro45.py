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
n,bg,ink,pi,sz,uv,pp='45-macro-purple-lilac',PUR,LIL,5,4800,(0.5,0.38),(900,1700)
PL=[plate_clean(pi,ink,sz,0)]; ox,oy=place(*uv,*pp,sz)
a=macro(bg,ink,pi,sz,ox,oy,0,seed=2); a.save(f'SFW-case-{n}.png'); a.resize((900,1840)).save('SFW-case-45-fixed-preview.png')
