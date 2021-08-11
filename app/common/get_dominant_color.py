# coding:utf-8
import sys
import os
from math import floor

from colorthief import ColorThief

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QPixmap, QColor
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QApplication


class DominantColor:
    """ 获取图像的主色调 """

    def __init__(self):
        self.rgb = tuple()

    def getDominantColor(self, imagePath: str, resType=str):
        """ 获取指定图片的主色调

        Parameters
        ----------
        imagePath: str
            图片路径

        reType:
            返回类型，str 返回十六进制字符串，否则为 rgb 元组
        """
        self.imagePath = imagePath
        colorThief = ColorThief(imagePath)

        # 调整图像大小，加快运算速度
        if max(colorThief.image.size) > 400:
            colorThief.image = colorThief.image.resize((400, 400))

        palette = colorThief.get_palette(quality=9)
        # 调整调色板明度
        palette = self.__adjustPaletteValue(palette)
        for rgb in palette[:]:
            h, s, v = self.rgb2hsv(rgb)
            if h < 0.02:
                palette.remove(rgb)
                if len(palette) <= 2:
                    break
        palette = palette[:4]
        palette.sort(key=lambda rgb: self.rgb2hsv(rgb)[1], reverse=True)
        self.rgb = palette[0]
        # 根据指定的返回类型决定返回十六进制颜色代码还是元组
        if resType is str:
            rgb = "".join([hex(i)[2:].rjust(2, "0") for i in self.rgb])
            return rgb
        return self.rgb

    def __adjustPaletteValue(self, palette: list):
        """ 调整调色板的明度 """
        newPalette = []
        for rgb in palette:
            h, s, v = self.rgb2hsv(rgb)
            if v > 0.9:
                factor = 0.8
            elif 0.8 < v <= 0.9:
                factor = 0.9
            elif 0.7 < v <= 0.8:
                factor = 0.95
            else:
                factor = 1
            v *= factor
            newPalette.append(self.hsv2rgb(h, s, v))
        return newPalette

    @staticmethod
    def rgb2hsv(rgb: tuple) -> tuple:
        """ rgb空间变换到hsv空间 """
        r, g, b = [i / 255 for i in rgb]
        mx = max(r, g, b)
        mn = min(r, g, b)
        df = mx - mn
        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g - b) / df) + 360) % 360
        elif mx == g:
            h = (60 * ((b - r) / df) + 120) % 360
        elif mx == b:
            h = (60 * ((r - g) / df) + 240) % 360
        s = 0 if mx == 0 else df / mx
        v = mx
        return (h, s, v)

    @staticmethod
    def hsv2rgb(h, s, v) -> tuple:
        """ hsv空间变换到rgb空间 """
        h60 = h / 60.0
        h60f = floor(h60)
        hi = int(h60f) % 6
        f = h60 - h60f
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        r, g, b = 0, 0, 0
        if hi == 0:
            r, g, b = v, t, p
        elif hi == 1:
            r, g, b = q, v, p
        elif hi == 2:
            r, g, b = p, v, t
        elif hi == 3:
            r, g, b = p, q, v
        elif hi == 4:
            r, g, b = t, p, v
        elif hi == 5:
            r, g, b = v, p, q
        r, g, b = int(r * 255), int(g * 255), int(b * 255)
        return (r, g, b)
