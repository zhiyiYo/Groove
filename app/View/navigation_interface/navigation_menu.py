# coding:utf-8

from ctypes.wintypes import HWND

from app.common.window_effect import WindowEffect
from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt

from .navigation_widget import NavigationWidget


class NavigationMenu(NavigationWidget):
    """ 导航菜单 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 是否削减设置按钮底部空白标志位
        self.__isShowBottomSpacing = False
        self.__ani = QPropertyAnimation(self, b"geometry")
        # 创建窗口效果
        self.windowEffect = WindowEffect()
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(60, 800)
        self.setWindowFlags(Qt.NoDropShadowWindowHint | Qt.Popup)
        self.windowEffect.setAcrylicEffect(self.winId(), "F2F2F299", False)
        self.switchToPlaylistInterfaceSig.connect(self.aniHide)
        self.switchInterfaceSig.connect(self.aniHide)

    def resizeEvent(self, e):
        """ 调整小部件尺寸 """
        super().resizeEvent(e)
        self.scrollArea.resize(self.width(), self.height() - 232)
        self.settingButton.move(
            0, self.height() - 62 - 10 - self.__isShowBottomSpacing * 115)
        self.searchLineEdit.resize(self.width() - 30, self.searchLineEdit.height())

    def aniShow(self):
        """ 动画显示 """
        super().show()
        self.activateWindow()
        self.searchLineEdit.show()
        self.__ani.setStartValue(QRect(self.x(), self.y(), 60, self.height()))
        self.__ani.setEndValue(QRect(self.x(), self.y(), 400, self.height()))
        self.__ani.setEasingCurve(QEasingCurve.InOutQuad)
        self.__ani.setDuration(85)
        self.__ani.start()

    def aniHide(self):
        """ 动画隐藏 """
        self.__ani.setStartValue(QRect(self.x(), self.y(), 400, self.height()))
        self.__ani.setEndValue(QRect(self.x(), self.y(), 60, self.height()))
        self.__ani.finished.connect(self.__hideAniFinishedSlot)
        self.__ani.setDuration(85)
        self.searchLineEdit.hide()
        self.__ani.start()

    def __hideAniFinishedSlot(self):
        """ 隐藏窗体的动画结束 """
        super().hide()
        self.resize(60, self.height())
        self.__ani.disconnect()

    def setBottomSpacingVisible(self, isBottomSpacingVisible: bool):
        """ 是否削减设置按钮底部空白 """
        self.__isShowBottomSpacing = isBottomSpacingVisible

    def onSearchButtonClicked(self):
        """ 搜索按钮点击槽函数 """
        text = self.searchLineEdit.text()
        if text:
            self.aniHide()
            self.searchSig.emit(text)

    @property
    def isShowBottomSpacing(self):
        return self.__isShowBottomSpacing
