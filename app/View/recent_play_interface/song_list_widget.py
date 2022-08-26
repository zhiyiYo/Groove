# coding:utf-8
from typing import List

from common.config import config
from common.database.entity import SongInfo
from common.signal_bus import signalBus
from components.dialog_box.message_dialog import MessageDialog
from components.song_list_widget import SongListWidget


class RecentSongListWidget(SongListWidget):
    """ Recent played song list widget """

    def __init__(self, songInfos: List[SongInfo], parent=None):
        super().__init__(songInfos, parent=parent)
        self.sortMode = "Last Played Time"
        self.sortModeMap = {
            "Last Played Time": "LastPlayedTime",
        }
        self.songCardNumChanged.connect(
            lambda i: self.guideLabel.setVisible(i == 0))

    def _showDeleteCardDialog(self):
        index = self.currentRow()
        songInfo = self.songInfos[index]

        title = self.tr("Are you sure you want to delete this?")
        content = self.tr("If you delete") + f' "{songInfo.title}" ' + \
            self.tr("it will no longer in the list, but won't be deleted.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(lambda: self.removeSongCard(index))
        w.yesSignal.connect(
            lambda: self.removeSongSignal.emit(songInfo))
        w.exec_()

    def prependOneSongCard(self, songInfo: SongInfo):
        super().prependOneSongCard(songInfo)
        self.songCardNumChanged.emit(len(self.songCards))

    def setPlayBySongInfo(self, songInfo: SongInfo):
        self.cancelState()

        if songInfo.file.startswith('http'):
            return

        index = self.index(songInfo)
        if index is None:
            self.prependOneSongCard(songInfo)
            # don't move `insert` to the outside of `if`
            self.songInfos.insert(0, songInfo)

            # remove song card at the bottom when number exceeds threshold
            N = config.get(config.recentPlaysNumber)
            if self.songCardNum > N:
                self.removeSongCard(N)

        elif index != 0:
            self.removeSongCard(index, False)
            self.prependOneSongCard(songInfo)
            self.songInfos.insert(0, songInfo)

        self.setPlay(0)
