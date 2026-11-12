exec(open('tee_organic2.py').read().split("outs=[]")[0])
def panel(seed,fw,fh,n,cols,outw,outh):
    global H_,WW
    H_,WW=fh,fw
    big=jq_fine(organic(seed,n,35),cols)
    return big.resize((outw,outh),Image.NEAREST)
C=[P_BG,P_INK]
front=panel(41,1050,1350,55,C,5250,6750); back=panel(42,1050,1350,55,C,5250,6750)
sl=panel(43,1050,600,22,C,5250,3000); sr=panel(44,1050,600,22,C,5250,3000)
cre=Image.open('/home/claude/merch/logos/SFW-logo-flower-cream.png').convert('RGBA')
white=Image.new('RGBA',cre.size,(255,255,255,255)); white.putalpha(cre.split()[3]); white.save('/home/claude/merch/logos/SFW-logo-flower-white-3000.png')
w=850; lg=white.resize((w,w),Image.LANCZOS); f=front.convert('RGBA'); f.alpha_composite(lg,(3350,1350)); front=f.convert('RGB')
for n,im in [('front',front),('back',back),('sleeve-left',sl),('sleeve-right',sr)]: im.save(f'SFW-aop-tee-microbes-{n}.png')
front.resize((525,675)).save('/tmp/front.png')
