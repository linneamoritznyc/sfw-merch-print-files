import sys, math, random, numpy as np
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS=None
W,H=4961,7016
L='/home/claude/merch/logos/'
def logo(im,path,w=760,m=300):
    o=im.convert('RGBA'); lg=Image.open(path).convert('RGBA').resize((w,w),Image.LANCZOS); o.alpha_composite(lg,(W-m-w,H-m-w)); return o.convert('RGB')
which=sys.argv[1]
if which=='collage':
    exec(open('teehq.py').read().split("import sys")[0])
    Lf=field(61,W//2,H//2,70,60); Lf=np.kron(Lf,np.ones((2,2),np.uint8))[:H,:W]
    im=Image.fromarray(np.where(Lf[...,None]==1,np.array(P_INK,np.uint8),np.array(P_BG,np.uint8)))
    logo(im,L+'SFW-logo-flower-white-3000.png').save('SFW-poster2-A2-microbe-collage.png')
if which=='collage-green':
    exec(open('teehq.py').read().split("import sys")[0])
    Lf=field(77,W//2,H//2,45,60); Lf=np.kron(Lf,np.ones((2,2),np.uint8))[:H,:W]
    im=Image.fromarray(np.where(Lf[...,None]==1,np.array((190,214,90),np.uint8),np.array((34,55,31),np.uint8)))
    logo(im,L+'SFW-logo-flower-deepgreen.png').save('SFW-poster2-A2-microbe-collage-green.png')
if which=='discs':
    exec(open('discs.py').read().split("def grid(")[0])
    r=random.Random(9); im=Image.new('RGB',(W,H),(34,55,31)); R=380; gap=40; dx=2*R+gap; dy=dx*math.sqrt(3)/2
    y=-R/3; row=0
    while y<H+R:
        x=(-R/2 if row%2 else R/2)
        while x<W+R:
            if not (x>W-1300 and y>H-1300):
                dd=disc(R,r.randrange(16),r.choice(PALS),r.choice([0,90,180,270]),24); im.paste(dd,(int(x-R),int(y-R)),dd)
            x+=dx
        y+=dy; row+=1
    logo(im,L+'SFW-logo-flower-cream.png').save('SFW-poster2-A2-specimen-discs.png')
if which=='ikat':
    exec(open('cases4.py').read().split("specs=[")[0])
    W,H=2480,3508
    B=ikat(bands(5,3,(600,900)),7); img=finish(compose(B,PUR,SAGE,7)).resize((4961,7016),Image.NEAREST)
    W,H=4961,7016; logo(img,L+'SFW-logo-flower-colour.png').save('SFW-poster2-A2-ikat-purple.png')
