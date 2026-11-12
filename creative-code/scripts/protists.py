import math, random, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt
exec(open('cases4.py').read().split("specs=[")[0])
def ring(d,cx,cy,rx,ry,w,rot=0,fill=0):
    pts=[(cx+rx*math.cos(t)*math.cos(rot)-ry*math.sin(t)*math.sin(rot), cy+rx*math.cos(t)*math.sin(rot)+ry*math.sin(t)*math.cos(rot)) for t in np.linspace(0,6.283,200)]
    d.line(pts+[pts[0]],fill=fill,width=w,joint='curve')
def amoeba(seed,cx,cy,R):
    r=random.Random(seed); m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
    # body: radius modulated by a few broad lobes (pseudopods)
    lobes=[(r.uniform(0,6.28),r.uniform(0.35,0.75),r.uniform(0.25,0.45)) for _ in range(5)]
    pts=[]
    for t in np.linspace(0,6.283,720):
        k=1+0.08*math.sin(3*t+seed)
        for a,amp,wd in lobes:
            dd=math.atan2(math.sin(t-a),math.cos(t-a)); k+=amp*math.exp(-(dd/wd)**2)
        pts.append((cx+R*k*math.cos(t),cy+R*1.15*k*math.sin(t)))
    d.polygon(pts,fill=255)
    ring(d,cx+R*0.1,cy-R*0.05,R*0.32,R*0.28,34,0.3)          # nucleus
    d.ellipse([cx+R*0.03,cy-R*0.12,cx+R*0.17,cy+R*0.02],fill=0)  # nucleolus
    for i in range(4):                                         # food vacuoles
        a=r.uniform(0,6.28); rr=R*r.uniform(0.45,0.7); s=R*r.uniform(0.06,0.11)
        ring(d,cx+rr*math.cos(a),cy+rr*1.1*math.sin(a),s,s,20)
    return m
def flagellate(seed,cx,cy,L,ang,curl=1):
    m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
    ca,sa=math.cos(ang),math.sin(ang)
    # teardrop body along the axis
    pts=[]
    for t in np.linspace(0,6.283,400):
        x=L*0.5*math.cos(t); y=L*0.22*math.sin(t)*(1-0.45*math.cos(t))
        pts.append((cx+x*ca-y*sa, cy+x*sa+y*ca))
    d.polygon(pts,fill=255)
    # flagellum from the front tip, long wavy, tapering
    fx,fy=cx+L*0.5*ca,cy+L*0.5*sa; w=70; a=ang
    for i in range(520):
        a=ang+curl*0.55*math.sin(i/38)
        nx,ny=fx+9*math.cos(a),fy+9*math.sin(a); d.ellipse([nx-w/2,ny-w/2,nx+w/2,ny+w/2],fill=255); fx,fy=nx,ny; w=max(14,w*0.996)
    ring(d,cx-L*0.05*ca,cy-L*0.05*sa,L*0.11,L*0.09,30,ang)    # nucleus
    ring(d,cx-L*0.27*ca,cy-L*0.27*sa,L*0.05,L*0.05,22)        # vacuole
    return m
def place_logo(img,B,path,maxw=520):
    occ=B.copy(); occ[:760,:820]=True; occ[:80]=occ[-80:]=True; occ[:,:80]=occ[:,-80:]=True
    dist=distance_transform_edt(~occ); y,x=np.unravel_index(dist.argmax(),dist.shape)
    w=int(min(maxw,dist.max()*1.6)); im=img.convert('RGBA')
    lg=Image.open(path).convert('RGBA').resize((w,w),Image.LANCZOS); im.alpha_composite(lg,(int(x-w/2),int(y-w/2))); return im.convert('RGB'),w
COL=LG+'SFW-logo-flower-colour.png'; CRE=LG+'SFW-logo-flower-cream.png'
OLV=hx('5B6B2E')
specs=[('54-ikat-amoeba-purple-cream', lambda: amoeba(3,1250,1900,620), PUR,CRM,COL),
       ('55-ikat-amoeba-deepgreen-sage', lambda: amoeba(8,700,2300,700), DG,SAGE,COL),
       ('56-ikat-flagellate-blue-cream', lambda: flagellate(2,1150,1250,1500,2.05), EB,CRM,COL),
       ('57-ikat-flagellate-purple-sage', lambda: flagellate(5,900,2500,1400,-1.25,-1), PUR,SAGE,COL)]
arts={}
for i,(n,shape,fg,bg,lp) in enumerate(specs):
    B=ikat(shape(),i+31); img=finish(compose(B,fg,bg,i+31)); img,w=place_logo(img,B,lp); print(n,w)
    img.save(f'SFW-case-{n}.png'); arts[n]=img
s=Image.new('RGB',(4*620+20,1247),(226,222,214))
for i,v in enumerate(arts.values()): s.paste(v.resize((600,1227)),(20+i*620,10))
s.save('/tmp/prot.png')
