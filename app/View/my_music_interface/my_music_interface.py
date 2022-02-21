# coding:utf-8
from typing import List

from common.database.entity import SongInfo
from common.library import Library
from common.signal_bus import signalBus
from components.widgets.stacked_widget import PopUpAniStackedWidget
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QWidget

from .album_tab_interface import AlbumTabInterface
from .song_tab_interface import SongTabInterface
from .tool_bar import ToolBar


class MyMusicInterface(QWidget):
    """ My music interface """

    currentIndexChanged = pyqtSignal(int)   # 当前标签页变化

    def __init__(self, library: Library, parent=None):
        super().__init__(parent=parent)
        self.library = library
        self.isInSelectionMode = False
        self.stackedWidget = PopUpAniStackedWidget(self)
        self.songTabInterface = SongTabInterface(self.library.songInfos, self)
        self.albumTabInterface = AlbumTabInterface(library, self)
        self.toolBar = ToolBar(self)

        self.songTabButton = self.toolBar.songTabButton
        self.albumTabButton = self.toolBar.albumTabButton
        self.currentSongSortAct = self.toolBar.songSortByCratedTimeAct
        self.currentAlbumSortAct = self.toolBar.albumSortByCratedTimeAct
        self.songListWidget = self.songTabInterface.songListWidget
        self.albumCardView = self.albumTabInterface.albumCardView

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.resize(1300, 970)

        self.stackedWidget.addWidget(self.songTabInterface, 0, 30)
        self.stackedWidget.addWidget(self.albumTabInterface, 0, 30)
        self.songTabButton.setSelected(True)

        text = self.tr(" Shuffle all")
        self.toolBar.randomPlayAllButton.setText(
            text+f" ({self.songListWidget.songCardNum()})")
        self.toolBar.randomPlayAllButton.adjustSize()

        # set background color
        self.setAutoFillBackground(True)
        palette = QPalette()
        palette.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(palette)

        self.__connectSignalToSlot()

    def __onCurrentTabChanged(self, index):
        """ current tab changed slot """
        self.toolBar.songSortModeButton.setVisible(index == 0)
        self.toolBar.albumSortModeButton.setVisible(index == 1)

        text = self.tr(" Shuffle all")
        if index == 0:
            self.toolBar.randomPlayAllButton.setText(
                text+f" ({self.songListWidget.songCardNum()})")
        elif index == 1:
            self.toolBar.randomPlayAllButton.setText(
                text+f" ({len(self.albumCardView.albumCards)})")

        self.toolBar.randomPlayAllButton.adjustSize()

    def deleteSongs(self, songPaths: List[str]):
        """ delete songs """
        self.songTabInterface.deleteSongs(songPaths)
        self.albumTabInterface.updateWindow(self.library.albumInfos)

    def exitSelectionMode(self):
        """ exit selection mode """
        self.songTabInterface.exitSelectionMode()
        self.__unCheckAlbumCards()

    def setCurrentTab(self, index: int):
        """ set current tab interface """
        self.setSelectedButton(index)
        self.stackedWidget.setCurrentIndex(index, duration=300)

    def setSelectedButton(self, index):
        """ set selected tab button """
        for button in [self.songTabButton, self.albumTabButton]:
            button.setSelected(button.tabIndex == index)

    def __onButtonSelected(self, tabIndex: int):
        """ tab button clicked slot """
        if self.isInSelectionMode:
            return

        self.setCurrentTab(tabIndex)
        self.currentIndexChanged.emit(tabIndex)

    def resizeEvent(self, e):
        self.stackedWidget.resize(self.size())
        self.toolBar.resize(self.width()-10, self.toolBar.height())

    def updateSongInfo(self, newSongInfo: SongInfo):
        """ update song information """
        self.songListWidget.updateOneSongCard(newSongInfo)
        self.albumTabInterface.updateWindow(self.library.albumInfos)

    def updateMultiSongInfos(self, songInfos: List[SongInfo]):
        """ update multi song information """
        self.songListWidget.updateMultiSongCards(songInfos)
        self.albumTabInterface.updateWindow(self.library.albumInfos)

    def __showSortModeMenu(self):
        """ show sort mode menu """
        pos = self.sender().pos()
        if self.sender() is self.toolBar.songSortModeButton:
            self.toolBar.songSortModeMenu.setDefaultAction(
                self.currentSongSortAct)
            actIndex = self.toolBar.songSortActions.index(
                self.currentSongSortAct)
            self.toolBar.songSortModeMenu.exec(
                self.mapToGlobal(QPoint(pos.x(), pos.y() - 37 * actIndex - 1)))

        elif self.sender() is self.toolBar.albumSortModeButton:
            self.toolBar.albumSortModeMenu.setDefaultAction(
                self.currentAlbumSortAct)
            actIndex = self.toolBar.albumSortActions.index(
                self.currentAlbumSortAct)
            self.toolBar.albumSortModeMenu.exec(
                self.mapToGlobal(QPoint(pos.x(), pos.y() - 37 * actIndex - 1)))

    def __sortSongCard(self):
        """ sort song cards """
        sender = self.sender()
        self.currentSongSortAct = sender
        self.toolBar.songSortModeButton.setText(sender.text())
        self.songListWidget.setSortMode(sender.property('mode'))

    def __sortAlbumCard(self):
        """ sort album cards """
        sender = self.sender()
        self.currentAlbumSortAct = sender
        self.toolBar.albumSortModeButton.setText(sender.text())
        self.albumTabInterface.setSortMode(sender.property('mode'))

    def scrollToLabel(self, label: str):
        """ scroll to the position specified by label """
        self.stackedWidget.currentWidget().scrollToLabel(label)

    def updateWindow(self):
        """ update window """
        self.songTabInterface.updateWindow(self.library.songInfos)
        self.albumTabInterface.updateWindow(self.library.albumInfos)

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.songTabButton.buttonSelected.connect(self.__onButtonSelected)
        self.albumTabButton.buttonSelected.connect(self.__onButtonSelected)

        self.toolBar.songSortModeButton.clicked.connect(
            self.__showSortModeMenu)
        self.toolBar.albumSortModeButton.clicked.connect(
            self.__showSortModeMenu)
        self.toolBar.randomPlayAllButton.clicked.connect(
            signalBus.randomPlayAllSig)
        for act in self.toolBar.songSortActions:
            act.triggered.connect(self.__sortSongCard)
        for act in self.toolBar.albumSortActions:
            act.triggered.connect(self.__sortAlbumCard)

        self.stackedWidget.currentChanged.connect(self.__onCurrentTabChanged)

        self.songListWidget.songCardNumChanged.connect(
            lambda: self.__onCurrentTabChanged(self.stackedWidget.currentIndex()))

        self.albumCardView.albumNumChanged.connect(
            lambda: self.__onCurrentTabChanged(self.stackedWidget.currentIndex()))
