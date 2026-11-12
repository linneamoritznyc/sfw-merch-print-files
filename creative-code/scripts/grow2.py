import math, random, numpy as np
from PIL import Image, ImageDraw
def grow(S=3000,R=1330,seed=3,G=(12,52,24),INK=(196,232,206),TRUNK=(160,214,180),cell=7,pb=0.06):
    rnd=random.Random(seed); SS=2; W=S*SS; c=W/2; Rp=R*SS
    im=Image.new('RGBA',(W,W),(0,0,0,0)); d=ImageDraw.Draw(im); d.ellipse([0,0,W-1,W-1],fill=G+(255,))
    gs=int(W/(cell*SS))+2; occ=np.full((gs,gs),-1,np.int32)
    tips=[]; q=[]; bid=0
    for k in range(9):
        a=k/9*2*math.pi+rnd.uniform(-.15,.15); q.append((c,c,a,12*SS,bid)); bid+=1
    import collections; q=collections.deque(q)
    while q:
        # breadth-ish growth: process one walker fully, but shuffle queue order for evenness
        x,y,a,w,b=q.popleft()
        lim=Rp*rnd.uniform(0.975,1.0); steps=0
        while True:
            out=math.atan2(y-c,x-c); da=(out-a+math.pi)%(2*math.pi)-math.pi
            a+=da*0.06+rnd.gauss(0,0.2)
            step=8*SS; nx=x+math.cos(a)*step; ny=y+math.sin(a)*step
            r=math.hypot(nx-c,ny-c)
            if r>lim: tips.append((x,y)); break
            gx,gy=int(nx/(cell*SS)),int(ny/(cell*SS))
            o=occ[gy,gx]
            if o!=-1 and o!=b and steps>3 and r>Rp*0.12: tips.append((x,y,1)); break
            occ[gy,gx]=b
            t=min(1,r/Rp); col=tuple(int(TRUNK[i]*(1-t)+INK[i]*t) for i in range(3))
            d.line([(x,y),(nx,ny)],fill=col+(240,),width=max(1,round(w)))
            x,y=nx,ny; steps+=1; w=max(1.5*SS,w*0.994)
            if rnd.random()<pb and bid<200000:
                q.append((x,y,a+rnd.choice([-1,1])*rnd.uniform(0.4,1.0),max(1.5*SS,w*0.7),bid)); bid+=1; w*=0.9
    for t in tips:
        x,y=t[0],t[1]
        if len(t)==2 or rnd.random()<0.08:
            s=rnd.uniform(3,4.5)*SS; d.ellipse([x-s,y-s,x+s,y+s],fill=INK+(255,))
    return im.resize((S,S),Image.LANCZOS)
if __name__=='__main__':
    import sys
    im=grow(seed=int(sys.argv[1]) if len(sys.argv)>1 else 3); im.save('SFW-myc-sticker-v6.png')
    p=Image.new('RGB',(620,620),(230,228,222)); t=im.copy(); t.thumbnail((600,600)); p.paste(t,(10,10),t); p.save('SFW-myc-sticker-v6-preview.jpg')
