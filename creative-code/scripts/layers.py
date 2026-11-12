import math, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
W,H=1800,3680; SS=2; CELL=13
def hx(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
OLV,FWG,LGR,PUR,EB,DG,SAGE,CRM,BR,TAN=map(hx,['5B6B2E','156826','59A66C','6B4C7A','3780B8','22371F','A8B49A','F4F1EA','4F3433','C89B7B'])
LIME=(190,214,90); LIL=(200,182,226); PG=(203,214,150); PY=(214,226,140); LB=(150,196,232); PLUM=(58,34,62); NAVY=(26,44,82)
def plate_alpha(i):
    p=Image.open(f'/home/claude/merch/micro/plate_{i}.png').convert('RGBA').split()[3]
    m=Image.new('L',p.size,0); c=p.width/2; r=p.width*0.465; ImageDraw.Draw(m).ellipse([c-r,c-r,c+r,c+r],fill=255)
    return Image.fromarray(np.minimum(np.asarray(p),np.asarray(m)))
def texture(base,dots,seed,density=1.0):
    r=random.Random(seed); t=Image.new('RGB',(W*SS,H*SS),base); d=ImageDraw.Draw(t)
    for li,col in enumerate(dots):
        src=Image.new('L',(W,H),0)
        for k in range(5):
            p=plate_alpha(r.randrange(16)); s=r.randint(1700,2600); p=p.resize((s,s)).rotate(r.choice([0,90,180,270]))
            src.paste(p,(r.randint(-700,W-900),r.randint(-500+k*700,300+k*700)),p)
        A=np.asarray(src.filter(ImageFilter.GaussianBlur(5))).astype(float)/255*density
        off=li*CELL/2
        for gy in np.arange(off,H,CELL):
            row=A[min(H-1,int(gy))]
            for gx in np.arange(off+(CELL/2 if int(gy/CELL)%2 else 0),W,CELL):
                v=row[min(W-1,int(gx))]
                if v<0.12: continue
                rad=CELL*0.48*min(1,v)**0.6; d.ellipse([(gx-rad)*SS,(gy-rad)*SS,(gx+rad)*SS,(gy+rad)*SS],fill=col)
    return t
def boundary(seed,base,amp=70):
    r=np.random.default_rng(seed); x=np.linspace(0,1,W)
    y=base+sum(amp/(k+1)*np.sin(2*math.pi*(k+1)*x*r.uniform(0.6,1.4)+r.uniform(0,6)) for k in range(4))
    return y
def layer_masks(seed,bases):
    ys=[boundary(seed+k,b) for k,b in enumerate(bases)]
    masks=[]; yy=np.arange(H)[:,None]
    edges=[np.full(W,-1e9)]+ys+[np.full(W,1e9)]
    for k in range(len(edges)-1):
        m=((yy>=edges[k][None,:])&(yy<edges[k+1][None,:])).astype(np.uint8)*255
        masks.append(Image.fromarray(m).resize((W*SS,H*SS),Image.BILINEAR))
    return masks
def root(seed,x0,w0=120,col_mask=None):
    rr=random.Random(seed); m=Image.new('L',(W*SS,H*SS),0); d=ImageDraw.Draw(m)
    def br(x,y,a,w,dep):
        while w>2.5 and y<H+50 and -100<x<W+100:
            a+=rr.gauss(0,0.09); a=0.96*a+0.04*(math.pi/2)
            nx,ny=x+10*math.cos(a),y+10*math.sin(a)
            d.line([x*SS,y*SS,nx*SS,ny*SS],fill=255,width=max(1,int(w*SS))); d.ellipse([(nx-w/2)*SS,(ny-w/2)*SS,(nx+w/2)*SS,(ny+w/2)*SS],fill=255)
            x,y=nx,ny; w*=0.991
            if rr.random()<0.03 and dep<5: br(x,y,a+rr.choice([-1,1])*rr.uniform(0.5,1.0),w*0.65,dep+1)
    br(x0,-40,math.pi/2,w0,0); return m
def logo(im,path,w,margin=110):
    lg=Image.open(path).convert('RGBA').resize((w*SS,w*SS),Image.LANCZOS)
    im.alpha_composite(lg,((W-margin-w)*SS,(H-margin-w)*SS))
def fin(im,seed):
    out=im.resize((W,H),Image.LANCZOS).convert('RGB'); a=np.asarray(out).astype(float)
    g=np.random.default_rng(seed).normal(0,1,a.shape[:2]); return Image.fromarray((a*(1+0.03*g[...,None])).clip(0,255).astype(np.uint8))
LOGO_C='/home/claude/merch/logos/SFW-logo-flower-cream.png'
def build(name,bases,pals,rootcol,seed,root_x=(560,1250),logo_path=LOGO_C):
    masks=layer_masks(seed,bases)
    im=Image.new('RGBA',(W*SS,H*SS),pals[0][0]+(255,))
    for k,(m,(base,dots)) in enumerate(zip(masks,pals)):
        im.paste(texture(base,dots,seed*10+k),(0,0),m)
    for j,x in enumerate(root_x):
        rm=root(seed+j,x,46-j*8); im.paste(Image.new('RGBA',im.size,rootcol+(255,)),(0,0),rm)
    logo(im,logo_path,500); a=fin(im,seed); a.save(f'SFW-case-{name}.png'); return a
arts=[]
arts.append(build('60-layers-green-purple',[640,1500,2400],[(LGR,[PG,LIME]),(FWG,[LGR,LIME]),(PUR,[LIL,PG]),(DG,[OLV,LIL])],CRM,1))
arts.append(build('61-layers-olive-blue',[700,1600,2550],[(SAGE,[PG,(255,255,240)]),(OLV,[LIME,PG]),(EB,[PY,LB]),(NAVY,[EB,LB])],CRM,2))
arts.append(build('62-layers-purple-down',[600,1450,2350],[(LIL,[(255,255,255),PG]),(PUR,[LIL,PG]),(FWG,[LGR,LIME]),(DG,[FWG,LGR])],PG,3,(900,)))
arts.append(build('63-layers-soil-colours',[620,1550,2450],[(LGR,[PG,LIME]),(BR,[TAN,LIL]),(OLV,[LIME,PG]),(PUR,[LIL,PG])],CRM,4,(450,1050,1500)))
s=Image.new('RGB',(4*620+20,1247),(226,222,214))
for i,v in enumerate(arts): s.paste(v.resize((600,1227)),(20+i*620,10))
s.save('SFW-cases-soil-layers-v2.jpg',quality=90)
