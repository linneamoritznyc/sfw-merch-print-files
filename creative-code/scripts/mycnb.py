import math, random
from PIL import Image, ImageDraw
def net(W,H,seed,bg,line,spore,origins,steps=900,w0=14,maxtips=55,branch=0.009,SS=2):
    r=random.Random(seed); im=Image.new('RGB',(W*SS,H*SS),bg); d=ImageDraw.Draw(im)
    tips=[]
    for (x,y,n) in origins:
        for k in range(n): tips.append([x*W,y*H,r.uniform(0,6.283),w0,0,r.randint(260,520)])
    sp=[]
    for it in range(steps):
        new=[]
        for t in tips:
            x,y,a,w,age,life=t
            a+=r.gauss(0,0.07); L=r.uniform(5,8)
            nx,ny=x+L*math.cos(a),y+L*math.sin(a)
            d.line([(x*SS,y*SS),(nx*SS,ny*SS)],fill=line,width=max(1,int(w*SS)))
            q=w*SS/2; d.ellipse([nx*SS-q,ny*SS-q,nx*SS+q,ny*SS+q],fill=line)
            t[0],t[1],t[2]=nx,ny,a; t[3]=max(1.5,w*0.998); t[4]+=1
            if r.random()<branch and len(tips)+len(new)<maxtips: new.append([nx,ny,a+r.choice([-1,1])*r.uniform(0.5,1.1),t[3]*0.7,0,r.randint(160,420)])
            if r.random()<0.004 and t[3]<4: sp.append((nx,ny))
        tips=[t for t in tips if t[4]<t[5] and -50<t[0]<W+50 and -50<t[1]<H+50]+new
        if not tips: break
    for (x,y) in sp:
        q=r.uniform(6,12)*SS; d.ellipse([x*SS-q,y*SS-q,x*SS+q,y*SS+q],fill=spore)
    return im.resize((W,H),Image.LANCZOS)
def hx(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
W,H=1800,3000
V=[('deepgreen',hx('22371F'),hx('CBD696'),hx('C8B6E2'),[(0.3,0.78,4)]),
   ('purple',hx('6B4C7A'),hx('C8B6E2'),hx('CBD696'),[(0.5,0.45,5)]),
   ('navy',hx('1A2C52'),hx('BED65A'),hx('96C4E8'),[(0.2,0.2,3),(0.8,0.85,3)]),
   ('cream',hx('F4F1EA'),hx('156826'),hx('6B4C7A'),[(0.5,0.92,5)])]
S=Image.new('RGB',(4*380+20,660),(226,222,214))
for i,(n,bg,ln,sp,o) in enumerate(V):
    im=net(W,H,i+3,bg,ln,sp,o); im.resize((900,1500),Image.LANCZOS).save(f'SFW-journalbook-mycelium-{n}.png'); S.paste(im.resize((360,600)),(20+i*380,30))
S.save('SFW-journalbook-mycelium-preview.jpg',quality=90)
