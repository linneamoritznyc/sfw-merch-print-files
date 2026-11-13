import numpy as np, cv2
from skimage import measure
from PIL import Image, ImageDraw, ImageFont, ImageCms
ICC=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
B='/home/claude/merch/brand/'; M='/home/claude/merch/micro/'
W,H=5400,7200; BG=(17,18,17); INK=(232,232,226)
im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
def F(wt,s): return ImageFont.truetype(B+f'ebg{wt}.ttf',s)
def spaced(y,t,size,sp,wt=600,fill=INK):
    f=F(wt,size); tw=sum(d.textlength(c,font=f) for c in t)+sp*(len(t)-1); x=(W-tw)/2
    for c in t: d.text((x,y),c,font=f,fill=fill); x+=d.textlength(c,font=f)+sp
    return tw
def fit(t,size,sp,wt,maxw):
    while True:
        f=F(wt,size); tw=sum(d.textlength(c,font=f) for c in t)+sp*(len(t)-1)
        if tw<=maxw: return size
        size-=4
mx=420; fw=W-2*mx
# title
ts=fit('SOIL FOOD WEB',760,20,600,fw); spaced(330,'SOIL FOOD WEB',ts,20)
# contour art frame
fx0,fy0,fx1,fy1=mx,1250,W-mx,1250+int(fw*0.78)
g=cv2.imread(M+'Testate amoebae 40x obj Jimena Fuentes.jpg',0).astype(np.float32)
aw,ah=fx1-fx0,fy1-fy0; h,w=g.shape; s=max(aw/w,ah/h)*1.05
g=cv2.resize(g,(int(w*s)+2,int(h*s)+2)); y0=(g.shape[0]-ah)//2; x0=(g.shape[1]-aw)//2; g=g[y0:y0+ah,x0:x0+aw]
g=cv2.GaussianBlur(cv2.resize(g,(aw//3,ah//3)),(0,0),7)
art=Image.new('L',(aw*2,ah*2),0); ad=ImageDraw.Draw(art)
for lv in np.linspace(g.min(),g.max(),20)[1:-1]:
    for c in measure.find_contours(g,lv):
        if len(c)<12: continue
        ad.line([(x*6,y*6) for y,x in c],fill=255,width=5,joint='curve')
art=art.resize((aw,ah),Image.LANCZOS)
im.paste(Image.new('RGB',(aw,ah),INK),(fx0,fy0),art)
d.rectangle([fx0,fy0,fx1,fy1],outline=INK,width=6)
f=F(500,58); d.text((fx0,fy1+40),'TESTATE AMOEBAE, TRACED',font=f,fill=INK)
d.text((fx0,fy1+115),'FROM A STUDENT MICROGRAPH BY JIMENA FUENTES',font=F(500,40),fill=INK)
t='2027 WORLD TOUR'; tw=d.textlength(t,font=f); d.text((fx1-tw,fy1+40),t,font=f,fill=INK)
# lineup
rows=[(['BACTERIA','EARTHWORMS','FUNGI'],330,600,22,1.5),
      (['NEMATODES','PROTOZOA','MYCORRHIZAL FUNGI'],210,600,14,1.55),
      (['SPRINGTAILS','MITES','CILIATES','FLAGELLATES','TARDIGRADES'],150,600,10,1.6),
      (['ROTIFERS','TESTATE AMOEBAE','ACTINOMYCETES','ENCHYTRAEIDS','ARCHAEA'],112,600,7,1.65),
      (['PAUROPODS','VAMPYRELLIDS','PROTURANS','DIPLURANS','SYMPHYLANS'],92,500,6,2.0),
      ('AND INTRODUCING',62,500,30,1.9),
      (['TRICHODERMA','STREPTOMYCES','RHIZOBIUM','BACILLUS','PSEUDOMONAS','MORTIERELLA'],76,500,5,1.6),
      (['ARTHROBOTRYS','COLPODA','VORTICELLA','ARCELLA','DIFFLUGIA','NOSTOC'],64,500,5,1.0)]
y=fy1+380
for names,size,wt,sp,lh in rows:
    t=names if isinstance(names,str) else '  ·  '.join(names)
    size=fit(t,size,sp,wt,fw*0.96); spaced(y,t,size,sp,wt); y+=int(size*lh)
y+=170; d.rectangle([mx,y,W-mx,y+8],fill=INK); y+=90
spaced(y,'LIVE BENEATH YOUR FEET',150,40,500)
print('bottom',y+150,H)
im.save('SFW-lineup-poster-18x24.png',icc_profile=ICC,dpi=(300,300))
im.resize((W//6,H//6),Image.LANCZOS).save('/tmp/lp.jpg',quality=90)
