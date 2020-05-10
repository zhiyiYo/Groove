from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtCore import QIODevice, QFile
from PyQt5.QtWidgets import qApp


def onLoadFont(strPath):
    """ 读取字体文件 """
    dFontFile = QFile(strPath)

    if not dFontFile.open(QIODevice.ReadOnly):
        # 打开字体文件失败
        return None

    nFontId = QFontDatabase.addApplicationFontFromData(dFontFile.readAll())
    if nFontId == -1:
        # 加载字体文件失败，字体文件不可用
        return None

    lFontFamily = QFontDatabase.applicationFontFamilies(nFontId)
    if not lFontFamily:
        # 说明从字体中获取字体簇失败了
        return None

    print(lFontFamily)
    font = QFont(lFontFamily[0])
    dFontFile.close()
    return font
