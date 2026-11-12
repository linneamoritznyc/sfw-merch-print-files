import math, random
from PIL import Image, ImageDraw, ImageFilter
exec(open('cases2.py').read().split("CAM=")[0])
LG='/home/claude/merch/logos/'
LOGO_COL=LG+'SFW-logo-flower-colour.png'; LOGO_DG=LG+'SFW-logo-flower-deepgreen.png'
BR=(79,52,51); FWG=(21,104,38); DG=(34,55,31); CRM=(244,241,234); EB=(55,128,184); PUR=(107,76,122); LGR=(89,166,108); TAN=(200,155,123)
def clearing(im,bg,cx,cy,r):
    ImageDraw.Draw(im).ellipse([(cx-r)*SS,(cy-r)*SS,(cx+r)*SS,(cy+r)*SS],fill=bg+(255,))
def centre_logo(im,bg,path,frac=0.45,cy=1840,clear=1.25):
    lw=int(W*frac); clearing(im,bg,W//2,cy,int(lw*clear/2)); logo(im,lw,(W-lw)//2,cy-lw//2,path)
def rnd_origins(seed,n): r=random.Random(seed); return [(r.uniform(0,W),r.uniform(0,H),r.uniform(0,6.28)) for _ in range(n)]
out={}
# 2b olive with big centred logo
im=canvas(OL); grow(im,rnd_origins(7,20),DO,steps=650,branch=0.012,maxtips=120,life=(180,360),w0=6,jit=0.2,seed=7,decay=0.997,minw=2.2,spore=PU,sporep=0.0012)
centre_logo(im,OL,LOGO_CR); out['2b-olive-logo-centre']=finish(im)
im=canvas(PUR); grow(im,rnd_origins(91,14),(160,190,110),steps=650,branch=0.012,maxtips=110,life=(180,360),w0=6,jit=0.2,seed=91,decay=0.997,minw=2.2,spore=BL2,sporep=0.0016)
centre_logo(im,PUR,LOGO_CR); out['purple-logo-centre']=finish(im)
# 7 soil brown, hyphae from bottom-left corner
im=canvas(BR); org=[(-20,H+20,-math.pi/2+k*0.13) for k in range(13)]
grow(im,org,CRM,steps=900,branch=0.012,maxtips=60,life=(250,520),w0=7,jit=0.16,seed=41,decay=0.997,minw=2,spore=(150,112,190),sporep=0.0018,avoid=lambda x,y:1340<x<1700 and 120<y<470)
logo(im,330,1350,130); out['7-soil-brown-corner']=finish(im)
# 8 food web green, big centred logo with light-green hyphae
im=canvas(FWG); grow(im,rnd_origins(51,16),LGR,steps=650,branch=0.012,maxtips=120,life=(180,360),w0=6,jit=0.2,seed=51,decay=0.997,minw=2.2,spore=CRM,sporep=0.0012)
centre_logo(im,FWG,LOGO_CR); out['8-food-web-green-logo']=finish(im)
# 9 cream, two-colour hyphae brown + green, colour logo
im=canvas(CRM)
grow(im,rnd_origins(61,9),BR,steps=650,branch=0.011,maxtips=70,life=(200,380),w0=6,jit=0.2,seed=61,decay=0.997,minw=2)
grow(im,rnd_origins(62,9),FWG,steps=650,branch=0.011,maxtips=70,life=(200,380),w0=6,jit=0.2,seed=62,decay=0.997,minw=2,spore=PUR,sporep=0.0015)
centre_logo(im,CRM,LOGO_COL); out['9-cream-two-colour']=finish(im)
# 10 education blue, single cream specimen with double ring
im=canvas(EB); cx,cy,R=900,2150,640
im.alpha_composite(plate(3,CRM,2*R),((cx-R)*SS,(cy-R)*SS)); ring(im,cx,cy,R+60,CRM,6); ring(im,cx,cy,R+88,CRM,3)
d=ImageDraw.Draw(im)
for k in range(48):
    a=k*2*math.pi/48; r1=R+100; r2=R+(150 if k%4==0 else 125)
    d.line([((cx+r1*math.cos(a))*SS,(cy+r1*math.sin(a))*SS),((cx+r2*math.cos(a))*SS,(cy+r2*math.sin(a))*SS)],fill=CRM+(255,),width=6*SS)
logo(im,320,1350,130); out['10-education-blue-specimen']=finish(im)
# 11 light green, deep-green specimen bottom-left + hyphae from top-right
im=canvas(LGR); cx,cy,R=420,2850,800
im.alpha_composite(plate(9,DG,2*R),((cx-R)*SS,(cy-R)*SS)); ring(im,cx,cy,R+30,DG,7)
org=[(W+20,-20,math.pi*0.5+k*0.12) for k in range(13)]
grow(im,org,DG,steps=900,branch=0.012,maxtips=60,life=(250,520),w0=7,jit=0.16,seed=71,decay=0.997,minw=2,spore=PUR,sporep=0.0015,avoid=lambda x,y:(x-cx)**2+(y-cy)**2<(R+45)**2 or (1300<x<1700 and 1650<y<2050))
logo(im,320,1350,1680,LOGO_DG); out['11-light-green-corner-specimen']=finish(im)
# 12 natural tan, deep green hyphae + deep green logo centred
im=canvas(TAN); grow(im,rnd_origins(81,14),DG,steps=650,branch=0.012,maxtips=110,life=(180,360),w0=6,jit=0.2,seed=81,decay=0.997,minw=2.2,spore=PUR,sporep=0.0012)
centre_logo(im,TAN,LOGO_DG,frac=0.42); out['12-natural-tan-logo']=finish(im)

import numpy as np
def best_plate(R,cx,cy,cands):
    best=None
    yy,xx=np.mgrid[0:2*R,0:2*R]; X=xx+cx-R; Y=yy+cy-R
    vis=((xx-R)**2+(yy-R)**2<R*R)&(X>=0)&(Y>=0)&~((X<820)&(Y<820))
    for i in cands:
        p=Image.open(f'/home/claude/merch/micro/plate_{i}.png').convert('RGBA').resize((2*R,2*R))
        for rot in (0,90,180,270):
            a=np.asarray(p.rotate(rot).split()[3])>128
            sc=(a&vis).sum()
            if best is None or sc>best[0]: best=(sc,i,rot)
    return best[1],best[2]
def lens_case(bg,ink,spore,cands,seed,logo_path=LOGO_CR):
    im=canvas(bg); cx,cy,R=470,470,860
    i,rot=best_plate(R,cx,cy,cands)
    pl=plate(i,ink,2*R).rotate(rot); im.alpha_composite(pl,((cx-R)*SS,(cy-R)*SS))
    d=ImageDraw.Draw(im)
    ring(im,cx,cy,R+24,ink,12)
    for k in range(96):
        a=k*2*math.pi/96; r1=R+56; r2=R+(130 if k%8==0 else 95)
        d.line([((cx+r1*math.cos(a))*SS,(cy+r1*math.sin(a))*SS),((cx+r2*math.cos(a))*SS,(cy+r2*math.sin(a))*SS)],fill=ink+(255,),width=(12 if k%8==0 else 8)*SS)
    org=[(cx+(R+140)*math.cos(a),cy+(R+140)*math.sin(a),a) for a in [0.2,0.5,0.8,1.1,1.4]]
    lcy=2600; lw=int(W*0.45); rc=int(lw*1.25/2)
    grow(im,org,ink,steps=700,branch=0.012,maxtips=60,life=(250,480),w0=6,seed=seed,decay=0.997,minw=2,spore=spore,sporep=0.002,avoid=lambda x,y:(x-cx)**2+(y-cy)**2<(R+135)**2)
    clearing(im,bg,W//2,lcy,rc); logo(im,lw,(W-lw)//2,lcy-lw//2,logo_path)
    print('lens plate',i,rot)
    try: USED[0]=i
    except NameError: pass
    return finish(im)
out['13-lens-food-web-green']=lens_case(FWG,PG,PU2,range(16),101)
USED=[None]
out['14-lens-purple']=lens_case(PUR,PG,BL2,[i for i in range(16) if i!=13],102)
out['15-lens-education-blue']=lens_case(EB,CRM,PG,[i for i in range(16) if i not in (13,USED[0])],103)
for k,v in out.items(): v.save(f'SFW-case-{k}.png')
exec(open('cases2.py').read().split("# mockups")[1].split("ms=[")[0])
ms=[mock(v) for v in out.values()]
sheet=Image.new('RGB',(len(ms)*1000+80,2040),(226,222,214)); x=50
for mm in ms: sheet.paste(mm,(x,80),mm); x+=1000
sheet.save('SFW-phone-cases-v3-preview.png'); sheet.resize((sheet.width//4,sheet.height//4)).save('/tmp/v3.png')
