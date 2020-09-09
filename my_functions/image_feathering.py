from PIL import Image
from PIL import ImageDraw
from PIL import ImageFilter

RADIUS = 30

# Open an image
im = Image.open('resource\\Album_Cover\\人間開花\\人間開花.jpg')  # type:Image.Image

# 在透明背景上粘贴图片
diam = 2 * RADIUS
back = Image.new(
    'RGBA', (im.size[0]+diam, im.size[1]+diam), (255, 255, 255, 0))
back.paste(im, (RADIUS, RADIUS))

# 创建遮罩
mask = Image.new('L', back.size, 0)
draw = ImageDraw.Draw(mask)
x0, y0 = 0, 0
x1, y1 = back.size
# 绘制遮罩
for d in range(diam+RADIUS):
    x1, y1 = x1-1, y1-1
    alpha = 255 if d < RADIUS else int(255 * (diam + RADIUS - d) / diam)
    # outline指定边框颜色,fill参数可以指定填充的颜色
    draw.rectangle([x0, y0, x1, y1], outline=alpha)
    x0, y0 = x0+1, y0+1

# 高斯模糊
blur = back.filter(ImageFilter.GaussianBlur(RADIUS / 2))
blur.show()
# 将模糊后的图片粘贴到原图中，保留原图部分，增加模糊边沿
back.paste(blur,mask=mask)
# 保存图片
back.save('test.png')
