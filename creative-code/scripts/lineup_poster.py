import numpy as np, cv2
from skimage import measure
from PIL import Image, ImageDraw, ImageFont, ImageCms
ICC=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
B='/home/claude/merch/brand/'; M='/home/claude/merch/micro/'
W,H=5400,7200; BG=(17,18,17); INK=(236,234,226); DIM=(88,90,84)
im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
# contour art, full bleed behind the top part
g=cv2.imread(M+'Testate amoebae 40x obj Jimena Fuentes.jpg',0).astype(np.float32)
aw,ah=W,int(H*0.62); h,w=g.shape; s=max(aw/w,ah/h)*1.1
g=cv2.resize(g,(int(w*s)+2,int(h*s)+2)); y0=(g.shape[0]-ah)//2; x0=(g.shape[1]-aw)//2; g=g[y0:y0+ah,x0:x0+aw]
g=cv2.GaussianBlur(cv2.resize(g,(aw//3,ah//3)),(0,0),8)
art=Image.new('L',(aw*2,ah*2),0); ad=ImageDraw.Draw(art)
for lv in np.linspace(g.min(),g.max(),18)[1:-1]:
    for c in measure.find_contours(g,lv):
        if len(c)<12: continue
        ad.line([(x*6,y*6) for y,x in c],fill=255,width=6,joint='curve')
art=art.resize((aw,ah),Image.LANCZOS)
fade=np.clip(np.linspace(1.6,-0.2,ah),0,1)[:,None]*np.ones((1,aw))
art=Image.fromarray((np.asarray(art)*fade).astype(np.uint8))
im.paste(Image.new('RGB',(aw,ah),(150,152,144)),(0,0),art)
def F(wt,s): return ImageFont.truetype(B+f'ebg{wt}.ttf',s)
mx=300; fw=W-2*mx
def row(y,words,wt=600,sep='·',gapk=0.55,maxsize=2000):
    # justify words across the full width, find the size where they fill it
    size=maxsize
    while True:
        f=F(wt,size); ws=[d.textlength(t,font=f) for t in words]; gap=size*gapk
        tot=sum(ws)+gap*(len(words)-1)
        if tot<=fw: break
        size-=4
    f=F(wt,size); ws=[d.textlength(t,font=f) for t in words]
    gap=(fw-sum(ws))/(len(words)-1) if len(words)>1 else 0
    x=mx if len(words)>1 else (W-ws[0])/2
    asc,desc=f.getmetrics()
    for i,t in enumerate(words):
        d.text((x,y),t,font=f,fill=INK); x+=ws[i]
        if i<len(words)-1:
            sf=F(wt,int(size*0.6)); sw=d.textlength(sep,font=sf)
            d.text((x+gap/2-sw/2,y+size*0.18),sep,font=sf,fill=INK); x+=gap
    return size
def center(y,t,size,sp,wt=500):
    f=F(wt,size); tw=sum(d.textlength(c,font=f) for c in t)+sp*(len(t)-1); x=(W-tw)/2
    for c in t: d.text((x,y),c,font=f,fill=INK); x+=d.textlength(c,font=f)+sp
center(260,'SOIL FOOD WEB PRESENTS',120,46)
s=row(470,['2027','WORLD','TOUR'],600,sep=' ',gapk=0.3,maxsize=900)
center(470+int(s*1.12),'LIVE BENEATH YOUR FEET  ·  ALL AGES  ·  EVERY SOIL ON EARTH',96,22)
rows=[['BACTERIA','FUNGI'],
      ['EARTHWORMS','NEMATODES','PROTOZOA'],
      ['MYCORRHIZAL FUNGI','SPRINGTAILS','MITES'],
      ['CILIATES','FLAGELLATES','TARDIGRADES','ROTIFERS','AMOEBAE'],
      ['TESTATE AMOEBAE','ACTINOMYCETES','ENCHYTRAEIDS','ARCHAEA'],
      ['PAUROPODS','VAMPYRELLIDS','PROTURANS','DIPLURANS','SYMPHYLANS','SLIME MOLDS'],
      ['TRICHODERMA','STREPTOMYCES','RHIZOBIUM','BACILLUS','PSEUDOMONAS','MORTIERELLA','NOSTOC'],
      ['ARTHROBOTRYS','COLPODA','VORTICELLA','ARCELLA','DIFFLUGIA','GLOMUS','AZOTOBACTER','HALTERIA']]
caps=[1000,560,430,330,300,230,190,160]
y=int(H*0.555)
for i,(ws,cap) in enumerate(zip(rows,caps)):
    s=row(y,ws,600 if i<5 else 500,maxsize=cap); y+=int(s*1.42)
    if i==0: y+=40
print('end',y)
y+=60; d.rectangle([mx,y,W-mx,y+8],fill=INK); y+=70
f=F(500,70); d.text((mx,y),'ART: TESTATE AMOEBAE, TRACED FROM A MICROGRAPH BY JIMENA FUENTES, SOIL FOOD WEB SCHOOL STUDENT',font=f,fill=INK)
lg=Image.open('/home/claude/merch/logos/SFW-logo-flower-white-3000.png').convert('RGBA'); lg.thumbnail((260,260),Image.LANCZOS)
im.paste(lg,(W-mx-lg.width,H-160-lg.height),lg)
im.save('SFW-lineup-poster-18x24.png',icc_profile=ICC,dpi=(300,300))
im.resize((W//6,H//6),Image.LANCZOS).save('/tmp/fp.jpg',quality=90)
