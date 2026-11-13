import sys, math, numpy as np
sys.path.insert(0,'/home/claude/merch/brand')
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageCms
from stitch import satin, place, fabric
ICC=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
W,H=1650,600; SS=3
WHITE=(250,250,246); LIME=(178,214,72); GOLD=(205,160,60); RUST=(170,92,40); MAROON=(110,40,46); CREAM=(240,232,210); PINK=(232,130,160); LAV=(186,160,226); DEEP=(30,62,46)
B='/home/claude/merch/brand/'
def canvas(): return Image.new('RGBA',(W*SS,H*SS),(0,0,0,0))
def L(px): return int(px*SS)
def ciliate(c1=WHITE,c2=LIME):
    im=canvas(); d=ImageDraw.Draw(im); cx,cy=W/2,H*0.36
    # bell
    pts=[]
    for i in range(41):
        t=i/40; a=math.pi*(1+t); r=150
        pts.append((cx+r*math.cos(a)*0.95, cy+ r*math.sin(a)*0.55))
    pts+= [(cx+120,cy+40),(cx+60,cy+190),(cx-60,cy+190),(cx-120,cy+40)]
    d.polygon([(x*SS,y*SS) for x,y in pts],fill=c2+(255,))
    d.line([(x*SS,y*SS) for x,y in pts+[pts[0]]],fill=c1+(255,),width=L(16),joint='curve')
    for dx in (-60,-20,20,60): d.line([((cx+dx)*SS,(cy-90)*SS),((cx+dx*1.3)*SS,(cy-130)*SS)],fill=c1+(255,),width=L(14))  # cilia
    # coiled stalk
    sp=[(cx+16*math.sin(i/6), cy+190+i*2.2) for i in range(0,150)]
    d.line([(x*SS,y*SS) for x,y in sp],fill=c1+(255,),width=L(16),joint='curve')
    return im
def nematode(c1=WHITE,c2=PINK):
    im=canvas(); d=ImageDraw.Draw(im)
    pts=[(150+i*2.3, H/2+90*math.sin(i/70*math.pi)) for i in range(0,580)]
    for k,(x,y) in enumerate(pts):
        w=40*math.sin(math.pi*k/len(pts))**0.4+8
        d.ellipse([(x-w/2)*SS,(y-w/2)*SS,(x+w/2)*SS,(y+w/2)*SS],fill=c1+(255,))
    x,y=pts[-12]; d.ellipse([(x-12)*SS,(y-12)*SS,(x+12)*SS,(y+12)*SS],fill=c2+(255,))
    return im
def spiral(c1=WHITE,c2=GOLD):
    im=canvas(); d=ImageDraw.Draw(im); cx,cy=W/2,H/2; a=0; r=14
    i=0
    while r<270:
        x,y=cx+r*math.cos(a),cy+r*math.sin(a); s=10+r*0.06
        d.ellipse([(x-s)*SS,(y-s)*SS,(x+s)*SS,(y+s)*SS],fill=(c1 if i%5 else c2)+(255,))
        a+= (2*s+10)/r; r=14+a*14; i+=1
    return im
def mushroom(c1=WHITE,c2=RUST):
    im=canvas(); d=ImageDraw.Draw(im); cx=W/2
    d.pieslice([(cx-170)*SS,90*SS,(cx+170)*SS,350*SS],180,360,fill=c2+(255,))
    for dx,dy,s in ((-90,170,18),(-20,140,14),(60,165,20),(110,200,12)): d.ellipse([(cx+dx-s)*SS,(dy-s)*SS,(cx+dx+s)*SS,(dy+s)*SS],fill=c1+(255,))
    d.rounded_rectangle([(cx-38)*SS,220*SS,(cx+38)*SS,400*SS],radius=L(30),fill=c1+(255,))
    rnd=np.random.default_rng(2)
    for k in range(9):
        x,y=cx+rnd.uniform(-30,30),400; a=math.pi/2+rnd.uniform(-1.2,1.2); pts=[(x,y)]
        for _ in range(16): a+=rnd.normal(0,0.25); x+=12*math.cos(a); y+=7*math.sin(a); pts.append((x,min(y,585)))
        d.line([(p[0]*SS,p[1]*SS) for p in pts],fill=c1+(255,),width=L(14),joint='curve')
    return im
def testate(c1=WHITE,c2=LAV):
    im=canvas(); d=ImageDraw.Draw(im); cx,cy=W/2,H/2
    d.ellipse([(cx-200)*SS,(cy-230)*SS,(cx+200)*SS,(cy+230)*SS],fill=c2+(255,),outline=c1+(255,),width=L(18))
    rnd=np.random.default_rng(5); pl=[]
    for _ in range(4000):
        x,y=rnd.uniform(cx-160,cx+160),rnd.uniform(cy-190,cy+190); s=rnd.uniform(16,30)
        if ((x-cx)/165)**2+((y-cy)/195)**2>1: continue
        if any(math.hypot(x-a,y-b)<s+t+12 for a,b,t in pl): continue
        pl.append((x,y,s)); d.ellipse([(x-s)*SS,(y-s)*SS,(x+s)*SS,(y+s)*SS],fill=c1+(255,))
    d.ellipse([(cx-40)*SS,(cy+170)*SS,(cx+40)*SS,(cy+230)*SS],fill=c1+(255,))
    return im
def word(t='SOILPUNK',c=WHITE):
    im=canvas(); d=ImageDraw.Draw(im); f=ImageFont.truetype(B+'ebg600.ttf',int(300*SS))
    d.text((W/2*SS,H/2*SS),t,font=f,fill=c+(255,),anchor='mm'); return im
def finish(im): 
    o=im.resize((W,H),Image.LANCZOS); a=np.asarray(o.split()[3]); o.putalpha(Image.fromarray(np.where(a>127,255,0).astype(np.uint8))); return o
def stitched(art,bg,seed):
    base=fabric(bg,seed).resize((W,W)).crop((0,(W-H)//2,W,(W-H)//2+H)).convert('RGB')
    a=np.asarray(art)
    cols={tuple(c) for c in a[a[...,3]>0][:,:3][::50].tolist()}
    for i,c in enumerate(sorted(cols)):
        m=Image.fromarray(((a[...,3]>0)&(np.abs(a[...,:3].astype(int)-c).sum(-1)<30)).astype(np.uint8)*255)
        if not np.asarray(m).any(): continue
        img,mm=satin(m,c,angle=[35,-40,80][i%3],pitch=4)
        place(base,img,mm,(0,0))
    return base
if __name__=='__main__':
    D=[('ciliate',ciliate()),('nematode',nematode()),('spiral',spiral()),('mushroom',mushroom()),('testate',testate()),('soilpunk',word())]
    JUNGLE=(62,80,52); DILL=(120,124,80)
    rows=[]
    for i,(n,im) in enumerate(D):
        f=finish(im); f.save(f'SFW-emb-{n}.png',icc_profile=ICC,dpi=(300,300))
        rows.append(stitched(f,[JUNGLE,DILL][i%2],i))
    C=Image.new('RGB',(2*W+90,3*H+120),(236,236,232))
    for i,r in enumerate(rows): C.paste(r,(30+(i%2)*(W+30),30+(i//2)*(H+30)))
    C.resize((C.width//2,C.height//2),Image.LANCZOS).save('SFW-embroidery-sheet.jpg',quality=90)
