import numpy as np
from PIL import Image
from scipy.ndimage.filters import gaussian_filter

from PyQt5.QtGui import QPixmap, QImage


def gaussianBlur(rawImagePath, savePath='', blurRadius=18, brightnessFactor=1,blurPicSize:tuple=None):
    """ 对图片进行高斯模糊处理，返回numpy数组 """
    if blurPicSize:
        # 调整图片尺寸，减小计算量，还能增加额外的模糊(手动滑稽)
        image=Image.open(rawImagePath)
        oldWidth, oldHeight = image.size
        ratio = min(blurPicSize[0] / oldWidth, blurPicSize[1] / oldHeight)
        newWidth, newHeight = oldWidth * ratio, oldHeight * ratio
        # 如果新的尺寸小于旧尺寸才resize
        if newWidth < oldWidth:
            imageArray = np.array(image.resize(
                (int(newWidth), int(newHeight)),Image.ANTIALIAS))
        else:
            imageArray = np.array(image)
    else:
        imageArray = np.array(Image.open(rawImagePath))
    blurImageArray = imageArray
    # 对每一个颜色通道分别磨砂
    for i in range(imageArray.shape[-1]):
        blurImageArray[:, :, i] = gaussian_filter(
            imageArray[:, :, i], blurRadius) * brightnessFactor
    # 将ndarray转换为Image对象
    if savePath:
        blurImage = Image.fromarray(blurImageArray)
        blurImage.save(savePath)
    return blurImageArray


def getBlurPixmap(imagePath, blurRadius=30, brightnessFactor=1, blurPicSize: tuple = None) -> QPixmap:
    """ 对原图进行高斯模糊处理，返回QPixmap """
    blurArray = gaussianBlur(
        imagePath, blurRadius=blurRadius, brightnessFactor=brightnessFactor, blurPicSize=blurPicSize)
    height, width, bytesPerComponent = blurArray.shape
    bytesPerLine = blurArray.shape[-1] * width  # 每行的字节数
    # 设置转换格式
    if blurArray.shape[-1] == 4:
        imageFormat = QImage.Format_RGBA8888
    else:
        imageFormat = QImage.Format_RGB888
    # 将ndarray转换为QPixmap
    blurPixmap = QPixmap.fromImage(
        QImage(blurArray.data, width, height, bytesPerLine, imageFormat))
    return blurPixmap


if __name__ == "__main__":
    gaussianBlur(
        'resource\\Album_Cover\\Girlfriend\\Girlfriend.jpg', '磨砂图片.jpg')
