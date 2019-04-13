from PIL import Image, ImageDraw
import numpy as np

def read_data(path = "star_data"):
    #function that read NASA HIP data
    with open(path) as f:
        lines = [s.strip() for s in f.readlines()]
    print(lines[4]) #show key
    lines =  list(map(processing_data,lines))
    lines = [line for line in lines if line != "No_data"]

    return lines[5:]

def processing_data(element):
    line = element.split("|")
    if len(line) != 6:
        return "No_data"
    line = line[1:5] #delete first and last data of each lines
    try:
        line = [float(value) for value in line]
    except:
        return "No_data"
    return line
def draw_star(image,x,y,color,brightness):
    #x = round(x)
    #y = round(y)
    #r = 10
    #for i in range(int(r / 2)):
    #    draw.ellipse((x-r, y-r, x+r, y+r), fill=color + (25 * (10 - r),))
    #    r -= 2
    draw = ImageDraw.Draw(image)
    draw.point(((x, y)), fill=color + (255,))

    r = int(brightness * 5) + 2

    img_size = image.size
    poly_size = (2 * r,2 * r)
    poly_offset = (int(x - r),int(y - r)) #location in larger image

    back = Image.new('RGBA', img_size, (0,0,0,255) )
    poly = Image.new('RGBA', poly_size )
    pdraw = ImageDraw.Draw(poly)
    pdraw.ellipse((0, 0, 2 * r, 2 * r), fill=color + (30,))

    image.paste(poly, poly_offset, mask=poly)


def rgb_from_bv(bv):
    T = 3.939654 - 0.395361 * bv + 0.2082113 * bv ** 2 - 0.0604097 * bv ** 3
    T = 10 ** T
    #http://zwxadz.hateblo.jp/entry/2017/05/02/065537
    if T < 4000 or 25000<T:
        return np.array([255,255,255])
    if T < 7500:
        x_d = (-4.6070 * 1e+9 / T ** 3) + (2.9678 * 1e+6 / T ** 2) + (0.09911 * 1e+3 / T) + 0.244063
    else:
        x_d = (-2.0064 * 1e+9 / T ** 3) + (1.9018 * 1e+6 / T ** 2) + (0.24748 * 1e+3 / T) + 0.237040
    y_d = -3 * x_d ** 2 + 2.870 * x_d - 0.275
    z_d = 1 - x_d - y_d
    mat = np.array([[3.2406,-1.5372,-0.4986],[-0.9689,1.8758,0.0415],[0.0557,-0.2040,1.0570]])
    xyz = np.array([x_d,y_d,z_d])
    rgb = np.dot(xyz,mat.T)
    rgb = rgb / np.max(rgb)
    rgb = rgb * 255

    return rgb

def xy_from_deg(ra,dec,width,height,view_angle):
    norm = max(width/2,height/2) / np.sin(view_angle)
    x = np.round((width/2) + np.sin(ra)*norm)
    y = np.round((height/2) + np.sin(dec)*norm)

    return x,y

def brightness_from_mag(mag,brightest_mag):
    return (1 / 100 ** (1/5)) ** (max(mag,brightest_mag) - brightest_mag)

VIEWING_ANGLE = 30
WIDTH = 512
HEIGHT = 512
MY_RA = 90
MY_DEC = 90

def rendering(star_data,eye_ra,eye_dec,width,height):
    brightest_mag = min([row[0] for row in star_data])
    sky = Image.new("RGBA",[width,height],(0,0,0,255))
    draw = ImageDraw.Draw(sky)
    for datum in star_data:
    #for i in range(100):
        #datum = star_data[i]
        if abs(datum[1] - MY_RA) < VIEWING_ANGLE:
            brightness = brightness_from_mag(datum[0],3)
            rgb = rgb_from_bv(datum[3]) * brightness * 5
            rgb = np.round(rgb).astype(np.uint8)
            x,y = xy_from_deg(datum[1] - MY_RA,datum[2] - MY_DEC,width,height,VIEWING_ANGLE)
            draw_star(sky,x,y,(rgb[0],rgb[1],rgb[2]),brightness)
        #print(datum)

    sky.save("test.png")


star_data = read_data("star_data.1534662788")
print(star_data[0])
rendering(star_data,0,0,1024,1024)
if False:
    sky = Image.new("RGBA",[512,512],(0,0,0,255))
    draw = ImageDraw.Draw(sky)
    draw_star(sky,50,50,(255,0,0),5)
    draw_star(sky,55,50,(0,0,255),5)
    sky.save("test.png")

#ra 地球の赤道の延長みたいな
#dec 地球の本初子午線の延長みたいな
#http://d.hatena.ne.jp/eji/20100804/1280937488
