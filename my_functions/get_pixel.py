import sys
import re
from json import load

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit


class Demo(QWidget):
    def __init__(self, albumPath: str):
        super().__init__()
        self.resize(240, 240)
        self.albumPic = QLabel(self)
        self.setAlbumPic(albumPath)
        self.lineEdit = QLineEdit(self)
        self.__initWidget()

    def __initWidget(self):
        """ 初始化 """
        self.lineEdit.setFixedSize(120, 40)
        self.lineEdit.move(int(self.width() / 2 - self.lineEdit.width() / 2),
                           int(self.height() / 2 - self.lineEdit.height() / 2)-30)
        self.lineEdit.textChanged.connect(self.printRgb)
        with open(r'resource\css\songInfoEditPanel.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def setAlbumPic(self, albumPath):
        """ 设置背景图 """
        self.albumPath = albumPath
        self.albumPixmap = QPixmap(albumPath).scaled(self.size(),
                                                     Qt.KeepAspectRatio, Qt.SmoothTransformation)  # type:QPixmap
        self.albumPic.setPixmap(self.albumPixmap)

    def printRgb(self):
        """ 打印像素信息 """
        coordinate = self.lineEdit.text()
        rex = r'(\d+) (\d+)'
        matchRes = re.match(rex, coordinate)
        if matchRes:
            x = int(matchRes.group(1))
            y = int(matchRes.group(2))
            # 获取QRgba对象
            pix = self.albumPixmap.toImage().pixel(x, y)
            # 返回rgba元组
            print(QColor(pix).getRgb())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo(r'resource\Album_Cover\つぶやきレター\つぶやきレター.jpg')
    demo.show()
    sys.exit(app.exec_())
