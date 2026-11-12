import sys
exec(open('teehq.py').read().split("import sys")[0])
GREEN=(21,104,38); WHITE=(250,249,244)
PAL={'gw':(GREEN,WHITE),'ps':(P_BG,P_INK)}
LOGOW=Image.open('/home/claude/merch/logos/SFW-logo-flower-white-3000.png').convert('RGBA')
def coll(seed,W,H,pal,density=1.0,scale=2):
    global BG
    bg,ink=PAL[pal]; BG=bg
    n=max(8,int(W*H/ (520*520) * density))
    Lf=field(seed,W//scale,H//scale,n,30); Lf=np.kron(Lf,np.ones((scale,scale),np.uint8))[:H,:W]
    return Image.fromarray(np.where(Lf[...,None]==1,np.array(ink,np.uint8),np.array(bg,np.uint8)))
def logo(im,size,pos):
    lg=LOGOW.resize((size,size),Image.LANCZOS); o=im.convert('RGBA')
    W,H=im.size; m=int(min(W,H)*0.06)
    if pos=='br': xy=(W-size-m,H-size-m)
    elif pos=='bc': xy=((W-size)//2,H-size-m)
    elif pos=='c': xy=((W-size)//2,(H-size)//2)
    else: xy=pos
    a=lg.split()[3]; pad=int(size*0.09)
    big=Image.new('L',(size+2*pad,size+2*pad),0); big.paste(a,(pad,pad))
    halo=big.filter(ImageFilter.GaussianBlur(pad/2)).point(lambda v:255 if v>6 else 0).filter(ImageFilter.GaussianBlur(2))
    o.paste(Image.new('RGBA',big.size,BG+(255,)),(xy[0]-pad,xy[1]-pad),halo)
    o.alpha_composite(lg,xy); return o.convert('RGB')
J=[
 ('deskmat',101,5610,3839,'gw',0.22,'br',1.0,3),
 ('mousepad',102,2700,2250,'ps',0.28,'br',1.0,2),
 ('mousepad-round',103,2625,2625,'gw',0.24,(2625//2-315,2625-630-260),1.0,2),
 ('laptop-sleeve',104,2325,1800,'ps',0.26,'br',1.0,2),
 ('ruled-notebook',105,1810,2534,'gw',0.32,'bc',1.0,2),
 ('spiral-journal',106,3113,2138,'ps',0.24,'br',1.0,2),
 ('softcover-journal',107,3714,2475,'gw',0.22,(3714*3//4-330,2475-660-170),1.0,2),
 ('bottle',108,2557,1582,'ps',0.25,(2557*3//4-250,(1582-500)//2),1.0,2),
 ('coaster',109,1181,1181,'gw',0.4,'c',2.5,2),
 ('postcard',110,1842,1240,'ps',0.22,'br',1.6,2),
]
only=sys.argv[1:] 
for name,seed,W,H,pal,lf,pos,dens,sc in J:
    if only and name not in only: continue
    im=coll(seed,W,H,pal,dens,sc)
    im=logo(im,int(min(W,H)*lf),pos)
    im.save(f'SFW-study-{name}-{pal}.png'); print(name,im.size)
