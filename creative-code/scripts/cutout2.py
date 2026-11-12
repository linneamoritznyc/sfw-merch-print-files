import math, random, numpy as np
from PIL import Image, ImageDraw
exec(open('cutout.py').read().split("def compose(")[0])
def T(cx,cy,rot): ca,sa=math.cos(rot),math.sin(rot); return lambda x,y:(cx+x*ca-y*sa,cy+x*sa+y*ca)
def leaf(d,cx,cy,L,rot,col,vein,shape='ovate',stem=True):
    P=T(cx,cy,rot); W=L*{'ovate':0.32,'lance':0.16,'round':0.45}[shape]
    def half(t): # t 0..1 along blade
        if shape=='ovate': return W*math.sin(math.pi*t)**0.8*(1.15-0.3*t)
        if shape=='lance': return W*math.sin(math.pi*t)**1.1
        return W*math.sin(math.pi*t)**0.6
    ts=np.linspace(0,1,120)
    up=[P(t*L,half(t)) for t in ts]; dn=[P(t*L,-half(t)) for t in ts[::-1]]
    d.polygon(up+dn,fill=col)
    if stem: d.line([P(-L*0.18,0),P(0,0)],fill=col,width=max(4,int(L*0.03)))
    d.line([P(0,0),P(L*0.95,0)],fill=vein,width=max(3,int(L*0.018)))
    n=7 if shape!='lance' else 9
    for k in range(1,n):
        t=k/n; x0=t*L
        for s in (1,-1): d.line([P(x0,0),P(x0+L*0.12,s*half(min(1,t+0.12))*0.85)],fill=vein,width=max(2,int(L*0.01)))
def flagellate(d,cx,cy,L,rot,col,inner):
    P=T(cx,cy,rot)
    d.polygon([P(L*0.5*math.cos(t), L*0.2*math.sin(t)*(1-0.5*math.cos(t))) for t in np.linspace(0,6.283,200)],fill=col)
    pts=[];ws=[]
    for i in range(160):
        t=i/159; x=L*0.5+t*L*1.3; y=L*0.09*math.sin(t*2*math.pi*2.2)
        pts.append(P(x,y)); ws.append(max(2,L*0.03*(1-t*0.7)))
    stroke(d,pts,ws,col)
    x,y=P(-L*0.05,0); r=L*0.08; d.ellipse([x-r,y-r,x+r,y+r],fill=inner)
def amoeba(d,cx,cy,R,seed,col,inner):
    blob(d,cx,cy,R,seed,7,0.7,0.85,col)
    r=R*0.25; d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=inner)
    rr=random.Random(seed)
    for k in range(4):
        a=rr.uniform(0,6.28); q=R*0.11; x,y=cx+R*0.55*math.cos(a),cy+R*0.45*math.sin(a); d.ellipse([x-q,y-q,x+q,y+q],fill=inner)
def paramecium(d,cx,cy,L,rot,col,inner):
    P=T(cx,cy,rot); body=[]
    for t in np.linspace(0,6.283,240):
        x=L*0.5*math.cos(t); y=L*0.18*math.sin(t)*(1+0.25*math.cos(t))
        if 0.6<t<1.6: y*=0.75
        body.append((x,y))
    for t in np.linspace(0,6.283,110):
        x=L*0.5*math.cos(t); y=L*0.18*math.sin(t)*(1+0.25*math.cos(t))
        d.line([P(x,y),P(x*1.08,y*1.25)],fill=col,width=max(2,int(L*0.008)))
    d.polygon([P(x,y) for x,y in body],fill=col)
    for x in (-0.15,0.2): xx,yy=P(L*x,0); q=L*0.06; d.ellipse([xx-q,yy-q,xx+q,yy+q],fill=inner)
