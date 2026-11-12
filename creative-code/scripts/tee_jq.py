exec(open('aop3.py').read().split("OL=hx('5B6B2E')")[0])
OL=hx('5B6B2E'); PG=hx('CBD696'); PUR=hx('6B4C7A'); LIL=hx('C8B6E2'); DG=hx('22371F'); FWG=hx('156826'); EB=hx('3780B8'); LGR=hx('59A66C'); CRM=hx('F4F1EA'); SAGE=hx('A8B49A'); LIME=(190,214,90)
def jq2(A,bg,ink,cw=6,ch=8):
    im=Image.new('RGB',(W_*2,H_*2),bg); d=ImageDraw.Draw(im)
    for y in range(0,H_,ch):
        for x in range(0,W_,cw):
            v=A[min(H_-1,y+ch//2),min(W_-1,x+cw//2)]
            col=ink if v>0.45 else bg
            X,Y=x*2,y*2
            d.polygon([(X,Y),(X+cw,Y+ch*0.4),(X+cw,Y+ch*2),(X,Y+ch*1.6)],fill=col)
            d.polygon([(X+cw,Y+ch*0.4),(X+cw*2,Y),(X+cw*2,Y+ch*1.6),(X+cw,Y+ch*2)],fill=tuple(int(c*0.88) for c in col))
    return im.resize((W_,H_),Image.LANCZOS)
P1=field_passion(3.0,-480,-200,0); P2=field_passion(4.0,-900,-150,25); P3=field_passion(2.4,-300,0,-15)
looks=[(jq2(P1,PUR,SAGE),PUR),(jq2(P2,DG,LIME),DG),(jq2(P3,EB,CRM),EB),(jq2(P1,SAGE,PUR),SAGE),(jq2(P2,CRM,FWG),FWG),(jq2(P3,PUR,LIL),PUR)]
S=Image.new('RGB',(3*920+20,2*1020+20),(226,222,214))
for i,(a,t) in enumerate(looks): S.paste(garment(a,tee_mask(),'tee',t),(20+(i%3)*920,20+(i//3)*1020))
S.save('SFW-aop-tees-jacquard.jpg',quality=90)
