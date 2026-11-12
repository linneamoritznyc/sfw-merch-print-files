import numpy as np, math, random
from PIL import Image, ImageDraw
def grow(S=3000,R=1330,seed=7,G=(12,52,24),INK=(196,232,206),TRUNK=(160,214,180)):
    rnd=random.Random(seed); SS=2; W=S*SS; c=W/2; Rp=R*SS
    im=Image.new('RGBA',(W,W),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.ellipse([0,0,W-1,W-1],fill=G+(255,))
    tips=[]
    stack=[]
    n0=11
    for k in range(n0):
        a=k/n0*2*math.pi+rnd.uniform(-.2,.2)
        stack.append((c,c,a,14*SS,0))
    segs=0
    while stack:
        x,y,a,w,gen=stack.pop()
        lim=Rp*rnd.uniform(0.93,1.0)
        while True:
            r=math.hypot(x-c,y-c)
            if r>=lim: tips.append((x,y)); break
            # bias outward
            out=math.atan2(y-c,x-c); da=(out-a+math.pi)%(2*math.pi)-math.pi
            a+=da*0.08+rnd.gauss(0,0.22)
            step=9*SS; nx=x+math.cos(a)*step; ny=y+math.sin(a)*step
            if math.hypot(nx-c,ny-c)>lim: tips.append((x,y)); break
            t=min(1,r/Rp); col=tuple(int(TRUNK[i]*(1-t)+INK[i]*t) for i in range(3))
            d.line([(x,y),(nx,ny)],fill=col+(235,),width=max(1,int(w)))
            x,y=nx,ny; w=max(1.6*SS,w*0.993); segs+=1
            pb=0.045 if r>Rp*0.15 else 0.02
            if rnd.random()<pb and segs<400000:
                stack.append((x,y,a+rnd.choice([-1,1])*rnd.uniform(0.35,0.9),w*0.72,gen+1))
                w*=0.85
    for x,y in tips:
        if rnd.random()<0.5: s=rnd.uniform(3,5)*SS; d.ellipse([x-s,y-s,x+s,y+s],fill=INK+(255,))
    return im.resize((S,S),Image.LANCZOS),len(tips)
if __name__=='__main__':
    im,n=grow(); print(n); im.save('SFW-myc-sticker-v6.png')
    p=Image.new('RGB',(620,620),(230,228,222)); t=im.copy(); t.thumbnail((600,600)); p.paste(t,(10,10),t); p.save('SFW-myc-sticker-v6-preview.jpg')
