from PIL import Image, ImageDraw, ImageFont, ImageCms
ICC=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
F='/home/claude/linneamoritznyc/sfw-newwebsite/tools/blog-cards/fonts/EBGaramond-Regular.ttf'
M='/home/claude/merch/micro/'
W,H=1842,1240; INK=(30,36,30); BG=(255,255,255)
cards=[
 ('Testate amoeba (encysted) 40x obj Robert Kenyon.jpg','A testate amoeba','resting inside its shell','Robert Kenyon',(0.22,0.28,0.5)),
 ('Ciliates (stalked) 40x obj Sid Jensen.jpg','Stalked ciliates','feeding on bacteria','Sid Jensen',None),
 ('Fungal spore 40x obj Josia Martens.jpg','A fungal spore','made of many cells','Josia Martens',None),
 ('Bacterial-feeding nematode 40x obj Casey Williams.jpg','A nematode','that eats bacteria','Casey Williams',None),
]
logo=Image.open('/home/claude/merch/logos/SFW-logo-flower-colour.png').convert('RGBA')
def f(s): return ImageFont.truetype(F,s)
for i,(fn,name,sub,who,cr) in enumerate(cards,1):
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    ph=Image.open(M+fn).convert('RGB'); S=H-2*110
    w,h=ph.size; c=min(w,h)
    if cr:
        c=int(c*cr[2]); cx=int(cr[0]*w); cy=int(cr[1]*h); x0=max(0,min(w-c,cx-c//2)); y0=max(0,min(h-c,cy-c//2))
    else: x0,y0=(w-c)//2,(h-c)//2
    ph=ph.crop((x0,y0,x0+c,y0+c)).resize((S,S),Image.LANCZOS)
    im.paste(ph,(110,110))
    x=110+S+90
    d.text((x,118),f'No. {i:02d}',font=f(40),fill=INK)
    d.text((x,330),'Look',font=f(150),fill=INK)
    d.text((x,480),'closer',font=f(150),fill=INK)
    d.text((x,720),name,font=f(44),fill=INK)
    d.text((x,775),sub+'.',font=f(44),fill=INK)
    d.text((x,880),'Photographed by '+who+',',font=f(34),fill=INK)
    d.text((x,925),'Soil Food Web School student.',font=f(34),fill=INK)
    lg=logo.copy(); lg.thumbnail((150,150),Image.LANCZOS)
    im.paste(lg,(W-110-lg.width,H-110-lg.height),lg)
    im.save(f'SFW-postcard-look-closer-{i:02d}.png',icc_profile=ICC,dpi=(300,300))
