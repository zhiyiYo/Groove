import sys

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QMenu, QAction, QGraphicsDropShadowEffect

from my_widget.my_menu import Menu

class Window(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.NoDropShadowWindowHint)
        self.resize(500, 500)
        self.menu = Menu(parent=self)
        self.openAct = QAction(QIcon('resource\\images\\正在播放.svg'),'打开', self)
        self.saveAct = QAction('保存', self)
        self.menu.addAction(self.openAct)
        self.menu.addAction(self.saveAct)
        print(self.menu.window())
        self.setWindowState(Qt.WindowFullScreen)

    def contextMenuEvent(self, e):
        self.menu.exec(self.cursor().pos())




if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Window()
    demo.show()
    sys.exit(app.exec_())
