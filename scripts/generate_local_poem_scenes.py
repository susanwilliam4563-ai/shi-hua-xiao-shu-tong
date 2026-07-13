from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import hashlib, math, random

OUT = Path(__file__).resolve().parents[1] / "public" / "images"
SCENES = {
    "jiang-nan": "lotus fish summer water",
    "hua": "mountain waterfall flowers birds",
    "yong-e": "white goose green water red feet",
    "min-nong-er": "farmer field noon sun grain",
    "gu-lang-yue-xing": "large moon clouds jade plate",
    "feng": "wind leaves flowers waves bamboo",
    "jing-ye-si": "moon window frost traveler",
    "chun-xiao": "spring birds rain fallen petals",
    "cun-ju": "willow children kite spring",
    "xiao-chi": "pond lotus dragonfly shade",
    "mei-hua": "plum blossom snow wall winter",
    "xiao-er-chui-diao": "child fishing grass pond",
    "jiang-xue": "snow mountains lone boat fisherman",
    "ye-su-shan-si": "high temple stars night",
    "chi-le-ge": "grassland mountain cattle sheep",
    "deng-guan-que-lou": "tower sunset yellow river",
    "wang-lu-shan-pu-bu": "high waterfall purple mist sun",
    "jue-ju": "willow orioles egrets snow boat",
    "fu-de-gu-yuan-cao": "grassland wildfire new shoots",
    "shan-xing": "autumn mountain red maple path",
    "zeng-liu-jing-wen": "late autumn lotus chrysanthemum oranges",
    "ye-shu-suo-jian": "autumn leaves fence lamp child",
    "wang-tian-men-shan": "river twin mountains sail sun",
    "yin-hu-shang": "west lake sunshine rain mist pavilion",
    "wang-dong-ting": "autumn moon lake island",
}

W, H = 720, 480

def seed_for(name): return int(hashlib.sha256(name.encode()).hexdigest()[:12], 16)

def wash(draw, rng, y, color, count=12):
    for _ in range(count):
        x=rng.randint(-100,W); yy=y+rng.randint(-45,45); rx=rng.randint(90,260)
        draw.ellipse((x-rx,yy-35,x+rx,yy+35), fill=color)

def mountains(draw, rng, snow=False):
    # 不规则长山势配合多层半透明干笔，避免规则三角形的扁平矢量感。
    for layer,(base,col) in enumerate([(300,(91,119,106,38)),(365,(65,92,80,52)),(430,(42,67,57,68))]):
        points=[(-50,H),(-50,base)]; x=-50
        while x<W+80:
            width=rng.randint(115,220); peak=base-rng.randint(50,145)
            points.extend([(x+width*.18,base-rng.randint(8,35)),(x+width*.42,peak),(x+width*.58,peak+rng.randint(10,45)),(x+width,base+rng.randint(-8,22))]); x+=width
        points.extend([(W+50,H)]); draw.polygon(points,fill=col)
        for _ in range(45):
            x1=rng.randint(0,W); y1=rng.randint(max(50,base-150),base); length=rng.randint(15,70)
            draw.line((x1,y1,x1-rng.randint(4,30),min(base,y1+length)),fill=(37,55,47,rng.randint(8,25)),width=rng.randint(1,4))
        if snow:
            for i in range(5):
                x=70+i*145+rng.randint(-25,25); y=base-rng.randint(65,125)
                draw.polygon([(x,y),(x-25,y+42),(x,y+32),(x+24,y+44)],fill=(245,244,235,145))
    for y in (300,365): wash(draw,rng,y,(248,244,229,48),7)

def tree(draw,x,y,scale=1,autumn=False,plum=False,willow=False):
    ink=(59,67,54,220); draw.line((x,y,x-8*scale,y-150*scale),fill=ink,width=max(3,int(9*scale)))
    for a in [-2.5,-2,-1.3,-.7]:
        ex=x+math.cos(a)*75*scale; ey=y-110*scale+math.sin(a)*55*scale
        draw.line((x-5*scale,y-105*scale,ex,ey),fill=ink,width=max(2,int(5*scale)))
    color=(181,61,43,175) if autumn else (83,135,91,150)
    if willow:
        color=(105,153,92,145)
        for k in range(12):
            xx=x-80*scale+k*13*scale
            draw.arc((xx,y-175*scale,xx+80*scale,y-35*scale),0,100,fill=color,width=max(2,int(3*scale)))
    else:
        for k in range(24):
            ang=k*2.4; xx=x+math.sin(ang)*rng_local(k)*72*scale; yy=y-145*scale+math.cos(ang)*45*scale
            r=(5 if plum else 13)*scale
            draw.ellipse((xx-r,yy-r,xx+r,yy+r),fill=((205,81,105,210) if plum else color))

