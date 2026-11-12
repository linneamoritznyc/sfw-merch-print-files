import sys
exec(open('teehq.py').read().split("import sys")[0])
LW=Image.open('/home/claude/merch/logos/SFW-logo-flower-white-3000.png').convert('RGBA')
def collage(W,H,name):
    Lf=field(51,W//2,H//2,30,30); Lf=np.kron(Lf,np.ones((2,2),np.uint8))[:H,:W]
    im=Image.fromarray(np.where(Lf[...,None]==1,np.array(P_INK,np.uint8),np.array(P_BG,np.uint8))).convert('RGBA')
    w=int(W*0.36); im.alpha_composite(LW.resize((w,w),Image.LANCZOS),((W-w)//2,(H-w)//2)); im.convert('RGB').save(name)
collage(1392,2220,'SFW-phonecase-tough-microbe-collage-centre.png')
collage(1396,2304,'SFW-phonecase-samsung-microbe-collage-centre.png')
# olive hyphae for samsung: stretch-fit from iPhone art
src=Image.open('SFW-phonecase-tough-44-macro-hypha.png'); W,H=1396,2304
s=max(W/src.width,H/src.height); r=src.resize((int(src.width*s)+1,int(src.height*s)+1),Image.LANCZOS)
r.crop(((r.width-W)//2,(r.height-H)//2,(r.width-W)//2+W,(r.height-H)//2+H)).save('SFW-phonecase-samsung-44-macro-hypha.png')
S=Image.new('RGB',(3*420+20,700),(226,222,214))
for i,f in enumerate(['SFW-phonecase-tough-microbe-collage-centre.png','SFW-phonecase-samsung-microbe-collage-centre.png','SFW-phonecase-samsung-44-macro-hypha.png']):
    S.paste(Image.open(f).resize((400,650)),(20+i*420,25))
S.save('/tmp/cc.jpg')
