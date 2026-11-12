exec(open('tee_collage.py').read().split("def overlap(")[0])
import random
WW=W_*2
def big_collage(seed,n=6):
    r=random.Random(seed); L=np.zeros((H_,WW),int); order=list(range(16)); r.shuffle(order)
    xs=np.linspace(-150,WW-450,n)
    for k in range(n):
        s=r.randint(1100,1500); cx=int(xs[k])+r.randint(-80,80); cy=r.randint(250,750)
        p=plate(order[k]).rotate(r.choice([0,90,180,270])).resize((s,s),Image.LANCZOS).filter(ImageFilter.GaussianBlur(4))
        c=Image.new('L',(WW,H_),0); c.paste(p,(cx-s//2+400,cy-s//2)); A=np.asarray(c).astype(float)/255
        L[A>0.4]=1+k%3
    return L
def jq_wide(L,cols,cw=7,ch=9):
    im=Image.new('RGB',(WW*2,H_*2),cols[0]); d=ImageDraw.Draw(im)
    for y in range(0,H_,ch):
        for x in range(0,WW,cw):
            col=cols[L[min(H_-1,y+ch//2),min(WW-1,x+cw//2)]]; X,Y=x*2,y*2
            d.polygon([(X,Y),(X+cw,Y+ch*0.4),(X+cw,Y+ch*2),(X,Y+ch*1.6)],fill=col)
            d.polygon([(X+cw,Y+ch*0.4),(X+cw*2,Y),(X+cw*2,Y+ch*1.6),(X+cw,Y+ch*2)],fill=tuple(int(c*0.88) for c in col))
    return im.resize((WW,H_),Image.LANCZOS)
def front_back(art,trim):
    f=garment(art.crop((0,0,W_,H_)),tee_mask(),'tee',trim)
    bm=tee_mask(); ImageDraw.Draw(bm).chord([380,0,520,110],0,180,fill=0)
    b=Image.new('RGB',(W_,H_),(236,233,227)); b.paste(art.crop((W_,0,WW,H_)),(0,0),bm)
    ImageDraw.Draw(b).arc([380,-30,520,60],0,180,fill=trim,width=10)
    s=Image.new('RGB',(WW+20,H_),(236,233,227)); s.paste(f,(0,0)); s.paste(b,(W_+20,0)); return s
P_BG=(100,85,104); P_INK=(176,176,146)
sets=[(1,[P_BG,P_INK,P_INK,P_INK],P_BG),(2,[P_BG,P_INK,P_INK,P_INK],P_BG),(3,[P_INK,P_BG,P_BG,P_BG],P_BG),(5,[P_BG,P_INK,P_INK,P_INK],P_INK)]
rows=[front_back(jq_wide(big_collage(s),c),t) for s,c,t in sets]
S=Image.new('RGB',(2*(WW+40)+20,2*(H_+20)+20),(226,222,214))
for i,r_ in enumerate(rows): S.paste(r_,(20+(i%2)*(WW+40),20+(i//2)*(H_+20)))
S.save('SFW-aop-tees-wrap-jacquard.jpg',quality=88)
