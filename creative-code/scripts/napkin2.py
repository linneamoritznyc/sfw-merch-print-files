import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S=6450
def disc(i,d,ink,bg,rot):
    p=Image.open(f'/home/claude/merch/micro/plate_{i}.png').convert('RGBA').split()[3].rotate(rot)
    p=p.resize((d,d),Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.5)); a=np.asarray(p)>110
    m=Image.new('L',(d,d),0); ImageDraw.Draw(m).ellipse([4,4,d-5,d-5],fill=255); mm=np.asarray(m)>0
    t=np.zeros((d,d,4),np.uint8); t[...,:3]=ink; t[...,3]=((a&mm)*255).astype(np.uint8)
    im=Image.fromarray(t,'RGBA'); ImageDraw.Draw(im).ellipse([4,4,d-5,d-5],outline=ink+(255,),width=10); return im
def make(name,bg,ink):
    im=Image.new('RGBA',(S,S),bg+(255,)); dr=ImageDraw.Draw(im)
    dr.rectangle([380,380,S-381,S-381],outline=ink+(255,),width=16); dr.rectangle([440,440,S-441,S-441],outline=ink+(255,),width=6)
    x0,y0,x1,y1=600,600,S-600,S-900; d=640; g=70
    cols=int((x1-x0+g)//(d+g)); step=d+g; rowh=int(d*0.88)
    rows=int((y1-y0-d)//rowh)+1
    k=0; order=[5,1,10,2,4,11,0,3,15,6,8,12,7,9,13,14]
    for r in range(rows):
        n=cols if r%2==0 else cols-1
        tot=n*d+(n-1)*g; sx=x0+((x1-x0)-tot)//2
        hy=y0+((y1-y0)-((rows-1)*rowh+d))//2+r*rowh
        for c in range(n):
            im.alpha_composite(disc(order[(k*5+r*3)%16],d,ink,bg,(k*90)%360),(sx+c*step,hy)); k+=1
    f=ImageFont.truetype('ebg500.ttf',150); t='SOIL FOOD WEB FOUNDATION'; sp=60
    w=sum(dr.textlength(ch,font=f)+sp for ch in t)-sp; x=(S-w)/2; y=S-760
    for ch in t: dr.text((x,y),ch,font=f,fill=ink+(255,)); x+=dr.textlength(ch,font=f)+sp
    im.convert('RGB').save(f'SFW-napkin-{name}-v3.png')
make('cream',(244,241,234),(21,104,38))
make('green',(34,55,31),(244,241,234))
S2=Image.new('RGB',(1310,660),(230,228,222))
for i,n in enumerate(['cream','green']): t=Image.open(f'SFW-napkin-{n}-v3.png'); t.thumbnail((640,640)); S2.paste(t,(10+i*650,10))
S2.save('SFW-napkins-v3-preview.jpg',quality=88)
