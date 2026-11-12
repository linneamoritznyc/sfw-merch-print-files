import math, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter
W,H=1800,3680; SS=2
PG=(203,214,150); PU2=(150,112,190); ROOT=(226,230,196)
TONES=[(30,42,20),(40,54,26),(52,66,30),(66,80,36),(84,98,44)]
def fbm(seed,shape,scales=(400,120,40),amps=(1,0.45,0.2)):
    r=np.random.default_rng(seed); out=np.zeros(shape)
    for s,a in zip(scales,amps):
        n=r.normal(0,1,(shape[0]//max(1,s//8)+3,shape[1]//max(1,s//8)+3)); n=gaussian_filter(n,1.2)
        out+=a*np.asarray(Image.fromarray(n.astype(np.float32)).resize((shape[1],shape[0]),Image.BICUBIC))/(n.std()+1e-9)
    return out
def build(seed,variant):
    r=random.Random(seed); rng=np.random.default_rng(seed)
    # layer boundaries
    bases=[0,620,1500,2350,3000] if variant==0 else [0,560,1350,2250,2950]
    xs=np.arange(W)
    bounds=[np.full(W,-10.0)]
    for k,b in enumerate(bases[1:]):
        n=fbm(seed+k,(1,W),(600,200,60),(1,0.5,0.25))[0]; bounds.append(b+n*55)
    yy=np.arange(H)[:,None]
    L=np.zeros((H,W),int)
    for k in range(1,5): L[yy>=bounds[k][None,:]]=k
    tone=np.array(TONES)[L]
    # ink density per layer + texture
    dens=np.array([0.05,0.16,0.09,0.05,0.04])[L]+0.08*fbm(seed+10,(H//4,W//4),(60,20,6),(1,.6,.4)).repeat(4,0).repeat(4,1)[:H,:W]
    ink=Image.fromarray((np.clip(dens,0,1)*255).astype(np.uint8)); d=ImageDraw.Draw(ink)
    # litter: leaf fragments
    for k in range(34):
        cx,cy=r.uniform(-50,W+50),r.uniform(60,bases[1]-40); L_=r.uniform(120,300); a=r.uniform(0,math.pi); w=L_*r.uniform(0.32,0.5)
        pts=[]
        for t in np.linspace(0,2*math.pi,40):
            px=L_/2*math.cos(t); py=w/2*math.sin(t)*(1-0.3*math.cos(t)); 
            if r.random()<0.12: px*=r.uniform(0.75,0.95)  # torn edge
            pts.append((cx+px*math.cos(a)-py*math.sin(a),cy+px*math.sin(a)+py*math.cos(a)))
        d.polygon(pts,fill=int(r.uniform(110,200)))
        d.line([(cx-L_/2*math.cos(a),cy-L_/2*math.sin(a)),(cx+L_/2*math.cos(a),cy+L_/2*math.sin(a))],fill=40,width=5)
    # aggregates in topsoil/subsoil
    for k in range(40):
        cx,cy=r.uniform(0,W),r.uniform(bases[1]+60,bases[3]); rr=r.uniform(25,80)
        for j in range(7):
            ox,oy=r.gauss(0,rr*0.6),r.gauss(0,rr*0.6); q=rr*r.uniform(0.3,0.6); d.ellipse([cx+ox-q,cy+oy-q,cx+ox+q,cy+oy+q],fill=int(r.uniform(70,130)))
    # stones in parent material, soft edges
    stones=Image.new('L',(W,H),0); ds=ImageDraw.Draw(stones)
    for k in range(16):
        cx,cy=r.uniform(-80,W+80),r.uniform(bases[4]+80,H+100); rx,ry=r.uniform(120,300),r.uniform(90,200)
        pts=[(cx+rx*math.cos(t)*(1+0.18*math.sin(3*t+k)),cy+ry*math.sin(t)*(1+0.15*math.cos(2*t+k))) for t in np.linspace(0,6.28,50)]
        ds.polygon(pts,fill=int(r.uniform(110,175)))
    stones=stones.filter(ImageFilter.GaussianBlur(18))
    ink=Image.fromarray(np.maximum(np.asarray(ink),np.asarray(stones)))
    inkA=np.asarray(ink.filter(ImageFilter.GaussianBlur(3))).astype(float)/255
    # halftone render
    im=Image.fromarray(tone.astype(np.uint8)).resize((W*SS,H*SS),Image.NEAREST).convert('RGBA'); dd=ImageDraw.Draw(im)
    c=15
    for gy in range(0,H,c):
        off=(c/2 if (gy//c)%2 else 0)
        for gx in np.arange(off,W,c):
            v=inkA[min(H-1,gy),min(W-1,int(gx))]
            if v<0.08: continue
            rad=c*0.58*v**0.7
            dd.ellipse([(gx-rad)*SS,(gy-rad)*SS,(gx+rad)*SS,(gy+rad)*SS],fill=PG+(255,))
    # stipple grain
    for k in range(9000):
        x,y=r.uniform(0,W),r.uniform(0,H); s=r.uniform(0.8,1.8); dd.ellipse([(x-s)*SS,(y-s)*SS,(x+s)*SS,(y+s)*SS],fill=PG+(int(r.uniform(60,160)),))
    # roots: tapering branching strokes
    tips=[]
    def root(x,y,a,w,depth,maxy):
        while w>1.2 and y<maxy:
            a+=r.gauss(0,0.08); a=a*0.9+math.pi/2*0.1
            nx,ny=x+9*math.cos(a),y+9*math.sin(a)
            dd.line([x*SS,y*SS,nx*SS,ny*SS],fill=ROOT+(255,),width=max(2,int(w*SS))); dd.ellipse([(nx-w/2)*SS,(ny-w/2)*SS,(nx+w/2)*SS,(ny+w/2)*SS],fill=ROOT+(255,))
            x,y=nx,ny; w*=0.991
            if r.random()<0.025 and depth<3: root(x,y,a+r.choice([-1,1])*r.uniform(0.5,1.0),w*0.6,depth+1,maxy)
        tips.append((x,y))
    starts=[(520,-20,1.62,34),(1250,-20,1.5,30)] if variant==0 else [(380,-20,1.55,32),(1000,-20,1.6,36),(1550,-20,1.5,22)]
    for x,y,a,w in starts: root(x,y,a,w,0,bases[3]+200)
    # hyphae web around tips
    for (tx,ty) in tips[::2]:
        for k in range(6):
            x,y,a=tx,ty,r.uniform(0,6.28)
            for s in range(r.randint(8,22)):
                a+=r.gauss(0,0.35); nx,ny=x+7*math.cos(a),y+7*math.sin(a); dd.line([x*SS,y*SS,nx*SS,ny*SS],fill=PG+(220,),width=SS); x,y=nx,ny
    # organisms from plates
    def cut(pi,mask_fn,col,size,pos,rot):
        p=Image.open(f'/home/claude/merch/micro/plate_{pi}.png').convert('RGBA').split()[3]
        m=Image.new('L',(900,900),0); mask_fn(ImageDraw.Draw(m)); m=m.filter(ImageFilter.GaussianBlur(14))
        a=Image.fromarray((np.asarray(p).astype(float)*np.asarray(m)/255).astype(np.uint8))
        a=a.rotate(rot,expand=True,resample=Image.BICUBIC); s=size/900; a=a.resize((int(a.width*s*SS),int(a.height*s*SS)),Image.LANCZOS)
        # dark pocket behind so it reads
        pocket=m.rotate(rot,expand=True).resize(a.size).filter(ImageFilter.GaussianBlur(10*SS))
        x,y=int(pos[0]*SS-a.width/2),int(pos[1]*SS-a.height/2)
        im.paste(Image.new('RGBA',a.size,TONES[0]+(255,)),(x,y),pocket.point(lambda v:int(v*0.85)))
        im.paste(Image.new('RGBA',a.size,col+(255,)),(x,y),a)
    nem=lambda d_: d_.polygon([(90,600),(140,520),(840,300),(840,370),(150,650)],fill=255)
    cil=lambda d_: d_.ellipse([500,300,740,720],fill=255)
    tes=lambda d_: d_.ellipse([40,410,460,840],fill=255)
    if variant==0:
        cut(11,nem,PU2,1250,(1000,1880),-8); cut(0,cil,PG,900,(1450,1150),20); cut(3,tes,PG,900,(380,2680),0)
    else:
        cut(11,nem,PG,1300,(820,2050),12); cut(0,cil,PU2,950,(420,1050),-15); cut(3,tes,PU2,950,(1370,2620),0)
    return im,bases
def add_logo(im,cx,cy,w):
    # pale halftone-edged pocket + colour logo
    R=int(w*0.6); pocket=Image.new('L',im.size,0); ImageDraw.Draw(pocket).ellipse([(cx-R)*SS,(cy-R)*SS,(cx+R)*SS,(cy+R)*SS],fill=255)
    im.paste(Image.new('RGBA',im.size,PG+(255,)),(0,0),pocket)
    lg=Image.open('/home/claude/merch/logos/SFW-logo-flower-colour.png').convert('RGBA').resize((w*SS,w*SS),Image.LANCZOS); im.alpha_composite(lg,((cx-w//2)*SS,(cy-w//2)*SS))
def finish(im,seed):
    out=im.resize((W,H),Image.LANCZOS).convert('RGB'); a=np.asarray(out).astype(float); g=np.random.default_rng(seed).normal(0,1,a.shape[:2])
    return Image.fromarray((a*(1+0.045*g[...,None])).clip(0,255).astype(np.uint8))
im,b=build(5,0); add_logo(im,1330,560,560); finish(im,5).save('SFW-case-47-soil-profile-halftone.png')
im,b=build(9,1); add_logo(im,1300,3320,540); finish(im,9).save('SFW-case-48-soil-profile-halftone.png')
