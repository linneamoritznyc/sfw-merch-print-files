import sys
src=open('pf44.py').read().split("W,H=1392,2220")[0]
exec(src)
OL_=None
cols={'navy':((28,44,82),(158,192,230)),'purple':((107,76,122),(200,182,226)),'deepgreen':((34,55,31),(168,200,120)),'green':((21,104,38),(240,244,234))}
for dev,(WW,HH) in {'tough':(1392,2220),'samsung':(1396,2304)}.items():
  W,H=WW,HH
  for k,(bg,ink) in cols.items():
    sz=4330; PL=[plate_clean(11,ink,sz,0)]; ox,oy=place(0.5,0.45,W//2,int(H*0.473),sz)
    a=macro(bg,ink,11,sz,ox,oy,0,logo_w=480,seed=1); a.save(f'SFW-phonecase-{dev}-44-hypha-{k}.png'); print(dev,k,a.size)
