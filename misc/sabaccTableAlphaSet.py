from PIL import ImageGrab, PngImagePlugin, Image

def lerp(p1, p2, t):
    t1 = t/255
    return round(p1 + (t1*(p2 - p1)))

def pxlerp(p):
    target = 128
    return (lerp(target, p[0], p[3]), lerp(target, p[1], p[3]), lerp(target, p[2], p[3]), 255)

image = Image.open('client/static/modern-theme-images/SabaccTable-NoBackground.png')
maxx = 0
minx = image.width - 1
maxy = 0
miny = image.height - 1

for ix in range(image.width):
    for iy in range(image.height):
        px = image.getpixel((ix, iy))
        if px[3] != 0 and px[3] != 255:
            image.putpixel((ix, iy), pxlerp(px))

            if ix < minx:
                minx = ix
            if ix > maxx:
                maxx = ix
            if iy < miny:
                miny = iy
            if iy > maxy:
                maxy = iy

image = image.crop((minx, miny, maxx, maxy))
image.save('client/static/modern-theme-images/SabaccTable-NoBackground.png', bitmap_format='png')