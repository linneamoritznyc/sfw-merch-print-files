exec(open('teehq.py').read().split("import sys")[0])
N=4125; GREEN=(21,104,38); WHITE=(250,249,244)
Lf=field(85,N//2,N//2,22,40); Lf=np.kron(Lf,np.ones((2,2),np.uint8))[:N,:N]
im=Image.fromarray(np.where(Lf[...,None]==1,np.array(WHITE,np.uint8),np.array(GREEN,np.uint8)))
# white border band like a classic bandana
d=ImageDraw.Draw(im); b=110; d.rectangle([0,0,N-1,N-1],outline=WHITE,width=b); d.rectangle([b+40,b+40,N-b-41,N-b-41],outline=WHITE,width=18)
w=620; lg=Image.open('/home/claude/merch/logos/SFW-logo-flower-white-3000.png').convert('RGBA').resize((w,w),Image.LANCZOS)
o=im.convert('RGBA'); gw=w+80
g=Image.new('RGBA',(gw,gw),(0,0,0,0)); ImageDraw.Draw(g).ellipse([0,0,gw-1,gw-1],fill=GREEN+(255,))
cx,cy=N-b-80-gw//2-60,N-b-80-gw//2-60; o.alpha_composite(g,(cx-gw//2,cy-gw//2)); o.alpha_composite(lg,(cx-w//2,cy-w//2))
o.convert('RGB').save('SFW-bandana-green-white.png'); o.convert('RGB').resize((900,900)).save('SFW-bandana-preview.jpg',quality=90)
