import sys
exec(open('teehq.py').read().split("import sys")[0])
GREEN=(21,104,38); WHITE=(250,249,244)
seeds={'front':91,'back':92,'sleeve_left':93,'sleeve_right':94}
p=sys.argv[1]
Lf=field(seeds[p],2100,2550,30,40); Lf=np.kron(Lf,np.ones((2,2),np.uint8))[:5100,:4200]
Image.fromarray(np.where(Lf[...,None]==1,np.array(WHITE,np.uint8),np.array(GREEN,np.uint8))).save(f'SFW-croptop-{p}.png')
