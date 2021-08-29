# coding:utf-8
from timeit import Timer
from colorthief import ColorThief


def getColor(path):
    """ 不改变图像大小 """
    thief = ColorThief(path)
    thief.get_palette(quality=9)


def getColor_(path):
    """ 改变图像大小 """
    thief = ColorThief(path)
    if max(thief.image.size) > 400:
        thief.image = thief.image.resize((400, 400))
    thief.get_palette(quality=9)


path = 'Album_Cover/ねぐせ/ねぐせ.jpg'

# 统计耗时
t1 = Timer(f"getColor('{path}')", "from __main__ import getColor")
t2 = Timer(f"getColor_('{path}')", "from __main__ import getColor_")

print('不改变图像大小平均耗时：', min(t1.repeat(20, 1)))
print('改变图像大小平均耗时：', min(t2.repeat(20, 1)))
