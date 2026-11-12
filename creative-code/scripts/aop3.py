import math, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
exec(open('aop2.py').read().split("OL=hx(")[0])
def field_passion(scale=2.4,ox=-500,oy=-300,rot=0):
    s=Image.open('passion/src.png').convert('L').rotate(rot); s=s.resize((int(s.width*scale),int(s.height*scale)),Image.LANCZOS)
    c=Image.new('L',(W_,H_),0); c.paste(s,(ox,oy)); a=np.asarray(c.filter(ImageFilter.GaussianBlur(2))).astype(float)/255
    return np.clip((a-0.2)/0.55,0,1)
def jacquard(A,bg,c1,c2,cw=8,ch=10):
    im=Image.new('RGB',(W_*2,H_*2),bg); d=ImageDraw.Draw(im)
    for y in range(0,H_,ch):
        for x in range(0,W_,cw):
            v=A[min(H_-1,y+ch//2),min(W_-1,x+cw//2)]
            col=bg if v<0.33 else (c1 if v<0.66 else c2)
            # V stitch
            X,Y=x*2,y*2
            d.polygon([(X,Y),(X+cw,Y+ch*0.4),(X+cw,Y+ch*2),(X,Y+ch*1.6)],fill=col)
            d.polygon([(X+cw,Y+ch*0.4),(X+cw*2,Y),(X+cw*2,Y+ch*1.6),(X+cw,Y+ch*2)],fill=tuple(int(c*0.9) for c in col))
    return im.resize((W_,H_),Image.LANCZOS)
def linetone(A,bg,ink,gap=7):
    im=Image.new('RGB',(W_*2,H_*2),bg); d=ImageDraw.Draw(im)
    for y in range(0,H_,gap):
        for x in range(0,W_,2):
            v=A[y,x]; t=gap*0.9*v
            if t>0.6: d.rectangle([x*2,(y-t/2)*2,(x+2)*2,(y+t/2)*2],fill=ink)
    return im.resize((W_,H_),Image.LANCZOS)
def rug(A,bg,c1,c2,n=60000,seed=1):
    r=random.Random(seed); im=Image.new('RGB',(W_*2,H_*2),bg); d=ImageDraw.Draw(im)
    for k in range(n):
        x,y=r.uniform(0,W_),r.uniform(0,H_); v=A[int(y),int(x)]
        col=c1 if v<0.5 else c2
        if v<0.15 and r.random()<0.6: col=tuple(int(c*0.85) for c in bg)
        a=r.uniform(0,6.28); L=r.uniform(4,9)
        d.arc([(x-L)*2,(y-L)*2,(x+L)*2,(y+L)*2],a*57,a*57+r.uniform(120,240),fill=col,width=5)
    return im.resize((W_,H_),Image.LANCZOS)
def bomber_mask():
    m=Image.new('L',(W_,H_),0); d=ImageDraw.Draw(m)
    d.polygon([(270,60),(380,40),(520,40),(630,60),(850,280),(860,800),(770,800),(700,420),(705,920),(195,920),(200,420),(130,800),(40,800),(50,280)],fill=255)
    return m.filter(ImageFilter.GaussianBlur(1.2))
def bomber(art,trim):
    m=bomber_mask(); bg=Image.new('RGB',(W_,H_),(236,233,227)); bg.paste(art,(0,0),m); d=ImageDraw.Draw(bg)
    for (box) in [[360,22,540,70],[195,900,705,960],[40,790,130,840],[770,790,860,840]]:
        d.rounded_rectangle(box,8,fill=trim)
        for x in range(box[0]+6,box[2],10): d.line([(x,box[1]+4),(x,box[3]-4)],fill=tuple(int(c*0.8) for c in trim),width=3)
    d.line([(450,70),(450,900)],fill=(210,205,195),width=6); return bg
OL=hx('5B6B2E'); PG=hx('CBD696'); PUR=hx('6B4C7A'); LIL=hx('C8B6E2'); DG=hx('22371F'); FWG=hx('156826'); EB=hx('3780B8'); LGR=hx('59A66C'); CRM=hx('F4F1EA'); SAGE=hx('A8B49A'); TAN=hx('C89B7B'); BR=hx('4F3433'); LIME=(190,214,90)
P=field_passion(); M1=crop_field(14,2200,-600,-500,90); M2=crop_field(4,2000,-550,-400); H1=hypha_field(3,[(-80,520,-0.35),(980,120,2.5)],140)
looks=[bomber(jacquard(M1,PUR,LIL,PG),DG), bomber(linetone(P,SAGE,FWG),FWG), bomber(rug(M2,TAN,PUR,LIL),PUR),
       garment(jacquard(H1,DG,LGR,LIME),jacket_mask(),'jacket',PUR), garment(linetone(M2,CRM,EB),jacket_mask(),'jacket',EB), bomber(rug(P,DG,LGR,LIL,seed=2),LGR)]
S=Image.new('RGB',(3*920+20,2*1020+20),(226,222,214))
for i,g in enumerate(looks): S.paste(g,(20+(i%3)*920,20+(i//3)*1020))
S.save('SFW-aop-jackets-textile.jpg',quality=90)
