import numpy as np, math, random
from PIL import Image, ImageDraw, ImageFilter
def mycelium(S=2400, seeds=4, steps=900, seed=3, bg=(46,58,28), line=(203,214,150), spore=(150,110,190), width=3):
    random.seed(seed); np.random.seed(seed)
    im=Image.new('RGBA',(S,S),bg+(255,)); d=ImageDraw.Draw(im)
    tips=[]
    for _ in range(seeds):
        x,y=random.uniform(0,S),random.uniform(0,S)
        for k in range(random.randint(3,5)):
            tips.append([x,y,random.uniform(0,2*math.pi),width*2.2,0])
    spores=[]
    for it in range(steps):
        new=[]
        for t in tips:
            x,y,a,w,age=t
            a+=random.gauss(0,0.22); L=random.uniform(5,9)
            nx,ny=x+L*math.cos(a),y+L*math.sin(a)
            for ox in (-S,0,S):
                for oy in (-S,0,S):
                    d.line([(x+ox,y+oy),(nx+ox,ny+oy)],fill=line+(255,),width=max(1,int(round(w))))
            t[0],t[1],t[2]=nx%S,ny%S,a; t[3]=max(1.0,w*0.997); t[4]+=1
            # wrap continuity: if wrapped, adjust
            if random.random()<0.012 and len(tips)+len(new)<220:
                new.append([t[0],t[1],a+random.choice([-1,1])*random.uniform(0.5,1.1),t[3]*0.8,0])
            if random.random()<0.0012: spores.append((t[0],t[1]))
        tips=[t for t in tips if t[4]<random.randint(140,320)]+new
        if not tips: break
    for (x,y) in spores:
        r=random.uniform(5,11)
        for ox in (-S,0,S):
            for oy in (-S,0,S):
                d.ellipse([x-r+ox,y-r+oy,x+r+ox,y+r+oy],fill=spore+(255,))
    return im
if __name__=='__main__':
    m=mycelium(); m.save('tile_myc_olive.png')
    m.convert('RGB').resize((800,800)).save('/tmp/myc_tile.png')
