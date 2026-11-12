import sys
exec(open('teehq.py').read().split("import sys")[0])
which=sys.argv[1]
def pan(seed,inv):
    Lf=field(seed,1350,1575,22,40); Lf=np.kron(Lf,np.ones((2,2),np.uint8))[:3150,:2700]
    if inv: Lf=1-Lf
    return stitch(Lf,10,13)
im=pan({'of':71,'ob':72,'if':73,'ib':74}[which], which[0]=='i')
if which=='of':
    lg=Image.open('/home/claude/merch/logos/SFW-logo-flower-white-3000.png').convert('RGBA').resize((520,520),Image.LANCZOS)
    o=im.convert('RGBA'); o.alpha_composite(lg,(int(2700*0.70)-260,int(3150*0.55)-260)); im=o.convert('RGB')
im.save(f'SFW-bucket-v2-{which}.png')
