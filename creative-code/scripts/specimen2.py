exec(open('specimen.py').read().split("fs=sorted")[0])
fs=sorted(glob.glob('/home/claude/merch/micro/*.jpg')); pick=[f for f in fs if parse(f)[2]]
order=[3,1,11,5,14,9,0,12,7,15,10,2]; pick=[pick[i] for i in order]
def poster(bg,ink,muted,name):
    W,H=4961,7016; P=Image.new('RGBA',(W,H),bg+(255,)); d=ImageDraw.Draw(P); m=420
    d.text((m,m),'THE LIFE IN THE SOIL',font=F('ebg500.ttf',150),fill=ink)
    d.text((m,m+200),'Twelve organisms, photographed by Soil Food Web students',font=F('ebg400.ttf',110),fill=muted)
    cols,rows=3,4; D=1060; gx=(W-2*m)/cols; y0=1050; gy=1170
    for i,f in enumerate(pick):
        c,r=i%cols,i//cols; cx=m+gx*(c+.5); cy=y0+r*gy+D/2
        P.alpha_composite(disc(f,D),(int(cx-D/2),int(cy-D/2)))
        d.text((int(cx-D/2)+10,int(cy+D/2)-40),f'{i+1:02d}',font=F('ebg600.ttf',95),fill=ink)
    # legend
    ly=y0+rows*gy+40; fl=F('ebg400.ttf',66); fb=F('ebg600.ttf',66)
    for i,f in enumerate(pick):
        n,_,who=parse(f); c,r=i//4,i%4; x=m+c*((W-2*m)/3); y=ly+r*170
        d.text((x,y),f'{i+1:02d}',font=fb,fill=ink); d.text((x+120,y),n,font=fb,fill=ink)
        d.text((x+120,y+74),who,font=fl,fill=muted)
    lg=Image.open('/home/claude/merch/logos/'+('SFW-logo-flower-white-3000.png' if bg[0]<100 else 'SFW-logo-flower-colour.png')).convert('RGBA').resize((560,560),Image.LANCZOS)
    P.alpha_composite(lg,(W-m-560,m-120)); P.convert('RGB').save(f'SFW-poster-A2-specimens-{name}.png'); return P
a=poster((244,241,234),(79,52,51),(140,120,115),'cream')
b=poster((24,46,30),(244,241,234),(176,190,170),'green')
pv=Image.new('RGB',(2040,1460),(226,222,214))
for i,p in enumerate([a,b]): t=p.convert('RGB'); t.thumbnail((1000,1420)); pv.paste(t,(10+i*1020,20))
pv.save('SFW-specimens-v2-preview.jpg',quality=88)
