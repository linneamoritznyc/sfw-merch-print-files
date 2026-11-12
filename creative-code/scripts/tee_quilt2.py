exec(open('tee_patch.py').read().split("rows=[")[0])
def quilt(seed,minsz=260):
    r=random.Random(seed); L=np.zeros((H_,WW),int); rects=[]
    def split(x,y,w,h,d):
        if (w<minsz*2 and h<minsz*2) or (d>2 and r.random()<0.35): rects.append((x,y,w,h)); return
        if (w>h and w>=minsz*2) or h<minsz*2:
            c=int(w*r.uniform(0.35,0.65)); split(x,y,c,h,d+1); split(x+c,y,w-c,h,d+1)
        else:
            c=int(h*r.uniform(0.35,0.65)); split(x,y,w,c,d+1); split(x,y+c,w,h-c,d+1)
    split(0,0,WW,H_,0)
    order=list(range(16)); r.shuffle(order)
    for k,(x,y,w,h) in enumerate(rects):
        s=int(max(w,h)*r.uniform(1.15,1.6)); A=scan(order[k%16],s,r.choice([0,90,180,270]))
        ox=r.randint(0,s-w); oy=r.randint(0,s-h); A=A[oy:oy+h,ox:ox+w]
        inv=r.random()<0.5; t=np.where(A>0.42,0 if inv else 1,1 if inv else 0)
        t[:,:7]=0 if not inv else 1; t[:7,:]=t[:,:7][0,0]
        L[y:y+h,x:x+w]=t
    return L
rows=[front_back(jq_wide(quilt(1),[P_BG,P_INK],3,4),P_BG),front_back(jq_wide(quilt(7),[P_BG,P_INK],3,4),P_INK),
      front_back(jq_wide(quilt(11,340),[P_BG,P_INK],3,4),P_BG),front_back(jq_wide(quilt(23),[P_BG,P_INK],3,4),P_BG)]
XX=[front_back(jq_wide(quilt(1),[P_BG,P_INK]),P_BG),front_back(jq_wide(quilt(7),[P_BG,P_INK]),P_INK),
      front_back(jq_wide(quilt(11,340),[P_BG,P_INK]),P_BG),front_back(jq_wide(patchwork(1,470,'square'),[P_BG,P_INK]),P_BG)]
S=Image.new('RGB',(2*(WW+40)+20,2*(H_+20)+20),(226,222,214))
for i,r_ in enumerate(rows): S.paste(r_,(20+(i%2)*(WW+40),20+(i//2)*(H_+20)))
S.save('SFW-aop-tees-quilt-fine.jpg',quality=88)
