# coding:utf-8
from typing import List, Tuple

from common.database.entity import Playlist, SongInfo
from common.library import Library
from common.signal_bus import signalBus
from common.style_sheet import setStyleSheet
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from ..album_card import AlbumCardViewBase
from ..dialog_box.message_dialog import MessageDialog
from ..playlist_card import PlaylistCardViewBase
from ..singer_card import SingerCardViewBase
from ..song_list_widget import BasicSongListWidget
from ..widgets.menu import AddToMenu, DownloadMenu
from ..widgets.scroll_area import ScrollArea
from .bar import SelectionModeBarFactory, SelectionModeBarType


class SelectionModeViewBase(QWidget):
    """ Selection mode view base class """

    checkedNumChanged = pyqtSignal(int, bool)

    def setAllChecked(self, isChecked: bool):
        """ set checked state of all widgets """
        raise NotImplementedError

    def uncheckAll(self):
        """ uncheck all widgets """
        raise NotImplementedError


class SelectionModeInterface(ScrollArea):
    """ Selection mode interface """

    def __init__(self, barType: SelectionModeBarType, parent=None):
        """
        Parameters
        ----------
        barType: SelectionModeBarType
            selection mode bar type

        parent:
            parent window
        """
        super().__init__(parent=parent)
        self.view = None
        self.isInSelectionMode = False
        self.scrollWidget = QWidget(self)
        self.vBox = QVBoxLayout(self.scrollWidget)
        self.selectionModeBar = SelectionModeBarFactory.create(barType, self)

        self.setWidget(self.scrollWidget)
        self.scrollWidget.setObjectName("scrollWidget")
        self.selectionModeBar.hide()
        self._setQss()

    def setView(self, view: SelectionModeViewBase):
        """ set the view in selection mode interface """
        if self.view:
            return

        self.view = view
        self.view.setParent(self.scrollWidget)
        self.vBox.addWidget(view)
        self._connectSignalToSlot()

    def resizeEvent(self, e):
        self.selectionModeBar.resize(
            self.width(), self.selectionModeBar.height())
        self.selectionModeBar.move(
            0, self.height()-self.selectionModeBar.height())

    def adjustScrollHeight(self):
        """ adjust the height of scroll widget """
        m = self.vBox.contentsMargins()
        h = self.view.height() + m.top() + m.bottom()
        self.scrollWidget.resize(self.width(), h)

    def _setQss(self):
        """ set style sheet """
        setStyleSheet(self, 'selection_mode_interface')

    def exitSelectionMode(self):
        """ exit selection mode """
        self._onCancel()

    def _getCheckedSongInfos(self) -> List[SongInfo]:
        """ get song information of checked widgets """
        raise NotImplementedError

    def _getCheckedSinger(self) -> str:
        """ get singer name of checked widget """
        raise NotImplementedError

    def _getCheckedAlbum(self) -> Tuple[str, str]:
        """ get album name of checked widget """
        raise NotImplementedError

    def _onCheckedNumChanged(self, n: int, isAllChecked: bool):
        """ checked widget number changed slot """
        if n > 0 and not self.isInSelectionMode:
            self.isInSelectionMode = True
            signalBus.selectionModeStateChanged.emit(True)
        elif n == 0 and self.isInSelectionMode:
            self.isInSelectionMode = False
            signalBus.selectionModeStateChanged.emit(False)
        elif n == 0 and not self.isInSelectionMode:
            return

        self.selectionModeBar.setVisible(self.isInSelectionMode)
        self.selectionModeBar.setPartButtonHidden(n > 1)
        self.selectionModeBar.checkAllButton.setCheckedState(not isAllChecked)
        self.selectionModeBar.move(
            0, self.height()-self.selectionModeBar.height())

    def _onCancel(self):
        """ selection mode bar cancel signal slot """
        self.view.uncheckAll()
        self.selectionModeBar.checkAllButton.setCheckedState(True)

    def _onPlay(self):
        """ selection mode bar play signal slot """
        signalBus.playCheckedSig.emit(self._getCheckedSongInfos())

    def _onNextToPlay(self):
        """ selection mode bar next to play signal slot """
        signalBus.nextToPlaySig.emit(self._getCheckedSongInfos())

    def _onAddTo(self):
        """ selection mode bar add to signal slot """
        menu = AddToMenu(parent=self)

        for act in menu.actions():
            act.triggered.connect(self.exitSelectionMode)

        songInfos = self._getCheckedSongInfos()
        menu.playingAct.triggered.connect(
            lambda: signalBus.addSongsToPlayingPlaylistSig.emit(songInfos))
        menu.addSongsToPlaylistSig.connect(
            lambda name: signalBus.addSongsToCustomPlaylistSig.emit(name, songInfos))
        menu.newPlaylistAct.triggered.connect(
            lambda: signalBus.addSongsToNewCustomPlaylistSig.emit(songInfos))
        menu.exec(menu.getPopupPos(self.selectionModeBar.addToButton))

    def _onDownload(self):
        """ selection mode bar download signal slot """
        menu = DownloadMenu(parent=self)
        songInfos = self._getCheckedSongInfos()
        menu.downloadSig.connect(self.exitSelectionMode)
        menu.downloadSig.connect(
            lambda quality: signalBus.downloadSongsSig.emit(songInfos, quality))
        menu.exec(menu.getPopupPos(self.selectionModeBar.downloadButton))

    def _onSinger(self):
        """ selection mode bar singer signal slot """
        singer = self._getCheckedSinger()
        self.exitSelectionMode()
        signalBus.switchToSingerInterfaceSig.emit(singer)

    def _onAlbum(self):
        """ album signal slot """
        singer, album = self._getCheckedAlbum()
        self.exitSelectionMode()
        signalBus.switchToAlbumInterfaceSig.emit(singer, album)

    def _onProperty(self):
        """ selection mode bar property signal slot """
        raise NotImplementedError

    def _onEditInfo(self):
        """ selection mode bar edit information signal slot """
        raise NotImplementedError

    def _onPinToStart(self):
        """ selection mode bar pin to start signal slot """
        raise NotImplementedError

    def _onRename(self):
        """ selection mode bar rename signal slot """
        raise NotImplementedError

    def _onMoveUp(self):
        """ selection mode bar move up signal slot """
        pass

    def _onMoveDown(self):
        """ selection mode bar move down signal slot """
        pass

    def _onDelete(self):
        """ selection mode bar delete signal slot """
        raise NotImplementedError

    def _onCheckAll(self, isCheck: bool):
        """ selection mode bar check all signal slot"""
        self.view.setAllChecked(isCheck)

    def _connectSignalToSlot(self):
        """ connect signal to slot """
        self.view.checkedNumChanged.connect(self._onCheckedNumChanged)
        self.selectionModeBar.cancelSig.connect(self._onCancel)
        self.selectionModeBar.playSig.connect(self._onPlay)
        self.selectionModeBar.nextToPlaySig.connect(self._onNextToPlay)
        self.selectionModeBar.addToSig.connect(self._onAddTo)
        self.selectionModeBar.singerSig.connect(self._onSinger)
        self.selectionModeBar.albumSig.connect(self._onAlbum)
        self.selectionModeBar.propertySig.connect(self._onProperty)
        self.selectionModeBar.editInfoSig.connect(self._onEditInfo)
        self.selectionModeBar.pinToStartSig.connect(self._onPinToStart)
        self.selectionModeBar.renameSig.connect(self._onRename)
        self.selectionModeBar.moveUpSig.connect(self._onMoveUp)
        self.selectionModeBar.moveDownSig.connect(self._onMoveDown)
        self.selectionModeBar.deleteSig.connect(self._onDelete)
        self.selectionModeBar.downloadSig.connect(self._onDownload)
        self.selectionModeBar.checkAllSig.connect(self._onCheckAll)


