from PIL import Image, ImageDraw, ImageFilter
import random
myc=Image.open('tile_myc_olive.png').convert('RGBA'); sl=Image.open('tile_slide_olive.png').convert('RGBA')
# combined: mycelium + sparse slides
from slide import scatter
from myc import mycelium
comb=myc.copy(); s2=scatter(bg=(0,0,0),n=14,seed=11)
a=s2.convert('L').point(lambda v:255 if v>8 else 0)
comb.paste(s2,(0,0),a); comb.save('tile_combined.png')
# purple colourway mycelium
mp=mycelium(bg=(52,38,72),line=(160,190,110),spore=(120,170,220),seed=9); mp.save('tile_myc_purple.png')
# blue colourway slides
sb=scatter(bg=(24,44,66),cols=[(160,190,110),(200,170,230),(150,200,235)],weights=[5,2,3],seed=21); sb.save('tile_slide_blue.png')
def fill(mask,tile,scale=1.0):
    W,H=mask.size; t=tile.resize((int(tile.width*scale),int(tile.height*scale)),Image.LANCZOS)
    big=Image.new('RGBA',(W,H))
    for x in range(0,W,t.width):
        for y in range(0,H,t.height): big.paste(t,(x,y))
    out=Image.new('RGBA',(W,H),(0,0,0,0)); out.paste(big,(0,0),mask); return out
def shadow(img,off=18,blur=22):
    a=img.split()[3]; sh=Image.new('RGBA',img.size,(0,0,0,0)); s=Image.new('RGBA',img.size,(0,0,0,90)); sh.paste(s,(0,0),a)
    sh=sh.filter(ImageFilter.GaussianBlur(blur)); c=Image.new('RGBA',(img.width+off*3,img.height+off*3),(0,0,0,0)); c.alpha_composite(sh,(off,off+6)); c.alpha_composite(img,(0,0)); return c
# phone case
def phone(tile,scale,logo=None):
    W,H=900,1840; m=Image.new('L',(W,H),0); ImageDraw.Draw(m).rounded_rectangle((0,0,W-1,H-1),150,fill=255)
    p=fill(m,tile,scale); d=ImageDraw.Draw(p)
    d.rounded_rectangle((60,60,400,400),95,fill=(20,24,14,255)); 
    for cx,cy in [(150,150),(150,310),(310,230)]: d.ellipse((cx-62,cy-62,cx+62,cy+62),fill=(8,10,8,255),outline=(70,80,60,255),width=8)
    if logo:
        lg=Image.open(logo).resize((300,300),Image.LANCZOS); p.alpha_composite(lg,(300,1440))
    return shadow(p)
L='/home/claude/merch/logos/SFW-logo-flower-cream.png'
phone(comb,0.75,L).save('mock_phone_combined.png'); phone(sl,0.6,L).save('mock_phone_slide.png'); phone(mp,0.75,L).save('mock_phone_purple.png')
# tracksuit jacket + pants
def jacket(tile,stripe,scale=0.45):
    W,H=1300,1300; m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
    body=[(390,150),(540,110),(650,170),(760,110),(910,150),(1010,230),(1230,900),(1100,950),(930,500),(930,1200),(370,1200),(370,500),(200,950),(70,900),(290,230)]
    d.polygon(body,fill=255)
    j=fill(m,tile,scale); dd=ImageDraw.Draw(j)
    # sleeve stripes
    sm=Image.new('L',(W,H),0); ds=ImageDraw.Draw(sm)
    ds.polygon([(290,230),(330,245),(130,925),(95,912)],fill=255); ds.polygon([(1010,230),(970,245),(1170,925),(1205,912)],fill=255)
    j.paste(stripe,(0,0),sm) if stripe.size==(W,H) else None
    # zip + collar
    dd.line([(650,175),(650,1200)],fill=(20,24,14,255),width=10); dd.polygon([(540,110),(650,170),(760,110),(740,90),(650,140),(560,90)],fill=(30,36,20,255))
    dd.rectangle((370,1150,930,1200),fill=(30,36,20,255)); dd.polygon([(200,950),(70,900),(60,940),(190,990)],fill=(30,36,20,255)); dd.polygon([(1100,950),(1230,900),(1240,940),(1110,990)],fill=(30,36,20,255))
    return shadow(j)
def pants(tile,stripe,scale=0.45):
    W,H=900,1400; m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
    d.polygon([(150,60),(750,60),(820,1340),(560,1340),(450,420),(340,1340),(80,1340)],fill=255)
    p=fill(m,tile,scale); dd=ImageDraw.Draw(p)
    sm=Image.new('L',(W,H),0); ds=ImageDraw.Draw(sm); ds.polygon([(150,60),(195,60),(125,1340),(80,1340)],fill=255); ds.polygon([(750,60),(705,60),(775,1340),(820,1340)],fill=255)
    p.paste(stripe.crop((0,0,W,H)),(0,0),sm)
    dd.rectangle((150,60,750,120),fill=(30,36,20,255)); dd.rectangle((80,1300,340,1340),fill=(30,36,20,255)); dd.rectangle((560,1300,820,1340),fill=(30,36,20,255))
    return shadow(p)
# stripe fill: slide pattern in purple tone
stripe=Image.new('RGBA',(1300,1400)); sp=scatter(S=1400,bg=(52,38,72),cols=[(200,170,230),(160,190,110)],weights=[3,1],n=30,seed=31).resize((1300,1400))
stripe.paste(sp,(0,0))
jacket(myc,stripe).save('mock_jacket.png'); pants(myc,stripe).save('mock_pants.png')
for f,t in [('tile_combined.png',0),('tile_myc_purple.png',0),('tile_slide_blue.png',0)]: Image.open(f).convert('RGB').resize((600,600)).save('/tmp/'+f)
