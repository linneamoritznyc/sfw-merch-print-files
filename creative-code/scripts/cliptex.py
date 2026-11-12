import math, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
exec(open('orgcontour.py').read().split("specs=[")[0].replace("W,H=1800,3680; h=2","W,H=1800,3680; h=2",1))
SS=2
EB=(55,128,184); NAVY=(26,44,82); PY=(214,226,140); LB=(150,196,232)
OL=(91,107,46); DGr=(34,55,31); LIME=(190,214,90); LIL=(200,182,226)
PUR=(107,76,122); PLUM=(58,34,62); PG=(203,214,150)
PAL={'blue':(EB,NAVY,[PY,LB]),'olive':(OL,DGr,[LIME,LIL]),'purple':(PUR,PLUM,[PG,LIL])}
def up(mask):  # half-res L -> full canvas SS
    return mask.resize((W*SS,H*SS),Image.BILINEAR).filter(ImageFilter.GaussianBlur(2)).point(lambda v:255 if v>127 else 0)
def texture(pal,seed,cell=13):
    field,base,dots=PAL[pal]; r=random.Random(seed)
    t=Image.new('RGBA',(W*SS,H*SS),base+(255,)); d=ImageDraw.Draw(t)
    for li,col in enumerate(dots):
        src=Image.new('L',(W,H),0)
        for k in range(3):
            p=Image.open(f'/home/claude/merch/micro/plate_{r.randrange(16)}.png').convert('RGBA').split()[3]
            s=r.randint(1500,2600); p=p.resize((s,s)).rotate(r.choice([0,90,180,270]))
            src.paste(Image.fromarray(np.maximum(np.asarray(src.crop((0,0,1,1)).resize((1,1))),0)) if False else p,(r.randint(-600,W-900),r.randint(-400+k*1200,600+k*1200)),p)
        A=np.asarray(src.filter(ImageFilter.GaussianBlur(5))).astype(float)/255
        off=li*cell/2
        for gy in np.arange(off,H,cell):
            row=A[min(H-1,int(gy))]
            for gx in np.arange(off+(cell/2 if int(gy/cell)%2 else 0),W,cell):
                v=row[min(W-1,int(gx))]
                if v<0.12: continue
                rad=cell*0.48*min(1,v)**0.6
                d.ellipse([(gx-rad)*SS,(gy-rad)*SS,(gx+rad)*SS,(gy+rad)*SS],fill=col+(255,))
    return t
def logo(im,cx,cy,w,path='/home/claude/merch/logos/SFW-logo-flower-cream.png'):
    lg=Image.open(path).convert('RGBA').resize((w*SS,w*SS),Image.LANCZOS); im.alpha_composite(lg,((cx-w//2)*SS,(cy-w//2)*SS))
def fin(im,seed):
    out=im.resize((W,H),Image.LANCZOS).convert('RGB'); a=np.asarray(out).astype(float); g=np.random.default_rng(seed).normal(0,1,a.shape[:2])
    return Image.fromarray((a*(1+0.03*g[...,None])).clip(0,255).astype(np.uint8))
out={}
# 50 giant logo silhouette, blue
im=Image.new('RGBA',(W*SS,H*SS),EB+(255,))
lg=Image.open('/home/claude/merch/logos/SFW-logo-flower-cream.png').convert('RGBA').split()[3]
ca=np.asarray(Image.open('/home/claude/merch/logos/SFW-logo-flower-colour.png').convert('RGBA')).copy()
hh,ww=ca.shape[:2]
# drop the lettering: the brown/green type band, keep ring, vine, flowers, roots
band=np.zeros((hh,ww),bool); band[int(hh*0.39):int(hh*0.63),int(ww*0.03):int(ww*0.98)]=True
ca[band,3]=0
lgm=Image.fromarray(ca[...,3])
S_=4200; m=Image.new('L',(W*SS,H*SS),0); m.paste(lgm.resize((S_*SS,S_*SS),Image.LANCZOS).point(lambda v:255 if v>127 else 0),(-1700*SS,-200*SS))
im.paste(texture('blue',1),(0,0),m); logo(im,1180,2050,520); out['50-clip-logo-silhouette-blue']=fin(im,1)
# 51 giant nematode, olive
bb=blank(); dn=ImageDraw.Draw(bb)
for i in range(700):
    t=i/699; y=-80+t*2000; x=470+260*math.sin(t*math.pi*1.5+0.6)
    w=280*min(1,(t/0.08)**0.5,((1-t)/0.35)**0.8)+6; dn.ellipse([x-w/2,y-w/2,x+w/2,y+w/2],fill=255)
im=Image.new('RGBA',(W*SS,H*SS),OL+(255,)); im.paste(texture('olive',2),(0,0),up(bb)); logo(im,1350,2950,540); out['51-clip-nematode-olive']=fin(im,2)
# 52 giant vorticella, purple
b,_,_=vorticella(); bb=b.transform(b.size,Image.AFFINE,(0.72,0,140,0,0.72,40))
im=Image.new('RGBA',(W*SS,H*SS),PUR+(255,)); im.paste(texture('purple',3),(0,0),up(bb)); logo(im,1330,2900,520); out['52-clip-vorticella-purple']=fin(im,3)
# 53 three overlapping organic shapes on olive
im=Image.new('RGBA',(W*SS,H*SS),OL+(255,)); r=random.Random(7)
def blob(cx,cy,R,seed):
    rr=random.Random(seed); m=Image.new('L',(W*SS,H*SS),0)
    pts=[(cx+R*(1+0.18*math.sin(3*t+seed)+0.1*math.sin(5*t))*math.cos(t),cy+R*1.25*(1+0.15*math.cos(2*t+seed))*math.sin(t)) for t in np.linspace(0,6.28,120)]
    ImageDraw.Draw(m).polygon([(x*SS,y*SS) for x,y in pts],fill=255); return m
def hypha(seed):
    rr=random.Random(seed); m=Image.new('L',(W*SS,H*SS),0); d=ImageDraw.Draw(m)
    def br(x,y,a,w,dep):
        while w>40 and -200<x<W+200 and y<H+200:
            a+=rr.gauss(0,0.04); nx,ny=x+14*math.cos(a),y+14*math.sin(a); d.line([x*SS,y*SS,nx*SS,ny*SS],fill=255,width=int(w*SS)); d.ellipse([(nx-w/2)*SS,(ny-w/2)*SS,(nx+w/2)*SS,(ny+w/2)*SS],fill=255); x,y=nx,ny; w*=0.9985
            if rr.random()<0.008 and dep<2: br(x,y,a+rr.choice([-1,1])*0.8,w*0.7,dep+1)
    br(-100,600,0.55,230,0); return m
m1=blob(1250,1100,620,1); m2=hypha(4); m3=blob(560,2700,700,9)
im.paste(texture('purple',11),(0,0),m1); im.paste(texture('blue',12),(0,0),m3); im.paste(texture('olive',13),(0,0),m2)
logo(im,1280,3050,500); out['53-clip-overlap-shapes']=fin(im,4)
for k,v in out.items(): v.save(f'SFW-case-{k}.png')
s=Image.new('RGB',(4*620,1227),(226,222,214))
for i,v in enumerate(out.values()): s.paste(v.resize((600,1227)),(i*620,0))
s.save('/tmp/ct.png')
