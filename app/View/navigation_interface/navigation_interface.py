# coding:utf-8
from common.signal_bus import signalBus
from PyQt5.QtCore import QEvent, QPoint, pyqtSignal
from PyQt5.QtWidgets import QWidget

from .navigation_bar import NavigationBar
from .navigation_menu import NavigationMenu
from .navigation_widget import NavigationWidget


class NavigationInterface(QWidget):
    """ Navigation interface """

    COMPACT = 0     # show navigation bar
    OVERLAY = 1     # show navigation menu
    IN_LINE = 2     # show navigation widget
    searchSig = pyqtSignal(str)                # 搜索信号
    displayModeChanged = pyqtSignal(int)       # 显示模式改变
    showCreatePlaylistDialogSig = pyqtSignal() # 显示创建播放列表对话框信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.navigationBar = NavigationBar(self)
        self.navigationWidget = NavigationWidget(self)
        self.navigationMenu = NavigationMenu(self)
        self.__navigation_list = [self.navigationBar,
                                  self.navigationWidget, self.navigationMenu]
        self.__displayMode = self.COMPACT
        self.__isExpanded = False
        self.__isOverlay = False
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.resize(self.navigationBar.width(), 800)
        self.setCurrentIndex(0)
        self.navigationWidget.hide()
        # self.navigationWidget.showBarButton.setToolTip(
        #     self.tr('Minimize navigation pane'))
        self.__connectSignalToSlot()
        self.navigationMenu.installEventFilter(self)

    def __connectSignalToSlot(self):
        """ connect signal to slot """

        # set selected button
        self.navigationBar.selectedButtonChanged.connect(
            self.__onSelectedButtonChanged)
        self.navigationWidget.selectedButtonChanged.connect(
            self.__onSelectedButtonChanged)
        self.navigationMenu.selectedButtonChanged.connect(
            self.__onSelectedButtonChanged)

        # search
        self.navigationMenu.searchSig.connect(self.__onSearch)
        self.navigationWidget.searchSig.connect(self.__onSearch)

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
                signalBus.showPlayingInterfaceSig)
            widget.settingButton.clicked.connect(
                signalBus.switchToSettingInterfaceSig)
            widget.myMusicButton.clicked.connect(
                signalBus.switchToMyMusicInterfaceSig)
            widget.playlistButton.clicked.connect(
                signalBus.switchToPlaylistCardInterfaceSig)
            widget.createPlaylistButton.clicked.connect(
                self.showCreatePlaylistDialogSig)

    def resizeEvent(self, e):
        self.navigationBar.resize(self.navigationBar.width(), self.height())
        self.navigationMenu.resize(self.navigationMenu.width(), self.height())
        self.navigationWidget.resize(
            self.navigationWidget.width(), self.height())

    def eventFilter(self, obj, e: QEvent):
        if obj is self.navigationMenu:
            if e.type() == QEvent.Hide:
                self.__isExpanded = False
                self.navigationBar.show()

        return super().eventFilter(obj, e)

    def __expandNavigationWindow(self):
        """ expand navigation window """
        self.__isExpanded = True
        if not self.__isOverlay:
            # show navigation widget
            self.__displayMode = self.IN_LINE
            self.resize(self.navigationWidget.width(), self.height())
            self.navigationWidget.updateWindow()
            self.displayModeChanged.emit(self.IN_LINE)
            self.navigationWidget.show()
            self.navigationBar.hide()
        else:
            # show navigation menu
            self.__displayMode = self.OVERLAY
            self.navigationMenu.move(self.mapToGlobal(QPoint(0, 0)))
            self.navigationMenu.updateWindow()
            self.navigationMenu.aniShow()
            self.displayModeChanged.emit(self.OVERLAY)
            self.navigationBar.hide()

    def __collapseWindow(self):
        """ collapese navigation window """
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
        """ set whether in overlay mode """
        self.__isOverlay = isOverlay

    def __onSelectedButtonChanged(self, name):
        """ selected button changed slot """
        for widget in self.__navigation_list:
            if widget is not self.sender():
                widget.setSelectedButton(name)

    def setCurrentIndex(self, index: int):
        """ set selected button """
        for widget in self.__navigation_list:
            widget.setCurrentIndex(index)

    def updateWindow(self):
        """ update window """
        self.navigationMenu.updateWindow()
        self.navigationWidget.updateWindow()

    def __onSearch(self, text):
        """ search slot """
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
