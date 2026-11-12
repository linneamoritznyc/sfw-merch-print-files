import math, random, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
exec(open('cases5.py').read().split("out={}")[0])
_T=T
def T(im,xy,txt,font,col,anchor='la',track=0):
    if track and anchor[0]=='r':
        d=ImageDraw.Draw(im); tot=sum(d.textlength(c,font=font) for c in txt)/SS+track*(len(txt)-1); return _T(im,(xy[0]-tot,xy[1]),txt,font,col,'l'+anchor[1],track)
    return _T(im,xy,txt,font,col,anchor,track)  # canvas, grow, plate, T, grain, circle_mask, fonts, colours
DO=(46,58,28); OL=(91,107,46); DG=(34,55,31); PG=(203,214,150); PU2=(150,112,190); BL2=(110,160,210); NAVY=(28,46,70); EB=(55,128,184)
G4=ImageFont.truetype('ebg400.ttf',10).path
def S(*v): return [int(x*SS) for x in v]
def worm(d,pts,w,col):
    for i in range(len(pts)-1):
        t=i/len(pts); ww=w*max(0.25,min(1,t*5,(1-t)*4))
        d.line(S(*pts[i],*pts[i+1]),fill=col+(255,),width=int(ww*SS))
def nem_pts(x,y,L,a,amp,n=60,ph=0):
    return [(x+L*t*math.cos(a)-amp*math.sin(t*9+ph)*math.sin(a), y+L*t*math.sin(a)+amp*math.sin(t*9+ph)*math.cos(a)) for t in np.linspace(0,1,n)]
