import sys
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import (
    QApplication, QGridLayout, QStackedWidget, QHBoxLayout, QVBoxLayout, QWidget, QPushButton)

from my_music_interface import MyMusicInterface


class MultiWindows(QWidget):
    """ 多窗口切换 """

    def __init__(self):
        super().__init__()
        self.resize(1300, 890)
        self.setStyleSheet('background:white')

        self.vbox = QVBoxLayout()
        self.stackWidget = QStackedWidget(self)
        self.musicGroup = MyMusicInterface(['D:\\KuGou\\test_audio'], self)
        self.initWidget()

    def initWidget(self):

        self.vbox.addWidget(self.stackWidget)
        self.stackWidget.addWidget(self.musicGroup)

        for albumCard in self.musicGroup.myMusicTabWidget.albumTag.albumCardViewer.albumCard_list:
            albumCard.songerName.clicked.connect(self.showSubWindow)

        self.setLayout(self.vbox)

    def showSubWindow(self):
        self.subWindow = SubWindow()
        self.subWindow.returnBt.clicked.connect(self.returnMainWindow)
        self.stackWidget.addWidget(self.subWindow)
        self.stackWidget.setCurrentWidget(self.subWindow)
        self.subWindow.show()

    def returnMainWindow(self):
        """ 从子窗口返回主界面 """
        self.stackWidget.setCurrentWidget(self.musicGroup)
        self.subWindow.close()


class SubWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.returnBt = QPushButton('返回', self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    multiWindows = MultiWindows()
    multiWindows.show()
    sys.exit(app.exec_())
