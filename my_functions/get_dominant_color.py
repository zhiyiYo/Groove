from haishoku.haishoku import Haishoku


def getDominantColor(imagePath) -> str:
    """ 获取指定图片的主色调，返回十六进制rgb字符串 """
    r, g, b = Haishoku.getDominant(imagePath)
    # 如果颜色太浅就使用主题色
    if r > 170 and g > 170 and b > 170:
        cond_1 = abs(r - g) <= 25 and abs(r - b) <= 25 and abs(g - b) <= 25
        cond_2 = (r > 220 and g > 220 and b > 200) or (
            (r > 200 and g > 220 and b > 220)) or (r > 220 and g > 200 and b > 200)
        if cond_1 or cond_2:
            r, g, b = 103, 108, 136
    rgbHex = hex(r)[2:].rjust(2, '0') + \
        hex(g)[2:].rjust(2, '0') + hex(b)[2:].rjust(2, '0')
    return rgbHex


if __name__ == "__main__":
    rgb = getDominantColor(
        r"D:\Python_Study\Groove\resource\Album_Cover\(un)sentimental spica\(un)sentimental spica.jpg")
    print(rgb)