def ciliate_draw(d,cx,cy,rx,ry,col,w=5,cil=True):
    d.ellipse(S(cx-rx,cy-ry,cx+rx,cy+ry),outline=col+(255,),width=w*SS)
    if cil:
        for k in range(60):
            a=k/60*2*math.pi; d.line(S(cx+rx*math.cos(a),cy+ry*math.sin(a),cx+(rx+22)*math.cos(a),cy+(ry+22)*math.sin(a)),fill=col+(255,),width=max(1,w//2)*SS)
    d.ellipse(S(cx-rx*0.3,cy-ry*0.15,cx+rx*0.25,cy+ry*0.25),outline=col+(255,),width=w*SS)
out={}
# 1 FIELD NOTEBOOK: deep-olive page, ruled lines, pencil annotations of a nematode
im=canvas(DO); d=ImageDraw.Draw(im)
for y in range(980,3600,110): d.line(S(80,y,1720,y),fill=OL+(255,),width=2*SS)
d.line(S(260,860,260,3600),fill=PU2+(255,),width=3*SS)
T(im,(320,1000),'Field notes — 12 Nov',F(G4I,74),PG,'ls')
T(im,(320,1110),'sample 4, under the oak, 2 cm deep',F(G4I,54),PG,'ls')
pts=nem_pts(380,1650,1100,0.1,110); worm(d,pts,64,PG)
for (x,y),lab in [(pts[2],'mouth / stylet?'),(pts[30],'gut'),(pts[-3],'tail, tapering')]:
    tx,ty=(x-40 if lab.startswith('tail') else x+40),y+(260 if lab.startswith('tail') else -260); d.line(S(x,y,tx,ty),fill=PG+(255,),width=3*SS); T(im,(tx+(-12 if lab.startswith('tail') else 12),ty),lab,F(G4I,62),PG,'rm' if lab.startswith('tail') else 'lm')
T(im,(320,2440),'Nematode — bacterial feeder.',F(G4I,60),PG,'ls')
T(im,(320,2550),'Moves like a sine wave. Counted 6 in one drop.',F(G4I,50),PG,'ls')
T(im,(320,2660),'Good sign: nutrient cycling at work.',F(G4I,50),PU2,'ls')
for k,(x,y) in enumerate([(380,2950),(560,3010),(720,2930)]):
    d.ellipse(S(x-50,y-50,x+50,y+50),outline=PG+(255,),width=3*SS)
T(im,(880,2990),'fungal spores, ×3',F(G4I,48),PG,'lm')
out['32-field-notebook']=im
# 2 PETRI DISH from above, navy
im=canvas(NAVY); d=ImageDraw.Draw(im); cx,cy,R=900,2050,820
d.ellipse(S(cx-R-40,cy-R-40,cx+R+40,cy+R+40),outline=BL2+(255,),width=8*SS); d.ellipse(S(cx-R,cy-R,cx+R,cy+R),fill=(36,58,86,255),outline=BL2+(255,),width=4*SS)
r=random.Random(7)
placed=[]
for k in range(400):
    if len(placed)>=17: break
    a=r.uniform(0,6.28); rr=R*math.sqrt(r.uniform(0,0.8)); x,y=cx+rr*math.cos(a),cy+rr*math.sin(a); s=r.choice([30,45,70,110,160]); c=r.choice([PG,PU2,(240,236,226),BL2])
    if any((x-px)**2+(y-py)**2<(s+ps+40)**2 for px,py,ps in placed) or rr+s>R-30: continue
    placed.append((x,y,s))
    d.ellipse(S(x-s,y-s,x+s,y+s),fill=c+(255,))
    if s>60: d.ellipse(S(x-s*0.6,y-s*0.6,x+s*0.6,y+s*0.6),outline=NAVY+(255,),width=3*SS)
fx,fy=cx-300,cy+250
grow(im,[(fx,fy,a) for a in np.linspace(0,6.28,14)],PG,steps=110,branch=0.03,maxtips=60,life=(60,110),w0=3,jit=0.25,seed=3,avoid=lambda x,y:(x-cx)**2+(y-cy)**2>(R-20)**2)
T(im,(900,3060),'PLATE 12  ·  SOIL EXTRACT  ·  DAY 4',F(G5,40),BL2,'mm',track=10)
out['33-petri-dish']=im
# 3 VERTICAL TYPE filled with micrograph texture, blue
im=canvas(EB); tm=Image.new('L',(H*SS,W*SS),0); dt=ImageDraw.Draw(tm)
sz=980
while ImageDraw.Draw(tm).textlength('LIVING SOIL',font=F(G6,sz))>H*SS*0.92: sz-=20
f=F(G6,sz); dt.text((H*SS/2+120*SS,W*SS*0.5),'LIVING SOIL',font=f,anchor='mm',fill=255)
tm=tm.rotate(90,expand=True)
tex=Image.new('RGBA',(W*SS,H*SS),NAVY+(255,)); r=random.Random(3)
for k in range(10):
    pl=plate(r.randrange(16),BL2 if k%2 else PG,1100); tex.alpha_composite(pl,S(r.randint(-300,1000),r.randint(-300,3200)))
im.paste(tex,(0,0),tm)
T(im,(1650,3560),'SOIL FOOD WEB',F(G5,40),NAVY,'rm',track=12)
out['34-vertical-type']=im
# 4 SOIL CROSS-SECTION layers with life
im=canvas(DG); d=ImageDraw.Draw(im)
layers=[(-120,PG,'O · LITTER'),(1100,OL,'A · TOPSOIL'),(1900,DO,'B · SUBSOIL'),(2800,DG,'C · PARENT MATERIAL')]
r=random.Random(2)
for i,(y0,c,lab) in enumerate(layers):
    y1=layers[i+1][0] if i<3 else H
    pts=[(x,y0+40*math.sin(x/170+i)) for x in range(-20,W+40,40)]
    poly=pts+[(W+40,H),(-20,H)]; d.polygon([tuple(int(v*SS) for v in p) for p in poly],fill=c+(255,))
for i,(y0,c,lab) in enumerate(layers):
    tc=DO if i==0 else PG; T(im,(1690,y0+(380 if i==0 else 140)),lab,F(G5,54),tc,'rm',track=10)
# life: leaves in O, hyphae+nematode+ciliates in A, roots in B, rock in C
for k in range(14):
    x,y=r.uniform(100,1700),r.uniform(880,1040); d.ellipse(S(x-60,y-22,x+60,y+22),fill=OL+(255,))
grow(im,[(300,1200,0.4),(1300,1250,2.6),(800,1150,1.5)],PG,steps=200,branch=0.02,maxtips=40,life=(120,200),w0=3,seed=9,avoid=lambda x,y:y<1150 or y>1880)
worm(d,nem_pts(380,1560,500,0.1,40),22,PU2); ciliate_draw(d,1350,1620,80,50,BL2,4)
grow(im,[(900,1150,1.57),(600,1150,1.75),(1250,1150,1.35)],(150,112,190),steps=380,branch=0.015,maxtips=20,life=(300,400),w0=9,jit=0.1,seed=13,avoid=lambda x,y:y>2750,decay=0.995,minw=2)
for k in range(9):
    x,y,s=r.uniform(100,1700),r.uniform(3000,3550),r.uniform(80,180); d.polygon([tuple(int(v*SS) for v in (x+s*math.cos(a)*r.uniform(0.7,1),y+s*0.7*math.sin(a)*r.uniform(0.7,1))) for a in np.linspace(0,6.28,7)[:-1]],fill=OL+(255,))
out['35-soil-profile']=im
# 5 STAR CHART: microbes as constellations on navy
im=canvas(NAVY); d=ImageDraw.Draw(im); r=random.Random(21)
for k in range(500):
    x,y,s=r.uniform(0,W),r.uniform(0,H),r.choice([1.5,2,2.5,3.5]); d.ellipse(S(x-s,y-s,x+s,y+s),fill=(220,226,236,255))
for rr in [700,1100,1500]: d.ellipse(S(900-rr,2000-rr,900+rr,2000+rr),outline=(60,86,120,255),width=2*SS)
def const(pts,name):
    for a,b in zip(pts,pts[1:]): d.line(S(*a,*b),fill=BL2+(255,),width=3*SS)
    for x,y in pts: d.ellipse(S(x-14,y-14,x+14,y+14),fill=PG+(255,))
    mx=sum(p[0] for p in pts)/len(pts); my=max(p[1] for p in pts)+90; T(im,(mx,my),name,F(G4I,52),PU2,'mm')
const(nem_pts(250,1150,1000,0.12,80,9),'Nematoda')
c=[(1150+170*math.cos(a),2050+250*math.sin(a)) for a in np.linspace(0,6.28,9)]; const(c,'Ciliata')
const([(330,2700),(520,2600),(700,2720),(880,2620),(760,2860),(560,2980)],'Hypha Major')
const([(1150,3050),(1330,3150),(1500,3020)],'Bacillus')
T(im,(900,3480),'THE SOIL FOOD WEB  ·  NORTHERN SKY',F(G5,38),BL2,'mm',track=10)
out['36-star-chart']=im
# 6 ROOT + RHIZOSPHERE, full height, purple
im=canvas(PUR); d=ImageDraw.Draw(im); r=random.Random(8)
xs=[900+180*math.sin(y/700)+60*math.sin(y/230) for y in range(-50,H+60,10)]
for i,y in enumerate(range(-50,H+60,10)):
    w=260-y*0.045; d.ellipse(S(xs[i]-w/2,y-w/2,xs[i]+w/2,y+w/2),fill=PG+(255,))
# root hairs
for i in range(0,len(xs),3):
    y=-50+i*10; w=260-y*0.045
    for side in (-1,1):
        L=r.uniform(60,190); a=r.uniform(-0.5,0.5)
        x0=xs[i]+side*w/2; d.line(S(x0,y,x0+side*L*math.cos(a),y+L*math.sin(a)),fill=PG+(255,),width=3*SS)
# microbes clustered in rhizosphere
for k in range(260):
    i=r.randrange(len(xs)); y=-50+i*10; w=260-y*0.045; side=r.choice([-1,1]); dist=w/2+abs(r.gauss(0,140))+30
    x=xs[i]+side*dist; c=r.choice([BL2,BL2,DO,(240,236,226)]); kind=r.random()
    if kind<0.6: d.ellipse(S(x-9,y-9,x+9,y+9),fill=c+(255,))
    elif kind<0.85: a=r.uniform(0,3.14); d.line(S(x-16*math.cos(a),y-16*math.sin(a),x+16*math.cos(a),y+16*math.sin(a)),fill=c+(255,),width=10*SS)
    else: d.ellipse(S(x-30,y-20,x+30,y+20),outline=c+(255,),width=4*SS)
grow(im,[(0,1400,0.2),(W,2300,3.0),(0,3000,-0.1)],DO,steps=220,branch=0.02,maxtips=40,life=(120,220),w0=4,seed=5)
T(im,(150,3480),'the rhizosphere',F(G4I,60),PG,'lm')
out['37-rhizosphere']=im
# 7 BOTANICAL PLATE numbered parts, deep olive
im=canvas(DO); d=ImageDraw.Draw(im); cx,cy=900,1950
ciliate_draw(d,cx,cy,380,560,PG,12)
d.line(S(cx,cy+560,cx-60,cy+1250),fill=PG+(255,),width=12*SS)  # stalk
for k in range(9): d.ellipse(S(cx-200+k*40,cy-320+((k*53)%220),cx-150+k*40,cy-270+((k*53)%220)),fill=PU2+(255,))
parts=[((cx,cy-560-20),(1550,1150),'1'),((cx-110,cy+20),(250,1700),'2'),((cx-60,cy-200),(1550,1600),'3'),((cx-30,cy+900),(1550,2900),'4')]
for (px,py),(lx,ly),n in parts:
    d.line(S(px,py,lx,ly),fill=PG+(255,),width=4*SS); d.ellipse(S(lx-52,ly-52,lx+52,ly+52),fill=DO+(255,),outline=PG+(255,),width=5*SS); T(im,(lx,ly),n,F(G5,64),PG,'mm')
T(im,(900,1030),'TAB. VII',F(G5,44),PU2,'mm',track=14)
legend='1 cilia   2 macronucleus   3 food vacuoles   4 contractile stalk'
T(im,(900,3380),'Vorticella campanula',F(G4I,74),PG,'mm'); T(im,(900,3490),legend,F(G4I,46),PG,'mm')
out['38-botanical-plate']=im
# 8 SPORE BURST from below, deep olive
im=canvas(DO); d=ImageDraw.Draw(im); r=random.Random(12); cx,cy=1100,3900
for k in range(140):
    a=r.uniform(math.pi*1.08,math.pi*1.92); L=r.uniform(1500,3900); ex,ey=cx+L*math.cos(a),cy+L*math.sin(a)
    d.line(S(cx,cy,ex,ey),fill=OL+(255,),width=2*SS)
    s_=r.choice([8,12,18,26]); c=r.choice([PG,PG,PU2,BL2]); d.ellipse(S(ex-s_,ey-s_,ex+s_,ey+s_),fill=c+(255,))
d.ellipse(S(cx-520,cy-520,cx+520,cy+520),fill=PG+(255,))
T(im,(150,3480),'sporulation',F(G4I,60),DO,'lm')
out['39-spore-burst']=im
arts={}
for k,v in out.items():
    a=grain(v.resize((W,H),Image.LANCZOS),0.05,hash(k)%100); a.save(f'SFW-case-{k}.png'); arts[k]=a
exec(open('cases2.py').read().split("# mockups")[1].split("ms=[")[0])
ms=[mock(v.convert('RGBA')) for v in arts.values()]
sheet=Image.new('RGB',(len(ms)*1000+80,2040),(226,222,214)); x=50
for mm in ms: sheet.paste(mm,(x,80),mm); x+=1000
sheet.save('SFW-phone-cases-v6-preview.png'); sheet.resize((sheet.width//4,sheet.height//4)).save('/tmp/v6.png')
