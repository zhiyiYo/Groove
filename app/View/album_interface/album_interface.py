# coding:utf-8
from typing import List

from common.database.entity import AlbumInfo, SongInfo
from common.library import Library
from common.signal_bus import signalBus
from common.thread.save_album_info_thread import SaveAlbumInfoThread
from components.dialog_box.album_info_edit_dialog import AlbumInfoEditDialog
from components.selection_mode_interface import (SelectionModeBarType,
                                                 SongSelectionModeInterface)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication

from .album_info_bar import AlbumInfoBar
from .song_list_widget import SongListWidget


class AlbumInterface(SongSelectionModeInterface):
    """ Album interface """

    songCardPlaySig = pyqtSignal(int)    # 在当前播放列表中播放这首歌

    def __init__(self, library: Library, albumInfo: AlbumInfo = None, parent=None):
        """
        Parameters
        ----------
        library: Library
            song library

        albumInfo: AlbumInfo
            album information

        parent:
            parent window
        """
        self.library = library
        self.__getInfo(albumInfo)
        super().__init__(SongListWidget(self.songInfos), SelectionModeBarType.ALBUM, parent)
        self.albumInfoBar = AlbumInfoBar(self.albumInfo, self)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.resize(1230, 900)
        self.vBox.setContentsMargins(0, 430, 0, 0)
        self.__connectSignalToSlot()

    def __getInfo(self, albumInfo: AlbumInfo):
        """ get album information """
        self.albumInfo = albumInfo if albumInfo else AlbumInfo()
        self.songInfos = self.albumInfo.songInfos
        self.album = self.albumInfo.album
        self.singer = self.albumInfo.singer
        self.year = self.albumInfo.year
        self.genre = self.albumInfo.genre

    def updateWindow(self, albumInfo: AlbumInfo):
        """ update window """
        if albumInfo == self.albumInfo:
            return

        self.verticalScrollBar().setValue(0)
        self.__getInfo(albumInfo)
        self.albumInfoBar.updateWindow(self.albumInfo)
        self.songListWidget.updateAllSongCards(self.songInfos)
        self.adjustScrollHeight()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.albumInfoBar.resize(self.width(), self.albumInfoBar.height())

    def updateSongInfo(self, newSongInfo: SongInfo):
        """ update song information

        Parameters
        ----------
        newSongInfo: SongInfo
            new song information
        """
        albumInfo = self.library.albumInfoController.getAlbumInfo(
            self.singer, self.album)
        if not albumInfo:
            return

        self.updateWindow(albumInfo)

    def updateMultiSongInfos(self, songInfos: List[SongInfo]):
        """ update multi song information """
        self.updateSongInfo(songInfos)

    def __showAlbumInfoEditDialog(self):
        """ show album information dialog """
        thread = SaveAlbumInfoThread(self)
        w = AlbumInfoEditDialog(self.albumInfo, self.window())

        # connect signal to slot
        w.saveInfoSig.connect(thread.setAlbumInfo)
        w.saveInfoSig.connect(thread.start)
        thread.saveFinishedSignal.connect(w.onSaveComplete)
        thread.saveFinishedSignal.connect(self.__onSaveAlbumInfoFinished)

        # show dialog box
        w.setStyle(QApplication.style())
        w.exec_()

    def __onSaveAlbumInfoFinished(self, oldAlbumInfo: AlbumInfo, newAlbumInfo: AlbumInfo, coverPath: str):
        """ save album information finished slot """
        self.sender().quit()
        self.sender().wait()
        self.sender().deleteLater()
        signalBus.editAlbumInfoSig.emit(oldAlbumInfo, newAlbumInfo, coverPath)

    def __onScrollBarValueChanged(self, value):
        """ adjust album information bar height when scrolling """
        h = 385 - value
        if h > 155:
            self.albumInfoBar.resize(self.albumInfoBar.width(), h)

    def setCurrentIndex(self, index: int):
        """ set currently played song """
        self.songListWidget.setPlay(index)

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        # album information bar signal
        self.albumInfoBar.playSig.connect(
            lambda: signalBus.playAlbumSig.emit(self.singer, self.album))
        self.albumInfoBar.editInfoSig.connect(self.__showAlbumInfoEditDialog)
        self.albumInfoBar.singerSig.connect(
            lambda: signalBus.switchToSingerInterfaceSig.emit(self.singer))
        self.albumInfoBar.addToPlayingPlaylistSig.connect(
            lambda: signalBus.addSongsToPlayingPlaylistSig.emit(self.songInfos))
        self.albumInfoBar.addToNewCustomPlaylistSig.connect(
            lambda: signalBus.addSongsToNewCustomPlaylistSig.emit(self.songInfos))
        self.albumInfoBar.addToCustomPlaylistSig.connect(
            lambda name: signalBus.addSongsToCustomPlaylistSig.emit(name, self.songInfos))
        self.albumInfoBar.viewOnlineSig.connect(
            lambda: signalBus.getAlbumDetailsUrlSig.emit(self.albumInfo))

        # song list widget signal
        self.songListWidget.playSignal.connect(self.songCardPlaySig)

        self.verticalScrollBar().valueChanged.connect(self.__onScrollBarValueChanged)
