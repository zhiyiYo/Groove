# coding:utf-8
from copy import deepcopy
from json import dump
from typing import Dict, List

import pinyin
from app.common.os_utils import moveToTrash
from app.components.buttons.three_state_button import ThreeStatePushButton
from app.components.dialog_box.message_dialog import MessageDialog
from app.components.dialog_box.rename_playlist_dialog import \
    RenamePlaylistDialog
from app.components.layout.grid_layout import GridLayout
from app.components.menu import AddToMenu, AeroMenu
from app.components.playlist_card import BlurBackground, PlaylistCard
from app.components.scroll_area import ScrollArea
from PyQt5.QtCore import (QDateTime, QParallelAnimationGroup, QPoint,
                          QPropertyAnimation, Qt, pyqtSignal)
from PyQt5.QtWidgets import QAction, QLabel, QPushButton, QWidget

from .selection_mode_bar import SelectionModeBar


class PlaylistCardInterface(ScrollArea):
    """ 播放列表卡界面 """

    playSig = pyqtSignal(list)
    createPlaylistSig = pyqtSignal()
    nextToPlaySig = pyqtSignal(list)
    deletePlaylistSig = pyqtSignal(str)
    renamePlaylistSig = pyqtSignal(dict, dict)
    selectionModeStateChanged = pyqtSignal(bool)
    switchToPlaylistInterfaceSig = pyqtSignal(str)
    addSongsToPlayingPlaylistSig = pyqtSignal(list)      # 添加歌曲到正在播放
    addSongsToNewCustomPlaylistSig = pyqtSignal(list)    # 添加歌曲到新的自定义的播放列表中
    addSongsToCustomPlaylistSig = pyqtSignal(str, list)  # 添加歌曲到自定义的播放列表中

    def __init__(self, playlists: dict, parent=None):
        """
        Parameters
        ----------
        playlists: dict
            播放列表字典
        """
        super().__init__(parent)
        self.columnNum = 1
        self.sortMode = "modifiedTime"
        self.playlists = playlists
        self.playlistCard_list = []      # type:List[PlaylistCard]
        self.playlistCardInfo_list = []  # type:List[dict]
        self.playlistName2Card_dict = {}   # type:Dict[str, PlaylistCard]
        self.checkedPlaylistCard_list = []    # type:List[PlaylistCard]
        self.isInSelectionMode = False
        self.isAllPlaylistCardChecked = False
        # 创建小部件
        self.__createWidgets()
        # 初始化
        self.__initWidget()

    def __createWidgets(self):
        """ 创建小部件 """
        # 创建磨砂背景
        self.scrollWidget = QWidget(self)
        self.gridLayout = GridLayout()
        self.blurBackground = BlurBackground(self.scrollWidget)
        # 创建播放列表卡
        self.__createPlaylistCards()
        # 创建白色遮罩
        self.whiteMask = QWidget(self)
        self.sortModeLabel = QLabel("排序依据:", self)
        self.playlistLabel = QLabel("播放列表", self)
        self.sortModeButton = QPushButton("修改日期", self)
        self.createPlaylistButton = ThreeStatePushButton(
            {
                "normal": r"app\resource\images\playlist_card_interface\newPlaylist_normal.png",
                "hover": r"app\resource\images\playlist_card_interface\newPlaylist_hover.png",
                "pressed": r"app\resource\images\playlist_card_interface\newPlaylist_pressed.png",
            },
            " 新的播放列表",
            (19, 19),
            self,
        )
        # 创建导航标签
        self.guideLabel = QLabel("这里没有可显示的内容。请尝试其他筛选器。", self)
        self.guideLabel.setStyleSheet(
            "color: black; font: 25px 'Microsoft YaHei'")
        self.guideLabel.resize(500, 26)
        self.guideLabel.move(44, 196)
        # 创建排序菜单
        self.sortModeMenu = AeroMenu(parent=self)
        self.sortByModifiedTimeAct = QAction(
            "修改时间", self, triggered=lambda: self.__sortPlaylist("modifiedTime"))
        self.sortByAToZAct = QAction(
            "A到Z", self, triggered=lambda: self.__sortPlaylist("AToZ"))
        self.sortAct_list = [self.sortByModifiedTimeAct, self.sortByAToZAct]
        # 创建选择状态栏
        self.selectionModeBar = SelectionModeBar(self)
        # 记录当前的排序方式
        self.currentSortAct = self.sortByModifiedTimeAct

    def __createPlaylistCards(self):
        """ 创建播放列表卡 """
        # 创建并行动画组
        self.hideCheckBoxAniGroup = QParallelAnimationGroup(self)
        self.hideCheckBoxAni_list = []
        for name, playlist in self.playlists.items():
            self.__createOnePlaylistCard(name, playlist)

    def __createOnePlaylistCard(self, playlistName: str, playlist: dict):
        """ 创建一个播放列表卡 """
        playlistCard = PlaylistCard(playlist, self)
        self.playlistCard_list.append(playlistCard)
        self.playlistName2Card_dict[playlistName] = playlistCard

        self.playlistCardInfo_list.append(
            {"playlistCard": playlistCard, "playlist": playlist})

        # 创建动画
        hideCheckBoxAni = QPropertyAnimation(
            playlistCard.checkBoxOpacityEffect, b"opacity")
        self.hideCheckBoxAniGroup.addAnimation(hideCheckBoxAni)
        self.hideCheckBoxAni_list.append(hideCheckBoxAni)

        # 信号连接到槽
        playlistCard.playSig.connect(self.playSig)
        playlistCard.nextToPlaySig.connect(self.nextToPlaySig)
        playlistCard.showBlurBackgroundSig.connect(self.__showBlurBackground)
        playlistCard.hideBlurBackgroundSig.connect(self.blurBackground.hide)
        playlistCard.renamePlaylistSig.connect(self.__showRenamePlaylistDialog)
        playlistCard.deleteCardSig.connect(self.__showDeleteCardDialog)
        playlistCard.checkedStateChanged.connect(
            self.__onPlaylistCardCheckedStateChanged)
        playlistCard.switchToPlaylistInterfaceSig.connect(
            self.switchToPlaylistInterfaceSig)
        playlistCard.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig)
        playlistCard.addSongsToNewCustomPlaylistSig.connect(
            self.addSongsToNewCustomPlaylistSig)
        playlistCard.addSongsToPlayingPlaylistSig.connect(
            self.addSongsToPlayingPlaylistSig)

    def __initWidget(self):
        """ 初始化小部件 """
        # 隐藏小部件
        self.blurBackground.hide()
        self.selectionModeBar.hide()
        self.guideLabel.setHidden(bool(self.playlistCard_list))
        # 初始化滚动条
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 将动作添加到菜单中
        self.sortModeMenu.addActions(self.sortAct_list)
        # 分配ID和属性
        self.scrollWidget.setObjectName("scrollWidget")
        self.playlistLabel.setObjectName("playlistLabel")
        self.sortModeLabel.setObjectName("sortModeLabel")
        self.sortModeButton.setObjectName("sortModeButton")
        self.createPlaylistButton.setObjectName("createPlaylistButton")
        self.sortModeMenu.setObjectName("sortModeMenu")
        self.sortModeMenu.setProperty("modeNumber", "2")
        self.__setQss()
        self.__initLayout()
        self.resize(1270, 760)
        self.__connectSignalToSlot()

    def __initLayout(self):
        """ 初始化布局 """
        self.playlistLabel.move(30, 54)
        self.sortModeLabel.move(190, 131)
        self.sortModeButton.move(264, 127)
        self.createPlaylistButton.move(30, 130)
        self.selectionModeBar.move(
            0, self.height() - self.selectionModeBar.height())
        # 设置布局的间距和外边距
        self.gridLayout.setVerticalSpacing(20)
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setContentsMargins(15, 175, 15, 120)
        self.setWidget(self.scrollWidget)
        self.scrollWidget.setLayout(self.gridLayout)
        # 如果没有播放列表就直接返回
        if not self.playlistCard_list:
            return
        # 按照修改日期排序播放列表
        self.__sortPlaylist("modifiedTime")

    def __setQss(self):
        """ 设置层叠样式 """
        with open(r"app\resource\css\playlist_card_interface.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def resizeEvent(self, e):
        """ 调整小部件尺寸和位置 """
        super().resizeEvent(e)
        self.whiteMask.resize(self.width() - 15, 175)
        self.selectionModeBar.resize(
            self.width(), self.selectionModeBar.height())
        if self.width() < 641 and self.columnNum != 1:
            self.__setColumnNum(1)
        elif 641 <= self.width() < 954 and self.columnNum != 2:
            self.__setColumnNum(2)
        elif 954 <= self.width() < 1267 and self.columnNum != 3:
            self.__setColumnNum(3)
        elif 1267 <= self.width() < 1580 and self.columnNum != 4:
            self.__setColumnNum(4)
        elif 1580 <= self.width() < 1893 and self.columnNum != 5:
            self.__setColumnNum(5)
        elif self.width() >= 1893 and self.columnNum != 6:
            self.__setColumnNum(6)

    def __setColumnNum(self, columnNum: int):
        """ 设置网格列数 """
        self.columnNum = columnNum
        self.gridLayout.updateColumnNum(columnNum, 298, 288)
        self.scrollWidget.resize(
            self.width(), 175 + self.gridLayout.rowCount() * 298 + 120)

    def __sortPlaylist(self, key):
        """ 排序播放列表 """
        self.sortMode = key
        if key == "modifiedTime":
            self.sortModeButton.setText("修改时间")
            self.currentSortAct = self.sortByModifiedTimeAct
            self.playlistCardInfo_list.sort(
                key=self.__sortPlaylistByModifiedTime, reverse=True)
        else:
            self.sortModeButton.setText("A到Z")
            self.currentSortAct = self.sortByAToZAct
            self.playlistCardInfo_list.sort(
                key=self.__sortPlaylistByAToZ, reverse=False)
        # 先将小部件布局中移除
        self.gridLayout.removeAllWidgets()
        # 将小部件添加到布局中
        for index, playlistCard_dict in enumerate(self.playlistCardInfo_list):
            row = index // self.columnNum
            column = index - self.columnNum * row
            playlistCard = playlistCard_dict["playlistCard"]
            self.gridLayout.addWidget(playlistCard, row, column, Qt.AlignLeft)

    def __showBlurBackground(self, pos: QPoint, playlistCoverPath: str):
        """ 显示磨砂背景 """
        # 将全局坐标转换为窗口坐标
        pos = self.scrollWidget.mapFromGlobal(pos)
        self.blurBackground.setBlurPic(playlistCoverPath, 40)
        self.blurBackground.move(pos.x() - 30, pos.y() - 20)
        self.blurBackground.show()

    def __showSortModeMenu(self):
        """ 显示排序方式菜单 """
        # 设置默认选中动作
        self.sortModeMenu.setDefaultAction(self.currentSortAct)
        actIndex = self.sortAct_list.index(self.currentSortAct)
        self.sortModeMenu.exec(
            self.mapToGlobal(
                QPoint(self.sender().x(), self.sender().y() - 37 * actIndex - 1)))

    def __onPlaylistCardCheckedStateChanged(self, playlistCard: PlaylistCard, isChecked: bool):
        """ 播放列表卡选中状态改变槽函数 """
        if playlistCard not in self.checkedPlaylistCard_list and isChecked:
            self.checkedPlaylistCard_list.append(playlistCard)
            self.__onCheckPlaylistCardNumChanged(
                len(self.checkedPlaylistCard_list))

        # 如果专辑信息已经在列表中且该专辑卡变为非选中状态就弹出该专辑信息
        elif playlistCard in self.checkedPlaylistCard_list and not isChecked:
            self.checkedPlaylistCard_list.pop(
                self.checkedPlaylistCard_list.index(playlistCard))
            self.__onCheckPlaylistCardNumChanged(
                len(self.checkedPlaylistCard_list))

        isAllChecked = (len(self.checkedPlaylistCard_list)
                        == len(self.playlistCard_list))
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
        elif not self.checkedPlaylistCard_list:
            self.__setAllPlaylistCardSelectionModeOpen(False)
            self.selectionModeBar.hide()
            self.selectionModeStateChanged.emit(False)
            self.isInSelectionMode = False

    def __setAllPlaylistCardSelectionModeOpen(self, isOpenSelectionMode: bool):
        """ 设置所有播放列表卡是否进入选择模式 """
        for playlistCard in self.playlistCard_list:
            playlistCard.setSelectionModeOpen(isOpenSelectionMode)
        if not isOpenSelectionMode:
            self.__startHideCheckBoxAni()

    def __startHideCheckBoxAni(self):
        """ 开始隐藏复选框动画 """
        for ani in self.hideCheckBoxAni_list:
            ani.setStartValue(1)
            ani.setEndValue(0)
            ani.setDuration(140)
        self.hideCheckBoxAniGroup.start()

    def __hideAllCheckBox(self):
        """ 隐藏所有复选框 """
        for playlistCard in self.playlistCard_list:
            playlistCard.checkBox.hide()

    def __unCheckPlaylistCards(self):
        """ 取消所有已处于选中状态的播放列表卡的选中状态 """
        checkedPlaylistCard_list_copy = self.checkedPlaylistCard_list.copy()
        for playlistCard in checkedPlaylistCard_list_copy:
            playlistCard.setChecked(False)
        # 更新按钮的图标为全选
        self.selectionModeBar.checkAllButton.setCheckedState(True)

    def setAllPlaylistCardCheckedState(self, isAllChecked: bool):
        """ 设置所有的专辑卡checked状态 """
        if self.isAllPlaylistCardChecked == isAllChecked:
            return
        self.isAllPlaylistCardChecked = isAllChecked
        for playlistCard in self.playlistCard_list:
            playlistCard.setChecked(isAllChecked)

    def __onCheckPlaylistCardNumChanged(self, num: int):
        """ 选中的歌曲卡数量改变对应的槽函数 """
        self.selectionModeBar.setPartButtonHidden(num > 1)
        self.selectionModeBar.move(
            0, self.height() - self.selectionModeBar.height())

    def __onSelectionModeBarCheckAllButtonClicked(self):
        """ 全选/取消全选按钮槽函数 """
        self.setAllPlaylistCardCheckedState(not self.isAllPlaylistCardChecked)

    def __sortPlaylistByModifiedTime(self, playlistCard_dict: dict) -> str:
        return playlistCard_dict["playlist"]["modifiedTime"]

    def __sortPlaylistByAToZ(self, playlistCard_dict: dict) -> str:
        return pinyin.get_initial(playlistCard_dict["playlist"]["playlistName"])[
            0
        ].lower()

    def addOnePlaylistCard(self, playlistName: str, playlist: dict):
        """ 添加一个播放列表卡 """
        self.playlists[playlistName] = playlist
        self.__createOnePlaylistCard(playlistName, playlist)
        self.guideLabel.hide()
        # 向布局添加小部件
        self.gridLayout.appendWidget(self.playlistCard_list[-1])
        self.scrollWidget.resize(
            self.width(), 175 + self.gridLayout.rowCount() * 298 + 120)
        # 按照当前排序方式重新排序播放列表卡
        self.__sortPlaylist(self.sortMode)

    def __showRenamePlaylistDialog(self, oldPlaylist: dict):
        """ 显示重命名播放列表面板 """
        w = RenamePlaylistDialog(oldPlaylist, self.window())
        w.renamePlaylistSig.connect(self.renamePlaylistSig)
        w.exec()

    def renamePlaylist(self, oldPlaylist: dict, newPlaylist: dict):
        """ 重命名播放列表 """
        oldName = oldPlaylist["playlistName"]
        newName = newPlaylist["playlistName"]

        # 更新播放列表卡
        playlistCard = self.playlistName2Card_dict.pop(oldName)
        playlistCard.updateWindow(newPlaylist)

        # 更新字典和列表
        self.playlistName2Card_dict[newName] = playlistCard
        self.playlists[newName] = newPlaylist
        self.playlists.pop(oldName)

        # 重新排序播放列表卡
        index = self.__getCardInfoIndex(oldName)
        self.playlistCardInfo_list[index]["playlist"] = newPlaylist
        self.__sortPlaylist(self.sortMode)

    def __showDeleteCardDialog(self, playlistName: str):
        """ 显示删除播放列表卡对话框 """
        title = "是否确定要删除此项？"
        content = f"""如果删除"{playlistName}"，它将不再位于此设备上。"""
        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(lambda: self.deleteOnePlaylistCard(playlistName))
        w.yesSignal.connect(lambda: self.deletePlaylistSig.emit(playlistName))
        w.exec()

    def deleteOnePlaylistCard(self, playlistName: str):
        """ 删除一个播放列表卡 """
        playlistCard = self.playlistName2Card_dict[playlistName]

        # 从布局中移除播放列表卡
        self.gridLayout.removeWidget(playlistCard)

        # 从列表中弹出小部件
        self.playlistCard_list.remove(playlistCard)
        self.playlistCardInfo_list.pop(self.__getCardInfoIndex(playlistName))

        # 更新字典
        self.playlists.pop(playlistName)
        self.playlistName2Card_dict.pop(playlistName)

        # 删除播放列表卡和播放列表文件
        playlistCard.deleteLater()
        moveToTrash(f'app/Playlists/{playlistName}.json')

        # 调整高度
        self.scrollWidget.resize(
            self.width(), 175 + self.gridLayout.rowCount() * 298 + 120)

        # 如果没有专辑卡就显示导航标签
        self.guideLabel.setHidden(bool(self.playlistCard_list))

    def deleteSongs(self, songPaths: list):
        """ 从各个播放列表中删除歌曲 """
        for name, playlist in self.playlists.items():
            songInfo_list = playlist["songInfo_list"]
            playlistCard = self.playlistName2Card_dict[name]

            for songInfo in songInfo_list.copy():
                if songInfo['songPath'] in songPaths:
                    songInfo_list.remove(songInfo)

            playlistCard.updateWindow(playlist)
            self.savePlaylist(playlist)

    def __deleteMultiPlaylistCards(self, playlistNames: list):
        """ 删除多个播放列表卡 """
        for name in playlistNames:
            self.deleteOnePlaylistCard(name)
            self.deletePlaylistSig.emit(name)

    def __emitCheckedPlaylists(self):
        """ 发送选中的播放列表中的歌曲 """
        # 发送播放列表
        playlist = []
        for playlistCard in self.checkedPlaylistCard_list:
            playlist.extend(playlistCard.songInfo_list)
        # 取消所有播放列表卡的选中
        self.__unCheckPlaylistCards()
        if self.sender() is self.selectionModeBar.playButton:
            self.playSig.emit(playlist)
        elif self.sender() is self.selectionModeBar.nextToPlayButton:
            self.nextToPlaySig.emit(playlist)

    def __onSelectionModeBarRenameButtonClicked(self):
        """ 选择栏重命名按钮的槽函数 """
        playlistCard = self.checkedPlaylistCard_list[0]
        self.__unCheckPlaylistCards()
        self.__showRenamePlaylistDialog(playlistCard.playlist)

    def __onSelectionModeBarDeleteButtonClicked(self):
        """ 选择栏删除按钮槽函数 """
        if len(self.checkedPlaylistCard_list) == 1:
            playlistCard = self.checkedPlaylistCard_list[0]
            # 取消所有歌曲卡的选中
            self.__unCheckPlaylistCards()
            self.__showDeleteCardDialog(playlistCard.playlistName)
        else:
            title = "确定要删除这些项？"
            content = f"若删除这些播放列表，它们将不再位于此设备上。"
            playlistNames = [
                i.playlistName for i in self.checkedPlaylistCard_list]

            # 取消所有歌曲卡的选中
            self.__unCheckPlaylistCards()

            # 显示删除对话框
            w = MessageDialog(title, content, self.window())
            w.yesSignal.connect(
                lambda: self.__deleteMultiPlaylistCards(playlistNames))
            w.exec()

    def addSongsToPlaylist(self, playlistName: str, songInfo_list: list) -> dict:
        """ 将歌曲添加到播放列表

        Parameters
        ----------
        playlistName: str
            播放列表名字

        songInfo_list: list
            新添加的歌曲列表
        """
        playlist = self.playlists[playlistName]
        playlistCard = self.playlistName2Card_dict[playlistName]
        playlist["songInfo_list"] += deepcopy(songInfo_list)
        playlist["modifiedTime"] = QDateTime.currentDateTime().toString(
            Qt.ISODate)
        playlistCard.updateWindow(playlist)

        # 更新json文件
        self.savePlaylist(playlist)

    def updateOneSongInfo(self, newSongInfo: dict):
        """ 更新一首歌曲信息 """
        for playlist in self.playlists.values():
            for i, songInfo in enumerate(playlist["songInfo_list"]):
                # 一个播放列表中可能有好几首相同的歌曲，需要全部更新
                if songInfo["songPath"] == newSongInfo["songPath"]:
                    playlist["songInfo_list"][i] = newSongInfo
                    name = playlist["playlistName"]
                    self.playlistName2Card_dict[name].updateWindow(playlist)
                    index = self.__getCardInfoIndex(name)
                    self.playlistCardInfo_list[index][1] = playlist
                    self.savePlaylist(playlist)

    def updateOnePlaylist(self, playlistName: str, songInfo_list: list):
        """ 更新一个播放列表中的歌曲

        Parameters
        ----------
        playlistName: str
            播放列表名字

        songInfo_list: list
            新的歌曲列表
        """
        playlist = self.playlists[playlistName]
        playlist["songInfo_list"] = deepcopy(songInfo_list)
        playlist["modifiedTime"] = QDateTime.currentDateTime().toString(
            Qt.ISODate)
        playlistCard = self.playlistName2Card_dict[playlistName]
        playlistCard.updateWindow(playlist)
        self.savePlaylist(playlist)

    def __getCardInfoIndex(self, playlistName: str) -> int:
        """ 通过播放列表名字获取播放列表在播放列表卡字典列表中的下标 """
        for index, info in enumerate(self.playlistCardInfo_list):
            if info["playlist"]["playlistName"] == playlistName:
                return index
        return None

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

        songInfo_list = []
        for playlistCard in self.checkedPlaylistCard_list:
            songInfo_list.extend(playlistCard.songInfo_list)

        menu.playingAct.triggered.connect(
            lambda: self.addSongsToPlayingPlaylistSig.emit(songInfo_list))
        menu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(name, songInfo_list))
        menu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(songInfo_list))
        menu.exec(QPoint(x, y))

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

    @staticmethod
    def savePlaylist(playlist: dict):
        """ 保存播放列表 """
        name = playlist["playlistName"]
        with open(f"app/Playlists/{name}.json", "w", encoding="utf-8") as f:
            dump(playlist, f)
