import math, random, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1800,3680
def hx(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
DG,SAGE,PUR,BR,TAN,FWG,CRM,EB,LGR=map(hx,['22371F','A8B49A','6B4C7A','4F3433','C89B7B','156826','F4F1EA','3780B8','59A66C'])
EBG='ebg500.ttf'; MON='mont600.ttf'
LG='/home/claude/merch/logos/'
def disc_path(d,pts,widths):
    for (x,y),w in zip(pts,widths):
        d.ellipse([x-w/2,y-w/2,x+w/2,y+w/2],fill=255)
def bands(seed,n=4,w0=(160,300)):
    r=random.Random(seed); m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
    for k in range(n):
        side=r.choice(['top','left','right','bottom'])
        x,y={'top':(r.uniform(0,W),-300),'bottom':(r.uniform(0,W),H+300),'left':(-300,r.uniform(0,H)),'right':(W+300,r.uniform(0,H))}[side]
        a=math.atan2(H/2+r.uniform(-900,900)-y,W/2+r.uniform(-500,500)-x)
        w=r.uniform(*w0); pts=[];ws=[]
        for i in range(700):
            a+=r.gauss(0,0.035); x+=8*math.cos(a); y+=8*math.sin(a); w*=0.9993
            pts.append((x,y)); ws.append(w)
            if i>120 and r.random()<0.004:  # a branch
                bx,by,ba,bw=x,y,a+r.choice([-1,1])*r.uniform(0.5,0.9),w*0.55
                for j in range(260):
                    ba+=r.gauss(0,0.04); bx+=8*math.cos(ba); by+=8*math.sin(ba); bw*=0.997
                    pts.append((bx,by)); ws.append(bw)
        disc_path(d,pts,ws)
    return m
def nematode(seed,amp=520,width=520):
    r=random.Random(seed); m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
    pts=[];ws=[]; N=900
    for i in range(N):
        t=i/(N-1); y=-500+t*(H+1000)
        x=W*0.5+amp*math.sin(t*math.pi*1.6+r.uniform(0,0.01)+seed)+120*math.sin(t*math.pi*4.3)
        taper=min(1,t/0.25,(1-t)/0.12); pts.append((x,y)); ws.append(width*max(0.08,taper**0.6))
    disc_path(d,pts,ws)
    # gut: knock out a thin inner channel + a few beads
    d2=ImageDraw.Draw(m)
    for (x,y),w in list(zip(pts,ws))[60:-60:3]:
        d2.ellipse([x+w*0.12-w*0.04,y-w*0.04,x+w*0.12+w*0.04,y+w*0.04],fill=0)
    return m
def ciliate(seed,mirror=False):
    r=random.Random(seed); m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
    cx,cy,ax,ay=W*0.78,H*0.55,1150,1900; rot=r.uniform(0.25,0.4)
    def pt(t,s=1.0):
        bulge=1+0.22*math.cos(t)
        x=ax*s*math.cos(t)*bulge; y=ay*s*math.sin(t)
        return (cx+x*math.cos(rot)-y*math.sin(rot), cy+x*math.sin(rot)+y*math.cos(rot))
    body=[pt(i/500*2*math.pi) for i in range(500)]
    d.polygon(body,fill=255)
    for i in range(0,500,5):
        t=i/500*2*math.pi; x1,y1=pt(t,0.98); x2,y2=pt(t,1.12+0.04*r.random())
        d.line([(x1,y1),(x2,y2)],fill=255,width=44)
    nx,ny=pt(2.6,0.45); 
    pts=[(nx+520*math.cos(u)+60*math.sin(3*u),ny+300*math.sin(u)) for u in np.linspace(0,6.28,200)]
    d.line(pts,fill=0,width=70)
    return m.transpose(Image.FLIP_LEFT_RIGHT).rotate(180) if mirror else m
def blown(i,scale,ox,oy,rot=0):
    p=Image.open(f'/home/claude/merch/micro/plate_{i}.png').convert('RGBA').split()[3].rotate(rot)
    p=p.filter(ImageFilter.GaussianBlur(5)).resize((scale,scale),Image.LANCZOS).filter(ImageFilter.GaussianBlur(scale/220)); m=Image.new('L',(W,H),0); m.paste(p,(ox,oy)); return m.point(lambda v:255 if v>100 else 0)
def ikat(m,seed,amp=7,streaks=1400):
    r=np.random.default_rng(seed); A=(np.asarray(m)>127)
    off=np.zeros(H,int); y=0
    while y<H:
        run=r.integers(2,10); off[y:y+run]=r.integers(-amp,amp+1); y+=run
    B=np.zeros_like(A)
    for y in range(H):
        o=off[y]
        if o>0: B[y,o:]=A[y,:-o]
        elif o<0: B[y,:o]=A[y,-o:]
        else: B[y]=A[y]
    # streaks from horizontal edges
    L=B[:,:-1]&~B[:,1:]; R=~B[:,:-1]&B[:,1:]
    ys,xs=np.nonzero(L|R); 
    if len(ys):
        idx=r.choice(len(ys),min(streaks,len(ys)),replace=False)
        for k in idx:
            y,x=ys[k],xs[k]; ln=int(r.integers(20,160)); th=int(r.integers(1,5)); right=L[y,x]
            seg=np.arange(ln); keep=r.random(ln)>np.linspace(0,0.9,ln)
            cols=(x+1+seg) if right else (x-seg)
            cols=cols[keep]; cols=cols[(cols>=0)&(cols<W)]
            val=bool(right)  # extend shape outward
            B[y:y+th,cols]=True
            # also bite back into the shape on the opposite side occasionally
            if r.random()<0.4:
                bc=(x-np.arange(int(r.integers(10,70))))[::2] if right else (x+1+np.arange(int(r.integers(10,70))))[::2]
                bc=bc[(bc>=0)&(bc<W)]; B[y:y+th,bc]=False
    return B
def compose(B,fg,bg,seed,grain=0.08):
    img=np.empty((H,W,3),float); img[:]=bg; img[B]=fg
    n=np.random.default_rng(seed+99).normal(0,1,(H,W)); n=np.asarray(Image.fromarray(((n*40)+128).clip(0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))).astype(float)/128-1
    img=img*(1+grain*n[...,None]); return img
def wordmark(img,B,fg,bg,font,size=50,y=3340,track=0.5):
    f=ImageFont.truetype(font,size); txt="SOIL FOOD WEB"
    tm=Image.new('L',(W,H),0); d=ImageDraw.Draw(tm)
    widths=[d.textlength(c,font=f) for c in txt]; sp=size*track; total=sum(widths)+sp*(len(txt)-1)
    x=(W-total)/2
    for c,w in zip(txt,widths): d.text((x,y),c,font=f,fill=255); x+=w+sp
    T=np.asarray(tm).astype(float)/255
    col=np.where(B[...,None],np.array(bg,float),np.array(fg,float))  # knocked out of shape, shape colour on background
    return img*(1-T[...,None])+col*T[...,None]
def finish(img): return Image.fromarray(img.clip(0,255).astype(np.uint8),'RGB')
def with_logo(im,path,size=360,clear_col=None):
    im=im.convert('RGBA')
    if clear_col:
        r=int(size*0.68); ImageDraw.Draw(im).ellipse([W//2-r,H//2-r,W//2+r,H//2+r],fill=clear_col+(255,))
    lg=Image.open(path).convert('RGBA'); lg=lg.resize((size,round(size*lg.height/lg.width)),Image.LANCZOS)
    im.alpha_composite(lg,((W-size)//2,(H-lg.height)//2)); return im.convert('RGB')
specs=[
 ('16-ikat-deep-green-sage-hyphae', lambda: bands(3,3,(480,700)), DG,SAGE,EBG,None),
 ('17-ikat-purple-sage-nematode', lambda: nematode(2,600,980), PUR,SAGE,MON,None),
 ('18-ikat-brown-tan-micrograph', lambda: blown(9,9000,-3800,-2400,0), BR,TAN,EBG,None),
 ('19-ikat-green-cream-ciliate', lambda: ciliate(4), FWG,CRM,MON,None),
 ('20-ikat-blue-cream-hyphae', lambda: bands(11,3,(520,760)), EB,CRM,EBG,None),
 ('21-ikat-lightgreen-deepgreen-logo', lambda: bands(21,3,(480,700)), LGR,DG,None,'cream'),
 ('22-ikat-purple-sage-micrograph-logo', lambda: blown(13,9000,-4200,-2600,90), PUR,SAGE,None,'colour'),
 ('23-ikat-deep-green-sage-ciliate', lambda: ciliate(8,True), DG,SAGE,MON,None),
]
out={}
for i,(name,shape,fg,bg,font,lg) in enumerate(specs):
    B=ikat(shape(),i+1); img=compose(B,fg,bg,i)
    if font: img=wordmark(img,B,fg,bg,font,size=58 if font==EBG else 44,track=0.55 if font==EBG else 0.7)
    im=finish(img)
    if lg=='cream': im=with_logo(im,LG+'SFW-logo-flower-cream.png',460,DG)
    if lg=='colour': im=with_logo(im,LG+'SFW-logo-flower-colour.png',460,SAGE)
    im.save(f'SFW-case-{name}.png'); out[name]=im; print(name)
# mockups as in cases2
from PIL import ImageFilter as IF
def mock(art):
    w,h=900,1840; a=art.resize((w,h),Image.LANCZOS).convert('RGBA')
    m=Image.new('L',(w,h),0); ImageDraw.Draw(m).rounded_rectangle((0,0,w-1,h-1),150,fill=255)
    p=Image.new('RGBA',(w,h),(0,0,0,0)); p.paste(a,(0,0),m); d=ImageDraw.Draw(p)
    d.rounded_rectangle((60,60,400,400),95,fill=(18,22,14,255))
    for qx,qy in [(150,150),(150,310),(310,230)]: d.ellipse((qx-62,qy-62,qx+62,qy+62),fill=(8,10,8,255),outline=(70,80,60,255),width=8)
    sh=Image.new('RGBA',(w+60,h+60),(0,0,0,0)); s=Image.new('RGBA',(w,h),(0,0,0,90)); sh.paste(s,(18,24),m); sh=sh.filter(IF.GaussianBlur(20)); sh.alpha_composite(p,(0,0)); return sh
ms=[mock(v) for v in out.values()]
sheet=Image.new('RGB',(len(ms)*1000+80,2040),(226,222,214)); x=50
for mm in ms: sheet.paste(mm,(x,80),mm); x+=1000
sheet.save('SFW-phone-cases-v4-preview.png'); sheet.resize((sheet.width//4,sheet.height//4)).save('/tmp/v4.png')
