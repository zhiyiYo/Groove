import numpy
from time import time
from PIL import Image, ImageOps


img_1 = numpy.array(Image.open('img_1.png'))
img_2 = numpy.array(Image.open('img_2.png'))

mask = img_1[:, :] == numpy.array([0,0,0,25])
img_2[mask] = img_1[mask]
Image.fromarray(img_2).show()