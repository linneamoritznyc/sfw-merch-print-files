import math, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
N=2400; SS=1
def hx(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
PALS=[(hx('6B4C7A'),[hx('C8B6E2'),hx('CBD696')]),(hx('3780B8'),[hx('D6E28C'),hx('96C4E8')]),(hx('156826'),[hx('59A66C'),hx('BED65A')]),
      (hx('5B6B2E'),[hx('BED65A'),hx('C8B6E2')]),(hx('22371F'),[hx('59A66C'),hx('CBD696')]),(hx('C8B6E2'),[hx('6B4C7A'),hx('F4F1EA')]),
      (hx('96C4E8'),[hx('1A2C52'),hx('F4F1EA')]),(hx('CBD696'),[hx('156826'),hx('6B4C7A')]),(hx('4F3433'),[hx('C89B7B'),hx('C8B6E2')])]
def plate(i):
    p=Image.open(f'/home/claude/merch/micro/plate_{i}.png').convert('RGBA').split()[3]
    m=Image.new('L',p.size,0); c=p.width/2; r=p.width*0.465; ImageDraw.Draw(m).ellipse([c-r,c-r,c+r,c+r],fill=255)
    return Image.fromarray(np.minimum(np.asarray(p),np.asarray(m)))
PL=[plate(i) for i in range(16)]
def disc(R,pi,pal,rot,cell):
    base,dots=pal; D=2*R; im=Image.new('RGBA',(D,D),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.ellipse([0,0,D-1,D-1],fill=base+(255,))
    A=np.asarray(PL[pi].rotate(rot).resize((D,D),Image.LANCZOS).filter(ImageFilter.GaussianBlur(max(1,D/300)))).astype(float)/255
    A2=np.asarray(PL[(pi+5)%16].rotate(rot+90).resize((D,D)).filter(ImageFilter.GaussianBlur(D/120))).astype(float)/255
    for li,(col,AA) in enumerate([(dots[1],A2*0.8),(dots[0],A)]):
        off=li*cell/2
        for gy in np.arange(off,D,cell):
            for gx in np.arange(off+(cell/2 if int(gy/cell)%2 else 0),D,cell):
                if (gx-R)**2+(gy-R)**2>(R-cell)**2: continue
                v=AA[int(gy),int(gx)]
                if v<0.12: continue
                rad=cell*0.5*min(1,v)**0.6; d.ellipse([gx-rad,gy-rad,gx+rad,gy+rad],fill=col+(255,))
    return im
def grid(name,bg,seed,R=150,gap=14,ring=None):
    r=random.Random(seed); im=Image.new('RGB',(N,N),bg)
    dx=2*R+gap; dy=dx*math.sqrt(3)/2
    y=-R/2; row=0
    while y<N+R:
        x=(-R/2 if row%2 else R/2); 
        while x<N+R:
            pal=r.choice(PALS); dd=disc(R,r.randrange(16),pal,r.choice([0,90,180,270]),max(6,R//14))
            if ring: ImageDraw.Draw(im).ellipse([x-R-6,y-R-6,x+R+6,y+R+6],outline=ring,width=4)
            im.paste(dd,(int(x-R),int(y-R)),dd); x+=dx
        y+=dy; row+=1
    im.save(f'SFW-pattern-{name}.png'); return im
def scatter(name,bg,seed,n=60):
    r=random.Random(seed); im=Image.new('RGB',(N,N),bg)
    for k in range(n):
        R=int(r.choice([60,90,130,180,240,320])); x,y=r.uniform(-R,N+R),r.uniform(-R,N+R)
        dd=disc(R,r.randrange(16),r.choice(PALS),r.choice([0,90,180,270]),max(6,R//14)); im.paste(dd,(int(x-R),int(y-R)),dd)
    im.save(f'SFW-pattern-{name}.png'); return im
a=grid('discs-cream',hx('F4F1EA'),1,ring=hx('22371F'))
b=grid('discs-deepgreen',hx('22371F'),2)
c=scatter('discs-scatter-sage',hx('A8B49A'),3)
d=grid('discs-big-purple',hx('6B4C7A'),4,R=260,gap=24)
S=Image.new('RGB',(2*1220+40,2*1220+40),(226,222,214))
for i,v in enumerate([a,b,c,d]): S.paste(v.resize((1200,1200),Image.LANCZOS),(20+(i%2)*1220,20+(i//2)*1220))
S.save('SFW-patterns-discs-colour.jpg',quality=88)
