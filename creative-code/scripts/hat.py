exec(open('tee_organic2.py').read().split("outs=[]")[0])
H_,WW=1575,1350
files={}
for name,seed,cols in [('outside_front',31,[P_BG,P_INK]),('outside_back',32,[P_BG,P_INK]),('inside_front',33,[P_INK,P_BG]),('inside_back',34,[P_INK,P_BG])]:
    big=jq_fine(organic(seed,55,35),cols); big=big.resize((2700,3150)); big.save(f'SFW-bucket-{name}.png'); files[name]=big
S=Image.new('RGB',(4*560+20,700),(226,222,214))
for i,v in enumerate(files.values()): S.paste(v.resize((540,630)),(20+i*560,35))
S.save('SFW-bucket-hat-files-preview.jpg',quality=90)
