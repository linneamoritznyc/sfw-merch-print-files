import math, random, numpy as np
from PIL import Image, ImageDraw
src=open('cliptex.py').read(); exec(src.split("out={}")[0])
PAL['bpurple']=((107,76,122),(107,76,122),[(200,182,226),(203,214,150)])
PAL['bblue']=((55,128,184),(55,128,184),[(214,226,140),(150,196,232)])
PAL['bgreen']=((21,104,38),(21,104,38),[(89,166,108),(190,214,90)])
def blobm(cx,cy,R,seed,sy=1.25):
    m=Image.new('L',(W*SS,H*SS),0)
    pts=[(cx+R*(1+0.18*math.sin(3*t+seed)+0.1*math.sin(5*t))*math.cos(t),cy+R*sy*(1+0.15*math.cos(2*t+seed))*math.sin(t)) for t in np.linspace(0,6.28,160)]
    ImageDraw.Draw(m).polygon([(x*SS,y*SS) for x,y in pts],fill=255); return m
def hyph(seed,starts,bp=0.008):
    rr=random.Random(seed); m=Image.new('L',(W*SS,H*SS),0); d=ImageDraw.Draw(m)
    def br(x,y,a,w,dep):
        while w>40 and -200<x<W+200 and -200<y<H+200:
            a+=rr.gauss(0,0.04); nx,ny=x+14*math.cos(a),y+14*math.sin(a)
            d.line([x*SS,y*SS,nx*SS,ny*SS],fill=255,width=int(w*SS)); d.ellipse([(nx-w/2)*SS,(ny-w/2)*SS,(nx+w/2)*SS,(ny+w/2)*SS],fill=255); x,y=nx,ny; w*=0.9985
            if rr.random()<bp and dep<2: br(x,y,a+rr.choice([-1,1])*0.8,w*0.7,dep+1)
    for s in starts: br(*s,0)
    return m
BG={'sage':(168,180,154),'deepgreen':(34,55,31),'cream':(244,241,234)}
LG={'sage':'SFW-logo-flower-colour.png','deepgreen':'SFW-logo-flower-cream.png','cream':'SFW-logo-flower-colour.png'}
def make(name,bg,shapes,hy,logo_pos,seed):
    im=Image.new('RGBA',(W*SS,H*SS),BG[bg]+(255,))
    for k,(pal,cx,cy,R,sd) in enumerate(shapes): im.paste(texture(pal,seed*7+k),(0,0),blobm(cx,cy,R,sd))
    im.paste(texture('bgreen',seed*7+9),(0,0),hyph(seed,hy))
    w=500; path='/home/claude/merch/logos/'+LG[bg]
    if logo_pos=='br': logo(im,W-80-w//2,H-80-w//2,w,path)
    else: logo(im,W//2,H-90-w//2,w,path)
    a=fin(im,seed); a.save(f'SFW-case-{name}.png'); return a
V=[('53c-sage-stack','sage',[('bblue',1050,900,620,1),('bpurple',700,2050,560,4)],[(-150,300,0.9,200),(W+150,1300,2.95,150)],'bc',1),
   ('53d-cream-diagonal','cream',[('bpurple',1350,700,520,2),('bblue',450,1900,600,7)],[(300,-150,1.25,210)],'br',2),
   ('53e-deepgreen-big','deepgreen',[('bblue',1500,1300,900,3)],[(-150,2400,-0.35,230),(300,-150,0.95,170)],'bc',3),
   ('53f-sage-trio','sage',[('bpurple',500,700,420,5),('bblue',1350,1550,480,8),('bpurple',600,2500,380,9)],[(W+150,400,2.3,190)],'br',4),
   ('53g-cream-cells','cream',[('bblue',900,1500,760,6)],[(-150,800,0.25,180),(W+150,2200,2.95,180)],'bc',5),
   ('53h-deepgreen-pair','deepgreen',[('bpurple',1200,900,560,11),('bblue',600,2200,520,12)],[(900,-150,1.6,240)],'br',6)]
arts=[make(*v) for v in V]
s=Image.new('RGB',(6*420+20,880),(226,222,214))
for i,v in enumerate(arts): s.paste(v.resize((400,818)),(20+i*420,30))
s.save('SFW-case-53-variations.jpg',quality=90)
