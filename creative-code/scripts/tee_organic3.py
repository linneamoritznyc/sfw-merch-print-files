exec(open("tee_organic.py").read().split("rows=[front_back(jq_wide(organic")[0])
def jq_fine(L,cols,cw=3,ch=4,K=2):
    # render at K x the garment resolution, so stitches are cw/K garment pixels
    Hh,Ww=H_*K,WW*K; Lb=np.kron(L,np.ones((K,K),int)); im=Image.new('RGB',(Ww,Hh),cols[0]); d=ImageDraw.Draw(im)
    for y in range(0,Hh,ch):
        for x in range(0,Ww,cw):
            col=cols[Lb[min(Hh-1,y+ch//2),min(Ww-1,x+cw//2)]]
            d.polygon([(x,y),(x+cw/2,y+ch*0.2),(x+cw/2,y+ch),(x,y+ch*0.8)],fill=col)
            d.polygon([(x+cw/2,y+ch*0.2),(x+cw,y),(x+cw,y+ch*0.8),(x+cw/2,y+ch)],fill=tuple(int(c*0.86) for c in col))
    return im
def front_back_big(art,trim,K=2):
    a=art.resize((WW,H_),Image.LANCZOS); return front_back(a,trim),art
outs=[]
for s,n,t in [(1,60,P_BG),(4,110,P_BG)]:
    big=jq_fine(organic(s,n,35),[P_BG,P_INK]); outs.append((front_back(big.resize((WW,H_),Image.LANCZOS),t),big))
S=Image.new('RGB',(2*(WW+40)+20,H_+40),(226,222,214))
for i,(r_,b) in enumerate(outs): S.paste(r_,(20+i*(WW+40),20))
S.save('SFW-aop-tees-organic-small.jpg',quality=90)
outs[0][1].crop((500,500,1300,1300)).save('SFW-aop-tee-small-closeup.png')
