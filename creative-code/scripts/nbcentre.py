import sys
src=open('teehq.py').read().split("import sys")[0].replace("    return L\n","    return L,reg\n",1)
exec(src)
GREEN=(21,104,38); WHITE=(250,249,244)
PAL={'gw':(GREEN,WHITE),'ps':(P_BG,P_INK)}
LOGOW=Image.open('/home/claude/merch/logos/SFW-logo-flower-white-3000.png').convert('RGBA')
def cover(seed,W,H,pal,logo_frac=0.42,dens=1.0,cx=None):
    cx=W//2 if cx is None else cx
    bg,ink=PAL[pal]; sc=2
    n=max(8,int(W*H/(520*520)*dens))
    Lf,reg=field(seed,W//sc,H//sc,n,30)
    h2,w2=reg.shape; yy,xx=np.mgrid[0:h2,0:w2]; rr=min(min(W,H),H)//sc*logo_frac*0.5
    ks=np.unique(reg[((yy-h2/2)**2+(xx-cx/sc)**2)<rr**2]); Lf[np.isin(reg,ks)]=0
    Lf=np.kron(Lf,np.ones((sc,sc),np.uint8))[:H,:W]
    im=Image.fromarray(np.where(Lf[...,None]==1,np.array(ink,np.uint8),np.array(bg,np.uint8))).resize((W,H))
    s=int(min(W,H)*logo_frac); lg=LOGOW.resize((s,s),Image.LANCZOS); o=im.convert('RGBA'); o.alpha_composite(lg,(cx-s//2,(H-s)//2)); return o.convert('RGB')
