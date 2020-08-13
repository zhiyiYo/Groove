import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QApplication, QPushButton, QWidget


class WindowMask(QWidget):
    """ 歌曲卡的半透明遮罩 """

    def __init__(self, parent, maskColor:tuple=(255,255,255,172)):
        super().__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground)
        # 设置背景色
        self.setStyleSheet(
            f'background:rgba({maskColor[0]},{maskColor[1]},{maskColor[2]},{maskColor[-1]});')
        self.hide()

    def show(self):
        """ 获取父窗口的位置后显示 """
        parent_rect = self.parent().geometry()
        self.setGeometry(0, 0, parent_rect.width(), parent_rect.height())
        self.raise_()
        super().show()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
