# coding:utf-8
from typing import List

from common.signal_bus import signalBus
from common.database.entity import SongInfo
from components.selection_mode_interface import (SelectionModeBarType,
                                                 SongSelectionModeInterface)
from components.song_list_widget import SongListWidget
from PyQt5.QtCore import Qt, pyqtSignal


class LocalSongInterface(SongSelectionModeInterface):

    def __init__(self, songInfos: List[SongInfo], parent=None):
        super().__init__(SongListWidget(songInfos), SelectionModeBarType.SONG_TAB, parent)
        self.vBox.setContentsMargins(0, 145, 0, 0)
        self.__connectSignalToSlot()

    def updateWindow(self, songInfos: List[SongInfo]):
        """ 更新窗口 """
        self.songListWidget.updateAllSongCards(songInfos)
        self.adjustScrollHeight()

    def deleteSongs(self, songPaths: List[str]):
        """ 删除歌曲 """
        self.songListWidget.removeSongCards(songPaths)
        self.adjustScrollHeight()

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.songListWidget.removeSongSignal.connect(
            lambda songInfo: signalBus.removeSongSig.emit([songInfo.file]))
