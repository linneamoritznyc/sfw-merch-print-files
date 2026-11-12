import math, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
def hx(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
W_,H_=900,1000
def plate(i):
    p=Image.open(f'/home/claude/merch/micro/plate_{i}.png').convert('RGBA').split()[3]
    m=Image.new('L',p.size,0); c=p.width/2; r=p.width*0.465; ImageDraw.Draw(m).ellipse([c-r,c-r,c+r,c+r],fill=255)
    return Image.fromarray(np.minimum(np.asarray(p),np.asarray(m)))
def halftone(A,bg,ink,cell=9):
    im=Image.new('RGB',(W_*2,H_*2),bg); d=ImageDraw.Draw(im); h,w=A.shape
    for gy in np.arange(0,h,cell):
        for gx in np.arange(cell/2 if int(gy/cell)%2 else 0,w,cell):
            v=A[int(gy),int(gx)]
            if v<0.15: continue
            r=cell*0.5*min(1,v)**0.6; d.ellipse([(gx-r)*2,(gy-r)*2,(gx+r)*2,(gy+r)*2],fill=ink)
    return im.resize((W_,H_),Image.LANCZOS)
def crop_field(pi,size,ox,oy,rot=0):
    p=plate(pi).rotate(rot).resize((size,size),Image.LANCZOS).filter(ImageFilter.GaussianBlur(3))
    c=Image.new('L',(W_,H_),0); c.paste(p,(ox,oy)); return np.asarray(c).astype(float)/255
def hypha_field(seed,starts,w0):
    m=Image.new('L',(W_,H_),0); d=ImageDraw.Draw(m); rr=random.Random(seed)
    def br(x,y,a,w,dep):
        while w>8 and -100<x<W_+100 and -100<y<H_+100:
            a+=rr.gauss(0,0.04); nx,ny=x+6*math.cos(a),y+6*math.sin(a); d.ellipse([nx-w/2,ny-w/2,nx+w/2,ny+w/2],fill=255); x,y=nx,ny; w*=0.998
            if rr.random()<0.008 and dep<2: br(x,y,a+rr.choice([-1,1])*0.8,w*0.6,dep+1)
    for s in starts: br(*s,w0,0)
    A=np.asarray(m.filter(ImageFilter.GaussianBlur(4))).astype(float)/255
    tex=crop_field(7,1400,-250,-200)*0.6+0.45
    return A*np.clip(tex,0,1)
def tee_mask():
    m=Image.new('L',(W_,H_),0); d=ImageDraw.Draw(m)
    d.polygon([(255,55),(360,35),(390,60),(510,60),(540,35),(645,55),(860,215),(770,400),(690,330),(700,960),(200,960),(210,330),(130,400),(40,215)],fill=255)
    d.chord([380,0,520,110],0,180,fill=0); return m.filter(ImageFilter.GaussianBlur(1.2))
def shirt_mask():
    m=Image.new('L',(W_,H_),0); d=ImageDraw.Draw(m)
    d.polygon([(275,50),(380,35),(450,90),(520,35),(625,50),(840,250),(860,760),(770,770),(700,380),(710,975),(190,975),(200,380),(130,770),(40,760),(60,250)],fill=255)
    return m.filter(ImageFilter.GaussianBlur(1.2))
def jacket_mask(): return shirt_mask()
def garment(art,mask,kind,trim):
    bg=Image.new('RGB',(W_,H_),(236,233,227)); bg.paste(art,(0,0),mask)
    # soft shading
    sh=Image.new('L',(W_,H_),0); ds=ImageDraw.Draw(sh)
    for x0 in (200,690): ds.rectangle([x0-6,380,x0+6,960],fill=60)
    sh=sh.filter(ImageFilter.GaussianBlur(14)); bg.paste((0,0,0),(0,0),Image.fromarray((np.asarray(sh)*np.asarray(mask)/255*0.6).astype(np.uint8)))
    d=ImageDraw.Draw(bg)
    if kind=='tee': d.arc([380,0,520,110],0,180,fill=trim,width=10)
    if kind=='shirt':
        d.polygon([(380,35),(450,90),(395,160),(345,70)],fill=trim); d.polygon([(520,35),(450,90),(505,160),(555,70)],fill=trim)
        d.line([(450,90),(450,975)],fill=(20,20,20),width=2)
        for y in range(190,960,115): d.ellipse([443,y,457,y+14],fill=(238,234,224))
    if kind=='jacket':
        d.rectangle([370,20,530,70],fill=trim); d.line([(450,70),(450,975)],fill=(220,220,220),width=5)
        d.rectangle([190,935,710,980],fill=trim); d.polygon([(130,770),(40,760),(42,720),(134,730)],fill=trim); d.polygon([(770,770),(860,760),(858,720),(766,730)],fill=trim)
    return bg
OL=hx('5B6B2E'); PG=hx('CBD696'); PUR=hx('6B4C7A'); LIL=hx('C8B6E2'); DG=hx('22371F'); DG2=hx('2E4A29'); FWG=hx('156826'); EB=hx('3780B8'); LGR=hx('59A66C'); CRM=hx('F4F1EA')
A1=crop_field(11,2300,-700,-650); A2=crop_field(14,2200,-600,-500,90); A3=crop_field(4,2100,-650,-450)
H1=hypha_field(3,[(-80,520,-0.35),(980,120,2.5)],120)
looks=[('oversized tee, olive',garment(halftone(A1,OL,PG),tee_mask(),'tee',PG)),
       ('button shirt, purple',garment(halftone(A2,PUR,LIL),shirt_mask(),'shirt',PUR)),
       ('track jacket, hypha',garment(halftone(H1,DG,LGR),jacket_mask(),'jacket',FWG)),
       ('tonal tee, deep green',garment(halftone(A3,DG,DG2),tee_mask(),'tee',DG2)),
       ('button shirt, blue on cream',garment(halftone(A3,CRM,EB),shirt_mask(),'shirt',EB)),
       ('tee, hypha on cream',garment(halftone(H1,CRM,FWG),tee_mask(),'tee',FWG))]
S=Image.new('RGB',(3*920+20,2*1020+20),(226,222,214))
for i,(n,g) in enumerate(looks): S.paste(g,(20+(i%3)*920,20+(i//3)*1020))
S.save('SFW-aop-fashion-v2.jpg',quality=90)
