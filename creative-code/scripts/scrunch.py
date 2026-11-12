import sys
exec(open('teehq.py').read().split("import sys")[0])
W,H=6000,1500
GREEN=(21,104,38); WHITE=(250,249,244); LG=(89,166,108)
def make(seed,bg,ink,name):
    Lf=field(seed,W//2,H//2,26,30); Lf=np.kron(Lf,np.ones((2,2),np.uint8))[:H,:W]
    im=Image.fromarray(np.where(Lf[...,None]==1,np.array(ink,np.uint8),np.array(bg,np.uint8))); im.save(f'SFW-scrunchie-{name}.png'); return im
a=make(81,GREEN,WHITE,'green-white'); b=make(82,WHITE,GREEN,'white-green'); c=make(83,GREEN,LG,'green-tonal')
S=Image.new('RGB',(1520,3*400+40),(226,222,214))
for i,v in enumerate([a,b,c]): S.paste(v.resize((1500,375)),(10,10+i*400))
S.save('SFW-scrunchie-preview.jpg',quality=90)