def rng_local(k): return .35 + ((k*37)%61)/100

def boat(draw,x,y,s=1,person=False):
    draw.polygon([(x-70*s,y),(x+75*s,y),(x+45*s,y+24*s),(x-50*s,y+24*s)],fill=(92,63,42,230))
    draw.line((x,y,x,y-95*s),fill=(70,55,45,230),width=max(2,int(4*s)))
    draw.polygon([(x+3*s,y-90*s),(x+3*s,y-15*s),(x+55*s,y-28*s)],fill=(238,225,190,220))
    if person:
        draw.ellipse((x-28*s,y-38*s,x-15*s,y-25*s),fill=(43,43,38,235)); draw.line((x-21*s,y-25*s,x-21*s,y),fill=(43,43,38,235),width=max(2,int(5*s)))

def add_scene(draw,rng,key,tags):
    night=any(x in tags for x in ['moon','night','stars']); snow='snow' in tags
    if night:
        draw.rectangle((0,0,W,H),fill=(36,61,75,105))
        draw.ellipse((690,65,805,180),fill=(250,238,190,235))
        if 'stars' in tags:
            for _ in range(45):
                x=rng.randrange(W); y=rng.randrange(300); draw.ellipse((x,y,x+3,y+3),fill=(252,239,188,210))
    mountains(draw,rng,snow)
    if any(x in tags for x in ['water','river','lake','pond','waterfall']):
        wash(draw,rng,505,(82,151,162,58),16)
        for i in range(7): draw.arc((-80+i*170,465+rng.randint(-8,8),170+i*170,545),190,350,fill=(61,125,139,120),width=3)
    if 'sun' in tags or 'sunset' in tags or 'noon' in tags:
        draw.ellipse((735,70,850,185),fill=(218,91,48,210))
    if 'waterfall' in tags:
        draw.rounded_rectangle((470,155,545,500),30,fill=(231,241,229,220)); draw.ellipse((420,465,610,530),fill=(225,239,231,175))
    if any(x in tags for x in ['willow','spring']): tree(draw,170,525,1.15,willow=True)
    if 'autumn' in tags or 'maple' in tags: tree(draw,760,520,1.15,autumn=True)
    if 'plum' in tags: tree(draw,250,535,1.2,plum=True)
    if 'lotus' in tags:
        for i in range(11):
            x=90+i*76+rng.randint(-18,18); y=475+rng.randint(-15,70)
            draw.ellipse((x-35,y-12,x+35,y+12),fill=(68,137,88,180)); draw.line((x,y,x,y-55),fill=(55,112,70,160),width=3)
            if i%3==0: draw.ellipse((x-10,y-70,x+10,y-48),fill=(221,106,136,210))
    if 'goose' in tags:
        draw.ellipse((350,420,505,505),fill=(247,244,225,245)); draw.arc((430,310,535,450),120,300,fill=(247,244,225,245),width=24); draw.ellipse((490,305,540,350),fill=(247,244,225,245)); draw.polygon([(536,328),(570,340),(536,344)],fill=(218,106,45,240))
    if 'fish' in tags:
        for x,y in [(260,540),(570,510),(730,560)]: draw.ellipse((x,y,x+55,y+24),fill=(202,102,63,180)); draw.polygon([(x,y+12),(x-18,y),(x-18,y+24)],fill=(202,102,63,180))
    if any(x in tags for x in ['boat','sail']): boat(draw,650,505,.8,person='fisherman' in tags)
    if 'fisherman' in tags: boat(draw,480,505,.8,True)
    if 'tower' in tags or 'temple' in tags or 'pavilion' in tags:
        x=610; base=455; floors=3 if ('tower' in tags or 'temple' in tags) else 1
        for f in range(floors):
            y=base-f*62; draw.rectangle((x-55,y-48,x+55,y),fill=(166,119,72,230)); draw.polygon([(x-85,y-50),(x+85,y-50),(x+55,y-70),(x-55,y-70)],fill=(58,78,67,235))
    if 'kite' in tags:
        draw.polygon([(650,180),(690,215),(650,250),(610,215)],fill=(210,85,71,220)); draw.arc((300,220,660,540),270,350,fill=(75,70,60,180),width=2)
    if any(x in tags for x in ['birds','orioles','egrets']):
        for i in range(7):
            x=520+i*42; y=175+(i%3)*25; draw.arc((x,y,x+25,y+15),190,350,fill=(42,54,49,210),width=3); draw.arc((x+22,y,x+47,y+15),190,350,fill=(42,54,49,210),width=3)
    if 'bamboo' in tags:
        for i in range(9):
            x=665+i*25; draw.line((x,540,x-80+rng.randint(-15,15),225),fill=(52,105,67,210),width=7)
    if 'farmer' in tags or 'child' in tags or 'traveler' in tags:
        x=400 if 'farmer' in tags else 300; y=500
        draw.ellipse((x-14,y-78,x+14,y-50),fill=(57,50,42,235)); draw.line((x,y-50,x,y),fill=(67,60,48,235),width=9); draw.line((x,y-30,x-30,y-5),fill=(67,60,48,235),width=6); draw.line((x,y-30,x+28,y-8),fill=(67,60,48,235),width=6)
    if 'cattle' in tags or 'sheep' in tags:
        for i in range(8):
            x=130+i*95; y=495+rng.randint(-10,50); col=(246,239,210,235) if i%2 else (93,76,55,230)
            draw.ellipse((x,y,x+48,y+28),fill=col); draw.ellipse((x+39,y+5,x+57,y+23),fill=col)
    if 'dragonfly' in tags:
        draw.line((615,365,650,340),fill=(37,71,67,240),width=4); draw.ellipse((600,342,630,355),fill=(116,184,186,155)); draw.ellipse((628,326,662,340),fill=(116,184,186,155))
    if 'flowers' in tags or 'chrysanthemum' in tags:
        for i in range(18):
            x=80+i*47; y=500+rng.randint(-10,70); col=(222,153,58,210) if 'chrysanthemum' in tags else (219,97,118,190)
            draw.ellipse((x-8,y-8,x+8,y+8),fill=col)
    if 'lamp' in tags:
        draw.rectangle((700,395,720,450),fill=(105,58,38,230)); draw.ellipse((680,365,740,425),fill=(246,184,73,220))
    if snow:
        for _ in range(150):
            x=rng.randrange(W); y=rng.randrange(H); r=rng.choice([1,2,3]); draw.ellipse((x-r,y-r,x+r,y+r),fill=(250,250,244,210))

