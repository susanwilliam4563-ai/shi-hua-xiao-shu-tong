"""Generate the 25 original, offline poem illustrations used by the site.

The drawings are deterministic and built from local vector-like primitives.  Each
poem owns a separate composition so an object is never borrowed from an unrelated
poem merely because it is convenient.  We render large and downsample to WebP for
clean edges and a small offline bundle.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import hashlib
import json
import math
import random


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "images"
W, H = 1080, 720
FINAL = (720, 480)
PAPER = (248, 244, 232, 255)
INK = (38, 59, 51, 235)
JADE = (57, 112, 90, 220)
PALE_JADE = (157, 190, 166, 135)
WATER = (93, 155, 164, 185)
CINNABAR = (190, 78, 56, 230)
GOLD = (223, 164, 71, 230)

SCENES = {
    "jiang-nan": ("江南", "层层莲叶、粉荷、穿行的小鱼"),
    "hua": ("画", "画轴中的远山、无声流水、常开花朵与安静小鸟"),
    "yong-e": ("咏鹅", "曲颈白鹅、绿水、红掌与清波"),
    "min-nong-er": ("悯农（其二）", "正午烈日、锄禾农人、汗水与稻田"),
    "gu-lang-yue-xing": ("古朗月行（节选）", "孩童仰望玉盘般的圆月与青云"),
    "feng": ("风", "被风吹动的秋叶、春花、江浪和竹林"),
    "jing-ye-si": ("静夜思", "窗前月光、地上如霜与思乡旅人"),
    "chun-xiao": ("春晓", "春日清晨、啼鸟、雨痕与满地落花"),
    "cun-ju": ("村居", "二月新草、黄莺、拂堤杨柳与儿童纸鸢"),
    "xiao-chi": ("小池", "泉眼、树阴、小荷尖角与停立的蜻蜓"),
    "mei-hua": ("梅花", "雪中墙角、独放白梅与暗香"),
    "xiao-er-chui-diao": ("小儿垂钓", "草边侧坐垂钓的孩子与远处问路人"),
    "jiang-xue": ("江雪", "空寂雪山、寒江孤舟与蓑笠渔翁"),
    "ye-su-shan-si": ("夜宿山寺", "星空、高山寺楼与轻声仰望的人"),
    "chi-le-ge": ("敕勒歌", "阴山、穹庐般长空、低草与牛羊"),
    "deng-guan-que-lou": ("登鹳雀楼", "落日依山、黄河远流与层层高楼"),
    "wang-lu-shan-pu-bu": ("望庐山瀑布", "香炉峰紫烟与从云天飞落的瀑布"),
    "jue-ju": ("绝句", "翠柳黄鹂、青天白鹭、西岭雪与门外船"),
    "fu-de-gu-yuan-cao": ("赋得古原草送别（节选）", "枯荣草原、远处野火与春风新芽"),
    "shan-xing": ("山行", "寒山石径、白云人家、停车与红枫"),
    "zeng-liu-jing-wen": ("赠刘景文", "残荷、傲霜菊与橙黄橘绿"),
    "ye-shu-suo-jian": ("夜书所见", "秋夜梧叶、江风、篱落儿童与一灯明"),
    "wang-tian-men-shan": ("望天门山", "天门对峙、碧水回旋与日边孤帆"),
    "yin-hu-shang": ("饮湖上初晴后雨", "西湖晴光与烟雨山色相接"),
    "wang-dong-ting": ("望洞庭", "秋月、镜面洞庭与青螺般君山"),
}


def seed_for(name):
    return int(hashlib.sha256(name.encode()).hexdigest()[:12], 16)


def overlay(img):
    return Image.new("RGBA", img.size, (0, 0, 0, 0))


def paper(rng, night=False):
    if night:
        top, bottom = (31, 55, 65), (63, 87, 86)
    else:
        top, bottom = (249, 246, 235), (238, 234, 215)
    img = Image.new("RGBA", (W, H), PAPER)
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        col = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3)) + (255,)
        for x in range(W):
            px[x, y] = col
    grain = overlay(img)
    gd = ImageDraw.Draw(grain, "RGBA")
    for _ in range(12000):
        x, y = rng.randrange(W), rng.randrange(H)
        gd.point((x, y), fill=(69, 58, 43, rng.randint(2, 10)))
    for _ in range(18):
        y = rng.randrange(H)
        gd.line((0, y, W, y + rng.randint(-3, 3)), fill=(255, 252, 239, 12), width=1)
    return Image.alpha_composite(img, grain)


def wash(img, boxes, color, blur=30):
    lay = overlay(img)
    d = ImageDraw.Draw(lay, "RGBA")
    for box in boxes:
        d.ellipse(box, fill=color)
    lay = lay.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(lay)


def clouds(d, rng, y, count=4, color=(255, 252, 239, 150)):
    for i in range(count):
        x = int((i + .3) * W / count) + rng.randint(-70, 70)
        widths = [150, 230, 175]
        for j, ww in enumerate(widths):
            yy = y + rng.randint(-18, 18) + j * 7
            d.ellipse((x - ww // 2 + j * 58, yy - 25, x + ww // 2 + j * 58, yy + 28), fill=color)


def mountain_range(d, rng, base=510, height=240, colors=None, snow=False, gap=False):
    colors = colors or [(156, 181, 161, 150), (105, 143, 125, 175), (59, 91, 79, 205)]
    for layer, col in enumerate(colors):
        b = base + layer * 58
        pts = [(-80, H), (-80, b)]
        x = -80
        while x < W + 100:
            width = rng.randint(190, 300)
            peak_x = x + width * rng.uniform(.35, .65)
            if gap and W * .43 < peak_x < W * .57:
                peak_x += width * .45
            peak_y = b - height + layer * 34 + rng.randint(-40, 35)
            pts += [(x + width * .17, b - rng.randint(10, 55)), (peak_x, peak_y), (x + width * .8, b - rng.randint(15, 70)), (x + width, b)]
            if snow:
                d.polygon([(peak_x, peak_y), (peak_x - 36, peak_y + 58), (peak_x, peak_y + 42), (peak_x + 38, peak_y + 61)], fill=(248, 247, 237, 220))
            x += width
        pts.append((W + 80, H))
        d.polygon(pts, fill=col)


def water(d, y=440, color=WATER, ripples=9):
    d.rectangle((0, y, W, H), fill=color)
    for i in range(ripples):
        yy = y + 30 + i * max(14, (H - y - 40) // max(1, ripples))
        off = 45 if i % 2 else -20
        d.arc((-100 + off, yy, 340 + off, yy + 60), 205, 335, fill=(239, 244, 226, 100), width=4)
        d.arc((350 - off, yy - 5, 820 - off, yy + 55), 205, 335, fill=(44, 112, 116, 75), width=3)
        d.arc((750 + off, yy, 1180 + off, yy + 58), 205, 335, fill=(239, 244, 226, 90), width=3)


def sun(d, x, y, r=48, moon=False):
    color = (247, 235, 187, 245) if moon else (217, 91, 51, 235)
    d.ellipse((x-r, y-r, x+r, y+r), fill=color)


def simple_house(d, x, y, s=1, warm=False):
    wall = (236, 227, 204, 235)
    roof = (57, 72, 61, 235)
    d.rectangle((x-50*s, y-48*s, x+50*s, y), fill=wall)
    d.polygon([(x-72*s, y-48*s), (x, y-88*s), (x+72*s, y-48*s)], fill=roof)
    d.rectangle((x-11*s, y-30*s, x+11*s, y), fill=(87, 58, 44, 230))
    if warm:
        d.rectangle((x+23*s, y-35*s, x+43*s, y-15*s), fill=(242, 183, 75, 245))


def tower(d, x, base, floors=3, s=1):
    for f in range(floors):
        y = base - f * 74 * s
        d.rectangle((x-48*s, y-54*s, x+48*s, y), fill=(205, 161, 103, 235))
        d.polygon([(x-82*s, y-55*s), (x+82*s, y-55*s), (x+54*s, y-78*s), (x-54*s, y-78*s)], fill=(53, 72, 62, 240))
        d.line((x, y-50*s, x, y), fill=(115, 74, 50, 210), width=max(2, int(5*s)))


def trunk(d, points, width=12):
    d.line(points, fill=INK, width=width, joint="curve")


def willow(d, x, base, s=1):
    trunk(d, [(x, base), (x-8*s, base-160*s), (x+8*s, base-280*s)], max(7, int(15*s)))
    for i in range(13):
        sx = x - 70*s + i*12*s
        sy = base - 235*s - (i % 3)*18*s
        d.arc((sx-30*s, sy, sx+70*s, sy+245*s), 265, 357, fill=(67, 124, 76, 210), width=max(3, int(5*s)))
        for j in range(4):
            yy = sy + 75*s + j*38*s
            d.ellipse((sx+30*s, yy, sx+48*s, yy+9*s), fill=(101, 153, 91, 195))


def branch(d, points, blossoms=None, leaves=None, rng=None):
    trunk(d, points, 11)
    if not rng:
        return
    x0, y0 = points[-1]
    for i in range(22):
        x = x0 + rng.randint(-180, 150)
        y = y0 + rng.randint(-110, 90)
        if blossoms:
            r = rng.randint(8, 14)
            for a in range(5):
                aa = a * math.tau / 5
                cx, cy = x + math.cos(aa)*r, y + math.sin(aa)*r
                d.ellipse((cx-7, cy-7, cx+7, cy+7), fill=blossoms)
            d.ellipse((x-4, y-4, x+4, y+4), fill=GOLD)
        if leaves:
            d.ellipse((x-18, y-8, x+18, y+8), fill=leaves)


def maple(d, x, base, rng, s=1):
    trunk(d, [(x, base), (x-5*s, base-150*s), (x+18*s, base-290*s)], max(8, int(16*s)))
    for _ in range(48):
        xx = x + rng.randint(int(-150*s), int(150*s))
        yy = base - rng.randint(int(150*s), int(330*s))
        r = rng.randint(9, 20)
        col = rng.choice([(184, 55, 43, 220), (211, 88, 50, 220), (224, 132, 52, 215)])
        d.regular_polygon((xx, yy, r), 5, rotation=rng.randint(0, 70), fill=col)


def bamboo(d, x, base, rng, count=8, lean=-.18):
    for i in range(count):
        bx = x + i * 34
        topx = bx + lean * rng.randint(260, 400)
        topy = base - rng.randint(330, 490)
        d.line((bx, base, topx, topy), fill=(45, 105, 66, 230), width=10)
        for t in (.25, .48, .7):
            yy = base + (topy-base)*t
            xx = bx + (topx-bx)*t
            d.line((xx-8, yy, xx+10, yy), fill=(33, 80, 54, 220), width=3)
            side = -1 if (i + int(t*10)) % 2 else 1
            d.line((xx, yy, xx + side*70, yy-45), fill=(45, 105, 66, 210), width=4)
            d.ellipse((xx + side*45-28, yy-65, xx + side*45+28, yy-45), fill=(67, 132, 77, 185))


def lotus(d, x, y, s=1, bud=False, dry=False):
    stem = (62, 119, 79, 195) if not dry else (104, 91, 62, 185)
    d.line((x, y+100*s, x, y), fill=stem, width=max(3, int(6*s)))
    if bud:
        d.polygon([(x, y-50*s), (x-18*s, y-8*s), (x, y+3*s), (x+18*s, y-8*s)], fill=(204, 93, 112, 220))
    elif dry:
        d.ellipse((x-22*s, y-8*s, x+22*s, y+8*s), outline=(105, 80, 49, 220), width=max(3, int(5*s)))
    else:
        for a in range(8):
            aa = a*math.tau/8
            cx, cy = x+math.cos(aa)*22*s, y+math.sin(aa)*12*s
            d.ellipse((cx-17*s, cy-12*s, cx+17*s, cy+12*s), fill=(214, 103, 130, 205))
        d.ellipse((x-7*s, y-7*s, x+7*s, y+7*s), fill=GOLD)


def lotus_leaf(d, x, y, s=1, dry=False):
    col = (77, 142, 91, 190) if not dry else (127, 104, 64, 155)
    d.ellipse((x-65*s, y-22*s, x+65*s, y+22*s), fill=col)
    d.line((x, y, x, y+90*s), fill=(62, 112, 76, 160), width=max(2, int(4*s)))


def fish(d, x, y, s=1, direction=1):
    col = (205, 103, 61, 220)
    d.ellipse((x-35*s, y-14*s, x+35*s, y+14*s), fill=col)
    tailx = x-35*s*direction
    d.polygon([(tailx, y), (tailx-28*s*direction, y-18*s), (tailx-28*s*direction, y+18*s)], fill=col)
    d.ellipse((x+20*s*direction-3, y-4, x+20*s*direction+3, y+2), fill=INK)


def bird(d, x, y, s=1, color=(222, 175, 53, 245), flying=False, white=False):
    col = (244, 245, 234, 245) if white else color
    if flying:
        if white:
            shadow = (75, 108, 111, 175)
            d.arc((x-44*s, y-16*s, x+2*s, y+28*s), 205, 345, fill=shadow, width=max(6, int(11*s)))
            d.arc((x-2*s, y-16*s, x+44*s, y+28*s), 195, 335, fill=shadow, width=max(6, int(11*s)))
        d.arc((x-42*s, y-18*s, x, y+24*s), 205, 345, fill=col, width=max(4, int(8*s)))
        d.arc((x, y-18*s, x+42*s, y+24*s), 195, 335, fill=col, width=max(4, int(8*s)))
        if white:
            d.ellipse((x-7*s, y+1*s, x+24*s, y+11*s), fill=col)
            d.arc((x+13*s, y-13*s, x+41*s, y+13*s), 205, 330, fill=col, width=max(3, int(5*s)))
            d.line((x-6*s, y+9*s, x-31*s, y+22*s), fill=col, width=max(2, int(3*s)))
        return
    d.ellipse((x-25*s, y-14*s, x+25*s, y+16*s), fill=col)
    d.ellipse((x+16*s, y-26*s, x+39*s, y-4*s), fill=col)
    d.polygon([(x+38*s, y-17*s), (x+55*s, y-11*s), (x+38*s, y-7*s)], fill=(202, 99, 45, 230))
    d.polygon([(x-20*s, y), (x-48*s, y-18*s), (x-40*s, y+10*s)], fill=col)
    d.ellipse((x+29*s, y-19*s, x+33*s, y-15*s), fill=INK)


def goose(d, x, y, s=1):
    d.ellipse((x-85*s, y-40*s, x+55*s, y+50*s), fill=(247, 245, 229, 250))
    d.arc((x-10*s, y-160*s, x+100*s, y+10*s), 95, 285, fill=(247, 245, 229, 250), width=max(16, int(30*s)))
    d.ellipse((x+58*s, y-166*s, x+105*s, y-120*s), fill=(247, 245, 229, 250))
    d.polygon([(x+102*s, y-148*s), (x+137*s, y-136*s), (x+102*s, y-128*s)], fill=CINNABAR)
    d.ellipse((x+88*s, y-153*s, x+94*s, y-147*s), fill=INK)
    for ox in (-35, 5):
        d.line((x+ox*s, y+40*s, x+(ox-5)*s, y+72*s), fill=CINNABAR, width=max(4, int(7*s)))
        d.ellipse((x+(ox-20)*s, y+65*s, x+(ox+10)*s, y+78*s), fill=CINNABAR)


def person(d, x, y, s=1, child=False, hat=False, robe=(74, 100, 86, 235), facing=1):
    head_r = 17*s if child else 20*s
    d.ellipse((x-head_r, y-125*s-head_r, x+head_r, y-125*s+head_r), fill=(211, 176, 132, 245))
    d.polygon([(x-30*s, y-105*s), (x+30*s, y-105*s), (x+48*s, y), (x-45*s, y)], fill=robe)
    d.line((x-12*s, y, x-25*s, y+35*s), fill=INK, width=max(4, int(8*s)))
    d.line((x+12*s, y, x+28*s, y+35*s), fill=INK, width=max(4, int(8*s)))
    if hat:
        d.polygon([(x-42*s, y-145*s), (x+42*s, y-145*s), (x, y-184*s)], fill=(115, 92, 58, 240))
    if child:
        for side in (-1, 1):
            d.line((x+side*8*s, y-145*s, x+side*32*s, y-170*s), fill=INK, width=max(2, int(5*s)))


def boat(d, x, y, s=1, sail=False, fisherman=False):
    d.polygon([(x-100*s, y), (x+110*s, y), (x+70*s, y+35*s), (x-70*s, y+35*s)], fill=(101, 70, 49, 235))
    if sail:
        d.line((x, y, x, y-180*s), fill=INK, width=max(3, int(6*s)))
        d.polygon([(x+7*s, y-170*s), (x+7*s, y-25*s), (x+105*s, y-55*s)], fill=(243, 229, 192, 235))
    if fisherman:
        person(d, x-5*s, y-10*s, .48*s, hat=True, robe=(79, 77, 64, 240))
        d.line((x+12*s, y-65*s, x+125*s, y+45*s), fill=INK, width=max(2, int(3*s)))


def dragonfly(d, x, y, s=1):
    d.line((x-20*s, y+12*s, x+28*s, y-18*s), fill=INK, width=max(3, int(5*s)))
    d.ellipse((x-35*s, y-23*s, x, y-7*s), fill=(139, 199, 196, 155))
    d.ellipse((x-5*s, y-39*s, x+30*s, y-20*s), fill=(139, 199, 196, 155))


def finish(img, rng):
    ink = overlay(img)
    d = ImageDraw.Draw(ink, "RGBA")
    for _ in range(170):
        x, y = rng.randrange(W), rng.randrange(H)
        length = rng.randint(5, 34)
        d.line((x, y, x+length, y+rng.randint(-2, 2)), fill=(40, 54, 45, rng.randint(3, 13)), width=1)
    img.alpha_composite(ink)
    return img.convert("RGB").resize(FINAL, Image.Resampling.LANCZOS)


def render(key):
    rng = random.Random(seed_for(key))
    night = key in {"jing-ye-si", "ye-su-shan-si", "ye-shu-suo-jian", "wang-dong-ting"}
    img = paper(rng, night)
    wash(img, [(-180, 20, 420, 250), (650, -80, 1250, 250)], (217, 157, 100, 28) if not night else (62, 94, 107, 45), 45)
    d = ImageDraw.Draw(img, "RGBA")

    if key == "jiang-nan":
        water(d, 250, (105, 171, 160, 175), 10)
        for x, y, s in [(120,420,1.0),(290,340,.85),(470,455,1.1),(670,340,.82),(870,430,1.0),(990,315,.7)]: lotus_leaf(d,x,y,s)
        for x, y, s in [(235,335,.9),(555,315,.8),(820,385,.9)]: lotus(d,x,y,s)
        for x,y,s,dr in [(170,510,.8,1),(390,570,.7,-1),(700,500,.9,1),(900,590,.7,-1)]: fish(d,x,y,s,dr)
    elif key == "hua":
        d.rounded_rectangle((95,70,985,650), 25, fill=(245,239,220,225), outline=(119,88,59,180), width=8)
        d.line((135,105,945,105), fill=(121,83,55,190), width=9); d.line((135,615,945,615), fill=(121,83,55,190), width=9)
        mountain_range(d,rng,470,210,[(165,185,161,160),(86,124,105,190)])
        d.rounded_rectangle((520,210,575,530),22,fill=(231,241,225,220)); clouds(d,rng,175,3)
        branch(d,[(170,570),(220,420),(330,330)],blossoms=(216,104,126,215),rng=rng)
        bird(d,760,425,.85,color=(86,112,89,240))
    elif key == "yong-e":
        water(d,230,(102,168,151,170),10); clouds(d,rng,90,3,(255,252,238,110))
        goose(d,320,410,1.15); goose(d,700,455,.88)
        for x,y in [(240,570),(530,545),(820,575)]: d.arc((x-80,y-25,x+80,y+25),205,335,fill=(244,239,216,120),width=5)
    elif key == "min-nong-er":
        sun(d,875,105,58); d.rectangle((0,430,W,H),fill=(190,164,82,150))
        for i in range(16):
            x=15+i*72; d.line((x,H,x+15,430),fill=(142,117,56,190),width=5); d.ellipse((x-8,450,x+27,470),fill=(211,177,69,200))
        person(d,485,525,1.1,hat=True,robe=(96,112,78,235)); d.line((520,400,665,575),fill=(86,65,45,240),width=8); d.arc((620,535,710,610),0,170,fill=(86,65,45,240),width=8)
        for x,y in [(456,365),(445,382),(438,398)]: d.ellipse((x,y,x+7,y+12),fill=(91,151,170,185))
    elif key == "gu-lang-yue-xing":
        d.rectangle((0,0,W,H),fill=(38,66,80,155)); sun(d,760,185,105,moon=True); clouds(d,rng,390,5,(239,244,233,145))
        person(d,285,575,.9,child=True,robe=(185,91,62,230)); d.line((300,430,390,340),fill=(211,176,132,240),width=12)
        d.arc((635,70,885,315),0,360,fill=(239,224,176,110),width=7)
    elif key == "feng":
        water(d,420,(87,151,163,175),6); bamboo(d,770,650,rng,8,-.34)
        branch(d,[(120,630),(190,470),(270,380)],leaves=(196,93,48,205),rng=rng)
        for i in range(15):
            x=220+i*38; y=150+(i%4)*45; d.regular_polygon((x,y,12),5,rotation=i*17,fill=(195,84,49,190))
        for x in range(70,360,60): d.ellipse((x,560-rng.randint(0,55),x+26,590-rng.randint(0,40)),fill=(218,95,124,205))
        for i in range(6): d.arc((-80+i*190,385,240+i*190,500),175,340,fill=(238,242,225,150),width=10)
    elif key == "jing-ye-si":
        sun(d,790,135,65,moon=True); d.rectangle((0,470,W,H),fill=(219,222,207,75)); d.rectangle((180,160,420,470),outline=(211,199,169,180),width=12)
        d.line((300,165,300,470),fill=(211,199,169,150),width=8); d.line((185,310,415,310),fill=(211,199,169,150),width=8)
        d.polygon([(420,470),(880,470),(1030,720),(250,720)],fill=(240,239,219,70)); person(d,620,560,1.05,robe=(93,116,111,235))
        d.rectangle((120,500,380,565),fill=(126,93,69,210)); d.polygon([(120,500),(380,500),(420,560),(75,560)],fill=(237,224,194,220))
    elif key == "chun-xiao":
        wash(img,[(0,0,1080,340)],(239,180,131,40),55); willow(d,155,700,1.1)
        for x,y in [(630,170),(730,125),(840,200)]: bird(d,x,y,.75,color=(225,171,46,240),flying=x!=630)
        simple_house(d,650,520,1.25,warm=True)
        for i in range(35):
            x=rng.randrange(W); y=rng.randrange(470,700); d.ellipse((x-8,y-4,x+8,y+4),fill=(214,94,119,150))
        for i in range(20):
            x=500+i*25; y=250+rng.randint(-90,110); d.line((x,y,x-7,y+18),fill=(82,142,167,105),width=3)
    elif key == "cun-ju":
        d.rectangle((0,500,W,H),fill=(144,184,112,140)); willow(d,170,670,1.2); willow(d,930,670,.9)
        bird(d,400,180,.7,color=(226,177,45,245),flying=True); bird(d,515,135,.65,color=(226,177,45,245),flying=True)
        person(d,380,590,.68,child=True,robe=(190,82,57,230)); person(d,520,610,.62,child=True,robe=(77,127,112,230))
        d.polygon([(790,120),(840,165),(790,210),(740,165)],fill=CINNABAR); d.line((790,210,510,525),fill=(73,65,54,175),width=3)
    elif key == "xiao-chi":
        water(d,355,(103,169,158,165),8); branch(d,[(70,360),(170,255),(310,145)],leaves=(68,132,82,190),rng=rng)
        d.polygon([(0,340),(75,295),(150,330),(215,300),(300,360),(0,420)],fill=(89,113,96,180))
        d.ellipse((72,330,142,387),fill=(32,61,53,220)); d.rounded_rectangle((115,356,430,376),10,fill=(207,232,221,225))
        d.arc((110,350,500,430),195,335,fill=(246,244,222,170),width=6)
        lotus_leaf(d,805,555,1.05); lotus(d,715,455,1.18,bud=True); dragonfly(d,715,384,1.55)
    elif key == "mei-hua":
        d.rectangle((0,370,W,H),fill=(240,239,226,170)); d.rectangle((70,190,285,620),fill=(210,203,180,165)); d.polygon([(45,190),(310,190),(275,145),(80,145)],fill=(74,82,65,210))
        branch(d,[(330,640),(400,430),(625,235)],blossoms=(244,241,223,240),rng=rng)
        for _ in range(120):
            x,y=rng.randrange(W),rng.randrange(H); r=rng.choice([2,3,5]); d.ellipse((x-r,y-r,x+r,y+r),fill=(255,255,246,185))
    elif key == "xiao-er-chui-diao":
        water(d,495,(98,157,155,165),6); d.rectangle((0,430,420,H),fill=(125,164,102,125))
        person(d,350,500,.75,child=True,robe=(105,133,89,235)); d.line((380,400,690,510),fill=(82,64,48,230),width=5); d.arc((665,500,820,600),185,335,fill=(82,64,48,170),width=2)
        person(d,850,535,.55,robe=(174,101,66,220)); d.line((820,435,760,390),fill=(211,176,132,220),width=7)
        for x in range(35,430,45): d.line((x,530,x+rng.randint(-15,15),420-rng.randint(0,70)),fill=(58,120,73,175),width=5)
        fish(d,690,590,.6,-1)
    elif key == "jiang-xue":
        mountain_range(d,rng,450,280,[(174,188,177,150),(115,139,127,175),(67,88,79,195)],snow=True)
        water(d,490,(94,127,137,145),5); boat(d,530,560,.72,fisherman=True)
        for _ in range(180):
            x,y=rng.randrange(W),rng.randrange(H); r=rng.choice([2,3,4]); d.ellipse((x-r,y-r,x+r,y+r),fill=(255,255,248,205))
    elif key == "ye-su-shan-si":
        d.rectangle((0,0,W,H),fill=(26,49,67,170)); sun(d,870,105,48,moon=True)
        for _ in range(70):
            x,y=rng.randrange(W),rng.randrange(430); r=rng.choice([2,3,4]); d.ellipse((x-r,y-r,x+r,y+r),fill=(248,235,180,220))
        mountain_range(d,rng,610,390,[(83,112,106,180),(42,72,68,220)]); tower(d,560,430,3,.85); person(d,690,520,.58,robe=(151,95,68,235)); d.line((700,400,755,285),fill=(211,176,132,220),width=7)
    elif key == "chi-le-ge":
        mountain_range(d,rng,395,190,[(125,151,138,170),(64,96,81,205)]); d.rectangle((0,410,W,H),fill=(113,154,86,170))
        clouds(d,rng,125,3,(249,245,225,115))
        for i in range(13):
            x=65+i*78; y=500+rng.randint(-30,140); col=(239,229,202,235) if i%3 else (103,79,53,235)
            d.ellipse((x-28,y-15,x+28,y+18),fill=col); d.ellipse((x+20,y-10,x+40,y+10),fill=col)
            d.line((x-15,y+14,x-17,y+37),fill=INK,width=4); d.line((x+15,y+14,x+17,y+37),fill=INK,width=4)
            if i%3==0:
                d.arc((x+23,y-20,x+44,y+5),175,285,fill=(239,226,190,220),width=3)
                d.arc((x+32,y-20,x+53,y+5),255,350,fill=(239,226,190,220),width=3)
            else:
                d.ellipse((x-22,y-20,x+3,y+4),fill=(247,241,219,180)); d.ellipse((x-5,y-24,x+19,y+2),fill=(247,241,219,180))
        for x in range(0,W,24): d.line((x,H,x+rng.randint(-35,10),470-rng.randint(0,100)),fill=(74,124,66,190),width=3)
    elif key == "deng-guan-que-lou":
        sun(d,790,155,58); mountain_range(d,rng,420,210,[(165,157,126,150),(91,112,92,190)])
        water(d,480,(145,153,129,150),6); tower(d,245,545,4,1.0)
        d.polygon([(330,530),(1080,470),(1080,640),(330,610)],fill=(178,143,75,85))
    elif key == "wang-lu-shan-pu-bu":
        sun(d,160,100,50); mountain_range(d,rng,620,470,[(159,172,150,150),(94,123,104,185),(45,76,65,225)])
        wash(img,[(340,120,850,400)],(141,101,169,75),45)
        d.rounded_rectangle((565,135,655,720),42,fill=(236,244,229,230)); d.ellipse((460,610,775,760),fill=(232,242,229,190)); clouds(d,rng,210,3,(230,220,239,125))
    elif key == "jue-ju":
        mountain_range(d,rng,405,210,[(169,191,173,145),(94,132,111,170)],snow=True); willow(d,155,650,1.0)
        bird(d,215,260,.62,color=(231,180,35,245)); bird(d,305,310,.62,color=(231,180,35,245))
        for i in range(7): bird(d,525+i*72,135+(i%2)*30,.78,flying=True,white=True)
        water(d,530,(91,148,160,150),4); boat(d,805,545,.55,sail=True)
        d.rectangle((15,35,500,410),outline=(104,75,53,190),width=14)
    elif key == "fu-de-gu-yuan-cao":
        d.rectangle((0,360,W,H),fill=(127,161,87,155)); mountain_range(d,rng,415,130,[(171,184,150,100)])
        for x in range(0,W,25):
            y=H-rng.randint(90,250); d.line((x,H,x+rng.randint(-20,20),y),fill=(67,124,64,200),width=4)
        for x,y in [(720,420),(785,390),(845,435)]:
            d.polygon([(x,y),(x-25,y+75),(x+6,y+50),(x+35,y+90),(x+60,y+18)],fill=(205,78,42,170))
        for x in range(100,470,50):
            d.arc((x,510,x+70,670),180,305,fill=(88,152,75,230),width=8)
    elif key == "shan-xing":
        mountain_range(d,rng,585,340,[(180,172,142,130),(106,128,102,170)]); clouds(d,rng,265,4,(251,248,233,175))
        d.line((80,700,280,560,480,500,620,335),fill=(190,181,151,235),width=42); simple_house(d,670,350,.65,warm=True)
        maple(d,850,690,rng,1.25); d.rectangle((410,520,520,565),fill=(91,61,43,235)); d.ellipse((425,555,453,583),fill=INK); d.ellipse((485,555,513,583),fill=INK)
    elif key == "zeng-liu-jing-wen":
        water(d,470,(121,157,145,115),5)
        for x in (130,300,465): lotus_leaf(d,x,500,.75,dry=True); lotus(d,x+25,440,.65,dry=True)
        for x in range(560,780,48):
            d.line((x,620,x,430-rng.randint(0,80)),fill=(78,119,72,190),width=5)
            cy=420-rng.randint(0,45)
            for ring,radius in [(0,12),(1,25)]:
                count=8+ring*6
                for a in range(count):
                    aa=a*math.tau/count; cx=x+math.cos(aa)*radius; yy=cy+math.sin(aa)*radius*.7
                    d.ellipse((cx-8,yy-4,cx+8,yy+4),fill=(231,193,91,210))
            d.ellipse((x-7,cy-7,x+7,cy+7),fill=(167,111,45,235))
        branch(d,[(900,690),(880,490),(840,330)],leaves=(73,130,72,195),rng=rng)
        for x,y,col in [(810,385,(218,139,52,240)),(900,440,(231,158,49,245)),(770,500,(95,150,70,240)),(960,525,(93,145,66,240))]: d.ellipse((x-28,y-28,x+28,y+28),fill=col)
    elif key == "ye-shu-suo-jian":
        sun(d,860,105,45,moon=True); water(d,480,(66,105,119,130),5)
        branch(d,[(120,610),(205,420),(330,250)],leaves=(161,90,48,185),rng=rng)
        d.line((520,640,520,405),fill=(120,86,55,210),width=8); d.line((520,440,970,440),fill=(120,86,55,210),width=7)
        for x in range(535,970,45): d.line((x,620,x,420),fill=(120,86,55,180),width=5)
        d.ellipse((765,390,835,460),fill=(245,183,70,170)); simple_house(d,800,455,.72,warm=True)
        person(d,680,545,.48,child=True,robe=(178,92,63,230)); person(d,735,565,.43,child=True,robe=(76,123,110,230))
    elif key == "wang-tian-men-shan":
        sun(d,860,115,50); mountain_range(d,rng,525,325,[(142,172,150,150),(57,105,85,220)],gap=True)
        water(d,365,(73,151,163,190),9); d.arc((335,390,745,655),170,340,fill=(241,241,219,130),width=12); boat(d,725,500,.75,sail=True)
    elif key == "yin-hu-shang":
        mountain_range(d,rng,390,190,[(177,196,183,90),(111,151,137,130)]); water(d,385,(110,166,170,150),8)
        wash(img,[(500,40,1150,520)],(219,229,223,95),55); clouds(d,rng,245,5,(241,244,234,155)); simple_house(d,265,400,.6)
        for i in range(35):
            x=560+i*14; y=100+rng.randint(0,350); d.line((x,y,x-7,y+25),fill=(87,135,154,90),width=2)
        for x in range(40,520,80): d.line((x,470,x+55,455),fill=(247,238,196,165),width=5)
    elif key == "wang-dong-ting":
        sun(d,790,125,62,moon=True); mountain_range(d,rng,420,150,[(86,121,109,125)])
        water(d,345,(75,119,132,145),8)
        for i in range(7):
            x=720-i*18; y=245+i*42; d.line((x-40,y,x+55,y),fill=(245,234,189,155-i*10),width=5)
        for i in range(5):
            d.arc((150+i*90,410+i*17,950-i*45,620-i*12),195,335,fill=(225,230,217,55+i*12),width=5)
        d.ellipse((430,390,660,520),fill=(49,93,70,220)); d.ellipse((495,345,615,445),fill=(61,116,82,235))

    return finish(img, rng)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for key in SCENES:
        render(key).save(OUT / f"{key}.webp", "WEBP", quality=70, method=6)
    sources = {
        "provider": "诗画小书童本地原创绘图",
        "license": "Original project artwork",
        "policy": "All 25 illustrations are generated locally from poem-specific vector primitives and bundled for offline use.",
        "works": {key: {"title": title, "source": "Local original illustration", "scene": scene} for key, (title, scene) in SCENES.items()},
    }
    (OUT / "sources.json").write_text(json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"generated {len(SCENES)} poem-specific illustrations in {OUT}")


if __name__ == "__main__":
    main()
