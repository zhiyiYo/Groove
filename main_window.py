# coding:utf-8

import sys
from ctypes.wintypes import HWND,MSG
from enum import Enum

from PyQt5.QtCore import QPoint, QRect, QSize, Qt
from PyQt5.QtGui import QCloseEvent, QIcon, QPixmap, QResizeEvent
from PyQt5.QtWidgets import (QAction, QApplication, QGraphicsDropShadowEffect,
                             QWidget)

from effects.window_effect import WindowEffect
from my_music_interface import MyMusicInterface
from my_play_bar.play_bar import PlayBar
from my_title_bar.title_bar import TitleBar
from navigation.navigation_bar import NavigationBar
from navigation.navigation_menu import NavigationMenu


class MainWindow(QWidget):
    """ 主窗口 """

    def __init__(self, songs_folder, parent=None):
        super().__init__(parent)

        # 实例化窗口特效
        self.windowEffect = WindowEffect()
        # 实例化小部件
        self.titleBar = TitleBar(self)
        self.navigationBar = NavigationBar(self)
        self.navigationMenu = NavigationMenu(self)
        self.currentNavigation = self.navigationBar
        self.myMusicInterface = MyMusicInterface(songs_folder, self)
        songInfo = {
            'songName': 'オオカミと少女 (狼与少女)', 'songer': 'RADWIMPS', 'duration': '3:50',
            'album': [r'resource\\Album Cover\\(un)sentimental spica\\(un)sentimental spica.jpg']}
        self.currentRightWindow = self.myMusicInterface
        self.titleBar = TitleBar(self)
        self.playBar = PlayBar(songInfo, self)
        # 初始化界面
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        self.resize(1400, 970)
        # 打开鼠标跟踪，用来检测鼠标是否位于边界处
        self.setMouseTracking(True)
        self.setObjectName('mainWindow')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet('QWidget#mainWindow{background:transparent}')
        self.setAttribute(Qt.WA_TranslucentBackground | Qt.WA_StyledBackground)
        # 居中显示
        desktop = QApplication.desktop()
        self.move(int(desktop.width() / 2 - self.width() / 2),
                  int((desktop.height()-120) / 2 - self.height() / 2))
        # 标题栏置顶
        self.titleBar.raise_()
        # 隐藏导航菜单
        self.navigationMenu.hide()
        # 设置窗口特效
        self.setWindowEffect()
        # 设置右边子窗口的位置
        self.setWidgetGeometry()
        # 将按钮点击信号连接到槽函数
        self.navigationBar.showMenuButton.clicked.connect(
            self.showNavigationMenu)
        self.navigationBar.searchButton.clicked.connect(
            self.showNavigationMenu)
        self.navigationMenu.showBarButton.clicked.connect(
            self.showNavigationBar)

    def setWindowEffect(self):
        """ 设置窗口特效 """
        # 开启亚克力效果和阴影效果
        self.hWnd = HWND(int(self.winId()))
        self.windowEffect.setAcrylicEffect(self.hWnd, 'F2F2F250', True)

    def setWidgetGeometry(self):
        """ 调整小部件的geometry """
        self.titleBar.resize(self.width(), 40)
        self.navigationBar.resize(60, self.height())
        self.navigationMenu.resize(400, self.height())
        self.currentRightWindow.move(self.currentNavigation.width(), 0)
        self.currentRightWindow.resize(self.width() - self.currentNavigation.width(), self.height())
        self.playBar.resize(self.width(),self.playBar.height())

    def resizeEvent(self, e: QResizeEvent):
        """ 调整尺寸时同时调整子窗口的尺寸 """
        self.setWidgetGeometry()

    def showNavigationMenu(self):
        """ 显示导航菜单和抬头 """
        self.currentNavigation = self.navigationMenu
        self.navigationBar.hide()
        self.navigationMenu.show()
        self.titleBar.title.show()
        self.setWidgetGeometry()
        if self.sender() == self.navigationBar.searchButton:
            self.navigationMenu.searchLineEdit.setFocus()

    def showNavigationBar(self):
        """ 显示导航栏 """
        self.currentNavigation = self.navigationBar
        self.navigationMenu.hide()
        self.titleBar.title.hide()
        self.navigationBar.show()
        self.setWidgetGeometry()

    def moveEvent(self, e):
        if hasattr(self, 'playBar'):
            if self.playBar.moveTime > 0:
                self.playBar.move(self.x() - 8, self.y() +
                                  self.height() - self.playBar.height())
            else:
                self.playBar.move(self.x() + 1, self.y() +
                                  self.height() - self.playBar.height() + 40)
            self.playBar.moveTime += 1

    def closeEvent(self, e: QCloseEvent):
        self.playBar.close()
        e.accept()

    def GET_X_LPARAM(self, param):
        return param & 0xffff

    def GET_Y_LPARAM(self, param):
        return param >> 16

    def nativeEvent(self, eventType, message):
        result = 0
        msg2 = MSG.from_address(message.__int__())
        #minV, maxV = 18, 22
        minV, maxV = 2,6
        if msg2.message == 0x0084:
            xPos = self.GET_X_LPARAM(msg2.lParam) - self.frameGeometry().x()
            yPos = self.GET_Y_LPARAM(msg2.lParam) - self.frameGeometry().y()
            if(xPos > minV and xPos < maxV):
                result = Flags.HTLEFT.value
            elif(xPos > (self.width() - maxV) and xPos < (self.width() - minV)):
                result = Flags.HTRIGHT.value
            elif(yPos > minV and yPos < maxV):
                result = Flags.HTTOP.value
            elif(yPos > (self.height() - maxV) and yPos < (self.height() - minV)):
                result = Flags.HTBOTTOM.value
            elif(xPos > minV and xPos < maxV and yPos > minV and yPos < maxV):
                result = Flags.HTTOPLEFT.value
            elif(xPos > (self.width() - maxV) and xPos < (self.width() - minV) and yPos > minV and yPos < maxV):
                result = Flags.HTTOPRIGHT.value
            elif(xPos > minV and xPos < maxV and yPos > (self.height() - maxV) and yPos < (self.height() - minV)):
                result = Flags.HTBOTTOMLEFT.value
            elif(xPos > (self.width() - maxV) and xPos < (self.width() - minV) and yPos > (self.height() - maxV) and yPos < (self.height() - minV)):
                result = Flags.HTBOTTOMRIGHT.value
            if result!=0:
                return (True, result)
        return QWidget.nativeEvent(self, eventType, message)
    

class Flags(Enum):
    """ 包含各宏定义的枚举类 """
    HTCAPTION = 2
    HTLEFT = 10
    HTRIGHT = 11
    HTTOP = 12
    HTTOPLEFT = 13
    HTTOPRIGHT = 14
    HTBOTTOM = 15
    HTBOTTOMLEFT = 16
    HTBOTTOMRIGHT = 17
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = MainWindow('D:\\KuGou\\')
    demo.show()
    demo.playBar.show()
    sys.exit(app.exec_())
