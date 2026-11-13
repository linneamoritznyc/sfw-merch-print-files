import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageCms, ImageChops
ICC=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
B='/home/claude/merch/brand/'; M='/home/claude/merch/micro/'
W,H=5400,7200
CREAM=(243,240,229); GREEN=(28,58,40); PURP=(98,74,160); LAV=(196,182,232); LIME=(206,226,110); BROWN=(122,70,36); MID=(62,128,80)
im=Image.new('RGB',(W,H),CREAM); d=ImageDraw.Draw(im)
def F(wt,s): return ImageFont.truetype(B+f'ebg{wt}.ttf',s)
def duo(f,size,c0,c1,zoom=1.0,cx=.5,cy=.5,seed=0):
    g=cv2.imread(M+f,0).astype(np.float32); h,w=g.shape; c=int(min(h,w)/zoom)
    x0=int(min(max(cx*w-c/2,0),w-c)); y0=int(min(max(cy*h-c/2,0),h-c))
    g=cv2.resize(g[y0:y0+c,x0:x0+c],(size,size),interpolation=cv2.INTER_CUBIC)
    g=cv2.equalizeHist(g.astype(np.uint8)).astype(np.float32)/255
    g=np.clip(g+np.random.default_rng(seed).normal(0,0.06,g.shape),0,1)  # print grain
    a=np.array(c0,np.float32); b=np.array(c1,np.float32)
    return Image.fromarray((a+(b-a)*g[...,None]).astype(np.uint8))
def shape_paste(art,mask,xy): im.paste(art,xy,mask)
t='SOIL FOOD WEB'; sz=1200
while d.textlength(t,font=F(600,sz))>W-2*300: sz-=10
tb=d.textbbox((0,0),t,font=F(600,sz)); TOP=300
title_y=TOP-tb[1]; title_bottom=TOP+(tb[3]-tb[1])
gy0=title_bottom+300; gy1=gy0+2900
# grid over the art zone
for x in range(0,W,300): d.line([(x,gy0),(x,gy1)],fill=(214,212,200),width=4)
for y in range(gy0,gy1+1,300): d.line([(0,y),(W,y)],fill=(214,212,200),width=4)
# big circle: testate amoebae duotone
D=2700; m=Image.new('L',(D,D),0); ImageDraw.Draw(m).ellipse([0,0,D-1,D-1],fill=255)
shape_paste(duo('Testate amoebae 40x obj Jimena Fuentes.jpg',D,(40,26,80),LAV,zoom=1.5,cx=.3,cy=.62),m,(300,gy0+100))
# arch (lime, ciliates) overlapping right
aw,ah=1900,2500; m=Image.new('L',(aw,ah),0); md=ImageDraw.Draw(m); md.ellipse([0,0,aw-1,aw-1],fill=255); md.rectangle([0,aw//2,aw-1,ah-1],fill=255)
shape_paste(duo('Ciliates (stalked) 40x obj Sid Jensen.jpg',ah,GREEN,LIME,zoom=1.2,cx=.45,cy=.4,seed=1).crop((300,0,300+aw,ah)),m,(3200,gy0+300))
# leaf (brown) and small solid circle
lw,lh=900,1500; m=Image.new('L',(lw,lh),0); md=ImageDraw.Draw(m)
md.ellipse([-lw*0.9,0,lw*0.9,lh],fill=255); m2=Image.new('L',(lw,lh),0); ImageDraw.Draw(m2).ellipse([lw*0.1,0,lw*1.9,lh],fill=255)
m=ImageChops.multiply(m,m2); im.paste(Image.new('RGB',(lw,lh),BROWN),(2550,gy0+1450),m)
d.ellipse([4300,gy0+2200,4900,gy0+2800],fill=MID)
d.text(((W-d.textlength(t,font=F(600,sz)))/2,title_y),t,font=F(600,sz),fill=GREEN)
# lineup, justified to full width
mx=300; fw=W-2*mx
def row(y,words,col,wt=600,maxsize=2000):
    size=maxsize
    while True:
        f=F(wt,size); ws=[d.textlength(t,font=f) for t in words]
        if sum(ws)+size*0.5*(len(words)-1)<=fw: break
        size-=4
    f=F(wt,size); ws=[d.textlength(t,font=f) for t in words]
    gap=(fw-sum(ws))/(len(words)-1) if len(words)>1 else 0; x=mx if len(words)>1 else (W-ws[0])/2
    for i,t in enumerate(words):
        d.text((x,y),t,font=f,fill=col); x+=ws[i]
        if i<len(words)-1:
            r=size*0.06; cx=x+gap/2; cy=y+F(wt,size).getbbox('H')[1]+(F(wt,size).getbbox('H')[3]-F(wt,size).getbbox('H')[1])/2; d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=col); x+=gap
    return size
rows=[(['BACTERIA','FUNGI'],PURP,620),
      (['EARTHWORMS','NEMATODES','PROTOZOA'],GREEN,420),
      (['MYCORRHIZAL FUNGI','SPRINGTAILS','MITES'],GREEN,330),
      (['CILIATES','FLAGELLATES','TARDIGRADES','ROTIFERS'],GREEN,260),
      (['TESTATE AMOEBAE','ACTINOMYCETES','ENCHYTRAEIDS','ARCHAEA'],GREEN,220),
      (['PAUROPODS','VAMPYRELLIDS','PROTURANS','DIPLURANS','SYMPHYLANS','SLIME MOLDS'],GREEN,170),
      (['TRICHODERMA','STREPTOMYCES','RHIZOBIUM','BACILLUS','PSEUDOMONAS','MORTIERELLA','NOSTOC'],GREEN,140)]
BAND=620; by=H-BAND
def capsize(words,wt,cap):
    size=cap
    while True:
        f=F(wt,size)
        if sum(d.textlength(t,font=f) for t in words)+size*0.5*(len(words)-1)<=fw: return size
        size-=4
sizes=[capsize(ws,600 if i<5 else 500,cap) for i,(ws,c,cap) in enumerate(rows)]
caph=[F(600 if i<5 else 500,s).getbbox('H') for i,s in enumerate(sizes)]
hs=[b[3]-b[1] for b in caph]
top=gy1+300; bottom=by-300
gap=(bottom-top-sum(hs))/(len(rows)-1)
y=top
for i,(ws,col,cap) in enumerate(rows):
    row(y-caph[i][1],ws,col,600 if i<5 else 500,sizes[i]); y+=hs[i]+gap
print('end',y)
# bottom band
d.rectangle([0,by,W,H],fill=GREEN)
f=F(600,230); t='2027 WORLD TOUR'; bb=d.textbbox((0,0),t,font=f); ty=by+(BAND-(bb[3]-bb[1]))/2-bb[1]
d.text((mx,ty),t,font=f,fill=CREAM)
f2=F(500,110); t2='LIVE BENEATH YOUR FEET'; b2=d.textbbox((0,0),t2,font=f2)
d.text((mx+d.textlength(t,font=f)+140,by+(BAND-(b2[3]-b2[1]))/2-b2[1]),t2,font=f2,fill=LIME)
lg=Image.open('/home/claude/merch/logos/SFW-logo-flower-white-3000.png').convert('RGBA'); lg.thumbnail((380,380),Image.LANCZOS)
im.paste(lg,(W-mx-lg.width,by+(BAND-lg.height)//2),lg)
im.save('SFW-lineup-poster-v3-18x24.png',icc_profile=ICC,dpi=(300,300))
im.resize((W//6,H//6),Image.LANCZOS).save('/tmp/fp3.jpg',quality=90)
