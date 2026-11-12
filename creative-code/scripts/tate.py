import sys
exec(open('teehq.py').read().split("import sys")[0])
from PIL import ImageFont
W,H=4961,7016
CR=(244,241,234)
def img(seed,w,h,bg,ink,n):
    L=field(seed,w//4,h//4,n,40); L=np.asarray(Image.fromarray(L*255).resize((w,h),Image.BICUBIC).filter(ImageFilter.GaussianBlur(3)))>127
    return Image.fromarray(np.where(L[...,None]==1,np.array(ink,np.uint8),np.array(bg,np.uint8)))
def poster(seed,bg,ink,paper,txt,n=3,title='Soil Life'):
    P=Image.new('RGB',(W,H),paper); m=300
    ih=int(H*0.72); P.paste(img(seed,W-2*m,ih,bg,ink,n),(m,m))
    d=ImageDraw.Draw(P)
    fT=ImageFont.truetype('ebg500.ttf',520); fS=ImageFont.truetype('ebg400i.ttf',150); fM=ImageFont.truetype('ebg400.ttf',105)
    y=m+ih+170
    d.text((m,y),title,font=fT,fill=txt)
    d.text((m,H-m-105),'Soil Food Web Foundation',font=fM,fill=txt)
    lg=Image.open('/home/claude/merch/logos/SFW-logo-flower-colour.png' if paper==CR else '/home/claude/merch/logos/SFW-logo-flower-white-3000.png').convert('RGBA').resize((720,720),Image.LANCZOS)
    o=P.convert('RGBA'); o.alpha_composite(lg,(W-m-720,H-m-720)); return o.convert('RGB')
res=[poster(201,P_BG,P_INK,CR,P_BG),poster(202,(21,104,38),CR,CR,(21,104,38)),poster(203,(28,44,82),(158,192,230),(28,44,82),(158,192,230))]
for i,r in enumerate(res): r.save(f'SFW-poster-A2-tate-{i}.png')
S=Image.new('RGB',(3*510+10,730),(230,228,222))
for i,im in enumerate(res): t=im.copy(); t.thumbnail((500,710)); S.paste(t,(10+i*510,10))
S.save('SFW-posters-tate-preview.jpg',quality=88)
