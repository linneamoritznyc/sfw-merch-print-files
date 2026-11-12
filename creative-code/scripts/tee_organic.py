exec(open('tee_patch.py').read().split("rows=[")[0])
from scipy.ndimage import gaussian_filter
def organic(seed,n=14,warp=90):
    r=random.Random(seed); g=np.random.default_rng(seed)
    yy,xx=np.mgrid[0:H_,0:WW].astype(float)
    wx=gaussian_filter(g.normal(0,1,(H_,WW)),60); wy=gaussian_filter(g.normal(0,1,(H_,WW)),60)
    wx*=warp/wx.std(); wy*=warp/wy.std(); X=xx+wx; Y=yy+wy
    pts=[(r.uniform(0,WW),r.uniform(0,H_)) for _ in range(n)]
    reg=np.stack([(X-x)**2+(Y-y)**2 for x,y in pts]).argmin(0)
    L=np.zeros((H_,WW),int); order=list(range(16)); r.shuffle(order); inv=[r.random()<0.5 for _ in range(n)]
    # balance invert so neighbours differ: sort by x
    for k,(px,py) in enumerate(pts):
        m=reg==k; ys,xs=np.nonzero(m); y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
        h,w=y1-y0,x1-x0; s=int(max(h,w)*1.25)+10
        A=scan(order[k%16],s,r.choice([0,90,180,270])); oy=(s-h)//2; ox=(s-w)//2; A=A[oy:oy+h,ox:ox+w]
        t=np.where(A>0.42,0 if inv[k] else 1,1 if inv[k] else 0)
        sub=L[y0:y1,x0:x1]; mm=m[y0:y1,x0:x1]; sub[mm]=t[mm]
    return L
rows=[front_back(jq_wide(organic(s,n),[P_BG,P_INK],3,4),t) for s,n,t in [(1,12,P_BG),(2,16,P_INK),(3,9,P_BG),(4,20,P_BG)]]
S=Image.new('RGB',(2*(WW+40)+20,2*(H_+20)+20),(226,222,214))
for i,r_ in enumerate(rows): S.paste(r_,(20+(i%2)*(WW+40),20+(i//2)*(H_+20)))
S.save('SFW-aop-tees-organic.jpg',quality=88)
