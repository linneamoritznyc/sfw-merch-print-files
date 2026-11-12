import glob, re, math
from PIL import Image, ImageDraw, ImageFont, ImageOps
CR=(244,241,234); INK=(79,52,51); GR=(21,104,38); TICK=(160,150,140)
F=lambda w,s: ImageFont.truetype(w,s)
def parse(f):
    n=f.split('/')[-1][:-4]; n=re.sub(r'\s*\(I\d\)','',n)
    m=re.match(r'(.*?) (\d+)x obj ?(.*)',n); name,mag,who=m.group(1),m.group(2),m.group(3).strip()
    if len(who)<=3: who=''
    return name,mag,who
def disc(f,D):
    im=Image.open(f).convert('RGB'); s=min(im.size); z=int(s*0.82)
    im=im.crop(((im.width-z)//2,(im.height-z)//2,(im.width+z)//2,(im.height+z)//2)).resize((D,D),Image.LANCZOS)
    m=Image.new('L',(D*4,D*4),0); ImageDraw.Draw(m).ellipse([0,0,D*4-1,D*4-1],fill=255); m=m.resize((D,D),Image.LANCZOS)
    o=Image.new('RGBA',(D,D),(0,0,0,0)); o.paste(im,(0,0),m); return o
def specimen(canvas,f,cx,cy,D,label=True,sc=1.0):
    d=ImageDraw.Draw(canvas); R=D/2
    # tick ring
    for k in range(72):
        a=k/72*2*math.pi; r1=R+D*0.06; r2=r1+(D*0.05 if k%6==0 else D*0.03)
        d.line([(cx+r1*math.cos(a),cy+r1*math.sin(a)),(cx+r2*math.cos(a),cy+r2*math.sin(a))],fill=TICK,width=max(2,int(D/180)))
    ImageDraw.Draw(canvas).ellipse([cx-R-D*0.025,cy-R-D*0.025,cx+R+D*0.025,cy+R+D*0.025],fill=(255,255,255))
    canvas.alpha_composite(disc(f,D),(int(cx-R),int(cy-R)))
    name,mag,who=parse(f)
    # mag badge
    bw,bh=int(D*0.26),int(D*0.13); bx,by=int(cx+R*0.62),int(cy-R*0.88)
    fb=F('ebg600.ttf',int(D*0.085)); t=f'{mag}×'; pass
    if label:
        d.text((cx,cy+R+D*0.2),name,font=F('ebg600.ttf',int(D*0.1)),fill=INK,anchor='mm')
        if who: d.text((cx,cy+R+D*0.33),who,font=F('ebg400.ttf',int(D*0.085)),fill=INK,anchor='mm')
fs=sorted(glob.glob('/home/claude/merch/micro/*.jpg'))
# A2 poster 4 x 4 grid (16)
W,H=4961,7016; P=Image.new('RGBA',(W,H),CR+(255,)); d=ImageDraw.Draw(P)
d.text((W//2,520),'The Life in the Soil',font=F('ebg500.ttf',300),fill=INK,anchor='mm')
d.text((W//2,800),'Photographed by our students, through their own microscopes',font=F('ebg400.ttf',120),fill=INK,anchor='mm')
D=820; cols,rows=4,4; gx=(W-2*450)/cols; gy=1180
pick=[f for f in fs if parse(f)[2]][:16]
for i,f in enumerate(pick):
    c,r=i%cols,i//cols; specimen(P,f,450+gx*(c+.5),1580+r*gy*1.04,D)
lg=Image.open('/home/claude/merch/logos/SFW-logo-flower-colour.png').convert('RGBA').resize((520,520),Image.LANCZOS)
P.alpha_composite(lg,((W-520)//2,H-700)); P.convert('RGB').save('SFW-poster-A2-specimens.png')
# mug wrap 2700x1050: 3 specimens + logo? just 3 with labels
M=Image.new('RGBA',(2700,1050),(255,255,255,255)); sel=[pick[1],pick[5],pick[12]]
for i,f in enumerate(sel): specimen(M,f,450+i*900,420,520)
M.convert('RGB').save('SFW-mug-specimens.png')
# tote 3000 square: 2x2 + logo
T=Image.new('RGBA',(3000,3000),(0,0,0,0))
for i,f in enumerate([pick[0],pick[3],pick[7],pick[10]]): specimen(T,f,800+(i%2)*1400,700+(i//2)*1450,900)
T.save('SFW-tote-specimens.png')
# preview
pv=Image.new('RGB',(2000,1500),(226,222,214)); a=P.convert('RGB'); a.thumbnail((1000,1420)); pv.paste(a,(20,40))
b=M.convert('RGB'); b.thumbnail((940,400)); pv.paste(b,(1040,40))
tb=Image.new('RGB',(3000,3000),CR); tb.paste(T,(0,0),T); tb.thumbnail((900,900)); pv.paste(tb,(1060,520))
pv.save('SFW-specimens-preview.jpg',quality=88)
