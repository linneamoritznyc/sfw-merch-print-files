import math, random, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
exec(open('cases2.py').read().split("CAM=")[0])   # canvas/grow/plate/logo/ring, SS=2
LG='/home/claude/merch/logos/'; LOGO_COL=LG+'SFW-logo-flower-colour.png'
F=lambda n,s: ImageFont.truetype(n,s*SS)
PUR=(107,76,122); CRM=(244,241,234)
G5,G5I,G6,G4I='ebg500.ttf','ebg500i.ttf','ebg600.ttf','ebg400i.ttf'
def T(im,xy,txt,font,col,anchor='la',track=0):
    d=ImageDraw.Draw(im); x,y=xy[0]*SS,xy[1]*SS
    if not track: d.text((x,y),txt,font=font,fill=col+(255,),anchor=anchor); return
    ws=[d.textlength(c,font=font) for c in txt]; tot=sum(ws)+track*SS*(len(txt)-1)
    if anchor[0]=='m': x-=tot/2
    for c,w in zip(txt,ws): d.text((x,y),c,font=font,fill=col+(255,),anchor='l'+anchor[1]); x+=w+track*SS
def grain(img,amt=0.07,seed=0):
    a=np.asarray(img.convert('RGB')).astype(float); n=np.random.default_rng(seed).normal(0,1,a.shape[:2])
    return Image.fromarray((a*(1+amt*n[...,None])).clip(0,255).astype(np.uint8))
def circle_mask(size):
    m=Image.new('L',(size,size),0); ImageDraw.Draw(m).ellipse((0,0,size-1,size-1),fill=255); return m
out={}
# 1 MACRO: one plate blown up crisp, cropped, pale green on deep olive
im=canvas(DO); p=plate(4,PG,3400); im.alpha_composite(p,(-900*SS,-200*SS))
T(im,(150,3470),'×4000  ·  fungal hypha, living soil',F(G4I,46),PG)
out['24-macro-crop']=im
# 2 GRID: 4x7 grid of micrograph discs, alternating tints, skip camera cells
im=canvas(OL); cell=400; ox,oy=100,230; k=0; cols=[PG,PU2,BL2,DO]
r=random.Random(5)
for j in range(8):
    for i in range(4):
        x,y=ox+i*cell,oy+j*cell
        if x<820 and y<820: continue
        if y+cell>H: continue
        s=330; c=cols[(i+j)%4]
        disc=Image.new('RGBA',(s*SS,s*SS),DO+(255,)) if c!=DO else Image.new('RGBA',(s*SS,s*SS),PG+(255,))
        pl=plate(r.randrange(16),c if c!=DO else DO,s); disc.alpha_composite(pl)
        im.paste(disc,((x+35)*SS,(y+35)*SS),circle_mask(s*SS))
out['25-grid-specimens']=im
# 3 SPECIMEN LABEL hero on purple
im=canvas(PUR); d=ImageDraw.Draw(im)
x0,y0,x1,y1=170,1180,1630,2900
d.rectangle([x0*SS,y0*SS,x1*SS,y1*SS],fill=CRM+(255,)); d.rectangle([(x0+30)*SS,(y0+30)*SS,(x1-30)*SS,(y1-30)*SS],outline=PUR+(255,),width=4*SS)
T(im,(900,y0+150),'SPECIMEN No. 07',F(G5,58),PUR,'mm',track=14)
d.line([(x0+120)*SS,(y0+230)*SS,(x1-120)*SS,(y0+230)*SS],fill=PUR+(255,),width=3*SS)
cx,cy,R=900,y0+620,330; disc=Image.new('RGBA',(2*R*SS,2*R*SS),DO+(255,)); disc.alpha_composite(plate(0,PG,2*R)); im.paste(disc,((cx-R)*SS,(cy-R)*SS),circle_mask(2*R*SS)); ring(im,cx,cy,R+18,PUR,4)
T(im,(900,y0+1080),'Vorticella',F(G4I,120),DO,'mm')
T(im,(900,y0+1200),'stalked ciliate · bacterial feeder',F(G4I,52),PUR,'mm')
T(im,(900,y0+1330),'COLLECTED FROM THE LIVING SOIL',F(G5,36),DO,'mm',track=9)
T(im,(900,y0+1430),'SOIL FOOD WEB FOUNDATION',F(G5,36),PUR,'mm',track=12)
out['26-specimen-label']=im
# 4 BIG TYPE stacked, olive
im=canvas(DO); words=[('DIRT',PU2),('IS',PU2),('DEAD.',PU2),('SOIL',PG),('IS',PG),('ALIVE.',PG)]
y=880
for w,c in words:
    T(im,(900,y),w,F(G6,470),c,'mt'); y+=440