class SongSelectionModeInterface(SelectionModeInterface):
    """ Song card selection mode interface """

    def __init__(self, songListWidget: BasicSongListWidget, barType: SelectionModeBarType, parent=None):
        """
        Parameters
        ----------
        songListWidget: BasicSongListWidget
            song list widget

        barType: SelectionModeBarType
            selection mode bar type

        parent:
            parent window
        """
        super().__init__(barType, parent)
        self.songListWidget = songListWidget
        self.songListWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setView(songListWidget)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.adjustScrollHeight()

    def _getCheckedSongInfos(self) -> List[SongInfo]:
        return [i.songInfo for i in self.songListWidget.checkedSongCards]

    def _getCheckedAlbum(self) -> Tuple[str, str]:
        songCard = self.songListWidget.checkedSongCards[0]
        return songCard.singer, songCard.album

    def _getCheckedSinger(self) -> str:
        return self.songListWidget.checkedSongCards[0].singer

    def _onProperty(self):
        songInfo = self._getCheckedSongInfos()[0]
        self.exitSelectionMode()
        self.songListWidget.showSongPropertyDialog(songInfo)

    def _onEditInfo(self):
        songInfo = self._getCheckedSongInfos()[0]
        self.exitSelectionMode()
        self.songListWidget.showSongInfoEditDialog(songInfo)

    def _onDelete(self):
        if len(self.songListWidget.checkedSongCards) > 1:
            title = self.tr("Are you sure you want to delete these?")
            content = self.tr(
                "If you delete these songs, they won't be on be this device anymore.")
        else:
            name = self.songListWidget.checkedSongCards[0].songName
            title = self.tr("Are you sure you want to delete this?")
            content = self.tr("If you delete") + f' "{name}" ' + \
                self.tr("it won't be on be this device anymore.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(self._onDeleteConfirmed)
        w.exec()

    def _onDeleteConfirmed(self):
        """ delete confirmed slot """
        songPaths = [i.songPath for i in self.songListWidget.checkedSongCards]

        for songCard in self.songListWidget.checkedSongCards.copy():
            songCard.setChecked(False)
            self.songListWidget.removeSongCard(songCard.itemIndex)

        signalBus.removeSongSig.emit(songPaths)


class SingerSelectionModeInterface(SelectionModeInterface):
    """ Singer card selection mode interface """

    def __init__(self, library: Library, view: SingerCardViewBase, barType: SelectionModeBarType, parent=None):
        """
        Parameters
        ----------
        library: Library
            song library

        view: SingerCardViewBase
            singer card view

        barType: SelectionModeBarType
            selection mode bar type

        parent:
            parent window
        """
        super().__init__(barType, parent)
        self.library = library
        self.singerCardView = view
        self.vBox.setSizeConstraint(QVBoxLayout.SetFixedSize)
        self.setView(view)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def adjustScrollHeight(self):
        self.scrollWidget.adjustSize()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        m = self.vBox.contentsMargins()
        w = self.width() - m.left() - m.right()
        self.singerCardView.setFixedWidth(w)
        self.singerCardView.adjustHeight()
        self.adjustScrollHeight()

    def _getCheckedSongInfos(self) -> List[SongInfo]:
        singers = [i.singer for i in self.singerCardView.checkedSingerCards]
        songInfos = self.library.songInfoController.getSongInfosBySingers(
            singers)
        return songInfos


class AlbumSelectionModeInterface(SelectionModeInterface):
    """ Album card selection mode interface """

    def __init__(self, library: Library, view: AlbumCardViewBase, barType: SelectionModeBarType, parent=None):
        """
        Parameters
        ----------
        library: Library
            song library

        view: AlbumCardViewBase
            alum card view

        barType: SelectionModeBarType
            selection mode bar type

        parent:
            parent window
        """
        super().__init__(barType, parent)
        self.library = library
        self.albumCardView = view
        self.vBox.setSizeConstraint(QVBoxLayout.SetFixedSize)
        self.setView(view)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def adjustScrollHeight(self):
        self.scrollWidget.adjustSize()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        m = self.vBox.contentsMargins()
        w = self.width() - m.left() - m.right()
        self.albumCardView.setFixedWidth(w)
        self.albumCardView.adjustHeight()
        self.adjustScrollHeight()

    def _getCheckedSongInfos(self) -> List[SongInfo]:
        singers = []
        albums = []
        for albumCard in self.albumCardView.checkedAlbumCards:
            singers.append(albumCard.singer)
            albums.append(albumCard.album)

        songInfos = self.library.songInfoController.getSongInfosBySingerAlbum(
            singers, albums)

        return songInfos

    def _getCheckedAlbum(self) -> Tuple[str, str]:
        card = self.albumCardView.checkedAlbumCards[0]
        return card.singer, card.album

    def _getCheckedSinger(self) -> str:
        return self.albumCardView.checkedAlbumCards[0].singer

    def _onEditInfo(self):
        singer, album = self._getCheckedAlbum()
        self.exitSelectionMode()
        self.albumCardView.showAlbumInfoEditDialog(singer, album)

    def _onDelete(self):
        if len(self.albumCardView.checkedAlbumCards) > 1:
            title = self.tr("Are you sure you want to delete these?")
            content = self.tr(
                "If you delete these albums, they won't be on be this device anymore.")
        else:
            name = self.albumCardView.checkedAlbumCards[0].album
            title = self.tr("Are you sure you want to delete this?")
            content = self.tr("If you delete") + f' "{name}" ' + \
                self.tr("it won't be on be this device anymore.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(self.__onDeleteConfirmed)
        w.exec()

    def __onDeleteConfirmed(self):
        """ delete confirmed slot """
        songInfos = self._getCheckedSongInfos()
        songPaths = [i.file for i in songInfos]
        self.exitSelectionMode()
        signalBus.removeSongSig.emit(songPaths)


class PlaylistSelectionModeInterface(SelectionModeInterface):
    """ Playlist card selection mode interface """

    def __init__(self, library: Library, view: PlaylistCardViewBase, barType: SelectionModeBarType, parent=None):
        """
        Parameters
        ----------
        library: Library
            song library

        view: PlaylistCardViewBase
            playlist card view

        barType: SelectionModeBarType
            selection mode bar type

        parent:
            parent window
        """
        super().__init__(barType, parent)
        self.library = library
        self.playlistCardView = view
        self.playlists = library.playlists
        self.playlistCards = self.playlistCardView.playlistCards
        self.vBox.setSizeConstraint(QVBoxLayout.SetFixedSize)
        self.setView(view)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def adjustScrollHeight(self):
        self.scrollWidget.adjustSize()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        m = self.vBox.contentsMargins()
        w = self.width() - m.left() - m.right()
        self.playlistCardView.setFixedWidth(w)
        self.playlistCardView.adjustHeight()
        self.adjustScrollHeight()

    def _getCheckedSongInfos(self) -> List[SongInfo]:
        names = [i.name for i in self.playlistCardView.checkedPlaylistCards]
        songInfos = []
        for playlist in self.library.playlistController.getPlaylists(names):
            songInfos.extend(playlist.songInfos)

        return songInfos

    def _onRename(self):
        card = self.playlistCardView.checkedPlaylistCards[0]
        self.exitSelectionMode()
        self.playlistCardView.showRenamePlaylistDialog(card.playlist.name)

    def _onDelete(self):
        if len(self.playlistCardView.checkedPlaylistCards) == 1:
            card = self.playlistCardView.checkedPlaylistCards[0]
            self.exitSelectionMode()
            self.playlistCardView.showDeleteCardDialog(card.name)
        else:
            title = self.tr("Are you sure you want to delete these?")
            content = self.tr(
                "If you delete these playlists, they won't be on be this device anymore.")
            names = [i.name for i in self.playlistCardView.checkedPlaylistCards]

            self.exitSelectionMode()

            # show delete playlist card dialog box
            w = MessageDialog(title, content, self.window())
            w.yesSignal.connect(lambda: self.__onDeleteConfirmed(names))
            w.exec()

    def __onDeleteConfirmed(self, names: List[str]):
        """ delete multi playlist cards """
        for name in names:
            signalBus.deletePlaylistSig.emit(name)

    def addPlaylistCard(self, name: str, playlist: Playlist):
        """ add a playlist card """
        self.playlists.append(playlist)
        self.playlistCardView.updateAllCards(self.playlists)

    def renamePlaylist(self, old: str, new: str):
        """ rename playlist card """
        self.playlistCardView.renamePlaylistCard(old, new)

    def deletePlaylistCard(self, name: str):
        """ delete a playlist card """
        self.playlistCardView.deletePlaylistCard(name)

    def addSongsToPlaylist(self, name: str, songInfos: List[SongInfo]) -> Playlist:
        """ add songs to playlist card """
        if not songInfos:
            return

        self.playlistCardView.addSongsToPlaylistCard(name, songInfos)

    def removeSongsFromPlaylist(self, name: str, songInfos: List[SongInfo]):
        """ remove songs from playlist card """
        self.playlistCardView.removeSongsFromPlaylistCard(name, songInfos)
