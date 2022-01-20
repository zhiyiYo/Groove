# coding:utf-8

from PyQt5.QtCore import pyqtSignal, QPoint, QEvent
from PyQt5.QtWidgets import QWidget

from .navigation_bar import NavigationBar
from .navigation_widget import NavigationWidget
from .navigation_menu import NavigationMenu


class NavigationInterface(QWidget):
    """ 导航界面 """

    COMPACT = 0     # 折叠窗口
    OVERLAY = 1     # 显示导航菜单，窗口不展开
    IN_LINE = 2     # 导航窗口展开
    searchSig = pyqtSignal(str)                     # 搜索信号
    displayModeChanged = pyqtSignal(int)            # 显示模式改变
    showPlayingInterfaceSig = pyqtSignal()          # 显示正在播放界面信号
    showCreatePlaylistDialogSig = pyqtSignal()      # 显示创建播放列表对话框信号
    switchToSettingInterfaceSig = pyqtSignal()      # 切换到设置界面信号
    switchToMyMusicInterfaceSig = pyqtSignal()      # 切换到我的音乐界面
    switchToPlaylistInterfaceSig = pyqtSignal(str)  # 切换到播放列表界面信号
    switchToPlaylistCardInterfaceSig = pyqtSignal()  # 切换到播放列表卡界面

    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建部件
        self.navigationBar = NavigationBar(self)
        self.navigationWidget = NavigationWidget(self)
        self.navigationMenu = NavigationMenu(self)
        self.__navigation_list = [self.navigationBar,
                                  self.navigationWidget, self.navigationMenu]
        # 设置显示导航菜单/导航部件标志位
        self.__displayMode = self.COMPACT
        self.__isExpanded = False
        self.__isOverlay = False
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(self.navigationBar.width(), 800)
        self.setCurrentIndex(0)
        self.navigationWidget.hide()
        self.navigationWidget.showBarButton.setToolTip(
            self.tr('Minimize navigation pane'))
        self.__connectSignalToSlot()
        self.navigationMenu.installEventFilter(self)

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        # 发送切换窗口信号
        self.navigationWidget.switchToPlaylistInterfaceSig.connect(
            self.switchToPlaylistInterfaceSig)
        self.navigationMenu.switchToPlaylistInterfaceSig.connect(
            self.switchToPlaylistInterfaceSig)

        # 同步按钮选中状态
        self.navigationBar.selectedButtonChanged.connect(
            self.__onSelectedButtonChanged)
        self.navigationWidget.selectedButtonChanged.connect(
            self.__onSelectedButtonChanged)
        self.navigationMenu.selectedButtonChanged.connect(
            self.__onSelectedButtonChanged)

        # 发送搜索信号
        self.navigationMenu.searchSig.connect(self.__onSearch)
        self.navigationWidget.searchSig.connect(self.__onSearch)

        # 按钮点击信号连接到槽
        self.navigationBar.showMenuButton.clicked.connect(
            self.__expandNavigationWindow)
        self.navigationBar.searchButton.clicked.connect(
            self.__expandNavigationWindow)
        self.navigationMenu.showBarButton.clicked.connect(
            self.__collapseWindow)
        self.navigationWidget.showBarButton.clicked.connect(
            self.__collapseWindow)
        self.navigationMenu.playingButton.clicked.connect(
            self.__collapseWindow)
        self.navigationMenu.searchSig.connect(self.__collapseWindow)
        for widget in self.__navigation_list:
            widget.playingButton.clicked.connect(
                self.showPlayingInterfaceSig)
            widget.settingButton.clicked.connect(
                self.switchToSettingInterfaceSig)
            widget.myMusicButton.clicked.connect(
                self.switchToMyMusicInterfaceSig)
            widget.playlistButton.clicked.connect(
                self.switchToPlaylistCardInterfaceSig)
            widget.createPlaylistButton.clicked.connect(
                self.showCreatePlaylistDialogSig)

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
                self.__isExpanded = False
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
            self.navigationMenu.aniShow()
            self.displayModeChanged.emit(self.OVERLAY)
            self.navigationBar.hide()

    def __collapseWindow(self):
        """ 折叠导航窗口 """
        self.__isExpanded = False
        self.__displayMode = self.COMPACT
        self.navigationBar.show()
        self.navigationWidget.hide()
        if self.sender() is self.navigationMenu.showBarButton:
            self.navigationMenu.aniHide()
        elif self.sender() is self.navigationMenu.playingButton:
            self.navigationMenu.hide()
        self.resize(self.navigationBar.width(), self.height())
        self.displayModeChanged.emit(self.__displayMode)

    def setOverlay(self, isOverlay: bool):
        """ 设置展开导航界面时是否为overlay显示模式 """
        self.__isOverlay = isOverlay

    def __onSelectedButtonChanged(self, name):
        """ 选中的按钮变化对应的槽函数 """
        for widget in self.__navigation_list:
            if widget is not self.sender():
                widget.setSelectedButton(name)

    def setCurrentIndex(self, index: int):
        """ 选中下标对应的按钮 """
        for widget in self.__navigation_list:
            widget.setCurrentIndex(index)

    def updateWindow(self):
        """ 更新窗口 """
        self.navigationMenu.updateWindow()
        self.navigationWidget.updateWindow()

    def __onSearch(self, text):
        """ 搜索信号槽函数 """
        self.navigationBar.currentButton.setSelected(False)
        self.navigationMenu.currentButton.setSelected(False)
        self.navigationWidget.currentButton.setSelected(False)
        self.searchSig.emit(text)

    @property
    def isOverlay(self):
        return self.__isOverlay

    @property
    def isExpanded(self):
        return self.__isExpanded

    @property
    def displayMode(self):
        return self.__displayMode