out['27-big-type']=im
# 5 COLLAGE: pasted square prints on olive with tape
im=canvas(OL); r=random.Random(9)
spots=[(1150,520,560,-6),(420,1250,700,4),(1250,1500,520,8),(700,2250,760,-3),(1300,2800,600,6),(380,3200,520,-9)]
for (cx,cy,s,ang),pi_ in zip(spots,[2,5,9,12,7,14]):
    card=Image.new('RGBA',((s+60)*SS,(s+130)*SS),CRM+(255,)); inner=Image.new('RGBA',(s*SS,s*SS),DO+(255,)); inner.alpha_composite(plate(pi_,r.choice([PG,PU2,BL2]),s)); card.paste(inner,(30*SS,30*SS))
    T(card,((s+60)//2,s+80),f'fig. {pi_+1}',F(G4I,40),DO,'mm')
    tape=Image.new('RGBA',(220*SS,70*SS),(203,214,150,170)); card.alpha_composite(tape,(((s+60)//2-110)*SS,0))
    card=card.rotate(ang,expand=True,resample=Image.BICUBIC); im.alpha_composite(card,(int(cx*SS-card.width/2),int(cy*SS-card.height/2)))
out['28-collage-prints']=im
# 6 ONE EDGE: mycelium only on right edge, navy; cream badge with colour logo mid-left
im=canvas(NAVY)
org=[(W+10,y,math.pi+random.Random(y).gauss(0,0.3)) for y in range(200,H,180)]
grow(im,org,BL2,steps=260,branch=0.02,maxtips=120,life=(80,190),w0=6,jit=0.22,seed=61,spore=PG,sporep=0.003,decay=0.993,minw=1.5)
cx,cy,R=620,1950,360; ImageDraw.Draw(im).ellipse([(cx-R)*SS,(cy-R)*SS,(cx+R)*SS,(cy+R)*SS],fill=CRM+(255,)); logo(im,560,cx-280,cy-280,LOGO_COL)
out['29-one-edge-blue']=im
# 7 OFF-CENTRE: tiny specimen low right, vast olive field, giant thin ring crossing; colour logo in cream disc bleeding? keep logo top-right small
im=canvas(OL); ring(im,1450,2950,1100,PU2,14); ring(im,1450,2950,1160,PU2,4); ring(im,1450,2950,1220,PU2,2)
cx,cy,R=1300,2860,300; disc=Image.new('RGBA',(2*R*SS,2*R*SS),PUR+(255,)); disc.alpha_composite(plate(3,PG,2*R)); im.paste(disc,((cx-R)*SS,(cy-R)*SS),circle_mask(2*R*SS))
T(im,(1300,3250),'one teaspoon, one billion lives',F(G4I,58),PG,'mm')
cx,cy,R=1430,500,230; ImageDraw.Draw(im).ellipse([(cx-R)*SS,(cy-R)*SS,(cx+R)*SS,(cy+R)*SS],fill=CRM+(255,)); logo(im,360,cx-180,cy-180,LOGO_COL)
out['30-off-centre-teaspoon']=im
# 8 COLONY CONTOURS: topographic rings from noise, olive tones + purple core
im=canvas(DO); rng=np.random.default_rng(3)
h=np.zeros((92,46)); 
for k in range(6):
    cx,cy=rng.uniform(5,41),rng.uniform(5,87); s=rng.uniform(6,14); yy,xx=np.mgrid[0:92,0:46]; h+=np.exp(-((xx-cx)**2+(yy-cy)**2)/(2*s*s))*rng.uniform(0.6,1.2)
yy,xx=np.mgrid[0:H*SS:4,0:W*SS:4].astype(float); sc=W*SS/46; hh=np.zeros(xx.shape); rng=np.random.default_rng(3)
for k in range(6):
    cx,cy=rng.uniform(5,41),rng.uniform(5,87); s_=rng.uniform(6,14); hh+=np.exp(-((xx/sc-cx)**2+(yy/sc-cy)**2)/(2*s_*s_))*rng.uniform(0.6,1.2)
A=np.asarray(Image.fromarray((hh/hh.max()*65535).astype(np.uint16).astype(np.int32),'I').resize((W*SS,H*SS),Image.BILINEAR)).astype(float)/65535*255
band=(np.floor(A/18)%2==0); edge=np.zeros_like(band); edge[1:]|=band[1:]!=band[:-1]; edge[:,1:]|=band[:,1:]!=band[:,:-1]
em=Image.fromarray((edge*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))
im.paste(Image.new('RGBA',im.size,PG+(255,)),(0,0),em)
core=Image.fromarray(((A>235)*255).astype(np.uint8)); im.paste(Image.new('RGBA',im.size,PU2+(255,)),(0,0),core)
T(im,(150,3470),'COLONY 03  ·  SOIL FOOD WEB',F(G5,40),PG,track=10)
out['31-colony-contours']=im
arts={}
for k,v in out.items():
    a=grain(v.resize((W,H),Image.LANCZOS),0.05,hash(k)%100); a.save(f'SFW-case-{k}.png'); arts[k]=a
exec(open('cases2.py').read().split("# mockups")[1].split("ms=[")[0])
ms=[mock(v.convert('RGBA')) for v in arts.values()]
sheet=Image.new('RGB',(len(ms)*1000+80,2040),(226,222,214)); x=50
for mm in ms: sheet.paste(mm,(x,80),mm); x+=1000
sheet.save('SFW-phone-cases-v5-preview.png'); sheet.resize((sheet.width//4,sheet.height//4)).save('/tmp/v5.png')
