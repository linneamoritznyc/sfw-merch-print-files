exec(open('nbcentre.py').read())
from PIL import ImageDraw
WH=Image.open('/home/claude/merch/logos/SFW-logo-flower-white-3000.png').convert('RGBA')
def coll(seed,W,H,pal,dens):
    bg,ink=PAL[pal]; sc=2; n=max(8,int(W*H/(520*520)*dens))
    Lf,reg=field(seed,W//sc,H//sc,n,30); Lf=np.kron(Lf,np.ones((sc,sc),np.uint8))[:H,:W]
    return Image.fromarray(np.where(Lf[...,None]==1,np.array(ink,np.uint8),np.array(bg,np.uint8))).resize((W,H))
def band(seed,W,H,pal):
    bg,ink=PAL[pal]; im=coll(seed,W,H,pal,2.2).convert('RGBA'); bh=int(H*0.2)
    ImageDraw.Draw(im).rectangle([0,(H-bh)//2,W,(H+bh)//2],fill=ink+(255,))
    s=int(bh*0.82); lg=WH.resize((s,s),Image.LANCZOS)
    # logo in bg colour on ink band
    a=lg.split()[3]; col=Image.new('RGBA',(s,s),bg+(255,)); col.putalpha(a); im.alpha_composite(col,((W-s)//2,(H-s)//2)); return im.convert('RGB')
def window(seed,W,H,pal):
    bg,ink=PAL[pal]; plain=Image.new('RGB',(W,H),ink)
    s=int(W*0.9); lg=WH.resize((s,s),Image.LANCZOS); a=lg.split()[3]
    tex=coll(seed,s,s,pal,6.0)
    out=plain.copy(); out.paste(tex,((W-s)//2,(H-s)//2),a); return out
res=[band(151,1725,2625,'gw'),band(152,1725,2625,'ps'),window(153,1725,2625,'gw'),window(154,1725,2625,'ps')]
for i,r in enumerate(res): r.save(f'SFW-nb-idea-{i}.png')
S=Image.new('RGB',(4*440+10,700),(230,228,222))
for i,im in enumerate(res): t=im.copy(); t.thumbnail((430,680)); S.paste(t,(10+i*440,10))
S.save('SFW-notebook-ideas.jpg',quality=88)
