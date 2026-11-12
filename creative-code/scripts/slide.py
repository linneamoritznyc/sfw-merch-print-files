import random
from PIL import Image
def tint(i,c,size):
    im=Image.open(f'/home/claude/merch/micro/plate_{i}.png').convert('RGBA').resize((size,size),Image.LANCZOS)
    o=Image.new('RGBA',im.size,c);o.putalpha(im.split()[3]);return o
def scatter(S=2400,bg=(46,58,28),cols=[(203,214,150),(150,110,190),(110,160,210)],weights=[6,2,2],n=46,seed=5):
    random.seed(seed); im=Image.new('RGBA',(S,S),bg+(255,)); placed=[]
    tries=0
    while len(placed)<n and tries<5000:
        tries+=1; r=random.choice([90,120,150,190,240]); x,y=random.uniform(0,S),random.uniform(0,S)
        ok=all(((x-px)%S if (x-px)%S<S/2 else S-(x-px)%S)**2+(((y-py)%S if (y-py)%S<S/2 else S-(y-py)%S))**2>(r+pr+18)**2 for px,py,pr in placed)
        if not ok: continue
        placed.append((x,y,r)); c=random.choices(cols,weights)[0]; t=tint(random.randrange(16),c,2*r)
        for ox in (-S,0,S):
            for oy in (-S,0,S): im.alpha_composite(t,(int(x-r+ox),int(y-r+oy))) if 0<=int(x-r+ox)<=S-2*r and 0<=int(y-r+oy)<=S-2*r else im.paste(t,(int(x-r+ox),int(y-r+oy)),t)
    return im
if __name__=='__main__':
    s=scatter(); s.save('tile_slide_olive.png'); s.convert('RGB').resize((800,800)).save('/tmp/slide.png')
