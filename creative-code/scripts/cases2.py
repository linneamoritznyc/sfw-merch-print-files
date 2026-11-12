import math, random
from PIL import Image, ImageDraw, ImageFilter
W,H=1800,3680; SS=2
DO=(46,58,28); OL=(91,107,46); PG=(203,214,150); PU=(107,76,122); PU2=(150,112,190); BL=(55,128,184); BL2=(110,160,210); NAVY=(28,46,70); CR=(244,241,234)
LOGO_CR='/home/claude/merch/logos/SFW-logo-flower-cream.png'
def canvas(bg): return Image.new('RGBA',(W*SS,H*SS),bg+(255,))
def finish(im): return im.resize((W,H),Image.LANCZOS)
def grow(im,origins,col,steps=700,branch=0.012,maxtips=160,life=(150,330),w0=5.0,jit=0.2,seed=1,avoid=None,spore=None,sporep=0.0015,decay=0.995,minw=1.0):
    random.seed(seed); d=ImageDraw.Draw(im); S=SS
    tips=[[x*S,y*S,a,w0*S,0,random.randint(*life)] for (x,y,a) in origins]
    for _ in range(steps):
        new=[]
        for t in tips:
            x,y,a,w,age,lf=t
            a+=random.gauss(0,jit); L=random.uniform(5,9)*S
            nx,ny=x+L*math.cos(a),y+L*math.sin(a)
            if avoid and avoid(nx/S,ny/S): t[4]=10**6; continue
            d.line([(x,y),(nx,ny)],fill=col+(255,),width=max(S,int(round(w))))
            t[0],t[1],t[2]=nx,ny,a; t[3]=max(minw*S,w*decay); t[4]+=1
            if random.random()<branch and len(tips)+len(new)<maxtips:
                new.append([nx,ny,a+random.choice([-1,1])*random.uniform(0.5,1.1),t[3]*0.75,0,random.randint(*life)])
            if spore and random.random()<sporep:
                r=random.uniform(6,12)*S; d.ellipse([nx-r,ny-r,nx+r,ny+r],fill=spore+(255,))
        tips=[t for t in tips if t[4]<t[5] and -200*S<t[0]<(W+200)*S and -200*S<t[1]<(H+200)*S]+new
        if not tips: break
def plate(i,col,size):
    p=Image.open(f'/home/claude/merch/micro/plate_{i}.png').convert('RGBA').resize((size*SS,size*SS),Image.LANCZOS)
    o=Image.new('RGBA',p.size,col+(255,)); o.putalpha(p.split()[3]); return o
def logo(im,size,x,y,path=LOGO_CR):
    lg=Image.open(path).convert('RGBA'); lg=lg.resize((size*SS,round(size*SS*lg.height/lg.width)),Image.LANCZOS); im.alpha_composite(lg,(x*SS,y*SS))
def ring(im,cx,cy,r,col,w=6):
    d=ImageDraw.Draw(im); S=SS; d.ellipse([(cx-r)*S,(cy-r)*S,(cx+r)*S,(cy+r)*S],outline=col+(255,),width=w*S)
CAM=(460,460)  # bump centre in artwork coords
out={}
# 1 hero specimen bleeding off, hyphae growing out
im=canvas(DO); cx,cy,R=1250,2450,1050
pl=plate(9,PG,2*R); im.alpha_composite(pl,((cx-R)*SS,(cy-R)*SS))
org=[]
for k in range(14):
    a=random.Random(k).uniform(math.pi*0.75,math.pi*1.6); org.append((cx+R*math.cos(a),cy+R*math.sin(a),a+random.Random(k+50).gauss(0,0.2)))
