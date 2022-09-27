# coding:utf-8
from typing import List

from common.icon import getIconColor
from common.database.entity import Playlist, SongInfo
from common.library import Library
from common.cover import Cover, CoverType
from common.signal_bus import signalBus
from common.style_sheet import setStyleSheet
from components.buttons.three_state_button import ThreeStatePushButton
from components.dialog_box.message_dialog import MessageDialog
from components.dialog_box.rename_playlist_dialog import RenamePlaylistDialog
from components.selection_mode_interface import (SelectionModeBarType,
                                                 SongSelectionModeInterface)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel

from .playlist_info_bar import PlaylistInfoBar
from .song_list_widget import SongListWidget


class PlaylistInterface(SongSelectionModeInterface):
    """ Playlist interface """

    songCardPlaySig = pyqtSignal(int)             # 在当前播放列表中播放这首歌
    removeSongSig = pyqtSignal(str, list)         # 从播放列表中移除歌曲
    switchToAlbumCardInterfaceSig = pyqtSignal()  # 切换到专辑卡界面

    def __init__(self, library: Library, playlist: Playlist = None, parent=None):
        """
        Parameters
        ----------
        library: Library
            Song library

        playlist: Playlist
            custom playlist

        parent:
            parent window
        """
        self.library = library
        self.__getPlaylistInfo(playlist)
        super().__init__(
            SongListWidget(self.songInfos),
            SelectionModeBarType.PLAYLIST,
            parent
        )

        self.playlistInfoBar = PlaylistInfoBar(self.playlist, self)
        self.noMusicLabel = QLabel(self.tr("No music in playlist?"), self)
        c = getIconColor()
        self.addMusicButton = ThreeStatePushButton(
            {
                "normal": f":/images/playlist_interface/album_{c}_normal.png",
                "hover": f":/images/playlist_interface/album_{c}_hover.png",
                "pressed": f":/images/playlist_interface/album_{c}_pressed.png",
            },
            self.tr(" Add songs from my collection"),
            (29, 29),
            self
        )

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.resize(1230, 900)
        self.vBox.setContentsMargins(0, 430, 0, 0)
        self.noMusicLabel.move(42, 455)
        self.addMusicButton.move(42, 515)
        self.__setQss()
        self.__connectSignalToSlot()

    def updateWindow(self, playlist: Playlist):
        """ update playlist interface """
        if playlist == self.playlist:
            return

        self.verticalScrollBar().setValue(0)
        self.__getPlaylistInfo(playlist)
        self.playlistInfoBar.updateWindow(self.playlist)
        self.songListWidget.updateAllSongCards(self.songInfos)
        self.adjustScrollHeight()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.playlistInfoBar.resize(
            self.width(), self.playlistInfoBar.height())

    def updateSongInfo(self, newSongInfo: SongInfo):
        """ update one song information

        Parameters
        ----------
        newSongInfo: SongInfo
            new song information
        """
        self.songListWidget.updateOneSongCard(newSongInfo)
        if self.songInfos and self.songInfos[0].file == newSongInfo.file:
            coverPath = Cover(
                newSongInfo.singer, newSongInfo.album).path(CoverType.PLAYLIST_BIG)
            if coverPath != self.playlistInfoBar.playlistCoverPath:
                self.playlistInfoBar.updateWindow(self.playlist)

    def updateMultiSongInfos(self, songInfos: List[SongInfo]):
        """ update multi song information """
        for songInfo in songInfos:
            self.updateSongInfo(songInfo)

    def __setQss(self):
        """ set style sheet """
        self.setObjectName("playlistInterface")
        setStyleSheet(self, 'playlist_interface')

    def __getPlaylistInfo(self, playlist: Playlist):
        """ get playlist information """
        self.playlist = playlist if playlist else Playlist()
        self.songInfos = self.playlist.songInfos
        self.playlistName = self.playlist.name

    def _onDelete(self):
        songInfos = []
        for songCard in self.songListWidget.checkedSongCards.copy():
            songCard.setChecked(False)
            songInfos.append(songCard.songInfo)
            self.songListWidget.removeSongCard(songCard.itemIndex)

        self.playlistInfoBar.updateWindow(self.playlist)
        self.adjustScrollHeight()
        self.removeSongSig.emit(self.playlistName, songInfos)
        self.__onSongListWidgetEmptyChanged(
            self.songListWidget.songCardNum == 0)

    def __onScrollBarValueChanged(self, value):
        """ change the height of playlist information bar when scrolling """
        h = 385 - value
        if h > 155:
            self.playlistInfoBar.resize(self.playlistInfoBar.width(), h)

    def __showDeletePlaylistDialog(self):
        """ show delete playlist dialog box """
        name = self.playlistName
        title = self.tr("Are you sure you want to delete this?")
        content = self.tr("If you delete") + f' "{name}" ' + \
            self.tr("it won't be on be this device anymore.")
        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(lambda: signalBus.deletePlaylistSig.emit(name))
        w.exec()

    def __showRenamePlaylistDialog(self, old: str):
        """ show rename playlist dialog box """
        w = RenamePlaylistDialog(self.library, old, self.window())
        w.renamePlaylistSig.connect(self.__renamePlaylist)
        w.exec()

    def __renamePlaylist(self, old: str, new: str):
        """ rename playlist """
        self.playlist.name = new
        self.__getPlaylistInfo(self.playlist)
        self.playlistInfoBar.updateWindow(self.playlist)
        signalBus.renamePlaylistSig.emit(old, new)

    def __onSongListWidgetRemoveSongs(self, songInfo: SongInfo):
        """ song list widget remove songs slot """
        self.playlistInfoBar.updateWindow(self.playlist)
        self.removeSongSig.emit(self.playlistName, [songInfo])
        self.adjustScrollHeight()
        self.__onSongListWidgetEmptyChanged(
            self.songListWidget.songCardNum == 0)

    def __onSongListWidgetEmptyChanged(self, isEmpty):
        """ song list widget empty changed slot """
        self.addMusicButton.setVisible(isEmpty)
        self.noMusicLabel.setVisible(isEmpty)

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.addMusicButton.clicked.connect(self.switchToAlbumCardInterfaceSig)

        # playlist information bar signal
        self.playlistInfoBar.playSig.connect(
            lambda: signalBus.playCheckedSig.emit(self.songInfos))
        self.playlistInfoBar.addToPlayingPlaylistSig.connect(
            lambda: signalBus.addSongsToPlayingPlaylistSig.emit(self.songInfos))
        self.playlistInfoBar.addToNewCustomPlaylistSig.connect(
            lambda: signalBus.addSongsToNewCustomPlaylistSig.emit(self.songInfos))
        self.playlistInfoBar.addToCustomPlaylistSig.connect(
            lambda name: signalBus.addSongsToCustomPlaylistSig.emit(name, self.songInfos))
        self.playlistInfoBar.renameSig.connect(
            lambda: self.__showRenamePlaylistDialog(self.playlist.name))
        self.playlistInfoBar.deleteSig.connect(
            self.__showDeletePlaylistDialog)

        # song list widget signal
        self.songListWidget.playSignal.connect(self.songCardPlaySig)
        self.songListWidget.removeSongSignal.connect(
            self.__onSongListWidgetRemoveSongs)
        self.songListWidget.emptyChangedSig.connect(
            self.__onSongListWidgetEmptyChanged)

        self.verticalScrollBar().valueChanged.connect(self.__onScrollBarValueChanged)
