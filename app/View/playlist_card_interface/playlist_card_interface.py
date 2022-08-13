# coding:utf-8
from common.icon import getIconColor
from common.database.entity import Playlist
from common.library import Library
from common.style_sheet import setStyleSheet
from components.buttons.three_state_button import ThreeStatePushButton
from components.playlist_card import GridPlaylistCardView, PlaylistCardType
from components.selection_mode_interface import (
    PlaylistSelectionModeInterface, SelectionModeBarType)
from components.widgets.menu import AeroMenu
from PyQt5.QtCore import QFile, QMargins, QPoint, Qt, pyqtSignal
from PyQt5.QtWidgets import QAction, QLabel, QPushButton, QWidget


class PlaylistCardInterface(PlaylistSelectionModeInterface):
    """ Playlist card interface """

    createPlaylistSig = pyqtSignal()

    def __init__(self, library: Library, parent=None):
        self.sortMode = "modifiedTime"
        self.playlists = library.playlists

        view = GridPlaylistCardView(
            library,
            self.playlists,
            PlaylistCardType.PLAYLIST_CARD,
            margins=QMargins(15, 0, 15, 0),
        )
        super().__init__(library, view, SelectionModeBarType.PLAYLIST_CARD, parent)

        self.playlistCards = self.playlistCardView.playlistCards

        self.__createWidgets()
        self.__initWidget()

    def __createWidgets(self):
        """ create widgets """
        self.whiteMask = QWidget(self)
        self.playlistLabel = QLabel(self.tr("Playlist"), self)
        self.sortModeLabel = QLabel(self.tr("Sort by:"), self)
        self.sortModeButton = QPushButton(self.tr("Date modified"), self)
        c = getIconColor()
        self.createPlaylistButton = ThreeStatePushButton(
            {
                "normal": f":/images/playlist_card_interface/Add_{c}_normal.png",
                "hover": f":/images/playlist_card_interface/Add_{c}_hover.png",
                "pressed": f":/images/playlist_card_interface/Add_{c}_pressed.png",
            },
            self.tr(" New playlist"),
            (19, 19),
            self,
        )

        self.guideLabel = QLabel(
            self.tr('There is nothing to display here. Try a different filter.'), self)

        self.sortModeMenu = AeroMenu(parent=self)
        self.sortByModifiedTimeAct = QAction(
            self.tr("Date modified"), self, triggered=lambda: self.__sortPlaylist("modifiedTime"))
        self.sortByAToZAct = QAction(
            self.tr("A to Z"), self, triggered=lambda: self.__sortPlaylist("AToZ"))
        self.sortActs = [self.sortByModifiedTimeAct, self.sortByAToZAct]

        self.currentSortAct = self.sortByModifiedTimeAct

    def __initWidget(self):
        """ initialize widgets """
        self.resize(1270, 760)
        self.vBox.setContentsMargins(0, 175, 0, 120)
        self.guideLabel.setHidden(bool(self.playlistCards))
        self.sortModeMenu.addActions(self.sortActs)
        self.guideLabel.raise_()

        self.__setQss()
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        """ initialize layout """
        self.guideLabel.move(44, 196)
        self.playlistLabel.move(30, 54)
        self.createPlaylistButton.move(30, 131)
        self.sortModeLabel.move(
            self.createPlaylistButton.geometry().right()+30, 133)
        self.sortModeButton.move(self.sortModeLabel.geometry().right()+7, 132)

    def __setQss(self):
        """ set style sheet """
        self.sortModeLabel.setMinimumSize(50, 28)
        self.guideLabel.setMinimumSize(600, 40)
        self.playlistLabel.setObjectName("playlistLabel")
        self.sortModeLabel.setObjectName("sortModeLabel")
        self.sortModeButton.setObjectName("sortModeButton")
        self.createPlaylistButton.setObjectName("createPlaylistButton")
        self.sortModeMenu.setObjectName("sortModeMenu")
        self.sortModeMenu.setProperty("modeNumber", "2")
        self.guideLabel.setObjectName('guideLabel')
        setStyleSheet(self, 'playlist_card_interface')
        self.createPlaylistButton.adjustSize()
        self.sortModeLabel.adjustSize()
        self.guideLabel.adjustSize()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.whiteMask.resize(self.width() - 15, 175)

    def __sortPlaylist(self, key):
        """ sort playlist cards """
        self.sortMode = key
        if key == "modifiedTime":
            self.sortModeButton.setText(self.tr("Date modified"))
            self.currentSortAct = self.sortByModifiedTimeAct
            self.playlistCardView.setSortMode('modifiedTime')
        else:
            self.sortModeButton.setText(self.tr("A to Z"))
            self.currentSortAct = self.sortByAToZAct
            self.playlistCardView.setSortMode('A To Z')

    def __showSortModeMenu(self):
        """ show sort mode menu """
        self.sortModeMenu.setDefaultAction(self.currentSortAct)
        index = self.sortActs.index(self.currentSortAct)
        pos = self.sender().pos()-QPoint(0, 37*index+1)
        self.sortModeMenu.exec(self.mapToGlobal(pos))

    def addPlaylistCard(self, name: str, playlist: Playlist):
        """ add a playlist card """
        super().addPlaylistCard(name, playlist)
        self.guideLabel.hide()

    def deletePlaylistCard(self, name: str):
        """ delete a playlist card """
        super().deletePlaylistCard(name)
        self.guideLabel.setHidden(bool(self.playlistCards))

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.sortModeButton.clicked.connect(self.__showSortModeMenu)
        self.createPlaylistButton.clicked.connect(self.createPlaylistSig)
