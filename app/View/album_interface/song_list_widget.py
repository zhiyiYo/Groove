# coding:utf-8
from typing import List

from common.database.entity import SongInfo
from components.dialog_box.message_dialog import MessageDialog
from components.song_list_widget import NoScrollSongListWidget, SongCardType
from components.widgets.menu import AddToMenu, DWMMenu
from PyQt5.QtCore import QFile, QMargins, Qt, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QAction


class SongCardListContextMenu(DWMMenu):
    """ 歌曲卡列表右击菜单 """

    def __init__(self, parent):
        super().__init__("", parent)
        # 创建主菜单动作
        self.playAct = QAction(self.tr("Play"), self)
        self.nextSongAct = QAction(self.tr("Play next"), self)
        self.editInfoAct = QAction(self.tr("Edit info"), self)
        self.showPropertyAct = QAction(self.tr("Properties"), self)
        self.deleteAct = QAction(self.tr("Delete"), self)
        self.selectAct = QAction(self.tr("Select"), self)
        # 创建菜单和子菜单
        self.addToMenu = AddToMenu(self.tr("Add to"), self)
        # 将动作添加到菜单中
        self.addActions([self.playAct, self.nextSongAct])
        # 将子菜单添加到主菜单
        self.addMenu(self.addToMenu)
        # 将其余动作添加到主菜单
        self.addActions(
            [self.editInfoAct, self.showPropertyAct, self.deleteAct])
        self.addSeparator()
        self.addAction(self.selectAct)


class SongListWidget(NoScrollSongListWidget):
    """ 专辑界面歌曲卡列表视图 """

    playSignal = pyqtSignal(int)                    # 播放指定歌曲
    playOneSongSig = pyqtSignal(SongInfo)           # 只播放选中的歌曲
    nextToPlayOneSongSig = pyqtSignal(SongInfo)     # 插入一首歌到播放列表中
    switchToSingerInterfaceSig = pyqtSignal(str)    # 切换到歌手界面

    def __init__(self, songInfos: List[SongInfo], parent=None):
        """
        Parameters
        ----------
        songInfos: List[SongInfo]
            歌曲信息列表

        parent:
            父级窗口
        """
        super().__init__(songInfos, SongCardType.ALBUM_INTERFACE_SONG_CARD, parent)
        self.createSongCards()
        self.__setQss()

    def __showMaskDialog(self):
        index = self.currentRow()
        name = self.songInfos[index]['songName']
        title = self.tr("Are you sure you want to delete this?")
        content = self.tr("If you delete") + f' "{name}" ' + \
            self.tr("it won't be on be this device anymore.")
        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(lambda: self.removeSongCard(index))
        w.exec_()

    def contextMenuEvent(self, e: QContextMenuEvent):
        """ 重写鼠标右击时间的响应函数 """
        hitIndex = self.indexAt(e.pos()).column()
        # 显示右击菜单
        if hitIndex > -1:
            contextMenu = SongCardListContextMenu(self)
            self.__connectMenuSignalToSlot(contextMenu)
            contextMenu.exec(self.cursor().pos())

    def sortSongCardByTrackNum(self):
        """ 以曲序为基准排序歌曲卡 """
        songInfos = self.sortSongInfo("track")
        self.updateAllSongCards(songInfos)

    def __playButtonSlot(self, index):
        """ 歌曲卡播放按钮槽函数 """
        self.playSignal.emit(index)
        self.setCurrentIndex(index)
        self.setPlay(index)

    def __onSongCardDoubleClicked(self, index):
        """ 发送当前播放的歌曲卡变化信号，同时更新样式和歌曲信息卡 """
        if self.isInSelectionMode:
            return
        self.setPlay(index)
        # 发送歌曲信息更新信号
        self.playSignal.emit(index)

    def __setQss(self):
        """ 设置层叠样式 """
        f = QFile(":/qss/album_interface_song_list_widget.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

    def __connectMenuSignalToSlot(self, menu: SongCardListContextMenu):
        """ 右击菜单信号连接到槽 """
        menu.deleteAct.triggered.connect(self.__showMaskDialog)
        menu.editInfoAct.triggered.connect(self.showSongInfoEditDialog)
        menu.showPropertyAct.triggered.connect(self.showSongPropertyDialog)
        menu.playAct.triggered.connect(
            lambda: self.playOneSongSig.emit(self.songCards[self.currentRow()].songInfo))
        menu.nextSongAct.triggered.connect(
            lambda: self.nextToPlayOneSongSig.emit(self.songCards[self.currentRow()].songInfo))
        menu.addToMenu.playingAct.triggered.connect(
            lambda: self.addSongToPlayingSignal.emit(self.songCards[self.currentRow()].songInfo))
        menu.selectAct.triggered.connect(
            lambda: self.songCards[self.currentRow()].setChecked(True))
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(name, self.songInfos))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit([self.songCards[self.currentRow()].songInfo]))

    def _connectSongCardSignalToSlot(self, songCard):
        """ 将歌曲卡信号连接到槽 """
        songCard.doubleClicked.connect(self.__onSongCardDoubleClicked)
        songCard.playButtonClicked.connect(self.__playButtonSlot)
        songCard.clicked.connect(self.setCurrentIndex)
        songCard.checkedStateChanged.connect(
            self.onSongCardCheckedStateChanged)
        songCard.switchToSingerInterfaceSig.connect(
            self.switchToSingerInterfaceSig)
