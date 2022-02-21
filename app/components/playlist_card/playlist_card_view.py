# coding:utf-8
from typing import Dict, List

import pinyin
from common.database.entity import Playlist, SongInfo
from common.library import Library
from common.signal_bus import signalBus
from components.dialog_box.message_dialog import MessageDialog
from components.dialog_box.rename_playlist_dialog import RenamePlaylistDialog
from components.layout import HBoxLayout, FlowLayout
from components.layout.h_box_layout import HBoxLayout
from PyQt5.QtCore import (QMargins, QParallelAnimationGroup, QPoint, Qt,
                          pyqtSignal)
from PyQt5.QtWidgets import QApplication, QWidget

from .blur_background import BlurBackground
from .playlist_card import (PlaylistCardBase, PlaylistCardFactory,
                            PlaylistCardType)


class PlaylistCardViewBase(QWidget):
    """ 播放列表卡视图 """

    checkedNumChanged = pyqtSignal(int, bool)

    def __init__(self, library: Library, playlists: List[Playlist], cardType: PlaylistCardType, create=True, parent=None):
        """
        Parameters
        ----------
        library: Library
            song library

        playlists: List[Playlist]
            playlist list

        cardType: PlaylistCardType
            playlist card type

        create: bool
            whether to create playlist card

        parent:
            parent window
        """
        super().__init__(parent=parent)
        self.library = library
        self.playlists = playlists
        self.cardType = cardType
        self.playlistCards = []         # type:List[PlaylistCardBase]
        self.playlistCardMap = {}       # type:Dict[str, PlaylistCardBase]
        self.checkedPlaylistCards = []  # type:List[PlaylistCardBase]
        self.blurBackground = BlurBackground(self)
        self.hideCheckBoxAniGroup = QParallelAnimationGroup(self)
        self.hideCheckBoxAniGroup.finished.connect(self.__hideAllCheckBox)
        self.blurBackground.hide()

        self.sortMode = 'modifiedTime'
        self.isInSelectionMode = False

        if create:
            for platlist in self.playlists:
                self._createPlaylistCard(platlist)
                QApplication.processEvents()

    def _createPlaylistCard(self, platlist: Playlist):
        """ create a playlist card """
        card = PlaylistCardFactory.create(self.cardType, platlist, self)
        self.hideCheckBoxAniGroup.addAnimation(card.hideCheckBoxAni)

        self._connectCardSignalToSlot(card)

        self.playlistCards.append(card)
        self.playlistCardMap[platlist.name] = card

    def _connectCardSignalToSlot(self, card: PlaylistCardBase):
        """ connect playlist card signal to slot """
        card.playSig.connect(
            lambda n: signalBus.playCheckedSig.emit(self.__getPlaylistSongInfos(n)))
        card.nextToPlaySig.connect(
            lambda n: signalBus.nextToPlaySig.emit(self.__getPlaylistSongInfos(n)))
        card.showBlurBackgroundSig.connect(self.__showBlurBackground)
        card.hideBlurBackgroundSig.connect(self.blurBackground.hide)
        card.renamePlaylistSig.connect(self.showRenamePlaylistDialog)
        card.deleteCardSig.connect(self.showDeleteCardDialog)
        card.checkedStateChanged.connect(self.__onPlaylistCardCheckedStateChanged)
        card.addSongsToCustomPlaylistSig.connect(
            lambda n1, n2: signalBus.addSongsToCustomPlaylistSig.emit(n1, self.__getPlaylistSongInfos(n2)))
        card.addSongsToNewCustomPlaylistSig.connect(
            lambda n: signalBus.addSongsToNewCustomPlaylistSig.emit(self.__getPlaylistSongInfos(n)))
        card.addSongsToPlayingPlaylistSig.connect(
            lambda n: signalBus.addSongsToPlayingPlaylistSig.emit(self.__getPlaylistSongInfos(n)))

    def __showBlurBackground(self, pos: QPoint, coverPath: str):
        """ show blur background """
        pos = self.mapFromGlobal(pos)
        self.blurBackground.setBlurPic(coverPath, 40)
        self.blurBackground.move(pos.x() - 30, pos.y() - 20)
        self.blurBackground.show()

    def showRenamePlaylistDialog(self, name: str):
        """ show rename playlist dialog box """
        w = RenamePlaylistDialog(self.library, name, self.window())
        w.renamePlaylistSig.connect(signalBus.renamePlaylistSig)
        w.exec()

    def showDeleteCardDialog(self, name: str):
        """ show delete playlist card dialog box """
        title = self.tr("Are you sure you want to delete this?")
        content = self.tr("If you delete") + f' "{name}" ' + \
            self.tr("it won't be on be this device anymore.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(lambda: signalBus.deletePlaylistSig.emit(name))
        w.exec()

    def __getPlaylistSongInfos(self, name: str):
        """ get song information of playlist """
        playlist = self.library.playlistController.getPlaylist(name)
        if not playlist:
            return []

        return playlist.songInfos

    def __hideAllCheckBox(self):
        """ hide check box of playlist cards """
        for card in self.playlistCards:
            card.checkBox.hide()

    def renamePlaylistCard(self, old: str, new: str):
        """ rename playlist card """
        if old not in self.playlistCardMap:
            return

        card = self.playlistCardMap.pop(old)
        card.playlist.name = new
        card.updateWindow(card.playlist)
        self.playlistCardMap[new] = card
        self.setSortMode(self.sortMode)

    def addSongsToPlaylistCard(self, name: str, songInfos: List[SongInfo]):
        """ add songs to playlist card """
        if name not in self.playlistCardMap:
            return

        card = self.playlistCardMap[name]
        index = self.playlistCards.index(card)
        playlist = self.library.playlistController.getPlaylist(name)
        self.playlists[index] = playlist
        card.updateWindow(playlist)

    def removeSongsFromPlaylistCard(self, name: str, songInfos: List[SongInfo]):
        """ remove songs from playlist card """
        if name not in self.playlistCardMap:
            return

        card = self.playlistCardMap[name]
        playlist = self.library.playlistController.getPlaylist(name)
        card.updateWindow(playlist)

    def deletePlaylistCard(self, name: str):
        """ delete a playlist card """
        if name not in self.playlistCardMap:
            return

        card = self.playlistCardMap.pop(name)
        self.layout().removeWidget(card)
        index = self.playlistCards.index(card)
        self.playlistCards.pop(index)
        self.hideCheckBoxAniGroup.takeAnimation(index)
        self.playlists.remove(card.playlist)
        card.deleteLater()

        self.adjustSize()

    def setPlaylistCards(self, playlistCards: List[PlaylistCardBase]):
        """ set playlist cards in the view and do not generate new cards """
        raise NotImplementedError

    def _addCardsToLayout(self):
        """ add all playlist cards to layout """
        raise NotImplementedError

    def _removeCardsFromLayout(self):
        """ remove all playlist cards from layout """
        raise NotImplementedError

    def updateAllCards(self, playlists: List[Playlist]):
        """ update all playlist cards """
        self._removeCardsFromLayout()

        N = len(playlists)
        N_ = len(self.playlistCards)
        if N < N_:
            for i in range(N_ - 1, N - 1, -1):
                card = self.playlistCards.pop()
                self.playlistCardMap.pop(card.name)
                self.hideCheckBoxAniGroup.takeAnimation(i)
                card.deleteLater()
        elif N > N_:
            for playlist in playlists[N_:]:
                self._createPlaylistCard(playlist)
                QApplication.processEvents()

        # update part of playlist cards
        self.playlists = playlists
        for i in range(min(N, N_)):
            playlist = playlists[i]
            self.playlistCards[i].updateWindow(playlist)
            QApplication.processEvents()

        self._addCardsToLayout()
        self.setStyle(QApplication.style())
        self.adjustSize()

    def setSortMode(self, mode: str):
        """ set the sort mode of playlist cards

        Parameters
        ----------
        mode: str
            sort mode, including `A To Z` and `modifiedTime`
        """
        self.sortMode = mode
        self._removeCardsFromLayout()

        if mode == 'modifiedTime':
            self.playlistCards.sort(key=lambda i: i.playlist[mode])
        else:
            self.playlistCards.sort(
                key=lambda i: pinyin.get_initial(i.playlist.name)[0].lower())

        self._removeCardsFromLayout()
        self._addCardsToLayout()

    def __onPlaylistCardCheckedStateChanged(self, card: PlaylistCardBase, isChecked: bool):
        """ playlist card checked state changed slot """
        N0 = len(self.checkedPlaylistCards)

        if card not in self.checkedPlaylistCards and isChecked:
            self.checkedPlaylistCards.append(card)
        elif card in self.checkedPlaylistCards and not isChecked:
            self.checkedPlaylistCards.remove(card)
        else:
            return

        N1 = len(self.checkedPlaylistCards)

        if N0 == 0 and N1 > 0:
            self.setSelectionModeOpen(True)
        elif N1 == 0:
            self.setSelectionModeOpen(False)

        isAllChecked = N1 == len(self.playlistCards)
        self.checkedNumChanged.emit(N1, isAllChecked)

    def setSelectionModeOpen(self, isOpen: bool):
        """ set whether to open selection mode """
        if self.isInSelectionMode == isOpen:
            return

        self.isInSelectionMode = isOpen
        for card in self.playlistCards:
            card.setSelectionModeOpen(isOpen)

        if not isOpen:
            self.hideCheckBoxAniGroup.start()

    def setAllChecked(self, isChecked: bool):
        """ set the checked state of all playlist cards """
        for card in self.playlistCards:
            card.setChecked(isChecked)

    def uncheckAll(self):
        """ uncheck all playlist cards """
        for card in self.checkedPlaylistCards.copy():
            card.setChecked(False)

    def adjustHeight(self):
        """ adjust view height """
        raise NotADirectoryError


class GridPlaylistCardView(PlaylistCardViewBase):
    """ Playlist card view with grid layout """

    def __init__(self, library: Library, playlists: List[Playlist], cardType: PlaylistCardType,
                 spacings=(10, 20), margins=QMargins(0, 0, 0, 0), create=True, parent=None):
        """
        Parameters
        ----------
        library: Library
            song library

        playlists: List[Playlist]
            playlist list

        cardType: PlaylistCardType
            playlist card type

        spacings: tuple
            horizontal and vertical spacing between playlist cards

        margins: QMargins
            margins of grid layout

        create: bool
            whether to create album card

        parent:
            parent window
        """
        super().__init__(library, playlists, cardType, create, parent)
        self.column = 3
        self.flowLayout = FlowLayout(self)
        self.flowLayout.setContentsMargins(margins)
        self.flowLayout.setHorizontalSpacing(spacings[0])
        self.flowLayout.setVerticalSpacing(spacings[1])

        if create:
            self._addCardsToLayout()

    def _addCardsToLayout(self):
        for card in self.playlistCards:
            self.flowLayout.addWidget(card)
            QApplication.processEvents()

    def _removeCardsFromLayout(self):
        self.flowLayout.removeAllWidgets()

    def setPlaylistCards(self, playlistCards: List[PlaylistCardBase]):
        self.playlistCards.clear()
        self.playlistCards.extend(playlistCards)
        self.playlists = [i.playlist for i in playlistCards]
        self.playlistCardMap = {i.name: i for i in self.playlistCards}

        self.hideCheckBoxAniGroup.clear()
        for card in self.playlistCards:
            self.hideCheckBoxAniGroup.addAnimation(card.hideCheckBoxAni)
            self._connectCardSignalToSlot(card)

        self._addCardsToLayout()

    def adjustHeight(self):
        h = self.flowLayout.heightForWidth(self.width())
        self.resize(self.width(), h)


class HorizonPlaylistCardView(PlaylistCardViewBase):
    """ Playlist card view with horizontal box layout """

    def __init__(self, library: Library, playlists: List[Playlist], cardType: PlaylistCardType,
                 spacing=20, margins=QMargins(0, 0, 0, 0), create=True, parent=None):
        """
        Parameters
        ----------
        library: Library
            song library

        playlists: List[Playlist]
            playlist list

        cardType: PlaylistCardType
            playlist card type

        spacing: int
            horizontal spacing between playlist cards

        margins: QMargins
            margins of grid layout

        create: bool
            whether to create album card

        parent:
            parent window
        """
        super().__init__(library, playlists, cardType, create, parent)
        self.hBoxLayout = HBoxLayout(self)
        self.hBoxLayout.setSpacing(spacing)
        self.hBoxLayout.setContentsMargins(margins)

        if create:
            self._addCardsToLayout()

    def _addCardsToLayout(self):
        for card in self.playlistCards:
            self.hBoxLayout.addWidget(card)
            QApplication.processEvents()

    def _removeCardsFromLayout(self):
        self.hBoxLayout.removeAllWidget()
