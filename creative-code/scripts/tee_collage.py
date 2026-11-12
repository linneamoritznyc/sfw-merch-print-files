exec(open('tee_jq.py').read().split("P1=field_passion")[0])
import random
from scipy.ndimage import gaussian_filter
def jqmulti(L,cols,cw=6,ch=8):
    im=Image.new('RGB',(W_*2,H_*2),cols[0]); d=ImageDraw.Draw(im)
    for y in range(0,H_,ch):
        for x in range(0,W_,cw):
            col=cols[L[min(H_-1,y+ch//2),min(W_-1,x+cw//2)]]; X,Y=x*2,y*2
            d.polygon([(X,Y),(X+cw,Y+ch*0.4),(X+cw,Y+ch*2),(X,Y+ch*1.6)],fill=col)
            d.polygon([(X+cw,Y+ch*0.4),(X+cw*2,Y),(X+cw*2,Y+ch*1.6),(X+cw,Y+ch*2)],fill=tuple(int(c*0.88) for c in col))
    return im.resize((W_,H_),Image.LANCZOS)
def overlap(seed,n=5):
    r=random.Random(seed); L=np.zeros((H_,W_),int); order=list(range(16)); r.shuffle(order); k=0
    for gy in range(4):
        for gx in range(3):
            s=r.randint(520,760); cx=120+gx*330+r.randint(-60,60); cy=80+gy*280+r.randint(-60,60)
            A=crop_field(order[k%16],s,cx-s//2,cy-s//2,r.choice([0,90,180,270])); L[A>0.42]=1+k%3; k+=1
    return L
def patch(seed,cells=7):
    r=random.Random(seed); pts=[(r.uniform(0,W_),r.uniform(0,H_)) for _ in range(cells)]
    yy,xx=np.mgrid[0:H_,0:W_]; D=np.stack([(xx-x)**2+(yy-y)**2 for x,y in pts]); reg=D.argmin(0)
    L=np.zeros((H_,W_),int)
    for k in range(cells):
        A=crop_field(r.randrange(16),r.randint(900,1400),r.randint(-400,300),r.randint(-300,500),r.choice([0,90,180,270]))
        m=reg==k; L[m]=np.where(A[m]>0.45,2*(k%3)+2,2*(k%3)+1)
    return L
looks=[
 (jqmulti(overlap(7),[SAGE,PUR,FWG,EB]),PUR),
 (jqmulti(overlap(8),[CRM,FWG,PUR,EB]),FWG),
 (jqmulti(overlap(9),[OL,PG,LIL,DG]),OL),
 (jqmulti(overlap(1),[PUR,SAGE,LIL,PG]),PUR),
 (jqmulti(overlap(2),[DG,LIME,LGR,LIL]),DG),
 (jqmulti(overlap(3),[EB,CRM,PG,LIL]),EB),
 (jqmulti(patch(4),[PUR,PUR,SAGE,DG,LIME,EB,CRM]),PUR),
 (jqmulti(patch(5),[DG,OL,PG,PUR,LIL,FWG,LIME]),DG),
 (jqmulti(patch(6),[SAGE,SAGE,PUR,CRM,FWG,LIL,EB]),FWG)]
S=Image.new('RGB',(3*920+20,3*1020+20),(226,222,214))
for i,(a,t) in enumerate(looks): S.paste(garment(a,tee_mask(),'tee',t),(20+(i%3)*920,20+(i//3)*1020))
S=S.crop((0,0,S.width,S.height));S.save('SFW-aop-tees-collage.jpg',quality=90)
