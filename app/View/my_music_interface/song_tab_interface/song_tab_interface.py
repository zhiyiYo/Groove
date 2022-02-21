# coding:utf-8
from typing import List

from common.database.entity import SongInfo
from common.signal_bus import signalBus
from components.selection_mode_interface import (SelectionModeBarType,
                                                 SongSelectionModeInterface)
from components.song_list_widget import SongListWidget


class SongTabInterface(SongSelectionModeInterface):
    """ Song tab interface """

    def __init__(self, songInfos: List[SongInfo], parent=None):
        super().__init__(SongListWidget(songInfos), SelectionModeBarType.SONG_TAB, parent)
        self.resize(1300, 970)
        self.vBox.setContentsMargins(0, 245, 0, 0)
        self.__connectSignalToSlot()

    def updateWindow(self, songInfos: List[SongInfo]):
        """ update window """
        self.songListWidget.updateAllSongCards(songInfos)
        self.adjustScrollHeight()

    def deleteSongs(self, songPaths: List[str]):
        """ delete songs """
        self.songListWidget.removeSongCards(songPaths)
        self.adjustScrollHeight()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.songListWidget.removeSongSignal.connect(
            lambda songInfo: signalBus.removeSongSig.emit([songInfo.file]))