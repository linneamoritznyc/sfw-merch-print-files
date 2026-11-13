import sys, numpy as np, random, glob
sys.path.insert(0,'/home/claude/merch/brand')
from orgcut import cut
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import gaussian_filter, zoom, binary_erosion
B='/home/claude/merch/brand/'; M='/home/claude/merch/micro/'
SLATE=(78,92,140); MOSS=(52,98,48); RUST=(170,92,40); MUSTARD=(205,160,60); CREAM=(246,240,224); WHITE=(255,255,255)
OLIVE=(98,104,60); BROWN=(96,62,40); LIME=(178,214,72); MAROON=(110,40,46); DEEP=(30,62,46)
f=lambda w,s: ImageFont.truetype(B+f'ebg{w}.ttf',s)
# ---------- ciliate silhouette (body + detail) ----------
body,det=cut('stalked-ciliates',(0.78,0.55),'edge')
def icon(h,fill,line):
    s=h/body.shape[0]; w=int(body.shape[1]*s)
    b=np.asarray(Image.fromarray((body*255).astype(np.uint8)).resize((w,h),Image.LANCZOS))>127
    dd=np.asarray(Image.fromarray((det*255).astype(np.uint8)).resize((w,h),Image.LANCZOS))>127
    inner=binary_erosion(b,iterations=max(2,h//40))
    o=np.zeros((h,w,4),np.uint8); o[b]=line+(255,); o[inner]=fill+(255,); o[inner&dd]=line+(255,)
    return Image.fromarray(o)
# ---------- 1. fleece all-over pattern from micrograph field ----------
def fleece(S=2400):
    srcs=[M+'circ_testate-amoeba.png',M+'circ_fungal-hyphae.png']
    g=np.asarray(Image.open(srcs[0]).convert('L').resize((300,300))).astype(float)
    g2=np.asarray(Image.open(srcs[1]).convert('L').resize((300,300))).astype(float)
    fld=gaussian_filter(-(g-gaussian_filter(g,30)),6)+0.6*gaussian_filter(-(g2-gaussian_filter(g2,30)),8)
    fld=(fld-fld.min())/(fld.max()-fld.min()); fld=zoom(fld,S/300,order=3)
    out=np.zeros((S,S,3),np.uint8); out[:]=SLATE
    out[fld>0.58]=MOSS
    band=np.abs(fld-0.46)<0.022; out[band]=RUST
    band2=np.abs(fld-0.40)<0.012; out[band2]=MUSTARD
    im=Image.fromarray(out); rnd=random.Random(4)
    for _ in range(22):
        ic=icon(rnd.randint(150,260),CREAM,MUSTARD).rotate(rnd.uniform(0,360),expand=True,resample=Image.BICUBIC)
        im.paste(ic,(rnd.randint(0,S-ic.width),rnd.randint(0,S-ic.height)),ic)
    return im
# ---------- 2. specimen patch ----------
def patch(W=900,H=1050):
    src=Image.open(M+'circ_stalked-ciliates.png').convert('RGB'); sw,sh=src.size
    c=src.crop((int(sw*0.60),int(sh*0.30),int(sw*0.96),int(sh*0.80))).resize((W-120,H-260),Image.LANCZOS)
    P=Image.new('RGB',(W,H),WHITE); P.paste(c,(60,60)); d=ImageDraw.Draw(P)
    d.text((W/2,H-150),'STALKED CILIATE',font=f(600,52),fill=DEEP,anchor='mm')
    d.text((W/2,H-90),'400x  ·  Sid Jensen',font=f(500,38),fill=DEEP,anchor='mm')
    return P
# ---------- mocks ----------
def tee_shape(d,fill,ox=0,oy=0,k=1):
    pts=[(380,120),(560,80),(840,80),(1020,120),(1330,330),(1220,560),(1080,480),(1080,1520),(320,1520),(320,480),(180,560),(70,330)]
    d.polygon([(ox+x*k,oy+y*k) for x,y in pts],fill=fill)
def board():
    C=Image.new('RGB',(3000,2000),(236,236,232)); d=ImageDraw.Draw(C)
    # fleece pullover silhouette filled with pattern
    pat=fleece(); mask=Image.new('L',(1300,1400),0); md=ImageDraw.Draw(mask)
    md.polygon([(330,90),(520,40),(780,40),(970,90),(1250,330),(1180,1250),(1040,1260),(1040,1380),(260,1380),(260,1260),(120,1250),(50,330)],fill=255)
    C.paste(pat.resize((1300,1400)),(60,80),mask)
    d.rectangle([60+560,80+20,60+740,80+120],fill=(70,80,120)); d.polygon([(60+600,80+40),(60+700,80+40),(60+650,80+330)],fill=(60,70,110))
    d.rectangle([60+780,80+300,60+900,80+350],fill=CREAM); d.text((60+840,80+325),'SOIL FOOD WEB',font=f(600,18),fill=MOSS,anchor='mm')
    # tank with patch
    tank=[(1500,160),(1600,140),(1640,260),(1780,290),(1920,260),(1960,140),(2060,160),(2040,420),(2100,700),(2100,1000),(1460,1000),(1460,700),(1520,420)]
    d.polygon(tank,fill=BROWN)
    for x in range(1470,2100,14): d.line([(x,420),(x,1000)],fill=(86,54,34),width=3)
    p=patch().resize((260,303),Image.LANCZOS); C.paste(p,(1650,560))
    # cap
    d.ellipse([2260,260,2860,700],fill=OLIVE); d.rectangle([2240,480,2880,720],fill=(236,236,232))
    d.pieslice([2260,260,2860,700],180,360,fill=OLIVE); d.ellipse([2200,560,2900,760],fill=(84,90,50)); d.pieslice([2260,260,2860,700],180,360,fill=OLIVE)
    d.ellipse([2545,250,2575,280],fill=(84,90,50))
    ic=icon(200,LIME,MAROON); C.paste(ic,(2560-ic.width//2,360),ic)
    # labels
    for x,t in ((710,'Microbe fleece, all-over pattern'),(1780,'Specimen patch crop tank'),(2560,'Embroidered ciliate cap')):
        d.text((x,1560),t,font=f(500,44),fill=(60,60,60),anchor='mm')
    return C,pat
if __name__=='__main__':
    C,pat=board(); C.save('SFW-clothes-round1.jpg',quality=90); pat.save('SFW-fleece-pattern.png')
    patch().save('SFW-specimen-patch.png'); icon(1200,LIME,MAROON).save('SFW-cap-ciliate-embroidery.png')
