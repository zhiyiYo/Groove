# coding:utf-8
from typing import Dict, List

from common.database.entity import Playlist, SongInfo
from common.library import Library
from components.buttons.three_state_button import ThreeStatePushButton
from components.dialog_box.message_dialog import MessageDialog
from components.playlist_card import (GridPlaylistCardView, PlaylistCard,
                                      PlaylistCardType)
from components.widgets.menu import AddToMenu, AeroMenu
from components.widgets.scroll_area import ScrollArea
from PyQt5.QtCore import QDateTime, QFile, QMargins, QPoint, Qt, pyqtSignal
from PyQt5.QtWidgets import QAction, QLabel, QPushButton, QWidget

from .selection_mode_bar import SelectionModeBar


class PlaylistCardInterface(ScrollArea):
    """ 播放列表卡界面 """

    playSig = pyqtSignal(list)
    createPlaylistSig = pyqtSignal()
    nextToPlaySig = pyqtSignal(list)
    deletePlaylistSig = pyqtSignal(str)
    renamePlaylistSig = pyqtSignal(str, str)
    selectionModeStateChanged = pyqtSignal(bool)
    switchToPlaylistInterfaceSig = pyqtSignal(str)
    addSongsToPlayingPlaylistSig = pyqtSignal(list)      # 添加歌曲到正在播放
    addSongsToNewCustomPlaylistSig = pyqtSignal(list)    # 添加歌曲到新的自定义的播放列表中
    addSongsToCustomPlaylistSig = pyqtSignal(str, list)  # 添加歌曲到自定义的播放列表中

    def __init__(self, library: Library, parent=None):
        super().__init__(parent)
        self.sortMode = "modifiedTime"
        self.library = library
        self.playlists = library.playlists
        self.checkedPlaylistCards = []    # type:List[PlaylistCard]
        self.isInSelectionMode = False
        self.isAllPlaylistCardChecked = False

        self.playlistCardView = GridPlaylistCardView(
            library,
            self.playlists,
            PlaylistCardType.PLAYLIST_CARD,
            margins=QMargins(15, 175, 15, 120),
            parent=self
        )
        self.playlistCards = self.playlistCardView.playlistCards

        self.__createWidgets()
        self.__initWidget()

    def __createWidgets(self):
        """ 创建小部件 """
        # 创建白色遮罩
        self.whiteMask = QWidget(self)
        self.playlistLabel = QLabel(self.tr("Playlist"), self)
        self.sortModeLabel = QLabel(self.tr("Sort by:"), self)
        self.sortModeButton = QPushButton(self.tr("Date modified"), self)
        self.createPlaylistButton = ThreeStatePushButton(
            {
                "normal": ":/images/playlist_card_interface/Add_normal.png",
                "hover": ":/images/playlist_card_interface/Add_hover.png",
                "pressed": ":/images/playlist_card_interface/Add_pressed.png",
            },
            self.tr(" New playlist"),
            (19, 19),
            self,
        )

        # 创建导航标签
        self.guideLabel = QLabel(
            self.tr('There is nothing to display here. Try a different filter.'), self)

        # 创建排序菜单
        self.sortModeMenu = AeroMenu(parent=self)
        self.sortByModifiedTimeAct = QAction(
            self.tr("Date modified"), self, triggered=lambda: self.__sortPlaylist("modifiedTime"))
        self.sortByAToZAct = QAction(
            self.tr("A to Z"), self, triggered=lambda: self.__sortPlaylist("AToZ"))
        self.sortActs = [self.sortByModifiedTimeAct, self.sortByAToZAct]

        # 创建选择状态栏
        self.selectionModeBar = SelectionModeBar(self)

        # 记录当前的排序方式
        self.currentSortAct = self.sortByModifiedTimeAct

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1270, 760)
        self.setWidget(self.playlistCardView)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.selectionModeBar.hide()
        self.guideLabel.setHidden(bool(self.playlistCards))
        self.sortModeMenu.addActions(self.sortActs)
        self.guideLabel.raise_()

        self.__setQss()
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        """ 初始化布局 """
        self.guideLabel.move(44, 196)
        self.playlistLabel.move(30, 54)
        self.createPlaylistButton.move(30, 130)
        self.sortModeLabel.move(
            self.createPlaylistButton.geometry().right()+30, 131)
        self.sortModeButton.move(self.sortModeLabel.geometry().right()+7, 127)

    def __setQss(self):
        """ 设置层叠样式 """
        self.playlistLabel.setObjectName("playlistLabel")
        self.sortModeLabel.setObjectName("sortModeLabel")
        self.sortModeButton.setObjectName("sortModeButton")
        self.createPlaylistButton.setObjectName("createPlaylistButton")
        self.sortModeMenu.setObjectName("sortModeMenu")
        self.sortModeMenu.setProperty("modeNumber", "2")
        self.guideLabel.setObjectName('guideLabel')

        f = QFile(":/qss/playlist_card_interface.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

        self.createPlaylistButton.adjustSize()
        self.sortModeLabel.adjustSize()
        self.guideLabel.adjustSize()

    def resizeEvent(self, e):
        """ 调整小部件尺寸和位置 """
        super().resizeEvent(e)
        self.whiteMask.resize(self.width() - 15, 175)
        self.playlistCardView.setFixedWidth(self.width())
        self.selectionModeBar.resize(
            self.width(), self.selectionModeBar.height())
        self.playlistCardView.adjustSize()

    def __sortPlaylist(self, key):
        """ 排序播放列表 """
        self.sortMode = key
        if key == "modifiedTime":
            self.sortModeButton.setText(self.tr("Date modified"))
            self.currentSortAct = self.sortByModifiedTimeAct
            self.playlistCardView.setSortMode('modifiedTime')
        else:
            self.sortModeButton.setText(self.tr("A to Z"))
            self.currentSortAct = self.sortByAToZAct
            self.playlistCardView.setSortMode('A To Z')

    def __showSortModeMenu(self):
        """ 显示排序方式菜单 """
        self.sortModeMenu.setDefaultAction(self.currentSortAct)
        index = self.sortActs.index(self.currentSortAct)
        pos = self.sender().pos()-QPoint(0, 37*index+1)
        self.sortModeMenu.exec(self.mapToGlobal(pos))

    def __onPlaylistCardCheckedStateChanged(self, playlistCard: PlaylistCard, isChecked: bool):
        """ 播放列表卡选中状态改变槽函数 """
        if playlistCard not in self.checkedPlaylistCards and isChecked:
            self.checkedPlaylistCards.append(playlistCard)
            self.__onCheckPlaylistCardNumChanged(
                len(self.checkedPlaylistCards))

        # 如果专辑信息已经在列表中且该专辑卡变为非选中状态就弹出该专辑信息
        elif playlistCard in self.checkedPlaylistCards and not isChecked:
            self.checkedPlaylistCards.pop(
                self.checkedPlaylistCards.index(playlistCard))
            self.__onCheckPlaylistCardNumChanged(
                len(self.checkedPlaylistCards))

        isAllChecked = (len(self.checkedPlaylistCards)
                        == len(self.playlistCards))
        if isAllChecked != self.isAllPlaylistCardChecked:
            self.isAllPlaylistCardChecked = isAllChecked
            self.selectionModeBar.checkAllButton.setCheckedState(
                not isAllChecked)

        # 如果先前不处于选择模式那么这次发生选中状态改变就进入选择模式
        if not self.isInSelectionMode:
            self.__setAllPlaylistCardSelectionModeOpen(True)
            self.isInSelectionMode = True
            self.selectionModeStateChanged.emit(True)
            self.selectionModeBar.show()
        elif not self.checkedPlaylistCards:
            self.__setAllPlaylistCardSelectionModeOpen(False)
            self.selectionModeBar.hide()
            self.selectionModeStateChanged.emit(False)
            self.isInSelectionMode = False

    def __setAllPlaylistCardSelectionModeOpen(self, isOpen: bool):
        """ 设置所有播放列表卡是否进入选择模式 """
        for card in self.playlistCards:
            card.setSelectionModeOpen(isOpen)

        if not isOpen:
            self.playlistCardView.hideCheckBoxAniGroup.start()

    def __unCheckPlaylistCards(self):
        """ 取消所有已处于选中状态的播放列表卡的选中状态 """
        for playlistCard in self.checkedPlaylistCards.copy():
            playlistCard.setChecked(False)

        self.selectionModeBar.checkAllButton.setCheckedState(True)

    def setAllPlaylistCardCheckedState(self, isAllChecked: bool):
        """ 设置所有的专辑卡checked状态 """
        if self.isAllPlaylistCardChecked == isAllChecked:
            return

        self.isAllPlaylistCardChecked = isAllChecked
        for playlistCard in self.playlistCards:
            playlistCard.setChecked(isAllChecked)

    def __onCheckPlaylistCardNumChanged(self, num: int):
        """ 选中的歌曲卡数量改变对应的槽函数 """
        self.selectionModeBar.setPartButtonHidden(num > 1)
        self.selectionModeBar.move(
            0, self.height() - self.selectionModeBar.height())

    def __onSelectionModeBarCheckAllButtonClicked(self):
        """ 全选/取消全选按钮槽函数 """
        self.setAllPlaylistCardCheckedState(not self.isAllPlaylistCardChecked)

    def addPlaylistCard(self, name: str, playlist: Playlist):
        """ 添加一个播放列表卡 """
        self.playlists.append(playlist)
        self.playlistCardView.updateAllCards(self.playlists)
        self.guideLabel.hide()

    def addSongsToPlaylist(self, name: str, songInfos: List[SongInfo]) -> Playlist:
        """ 将歌曲添加到播放列表 """
        if not songInfos:
            return

        self.playlistCardView.addSongsToPlaylistCard(name, songInfos)

    def renamePlaylist(self, old: str, new: str):
        """ 重命名播放列表 """
        self.playlistCardView.renamePlaylistCard(old, new)

    def deletePlaylistCard(self, name: str):
        """ 删除一个播放列表卡 """
        self.playlistCardView.deletePlaylistCard(name)
        self.guideLabel.setHidden(bool(self.playlistCards))

    def __deleteMultiPlaylistCards(self, playlistNames: list):
        """ 删除多个播放列表卡 """
        for name in playlistNames:
            self.deletePlaylistCard(name)
            self.deletePlaylistSig.emit(name)

    def removeSongsFromPlaylist(self, name: str, songInfos: List[SongInfo]):
        """ 移除一个播放列表中的歌曲 """
        self.playlistCardView.removeSongsFromPlaylistCard(name, songInfos)

    def __emitCheckedPlaylists(self):
        """ 发送选中的播放列表中的歌曲 """
        playlist = self.getCheckedPlaylistsSongInfos()
        self.__unCheckPlaylistCards()

        if self.sender() is self.selectionModeBar.playButton:
            self.playSig.emit(playlist)
        elif self.sender() is self.selectionModeBar.nextToPlayButton:
            self.nextToPlaySig.emit(playlist)

    def __onSelectionModeBarRenameButtonClicked(self):
        """ 选择栏重命名按钮的槽函数 """
        card = self.checkedPlaylistCards[0]
        self.__unCheckPlaylistCards()
        self.playlistCardView.showRenamePlaylistDialog(card.playlist)

    def __onSelectionModeBarDeleteButtonClicked(self):
        """ 选择栏删除按钮槽函数 """
        if len(self.checkedPlaylistCards) == 1:
            playlistCard = self.checkedPlaylistCards[0]
            self.__unCheckPlaylistCards()
            self.playlistCardView.showDeleteCardDialog(playlistCard.name)
        else:
            title = self.tr("Are you sure you want to delete these?")
            content = self.tr(
                "If you delete these playlists, they won't be on be this device anymore.")
            names = [i.name for i in self.checkedPlaylistCards]

            # 取消所有歌曲卡的选中
            self.__unCheckPlaylistCards()

            # 显示删除对话框
            w = MessageDialog(title, content, self.window())
            w.yesSignal.connect(lambda: self.__deleteMultiPlaylistCards(names))
            w.exec()

    def exitSelectionMode(self):
        """ 退出选择模式 """
        self.__unCheckPlaylistCards()

    def __showAddToMenu(self):
        """ 显示添加到菜单 """
        # 初始化菜单动作触发标志
        menu = AddToMenu(parent=self)

        # 计算菜单弹出位置
        pos = self.selectionModeBar.mapToGlobal(
            QPoint(self.selectionModeBar.addToButton.x(), 0))
        x = pos.x() + self.selectionModeBar.addToButton.width() + 5
        y = pos.y() + self.selectionModeBar.addToButton.height() // 2 - \
            (13 + 38 * menu.actionCount()) // 2

        # 获取选中的歌曲信息列表
        for act in menu.action_list:
            act.triggered.connect(self.exitSelectionMode)

        songInfos = self.getCheckedPlaylistsSongInfos()

        menu.playingAct.triggered.connect(
            lambda: self.addSongsToPlayingPlaylistSig.emit(songInfos))
        menu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(name, songInfos))
        menu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(songInfos))
        menu.exec(QPoint(x, y))

    def getCheckedPlaylistsSongInfos(self):
        """ 获取所有选中的播放列表的歌曲信息 """
        names = [i.name for i in self.checkedPlaylistCards]
        songInfos = []
        for playlist in self.library.playlistController.getPlaylists(names):
            songInfos.extend(playlist.songInfos)

        return songInfos

    def __connectSignalToSlot(self):
        """ 将信号连接到槽 """
        self.selectionModeBar.cancelButton.clicked.connect(
            self.__unCheckPlaylistCards)
        self.selectionModeBar.checkAllButton.clicked.connect(
            self.__onSelectionModeBarCheckAllButtonClicked)
        self.selectionModeBar.playButton.clicked.connect(
            self.__emitCheckedPlaylists)
        self.selectionModeBar.nextToPlayButton.clicked.connect(
            self.__emitCheckedPlaylists)
        self.selectionModeBar.renameButton.clicked.connect(
            self.__onSelectionModeBarRenameButtonClicked)
        self.selectionModeBar.deleteButton.clicked.connect(
            self.__onSelectionModeBarDeleteButtonClicked)
        self.selectionModeBar.addToButton.clicked.connect(self.__showAddToMenu)

        self.sortModeButton.clicked.connect(self.__showSortModeMenu)
        self.createPlaylistButton.clicked.connect(self.createPlaylistSig)

        self.playlistCardView.playSig.connect(self.playSig)
        self.playlistCardView.nextToPlaySig.connect(self.nextToPlaySig)
        self.playlistCardView.renamePlaylistSig.connect(self.renamePlaylistSig)
        self.playlistCardView.deletePlaylistSig.connect(self.deletePlaylistSig)
        self.playlistCardView.deletePlaylistSig.connect(
            lambda: self.guideLabel.setHidden(bool(self.playlistCards)))
        self.playlistCardView.checkedStateChanged.connect(
            self.__onPlaylistCardCheckedStateChanged)
        self.playlistCardView.switchToPlaylistInterfaceSig.connect(
            self.switchToPlaylistInterfaceSig)
        self.playlistCardView.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig)
        self.playlistCardView.addSongsToNewCustomPlaylistSig.connect(
            self.addSongsToNewCustomPlaylistSig)
        self.playlistCardView.addSongsToPlayingPlaylistSig.connect(
            self.addSongsToPlayingPlaylistSig)
