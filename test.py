import sys

from colorthief import ColorThief
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QPixmap,QColor
from PyQt5.QtWidgets import QAction, QApplication, QFileDialog, QMenu, QWidget, QLabel


class Demo(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(500, 500)
        self.pic = QLabel(self)
        self.pic.resize(250, 250)
        self.menu = QMenu(self)
        self.openAct = QAction('打开', self)
        self.menu.addAction(self.openAct)
        self.openAct.triggered.connect(self.selectPic)
        self.pic.move(125, 125)

    def contextMenuEvent(self, e):
        self.menu.exec(e.globalPos())

    def selectPic(self):
        """ 选择图片 """
        filePath, filterType = QFileDialog.getOpenFileName(
            self, '打开', 'resource\\Album_Cover', '图片(*.png;*.jpg;*.jpeg)')
        if filePath:
            colorThief = ColorThief(filePath)
            r, g, b = colorThief.get_color()
            print('主色调：', (r, g, b))
            palette = QPalette()
            palette.setColor(self.backgroundRole(), QColor(r, g, b))
            self.setPalette(palette)
            self.pic.setPixmap(QPixmap(filePath).scaled(
                250, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
