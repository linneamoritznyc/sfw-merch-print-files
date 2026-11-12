exec(open('nbideas.py').read().split("res=[")[0])
PAL.update({'mg':((28,64,34),(21,104,38)),'mk':((28,28,28),(244,241,234)),'mp':((78,58,92),(107,76,122))})
def band2(seed,W,H,pal,dens=6.0,bandcol=None,logocol=None):
    bg,ink=PAL[pal]; im=coll(seed,W,H,pal,dens).convert('RGBA'); bh=int(H*0.2)
    bc=bandcol or ink; lc=logocol or bg
    ImageDraw.Draw(im).rectangle([0,(H-bh)//2,W,(H+bh)//2],fill=bc+(255,))
    s=int(bh*0.82); a=WH.resize((s,s),Image.LANCZOS).split()[3]; col=Image.new('RGBA',(s,s),lc+(255,)); col.putalpha(a); im.alpha_composite(col,((W-s)//2,(H-s)//2)); return im.convert('RGB')
CR=(244,241,234)
res=[band2(171,1725,2625,'gw'),band2(172,1725,2625,'ps'),band2(173,1725,2625,'mg',bandcol=CR,logocol=(21,104,38)),band2(174,1725,2625,'mk'),band2(175,1725,2625,'mp',bandcol=(200,182,226),logocol=(78,58,92))]
for i,r in enumerate(res): r.save(f'SFW-nb-band-{i}.png')
S=Image.new('RGB',(5*350+10,560),(230,228,222))
for i,im in enumerate(res): t=im.copy(); t.thumbnail((340,540)); S.paste(t,(10+i*350,10))
S.save('SFW-notebook-band-v2.jpg',quality=88)