def vorticella(d,cx,cy,H,rot,col):
    P=T(cx,cy,rot)
    bell=[P(-H*0.18*math.sin(t*math.pi)*(1+0.6*t), -H*0.35*t) for t in np.linspace(0,1,60)]
    bell2=[P(H*0.18*math.sin(t*math.pi)*(1+0.6*t), -H*0.35*t) for t in np.linspace(1,0,60)]
    top=[P(-H*0.0,-H*0.35)]
    d.polygon(bell+bell2,fill=col)
    d.polygon([P(H*0.2*math.cos(t),-H*0.35+H*0.05*math.sin(t)) for t in np.linspace(0,6.283,60)],fill=col)
    pts=[P(H*0.04*math.sin(t*30),t*H*0.65) for t in np.linspace(0,1,200)]
    stroke(d,pts,[max(3,H*0.025)]*200,col)
def testate(d,cx,cy,R,col,inner):
    d.ellipse([cx-R,cy-R*0.9,cx+R,cy+R*0.9],fill=col); r=R*0.35; d.ellipse([cx-r,cy-r*0.8,cx+r,cy+r*0.8],fill=inner)
    r2=R*0.12; d.ellipse([cx-r2,cy-r2,cx+r2,cy+r2],fill=col)
def compose(W,H,seed,bg,P,name):
    r=random.Random(seed); im=Image.new('RGB',(W,H),C[bg]); d=ImageDraw.Draw(im); S=W/2400
    blob(d,W*0.16,H*0.38,430*S,seed+1,6,0.4,1.1,C[P[0]])
    blob(d,W*0.80,H*0.62,520*S,seed+2,7,0.45,0.9,C[P[1]])
    blob(d,W*0.50,H*0.10,300*S,seed+3,5,0.35,1,C[P[2]])
    rr=random.Random(seed+9)
    hypha(d,-50,H*0.95,-0.55,40*S,C[P[6]],rr,380); hypha(d,W+50,H*0.05,2.6,32*S,C[P[7]],rr,380)
    # leaves cluster bottom center and top left
    for k,(x,y,L,rot,sh,col) in enumerate([(0.56,1.02,520,-1.9,'ovate',P[10]),(0.62,1.02,460,-1.35,'lance',P[3]),(0.50,1.02,420,-2.4,'ovate',P[6]),
                                           (0.05,0.02,380,0.6,'lance',P[10]),(0.10,0.0,320,1.1,'ovate',P[3]),(0.95,0.95,300,-2.6,'round',P[2])]):
        leaf(d,W*x,H*y,L*S,rot,C[col],C[bg] if col!=bg else C[P[1]],sh)
    nematode(d,W*0.38,H*0.55,800*S,-0.2,55*S,C[P[8]])
    paramecium(d,W*0.27,H*0.82,330*S,0.25,C[P[9]],C[P[1]])
    flagellate(d,W*0.70,H*0.28,200*S,2.8,C[P[4]],C[P[2]])
    flagellate(d,W*0.88,H*0.40,140*S,-2.4,C[P[9]],C[P[1]])
    amoeba(d,W*0.30,H*0.22,120*S,seed+30,C[P[5]],C[P[0]])
    vorticella(d,W*0.86,H*0.83,330*S,-0.3,C[P[5]])
    vorticella(d,W*0.92,H*0.80,260*S,0.25,C[P[5]])
    testate(d,W*0.50,H*0.40,70*S,C[P[4]],C[P[2]])
    testate(d,W*0.12,H*0.68,55*S,C[P[9]],C[P[0]])
    for k in range(10):
        x,y=r.uniform(0,W),r.uniform(0,H); q=r.uniform(8,18)*S; d.ellipse([x-q,y-q,x+q,y+q],fill=C[r.choice(P[:6])])
    im.save(name); return im
a=compose(2400,1300,1,'cream',['lblue','purple','pg','fwg','navy','lil','dg','blue','purple','lime','lg'],'SFW-cutout-a.png')
b=compose(2400,1300,2,'navy',['fwg','purple','blue','lime','lil','lg','pg','lblue','lime','lil','lg'],'SFW-cutout-b.png')
c=compose(2400,1300,3,'lil',['blue','fwg','pg','purple','navy','lime','dg','lg','navy','lime','fwg'],'SFW-cutout-c.png')
S=Image.new('RGB',(1240,3*670+20),(226,222,214))
for i,v in enumerate([a,b,c]): S.paste(v.resize((1200,650),Image.LANCZOS),(20,20+i*670))
S.save('SFW-cutout-preview.jpg',quality=90)
