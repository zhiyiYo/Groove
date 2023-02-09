# coding:utf-8
from random import shuffle

from common.database.entity import SongInfo
from common.library import Library
from common.signal_bus import signalBus
from common.style_sheet import setStyleSheet
from components.buttons.three_state_button import RandomPlayAllButton
from components.dialog_box.message_dialog import MessageDialog
from components.selection_mode_interface import (SelectionModeBarType,
                                                 SongSelectionModeInterface)
from PyQt5.QtWidgets import QLabel, QPushButton, QWidget, QApplication

from .song_list_widget import RecentSongListWidget


class RecentPlayInterface(SongSelectionModeInterface):
    """ Recent play interface """

    def __init__(self, library: Library, parent=None):
        super().__init__(
            RecentSongListWidget(library.recentPlaySongInfos),
            SelectionModeBarType.SONG_TAB,
            parent=parent
        )
        self.library = library
        self.vBox.setContentsMargins(0, 180, 0, 0)
        self.whiteMask = QWidget(self)
        self.recentPlayLabel = QLabel(self.tr("Recent Plays"), self)
        self.sortModeLabel = QLabel(self.tr("Sort by:"), self)
        self.sortModeButton = QPushButton(self.tr("Last Played Time"), self)
        self.randomPlayAllButton = RandomPlayAllButton(self)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.resize(1300, 970)
        self.__setQss()

        self.randomPlayAllButton.setNumber(self.songListWidget.songCardNum)

        self.recentPlayLabel.move(30, 54)
        self.randomPlayAllButton.move(30, 131)
        self.sortModeLabel.move(
            self.randomPlayAllButton.geometry().right()+30, 131)
        self.sortModeButton.move(self.sortModeLabel.geometry().right()+7, 128)

        self.__connectSignalToSlot()

    def __setQss(self):
        """ set style sheet """
        self.whiteMask.setObjectName('mask')
        self.recentPlayLabel.setObjectName('recentPlayLabel')
        self.sortModeLabel.setObjectName("sortModeLabel")
        self.sortModeButton.setObjectName("sortModeButton")

        # force style sheets to take effect
        setStyleSheet(self, 'recent_play_interface')
        self.setStyle(QApplication.style())
        QApplication.processEvents()

        self.randomPlayAllButton.adjustSize()
        self.sortModeLabel.adjustSize()
        self.sortModeButton.adjustSize()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.whiteMask.resize(self.width() - 15, 175)

    def onRandomPlayAll(self):
        """ random play recent played songs """
        songInfos = self.songListWidget.songInfos.copy()
        shuffle(songInfos)
        signalBus.playCheckedSig.emit(songInfos)

    def _onDelete(self):
        if len(self.songListWidget.checkedSongCards) > 1:
            title = self.tr("Are you sure you want to delete these?")
            content = self.tr(
                "If you delete these songs, they will no longer in the list, but won't be deleted.")
        else:
            name = self.songListWidget.checkedSongCards[0].songName
            title = self.tr("Are you sure you want to delete this?")
            content = self.tr("If you delete") + f' "{name}" ' + \
                self.tr("it will no longer in the list, but won't be deleted.")

        w = MessageDialog(title, content, self.window())
        if not w.exec():
            return

        files = [i.songPath for i in self.songListWidget.checkedSongCards]

        for songCard in self.songListWidget.checkedSongCards.copy():
            songCard.setChecked(False)
            self.songListWidget.removeSongCard(songCard.itemIndex)

        self.library.recentPlayController.deleteBatch(files)

    def __addRecentPlay(self, songInfo: SongInfo):
        self.adjustScrollHeight()
        self.library.recentPlayController.add(songInfo.file)

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.randomPlayAllButton.clicked.connect(self.onRandomPlayAll)

        self.songListWidget.songCardNumChanged.connect(
            self.randomPlayAllButton.setNumber)
        self.songListWidget.removeSongSignal.connect(
            lambda i: self.library.recentPlayController.delete(i.file))

        signalBus.playBySongInfoSig.connect(self.__addRecentPlay)
