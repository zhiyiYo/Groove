from PIL import Image

from scipy.ndimage.filters import gaussian_filter
import numpy as np

def gaussianBlur(rawImagePath,savePath,blurRadius=18):
    """ 对图片进行高斯模糊 """
    image = np.array(Image.open(rawImagePath))
    blurImage = image

    # 对每一个颜色通道分别磨砂
    for i in range(3):
        blurImage[:, :, i] = gaussian_filter(image[:, :, i], blurRadius)
    blurImage = Image.fromarray(blurImage)
    blurImage.save(savePath)

if __name__ == "__main__":
    gaussianBlur('resource\\Album Cover\\Girlfriend\\Girlfriend.jpg','磨砂图片.jpg')
