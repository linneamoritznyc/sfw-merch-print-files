import numpy as np, glob
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageCms
from scipy.ndimage import gaussian_filter
Image.MAX_IMAGE_PIXELS=None
M='/home/claude/merch/micro/'; B='/home/claude/merch/brand/'
ICC=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
W,H=3600,4800
def panel(src,cx,cy,cw,ch,w,h,rot=0):
    im=ImageOps.grayscale(Image.open(src).convert('RGB'))
    if rot: im=im.rotate(rot,expand=False,fillcolor=int(np.median(np.asarray(im))))
    iw,ih=im.size
    cw=ch*ih*w/h/iw
    box=(int((cx-cw/2)*iw),int((cy-ch/2)*ih),int((cx+cw/2)*iw),int((cy+ch/2)*ih))
    g=np.asarray(im.crop(box).resize((w,h),Image.LANCZOS)).astype(np.float32)
    loc=g-gaussian_filter(g,w/10)                      # local darkness
    t=gaussian_filter(-loc,1.4)
    ink=t>np.percentile(t,58)                          # organism + texture
    dark=gaussian_filter(g,2)<np.percentile(g,22)      # solid dark bodies
    m=(ink|dark).astype(np.float32)
    return gaussian_filter(m,1.0)                      # 0..1 soft edge, thresholded later
def make(ink=(110,40,46),name='SFW-concert-tee-lineup'):
    A=np.zeros((H,W),np.float32)
    members=[(M+'circ_stalked-ciliates.png',0.72,0.50,0.36,0.62,'CILIATE'),
             (M+'circ_nematode.png',0.50,0.50,0.30,0.62,'NEMATODE'),
             ([f for f in glob.glob(M+'*.jpg') if 'Testate amoebae' in f][0],0.34,0.62,0.27,0.66,'TESTATE'),
             ([f for f in glob.glob(M+'*.jpg') if 'Amoeba cyst' in f][0],0.53,0.47,0.17,0.42,'AMOEBA'),
             ([f for f in glob.glob(M+'*.jpg') if 'Fungal spore' in f][0],0.47,0.47,0.30,0.72,'FUNGUS',75)]
    pw,ph=660,1300; x0=(W-5*pw)//2; y0=720
    for i,mm in enumerate(members):
        s,cx,cy,cw,ch=mm[:5]; rot=mm[6] if len(mm)>6 else 0
        A[y0:y0+ph,x0+i*pw:x0+(i+1)*pw]=panel(s,cx,cy,cw,ch,pw,ph,rot)
    # ragged photo edge: keep inside a slightly rough rectangle
    rnd=np.random.default_rng(2); yy,xx=np.mgrid[0:H,0:W]
    edge=gaussian_filter(rnd.random((H,W)),3)
    inside=(xx>x0+ (edge-0.5)*40)&(xx<x0+5*pw-(edge-0.5)*40)&(yy>y0+(edge-0.5)*40)&(yy<y0+ph-(edge-0.5)*40)
    A*=inside
    a=(A>0.5).astype(np.uint8)*255
    P=Image.new('RGBA',(W,H),(0,0,0,0)); P.paste(Image.new('RGBA',(W,H),ink+(255,)),(0,0),Image.fromarray(a))
    d=ImageDraw.Draw(P)
    def spaced(y,t,size,sp,wt=600):
        f=ImageFont.truetype(B+f'ebg{wt}.ttf',size); tw=sum(d.textlength(c,font=f) for c in t)+sp*(len(t)-1); x=(W-tw)/2
        for c in t: d.text((x,y),c,font=f,fill=ink+(255,)); x+=d.textlength(c,font=f)+sp
    tsz=480
    while True:
        f=ImageFont.truetype(B+'ebg600.ttf',tsz); tw=sum(d.textlength(c,font=f) for c in 'SOIL FOOD WEB')+10*12
        if tw<=5*pw: break
        tsz-=4
    spaced(140,'SOIL FOOD WEB',tsz,10)
    f=ImageFont.truetype(B+'ebg600.ttf',96)
    for i,m in enumerate(members):
        pass
    rows=[(['BACTERIA','EARTHWORMS'],250,600,14,1.55),
          (['MYCORRHIZAL FUNGI','SPRINGTAILS','MITES'],150,600,9,1.6),
          (['FLAGELLATES','TARDIGRADES','ROTIFERS','ARCHAEA'],112,600,7,1.65),
          (['ACTINOMYCETES','ENCHYTRAEIDS','PAUROPODS','VAMPYRELLIDS'],86,500,6,2.0),
          ('AND INTRODUCING',56,500,22,1.9),
          (['TRICHODERMA','STREPTOMYCES','RHIZOBIUM','BACILLUS','MORTIERELLA'],64,500,5,1.7),
          (['ARTHROBOTRYS','COLPODA','VORTICELLA','ARCELLA','DIFFLUGIA','PROTURANS'],52,500,4,1.0)]
    y=y0+ph+150; maxw=0.94*5*pw
    for names,size,wt,sp,lh in rows:
        t=names if isinstance(names,str) else '  ·  '.join(names)
        while True:
            f=ImageFont.truetype(B+f'ebg{wt}.ttf',size); tw=sum(d.textlength(c,font=f) for c in t)+sp*(len(t)-1)
            if tw<=maxw: break
            size-=2
        spaced(y,t,size,sp,wt); y+=int(size*lh)
    y+=150
    d.rectangle([x0,y,x0+5*pw,y+12],fill=ink+(255,)); y+=70
    spaced(y,'2027 WORLD TOUR',250,34,600); y+=360
    d.rectangle([x0,y,x0+5*pw,y+12],fill=ink+(255,)); y+=70
    spaced(y,'LIVE BENEATH YOUR FEET',120,30,500)
    # worn vintage print: small cracks and specks knocked out of the ink
    al=np.asarray(P.split()[3]).astype(np.float32)/255
    r=np.random.default_rng(7)
    n1=gaussian_filter(r.random((H,W)),2.2); n2=gaussian_filter(r.random((H,W)),14)
    holes=(n1>np.percentile(n1,93))&(n2>np.percentile(n2,45))
    cr=gaussian_filter(r.random((H,W)),1.0); holes|=(cr>np.percentile(cr,99.2))
    al=np.where(holes,0,al)
    P.putalpha(Image.fromarray(((al>0.5)*255).astype(np.uint8)))
    P=P.crop(P.getbbox()); P.save(B+name+'.png',icc_profile=ICC,dpi=(300,300)); return P
if __name__=='__main__':
    P=make()
    M2=Image.new('RGB',(1400,1600),(232,232,232)); d=ImageDraw.Draw(M2)
    d.polygon([(380,120),(560,80),(840,80),(1020,120),(1330,330),(1220,560),(1080,480),(1080,1520),(320,1520),(320,480),(180,560),(70,330)],fill=(178,178,176))
    d.ellipse([560,40,840,170],fill=(232,232,232))
    pw=640; p=P.resize((pw,int(pw*P.height/P.width)),Image.LANCZOS); M2.paste(p,((1400-pw)//2,250),p)
    M2.save(B+'SFW-concert-tee-lineup-preview.jpg',quality=90)
    q=Image.new('RGBA',P.size,(178,178,176,255)); q.alpha_composite(P); q.convert('RGB').resize((P.width//3,P.height//3),Image.LANCZOS).save(B+'SFW-concert-tee-lineup-flat.jpg',quality=90)
