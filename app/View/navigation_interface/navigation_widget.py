# coding:utf-8
from pathlib import Path

from common.os_utils import getPlaylistNames
from common.signal_bus import signalBus
from components.widgets.scroll_area import ScrollArea
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import QWidget

from .navigation_button import CreatePlaylistButton, PushButton, ToolButton
from .navigation_widget_base import NavigationWidgetBase
from .search_line_edit import SearchLineEdit


class NavigationWidget(NavigationWidgetBase):
    """ Navigation widget """

    searchSig = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.scrollArea = ScrollArea(self)
        self.scrollWidget = ScrollWidget(self)
        self.searchLineEdit = SearchLineEdit(self)
        self.__createButtons()
        self.__initWidget()

    def __createButtons(self):
        """ create buttons """
        self.showBarButton = ToolButton(
            ":/images/navigation_interface/GlobalNavButton.png", parent=self)
        self.myMusicButton = PushButton(
            ":/images/navigation_interface/MusicInCollection.png", self.tr("My music"), (400, 60), self.scrollWidget)
        self.historyButton = PushButton(
            ":/images/navigation_interface/Recent.png", self.tr("Recent plays"), (400, 62), self.scrollWidget)
        self.playingButton = PushButton(
            ":/images/navigation_interface/Playing.png", self.tr("Now playing"), (400, 62), self.scrollWidget)
        self.playlistButton = PushButton(
            ":/images/navigation_interface/Playlist.png", self.tr("Playlists"), (340, 60), self.scrollWidget)
        self.createPlaylistButton = CreatePlaylistButton(self.scrollWidget)
        self.settingButton = PushButton(
            ":/images/navigation_interface/Settings.png", self.tr("Settings"), (400, 62), self)

        self.__createPlaylistNameButtons(getPlaylistNames())

        self.currentButton = self.myMusicButton

        self._selectableButtons = [
            self.myMusicButton,
            self.historyButton,
            self.playingButton,
            self.playlistButton,
            self.settingButton,
        ] + self.playlistNameButtons

        self._selectableButtonNames = [
            "myMusicButton",
            "historyButton",
            "playingButton",
            "playlistButton",
            "settingButton",
        ] + self.playlistNames

    def __initWidget(self):
        """ initialize widgets """
        self.resize(400, 800)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setSelectedButton(self.myMusicButton.property('name'))

        # connect signal to slot
        self._connectButtonClickedSigToSlot()
        self.__connectPlaylistNameClickedSigToSlot()
        self.searchLineEdit.searchButton.clicked.connect(
            self._onSearchButtonClicked)

        self.__initLayout()

    def __initLayout(self):
        """ initialize layout """
        self.scrollArea.move(0, 162)
        self.scrollArea.setWidget(self.scrollWidget)

        self.historyButton.move(0, 62)
        self.showBarButton.move(0, 40)
        self.playingButton.move(0, 124)
        self.playlistButton.move(0, 186)
        self.searchLineEdit.move(15, 108)
        self.createPlaylistButton.move(340, 186)
        self.settingButton.move(0, self.height() - 187)
        self.__addPlaylistNameButtonsToScrollWidget()
        self.__adjustScrollWidgetHeight()

    def resizeEvent(self, e):
        self.scrollArea.resize(self.width(), self.height() - 347)
        self.scrollWidget.resize(self.width(), self.scrollWidget.height())
        self.settingButton.move(0, self.height() - 62 - 115 - 10)

    def paintEvent(self, e):
        """ paint seperator """
        painter = QPainter(self)
        painter.setPen(QColor(0, 0, 0, 30))
        painter.drawLine(15, self.settingButton.y()-1,
                         self.width()-15, self.settingButton.y()-1)

    def __addPlaylistNameButtonsToScrollWidget(self):
        """ add playlist name buttons to scroll widget """
        for index, button in enumerate(self.playlistNameButtons):
            button.move(0, 246 + index * 62)
            button.show()

    def __adjustScrollWidgetHeight(self):
        """ adjust the height of scroll widget """
        buttonHeight = 246 + 62 * len(self.playlistNames)
        height = self.height()-346 if self.height()-346 > buttonHeight else buttonHeight
        self.scrollWidget.resize(400, height)

    def updateWindow(self):
        """ update window """
        playlistNames = getPlaylistNames()
        if playlistNames == self.playlistNames:
            return

        while self.playlistNameButtons:
            self._selectableButtons.pop()
            self._selectableButtonNames.pop()
            button = self.playlistNameButtons.pop()
            button.deleteLater()

        # create new buttons
        self.__createPlaylistNameButtons(playlistNames)
        self._selectableButtonNames += playlistNames
        self._selectableButtons += self.playlistNameButtons
        self._connectButtonClickedSigToSlot()
        self.__connectPlaylistNameClickedSigToSlot()

        # move buttons
        self.__addPlaylistNameButtonsToScrollWidget()
        self.__adjustScrollWidgetHeight()
        self.update()

    def __createPlaylistNameButtons(self, playlistNames: list):
        """ create playlist name buttons """
        self.playlistNames = playlistNames
        self.playlistNameButtons = [
            PushButton(":/images/navigation_interface/Album.png",
                       i, (400, 62), self.scrollWidget)
            for i in playlistNames
        ]

    def __connectPlaylistNameClickedSigToSlot(self):
        """ connect playlist name button clicked signal to slot """
        for button in self.playlistNameButtons:
            name = button.property('name')
            button.clicked.connect(
                lambda checked, name=name: signalBus.switchToPlaylistInterfaceSig.emit(name))

    def _onSearchButtonClicked(self):
        """ search button clicked slot """
        text = self.searchLineEdit.text()
        if text:
            self.currentButton.setSelected(False)
            self.searchSig.emit(text)


class ScrollWidget(QWidget):
    """ Scroll widget """

    def paintEvent(self, e):
        """ paint seperator """
        painter = QPainter(self)
        pen = QPen(QColor(0, 0, 0, 30))
        painter.setPen(pen)
        painter.drawLine(15, 185, self.width() - 15, 185)
