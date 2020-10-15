# coding:utf-8

from ctypes.wintypes import HWND

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, Qt, QRect

from .navigation_widget import NavigationWidget
from effects import WindowEffect


class NavigationMenu(NavigationWidget):
    """ 导航菜单 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.windowEffect = WindowEffect()
        # 是否削减设置按钮底部空白标志位
        self.__isShowBottomSpacing = False
        self.__ani = QPropertyAnimation(self, b'geometry')
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(60, 800)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.NoDropShadowWindowHint | Qt.Popup)
        self.hWnd = HWND(int(self.winId()))
        self.windowEffect.setAcrylicEffect(self.hWnd, 'F2F2F299')

    def resizeEvent(self, e):
        """ 调整小部件尺寸 """
        super().resizeEvent(e)
        self.settingButton.move(0, self.height()-62 -
                                10 - self.__isShowBottomSpacing * 115)
        self.searchLineEdit.resize(
            self.width() - 30, self.searchLineEdit.height())

    def aniShow(self):
        """ 动画显示 """
        super().show()
        self.__ani.setStartValue(QRect(self.x(), self.y(), 60, self.height()))
        self.__ani.setEndValue(QRect(self.x(), self.y(), 400, self.height()))
        self.__ani.setDuration(85)
        self.__ani.start()
        self.__ani.setEasingCurve(QEasingCurve.InOutQuad)

    def aniHide(self):
        """ 动画隐藏 """
        self.__ani.setStartValue(QRect(self.x(), self.y(), 400, self.height()))
        self.__ani.setEndValue(QRect(self.x(), self.y(), 60, self.height()))
        self.__ani.finished.connect(self.__hideAniFinishedSlot)
        self.__ani.setDuration(85)
        self.__ani.start()

    def __hideAniFinishedSlot(self):
        """ 隐藏窗体的动画结束 """
        super().hide()
        self.resize(60, self.height())
        self.__ani.disconnect()

    def setBottomSpacingVisible(self, isBottomSpacingVisible: bool):
        """ 是否削减设置按钮底部空白 """
        self.__isShowBottomSpacing = isBottomSpacingVisible
        
    @property
    def isShowBottomSpacing(self):
        return self.__isShowBottomSpacing