grow(im,org,PG,steps=500,branch=0.015,maxtips=90,life=(180,380),w0=6,seed=3,decay=0.997,minw=2,avoid=lambda x,y:(x-cx)**2+(y-cy)**2<(R-10)**2,spore=PU2,sporep=0.002)
logo(im,300,1360,170); out['1-hero-specimen']=finish(im)
# 2 two-tone olive fine hyphae
im=canvas(OL); rr=random.Random(7)
org=[(rr.uniform(0,W),rr.uniform(0,H),rr.uniform(0,6.28)) for _ in range(20)]
grow(im,org,DO,steps=650,branch=0.012,maxtips=120,life=(180,360),w0=6,jit=0.2,seed=7,decay=0.997,minw=2.2,spore=PU,sporep=0.0012)
logo(im,300,750,3200); out['2-two-tone-olive']=finish(im)
# 3 purple with single pale-green specimen
im=canvas(PU); cx,cy,R=900,1950,620
im.alpha_composite(plate(0,PG,2*R),((cx-R)*SS,(cy-R)*SS)); ring(im,cx,cy,R+60,PG,4); ring(im,cx,cy,R+80,PG,2)
logo(im,300,750,3200); out['3-purple-specimen']=finish(im)
# 4 blue night
im=canvas(NAVY); rr=random.Random(12)
org=[(rr.uniform(0,W),rr.uniform(0,H),rr.uniform(0,6.28)) for _ in range(10)]
grow(im,org,BL2,steps=650,branch=0.012,maxtips=150,life=(180,360),w0=5,seed=12,decay=0.997,minw=1.8,spore=PG,sporep=0.0018)
logo(im,300,750,3200); out['4-blue-night']=finish(im)
# 5 lens: camera inside field-of-view ring
im=canvas(DO); cx,cy=CAM; R=720
im.alpha_composite(plate(7,PG,2*R),((cx-R)*SS,(cy-R)*SS))
d=ImageDraw.Draw(im)
# punch bump area handled in mockup; ticks around ring
for k in range(72):
    a=k*2*math.pi/72; r1=R+40; r2=R+(80 if k%6==0 else 60)
    d.line([((cx+r1*math.cos(a))*SS,(cy+r1*math.sin(a))*SS),((cx+r2*math.cos(a))*SS,(cy+r2*math.sin(a))*SS)],fill=PG+(255,),width=7*SS)
ring(im,cx,cy,R+20,PG,8)
org=[(cx+(R+90)*math.cos(a),cy+(R+90)*math.sin(a),a) for a in [0.35,0.7,1.0,1.3,1.55,1.85]]
grow(im,org,PG,steps=600,branch=0.012,maxtips=70,life=(220,420),w0=6,seed=21,decay=0.997,minw=2,avoid=lambda x,y:(x-cx)**2+(y-cy)**2<(R+85)**2,spore=PU2,sporep=0.002)
logo(im,300,750,3200); out['5-lens']=finish(im)
# 6 minimal few hyphae
im=canvas(DO)
org=[(-50,900,0.15),(1850,1700,3.0),(-50,2600,-0.1)]
grow(im,org,PG,steps=900,branch=0.006,maxtips=12,life=(500,800),w0=7,jit=0.12,seed=33,decay=0.999,minw=3.5,avoid=lambda x,y:700<x<1100 and 3180<y<3580)
logo(im,240,780,3260); out['6-minimal']=finish(im)
for k,v in out.items(): v.save(f'SFW-case-{k}.png')
# mockups
def mock(art):
    w,h=900,1840; a=art.resize((w,h),Image.LANCZOS)
    m=Image.new('L',(w,h),0); ImageDraw.Draw(m).rounded_rectangle((0,0,w-1,h-1),150,fill=255)
    p=Image.new('RGBA',(w,h),(0,0,0,0)); p.paste(a,(0,0),m); d=ImageDraw.Draw(p)
    d.rounded_rectangle((60,60,400,400),95,fill=(18,22,14,255))
    for qx,qy in [(150,150),(150,310),(310,230)]: d.ellipse((qx-62,qy-62,qx+62,qy+62),fill=(8,10,8,255),outline=(70,80,60,255),width=8)
    sh=Image.new('RGBA',(w+60,h+60),(0,0,0,0)); s=Image.new('RGBA',(w,h),(0,0,0,90)); sh.paste(s,(18,24),m); sh=sh.filter(ImageFilter.GaussianBlur(20)); sh.alpha_composite(p,(0,0)); return sh
ms=[mock(v) for v in out.values()]
sheet=Image.new('RGB',(6*1000+80,2040),(226,222,214)); x=50
for mm in ms: sheet.paste(mm,(x,80),mm); x+=1000
sheet.save('SFW-phone-cases-v2-preview.png'); sheet.resize((sheet.width//4,sheet.height//4)).save('/tmp/v2.png')
