from PIL import Image

img = Image.open('resource\\images\\titleBar\\黑色返回按钮_60_40.png') #type:Image.Image

hoverImage = Image.new('RGBA', img.size, (0, 0, 0, 40))
hoverImage.paste(img,(0,0),img)

hoverImage.save('test.png')