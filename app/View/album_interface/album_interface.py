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
    """ 专辑界面 """

    songCardPlaySig = pyqtSignal(int)                    # 在当前播放列表中播放这首歌

    def __init__(self, library: Library, albumInfo: AlbumInfo = None, parent=None):
        """
        Parameters
        ----------
        library: Library
            歌曲库

        albumInfo: AlbumInfo
            专辑信息

        parent:
            父级窗口
        """
        self.library = library
        self.__getInfo(albumInfo)
        super().__init__(SongListWidget(self.songInfos), SelectionModeBarType.ALBUM, parent)
        self.albumInfoBar = AlbumInfoBar(self.albumInfo, self)
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1230, 900)
        self.vBox.setContentsMargins(0, 430, 0, 0)
        self.__connectSignalToSlot()

    def __getInfo(self, albumInfo: AlbumInfo):
        """ 获取信息 """
        self.albumInfo = albumInfo if albumInfo else AlbumInfo()
        self.songInfos = self.albumInfo.songInfos
        self.album = self.albumInfo.album
        self.singer = self.albumInfo.singer
        self.year = self.albumInfo.year
        self.genre = self.albumInfo.genre

    def updateWindow(self, albumInfo: AlbumInfo):
        """ 更新窗口 """
        if albumInfo == self.albumInfo:
            return

        self.verticalScrollBar().setValue(0)
        self.__getInfo(albumInfo)
        self.albumInfoBar.updateWindow(self.albumInfo)
        self.songListWidget.updateAllSongCards(self.songInfos)
        self.adjustScrollHeight()

    def resizeEvent(self, e):
        """ 改变尺寸时改变小部件大小 """
        super().resizeEvent(e)
        self.albumInfoBar.resize(self.width(), self.albumInfoBar.height())

    def updateSongInfo(self, newSongInfo: SongInfo):
        """ 更新一首歌曲信息

        Parameters
        ----------
        oldSongInfo: SongInfo
            旧的歌曲信息

        newSongInfo: SongInfo
            更新后的歌曲信息
        """
        albumInfo = self.library.albumInfoController.getAlbumInfo(
            self.singer, self.album)
        if not albumInfo:
            return

        self.updateWindow(albumInfo)

    def updateMultiSongInfos(self, songInfos: List[SongInfo]):
        """ 更新多首歌曲信息 """
        self.updateSongInfo(songInfos)

    def __showAlbumInfoEditDialog(self):
        """ 显示专辑信息编辑对话框 """
        # 创建线程和对话框
        thread = SaveAlbumInfoThread(self)
        w = AlbumInfoEditDialog(self.albumInfo, self.window())

        # 信号连接到槽
        w.saveInfoSig.connect(thread.setAlbumInfo)
        w.saveInfoSig.connect(thread.start)
        thread.saveFinishedSignal.connect(w.onSaveComplete)
        thread.saveFinishedSignal.connect(self.__onSaveAlbumInfoFinished)

        # 显示对话框
        w.setStyle(QApplication.style())
        w.exec_()

    def __onSaveAlbumInfoFinished(self, oldAlbumInfo: AlbumInfo, newAlbumInfo: AlbumInfo, coverPath: str):
        """ 保存专辑信息 """
        self.sender().quit()
        self.sender().wait()
        self.sender().deleteLater()
        signalBus.editAlbumInfoSig.emit(oldAlbumInfo, newAlbumInfo, coverPath)

    def __onScrollBarValueChanged(self, value):
        """ 滚动时改变专辑信息栏高度 """
        h = 385 - value
        if h > 155:
            self.albumInfoBar.resize(self.albumInfoBar.width(), h)

    def setCurrentIndex(self, index: int):
        """ 设置当前播放歌曲 """
        self.songListWidget.setPlay(index)

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        # 专辑信息栏信号
        self.albumInfoBar.playAllButton.clicked.connect(
            lambda: signalBus.playAlbumSig.emit(self.singer, self.album))
        self.albumInfoBar.editInfoButton.clicked.connect(
            self.__showAlbumInfoEditDialog)
        self.albumInfoBar.showSingerButton.clicked.connect(
            lambda: signalBus.switchToSingerInterfaceSig.emit(self.singer))
        self.albumInfoBar.addToPlayingPlaylistSig.connect(
            lambda: signalBus.addSongsToPlayingPlaylistSig.emit(self.songInfos))
        self.albumInfoBar.addToNewCustomPlaylistSig.connect(
            lambda: signalBus.addSongsToNewCustomPlaylistSig.emit(self.songInfos))
        self.albumInfoBar.addToCustomPlaylistSig.connect(
            lambda name: signalBus.addSongsToCustomPlaylistSig.emit(name, self.songInfos))
        self.albumInfoBar.action_list[-2].triggered.connect(
            self.__showAlbumInfoEditDialog)

        # 歌曲列表信号
        self.songListWidget.playSignal.connect(self.songCardPlaySig)

        # 将滚动信号连接到槽函数
        self.verticalScrollBar().valueChanged.connect(self.__onScrollBarValueChanged)
