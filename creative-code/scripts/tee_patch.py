exec(open('tee_wrap2.py').read().split("P_BG=")[0])
import random
P_BG=(100,85,104); P_INK=(176,176,146)
def scan(i,s,rot):
    p=plate(i).rotate(rot).resize((s,s),Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.5))
    return np.asarray(p).astype(float)/255
def patchwork(seed,s=470,mode='square'):
    r=random.Random(seed); L=np.zeros((H_,WW),int); order=list(range(16)); r.shuffle(order); k=0
    yy,xx=np.mgrid[0:s,0:s]; circ=((xx-s/2)**2+(yy-s/2)**2)<(s*0.47)**2
    for gy in range(-1,3):
        for gx in range(-1,5):
            ox=gx*s+(s//2 if (mode=='circle' and gy%2) else 0)+60; oy=gy*s+40
            A=scan(order[k%16],int(s/0.93),r.choice([0,90,180,270]))
            c0=(A.shape[0]-s)//2; A=A[c0:c0+s,c0:c0+s]
            inv=(gx+gy)%2==1
            if mode=='square':
                tile=np.where(A>0.42,0 if inv else 1,1 if inv else 0); mask=np.ones((s,s),bool)
            else:
                tile=np.where(A>0.42,1,0); mask=circ
            y0,x0=oy,ox; ys=slice(max(0,y0),min(H_,y0+s)); xs=slice(max(0,x0),min(WW,x0+s))
            ty=slice(ys.start-y0,ys.stop-y0); tx=slice(xs.start-x0,xs.stop-x0)
            if ys.stop>ys.start and xs.stop>xs.start:
                sub=L[ys,xs]; m=mask[ty,tx]; sub[m]=tile[ty,tx][m]; L[ys,xs]=sub
            k+=1
    return L
rows=[front_back(jq_wide(patchwork(1,470,'square'),[P_BG,P_INK]),P_BG),
      front_back(jq_wide(patchwork(2,620,'square'),[P_BG,P_INK]),P_INK),
      front_back(jq_wide(patchwork(3,430,'circle'),[P_BG,P_INK]),P_BG),
      front_back(jq_wide(patchwork(4,560,'circle'),[P_INK,P_BG]),P_BG)]
S=Image.new('RGB',(2*(WW+40)+20,2*(H_+20)+20),(226,222,214))
for i,r_ in enumerate(rows): S.paste(r_,(20+(i%2)*(WW+40),20+(i//2)*(H_+20)))
S.save('SFW-aop-tees-patchwork.jpg',quality=88)