def render(key,tags):
    rng=random.Random(seed_for(key)); img=Image.new('RGBA',(W,H),(244,238,218,255)); d=ImageDraw.Draw(img,'RGBA')
    wash(d,rng,130,(235,194,151,28),12); wash(d,rng,280,(172,196,173,25),10)
    add_scene(d,rng,key,tags.split())
    texture=Image.new('RGBA',(W,H),(0,0,0,0)); td=ImageDraw.Draw(texture,'RGBA')
    for _ in range(7000):
        x=rng.randrange(W); y=rng.randrange(H); v=rng.choice([(75,61,45,8),(255,255,245,10)]); td.point((x,y),fill=v)
    img=Image.alpha_composite(img,texture).convert('RGB')
    # 宣纸颗粒、柔和晕染与墨线叠印，形成淡彩水墨而非扁平插画。
    softened=img.filter(ImageFilter.GaussianBlur(1.7))
    edges=img.filter(ImageFilter.FIND_EDGES).convert('L').point(lambda x: 255-x)
    ink=Image.new('RGB',(W,H),(50,55,47))
    img=Image.blend(img,softened,.42)
    img=Image.composite(ink,img,edges.point(lambda x: 44 if x<150 else 0))
    img.save(OUT/f"{key}.webp",'WEBP',quality=72,method=6)

OUT.mkdir(parents=True,exist_ok=True)
for key,tags in SCENES.items(): render(key,tags)
for size,name in [(192,'app-icon.png'),(512,'app-icon-512.png')]:
    icon=Image.new('RGB',(size,size),(246,239,220)); d=ImageDraw.Draw(icon)
    d.ellipse((size*.18,size*.14,size*.82,size*.78),fill=(211,229,217),outline=(42,92,74),width=max(3,size//40))
    d.line((size*.5,size*.67,size*.5,size*.36),fill=(42,92,74),width=max(5,size//22))
    d.ellipse((size*.35,size*.32,size*.51,size*.47),fill=(77,135,93)); d.ellipse((size*.49,size*.25,size*.67,size*.41),fill=(77,135,93))
    d.rectangle((size*.28,size*.68,size*.72,size*.79),fill=(178,91,60))
    icon.save(OUT/name,optimize=True)
print(f"generated {len(SCENES)} lightweight ink-wash images in {OUT}")
