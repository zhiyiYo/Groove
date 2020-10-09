# coding:utf-8

from ctypes.wintypes import HWND

from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QEvent
from PyQt5.QtWidgets import QWidget

from .navigation_bar import NavigationBar
from .navigation_widget import NavigationWidget
from effects import WindowEffect


class NavigationInterface(QWidget):
    """ 导航界面 """

    COLLAPE = 0     # 折叠窗口
    OVERLAY = 1     # 显示导航菜单，窗口不展开
    IN_LINE = 2     # 导航窗口展开
    displayModeChanged = pyqtSignal(int)
    switchInterfaceSig = pyqtSignal(int)
    showPlayingInterfaceSig = pyqtSignal()
    showCreatePlaylistPanelSig = pyqtSignal()
    switchToSettingInterfaceSig = pyqtSignal()
    switchToMyMusicInterfaceSig = pyqtSignal()
    switchToPlaylistCardInterfaceSig = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.effect = WindowEffect()
        # 创建部件
        self.navigationBar = NavigationBar(self)
        self.navigationWidget = NavigationWidget(self)
        self.navigationMenu = NavigationWidget(self)
        self.__navigation_list = [self.navigationBar,
                                  self.navigationWidget, self.navigationMenu]
        # 设置显示导航菜单/导航部件标志位
        self.__displayMode = self.COLLAPE
        self.__isExpanded = False
        self.__isOverlay = False
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(self.navigationBar.width(), 800)
        self.setCurrentIndex(0)
        self.navigationWidget.hide()
        # 设置弹出菜单
        self.navigationMenu.setWindowFlags(
            Qt.NoDropShadowWindowHint | Qt.Popup)
        self.effect.setAcrylicEffect(
            HWND(int(self.navigationMenu.winId())), 'F2F2F299')
        # 信号连接到槽
        self.__connectSignalToSlot()
        # 安装事件过滤器
        self.navigationMenu.installEventFilter(self)

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        # 发送切换窗口信号
        self.navigationBar.switchInterfaceSig.connect(self.switchInterfaceSig)
        self.navigationMenu.switchInterfaceSig.connect(self.switchInterfaceSig)
        # 同步按钮选中状态
        self.navigationBar.selectedButtonChanged.connect(
            self.__selectedButtonChangedSlot)
        self.navigationWidget.selectedButtonChanged.connect(
            self.__selectedButtonChangedSlot)
        self.navigationMenu.selectedButtonChanged.connect(
            self.__selectedButtonChangedSlot)
        # 发送切换窗口信号
        self.navigationWidget.switchInterfaceSig.connect(
            self.switchInterfaceSig)
        # 按钮点击信号连接到槽
        self.navigationBar.showMenuButton.clicked.connect(
            self.__expandNavigationWindow)
        self.navigationBar.searchButton.clicked.connect(
            self.__expandNavigationWindow)
        self.navigationMenu.showBarButton.clicked.connect(
            self.__collapseWindow)
        self.navigationWidget.showBarButton.clicked.connect(
            self.__collapseWindow)
        for widget in self.__navigation_list:
            widget.playingButton.clicked.connect(
                self.showPlayingInterfaceSig)
            widget.settingButton.clicked.connect(
                self.switchToSettingInterfaceSig)
            widget.musicGroupButton.clicked.connect(
                self.switchToMyMusicInterfaceSig)
            widget.playlistButton.clicked.connect(
                self.switchToPlaylistCardInterfaceSig)
            widget.createPlaylistButton.clicked.connect(
                self.showCreatePlaylistPanelSig)

    def resizeEvent(self, e):
        """ 调整小部件尺寸 """
        self.navigationBar.resize(self.navigationBar.width(), self.height())
        self.navigationMenu.resize(self.navigationMenu.width(), self.height())
        self.navigationWidget.resize(
            self.navigationWidget.width(), self.height())

    def eventFilter(self, obj, e: QEvent):
        """ 过滤事件 """
        if obj == self.navigationMenu:
            if e.type() == QEvent.Hide:
                self.navigationBar.show()
        return super().eventFilter(obj, e)

    def __expandNavigationWindow(self):
        """ 展开导航窗口 """
        self.__isExpanded = True
        if not self.__isOverlay:
            # 显示导航部件
            self.__displayMode = self.IN_LINE
            self.resize(self.navigationWidget.width(), self.height())
            self.navigationWidget.updateWindow()
            self.displayModeChanged.emit(self.IN_LINE)
            self.navigationWidget.show()
            self.navigationBar.hide()
        else:
            # 显示导航菜单
            self.__displayMode = self.OVERLAY
            self.navigationMenu.move(self.mapToGlobal(QPoint(0, 0)))
            self.navigationMenu.updateWindow()
            self.navigationMenu.show()
            #self.displayModeChanged.emit(self.OVERLAY)
            self.navigationMenu.stackUnder(self.navigationBar)
            self.navigationBar.hide()

    def __collapseWindow(self):
        """ 折叠导航窗口 """
        self.__isExpanded = False
        self.__displayMode = self.COLLAPE
        self.navigationBar.show()
        self.navigationMenu.hide()
        self.navigationWidget.hide()
        self.resize(self.navigationBar.width(), self.height())
        self.displayModeChanged.emit(self.__displayMode)

    def setOverlay(self, isOverlay: bool):
        """ 设置展开导航界面时是否为overlay显示模式 """
        self.__isOverlay = isOverlay

    def __selectedButtonChangedSlot(self, name):
        """ 选中的按钮变化对应的槽函数 """
        for widget in self.__navigation_list:
            if not (widget is self.sender()):
                widget.setSelectedButton(name)

    def setCurrentIndex(self, index: int):
        """ 选中下标对应的按钮 """
        for widget in self.__navigation_list:
            widget.setCurrentIndex(index)

    def updateWindow(self):
        """ 更新窗口 """
        self.navigationMenu.updateWindow()
        self.navigationWidget.updateWindow()

    @property
    def isOverlay(self):
        return self.__isOverlay

    @property
    def isExpanded(self):
        return self.__isExpanded

    @property
    def displayMode(self):
        return self.__displayMode
