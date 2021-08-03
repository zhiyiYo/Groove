# coding:utf-8

from copy import deepcopy
from json import dump
from os import remove

import pinyin
from app.components.buttons.three_state_button import ThreeStatePushButton
from app.components.dialog_box.delete_card_dialog import DeleteCardDialog
from app.components.dialog_box.rename_playlist_dialog import \
    RenamePlaylistDialog
from app.components.layout.grid_layout import GridLayout
from app.components.menu import AeroMenu
from app.components.scroll_area import ScrollArea
from PyQt5.QtCore import (QDateTime, QParallelAnimationGroup, QPoint,
                          QPropertyAnimation, Qt, pyqtSignal)
from PyQt5.QtWidgets import QAction, QLabel, QPushButton, QWidget

from .blur_background import BlurBackground
from .playlist_card import PlaylistCard
from .selection_mode_bar import SelectionModeBar


class PlaylistCardInterface(QWidget):
    """ 播放列表卡界面 """

    playSig = pyqtSignal(list)
    createPlaylistSig = pyqtSignal()
    nextToPlaySig = pyqtSignal(list)
    deletePlaylistSig = pyqtSignal(dict)
    renamePlaylistSig = pyqtSignal(dict, dict)
    selectionModeStateChanged = pyqtSignal(bool)

    def __init__(self, playlists: list, parent=None):
        super().__init__(parent)
        self.columnNum = 1
        self.sortMode = "modifiedTime"
        self.playlists = deepcopy(playlists)
        self.playlistCard_list = []
        self.playlistCardDict_list = []  # type:list[dict]
        self.checkedPlaylistCard_list = []
        self.isInSelectionMode = False
        self.isAllPlaylistCardChecked = False
        # 创建小部件
        self.__createWidgets()
        # 初始化
        self.__initWidget()

    def __createWidgets(self):
        """ 创建小部件 """
        # 创建磨砂背景
        self.scrollArea = ScrollArea(self)
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
            "修改时间", self, triggered=lambda: self.__sortPlaylist("modifiedTime")
        )
        self.sortByAToZAct = QAction(
            "A到Z", self, triggered=lambda: self.__sortPlaylist("AToZ")
        )
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
        for playlist in self.playlists:
            self.__createOnePlaylistCard(playlist)

    def __createOnePlaylistCard(self, playlist: dict):
        """ 创建一个播放列表卡 """
        playlistCard = PlaylistCard(playlist, self)
        self.playlistCard_list.append(playlistCard)
        self.playlistCardDict_list.append(
            {"playlistCard": playlistCard, "playlist": playlist})
        # 创建动画
        hideCheckBoxAni = QPropertyAnimation(
            playlistCard.checkBoxOpacityEffect, b"opacity")
        self.hideCheckBoxAniGroup.addAnimation(hideCheckBoxAni)
        self.hideCheckBoxAni_list.append(hideCheckBoxAni)
        # 信号连接到槽
        playlistCard.showBlurBackgroundSig.connect(self.__showBlurBackground)
        playlistCard.hideBlurBackgroundSig.connect(self.blurBackground.hide)
        playlistCard.renamePlaylistSig.connect(self.__showRenamePlaylistPanel)
        playlistCard.deleteCardSig.connect(self.__showDeleteCardPanel)
        playlistCard.playSig.connect(self.playSig)
        playlistCard.checkedStateChanged.connect(
            self.__playlistCardCheckedStateChangedSlot)
        playlistCard.nextToPlaySig.connect(self.nextToPlaySig)

    def __initWidget(self):
        """ 初始化小部件 """
        # 隐藏小部件
        self.blurBackground.hide()
        self.selectionModeBar.hide()
        self.guideLabel.setHidden(bool(self.playlistCard_list))
        # 初始化滚动条
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
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
        self.scrollArea.move(0, 0)
        self.playlistLabel.move(30, 54)
        self.sortModeLabel.move(190, 135)
        self.sortModeButton.move(264, 130)
        self.createPlaylistButton.move(30, 130)
        self.selectionModeBar.move(
            0, self.height() - self.selectionModeBar.height())
        # 设置布局的间距和外边距
        self.gridLayout.setVerticalSpacing(20)
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setContentsMargins(15, 175, 15, 120)
        self.scrollArea.setWidget(self.scrollWidget)
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
        self.scrollArea.resize(self.size())
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
            self.width(), 175 + self.gridLayout.rowCount() * 298 + 120
        )

    def __sortPlaylist(self, key):
        """ 排序播放列表 """
        self.sortMode = key
        if key == "modifiedTime":
            self.sortModeButton.setText("修改时间")
            self.currentSortAct = self.sortByModifiedTimeAct
            self.playlistCardDict_list.sort(
                key=self.__sortPlaylistByModifiedTime, reverse=True
            )
        else:
            self.sortModeButton.setText("A到Z")
            self.currentSortAct = self.sortByAToZAct
            self.playlistCardDict_list.sort(
                key=self.__sortPlaylistByAToZ, reverse=False
            )
        # 先将小部件布局中移除
        self.gridLayout.removeAllWidgets()
        # 将小部件添加到布局中
        for index, playlistCard_dict in enumerate(self.playlistCardDict_list):
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
                QPoint(self.sender().x(), self.sender().y() - 37 * actIndex - 1)
            )
        )

    def __playlistCardCheckedStateChangedSlot(
        self, playlistCard: PlaylistCard, isChecked: bool
    ):
        """ 播放列表卡选中状态改变槽函数 """
        # 如果专辑信息不在选中的专辑信息列表中且对应的专辑卡变为选中状态就将专辑信息添加到列表中
        if playlistCard not in self.checkedPlaylistCard_list and isChecked:
            self.checkedPlaylistCard_list.append(playlistCard)
            self.__checkPlaylistCardNumChangedSlot(
                len(self.checkedPlaylistCard_list))
        # 如果专辑信息已经在列表中且该专辑卡变为非选中状态就弹出该专辑信息
        elif playlistCard in self.checkedPlaylistCard_list and not isChecked:
            self.checkedPlaylistCard_list.pop(
                self.checkedPlaylistCard_list.index(playlistCard)
            )
            self.__checkPlaylistCardNumChangedSlot(
                len(self.checkedPlaylistCard_list))
        # 如果先前不处于选择模式那么这次发生选中状态改变就进入选择模式
        if not self.isInSelectionMode:
            # 所有专辑卡进入选择模式
            self.__setAllPlaylistCardSelectionModeOpen(True)
            # 发送信号要求主窗口隐藏播放栏
            self.selectionModeStateChanged.emit(True)
            self.selectionModeBar.show()
            # 更新标志位
            self.isInSelectionMode = True
        else:
            if not self.checkedPlaylistCard_list:
                # 所有专辑卡退出选择模式
                self.__setAllPlaylistCardSelectionModeOpen(False)
                # 发送信号要求主窗口显示播放栏
                self.selectionModeBar.hide()
                self.selectionModeStateChanged.emit(False)
                # 更新标志位
                self.isInSelectionMode = False

    def __setAllPlaylistCardSelectionModeOpen(self, isOpenSelectionMode: bool):
        """ 设置所有播放列表卡是否进入选择模式 """
        for playlistCard in self.playlistCard_list:
            playlistCard.setSelectionModeOpen(isOpenSelectionMode)
        # 退出选择模式时开启隐藏所有复选框的动画
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

    def __checkPlaylistCardNumChangedSlot(self, num: int):
        """ 选中的歌曲卡数量改变对应的槽函数 """
        self.selectionModeBar.setPartButtonHidden(num > 1)
        self.selectionModeBar.move(
            0, self.height() - self.selectionModeBar.height())

    def __checkAllButtonSlot(self):
        """ 全选/取消全选按钮槽函数 """
        self.setAllPlaylistCardCheckedState(not self.isAllPlaylistCardChecked)

    def __sortPlaylistByModifiedTime(self, playlistCard_dict: dict) -> str:
        return playlistCard_dict["playlist"]["modifiedTime"]

    def __sortPlaylistByAToZ(self, playlistCard_dict: dict) -> str:
        return pinyin.get_initial(playlistCard_dict["playlist"]["playlistName"])[
            0
        ].lower()

    def addOnePlaylistCard(self, playlist: dict):
        """ 添加一个播放列表卡 """
        self.__createOnePlaylistCard(playlist)
        self.playlists.append(playlist)
        self.guideLabel.hide()
        # 向布局添加小部件
        self.gridLayout.appendWidget(self.playlistCard_list[-1])
        self.scrollWidget.resize(
            self.width(), 175 + self.gridLayout.rowCount() * 298 + 120
        )
        # 按照当前排序方式重新排序播放列表卡
        self.__sortPlaylist(self.sortMode)

    def __showRenamePlaylistPanel(
        self, oldPlaylist: dict, playlistCard: PlaylistCard = None
    ):
        """ 显示重命名播放列表面板 """
        playlistCard = (
            self.sender() if not playlistCard else playlistCard
        )  # type:PlaylistCard
        renamePlaylistPanel = RenamePlaylistDialog(oldPlaylist, self.window())
        renamePlaylistPanel.renamePlaylistSig.connect(
            lambda oldPlaylist, newPlaylist: self.__renamePlaylistSlot(
                oldPlaylist, newPlaylist, playlistCard
            )
        )
        renamePlaylistPanel.exec()

    def __renamePlaylistSlot(
        self, oldPlaylist: dict, newPlaylist: dict, playlistCard: PlaylistCard
    ):
        """ 重命名播放列表槽函数 """
        playlistCard.updateWindow(newPlaylist)
        # 重新排序播放列表卡
        index = self.playlists.index(oldPlaylist)
        self.playlists[index] = newPlaylist
        index = self.getIndexByPlaylist(oldPlaylist)
        self.playlistCardDict_list[index]["playlist"] = newPlaylist
        self.__sortPlaylist(self.sortMode)
        # 发送信号
        self.renamePlaylistSig.emit(oldPlaylist, newPlaylist)

    def __showDeleteCardPanel(self, playlist: dict, playlistCard: PlaylistCard = None):
        """ 显示删除播放列表卡对话框 """
        playlistCard = self.sender() if not playlistCard else playlistCard
        title = "是否确定要删除此项？"
        content = f"""如果删除"{playlist['playlistName']}"，它将不再位于此设备上。"""
        w = DeleteCardDialog(title, content, self.window())
        w.deleteCardSig.connect(
            lambda: self.__deleteOnePlaylistCard(playlistCard, playlist)
        )
        w.exec()

    def __deleteOnePlaylistCard(self, playlistCard: PlaylistCard, playlist: dict):
        """ 删除一个播放列表卡 """
        # 从布局中移除播放列表卡
        self.gridLayout.removeWidget(playlistCard)
        # 从列表中弹出小部件
        self.playlists.remove(playlist)
        self.playlistCard_list.remove(playlistCard)
        self.playlistCardDict_list.pop(
            self.getIndexByPlaylistCard(playlistCard))
        # 删除播放列表卡
        playlistCard.deleteLater()
        # 调整高度
        self.scrollWidget.resize(
            self.width(), 175 + self.gridLayout.rowCount() * 298 + 120
        )
        # 删除json文件并发送删除播放列表的信号
        remove(f'app\\Playlists\\{playlist["playlistName"]}.json')
        self.deletePlaylistSig.emit(playlist)
        # 如果没有专辑卡就显示导航标签
        self.guideLabel.setHidden(bool(self.playlistCard_list))

    def __deleteMultiPlaylistCards(self, playlistCard_list: list, playlists: list):
        """ 删除多个播放列表卡 """
        for playlistCard, playlist in zip(playlistCard_list, playlists):
            self.__deleteOnePlaylistCard(playlistCard, playlist)

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

    def __selectionBarRenameButtonSlot(self):
        """ 选择栏重命名按钮的槽函数 """
        playlistCard = self.checkedPlaylistCard_list[0]
        self.__unCheckPlaylistCards()
        self.__showRenamePlaylistPanel(playlistCard.playlist, playlistCard)

    def __selectionModeBarDeleteButtonSlot(self):
        """ 选择栏删除按钮槽函数 """
        if len(self.checkedPlaylistCard_list) == 1:
            playlistCard = self.checkedPlaylistCard_list[0]
            # 取消所有歌曲卡的选中
            self.__unCheckPlaylistCards()
            self.__showDeleteCardPanel(playlistCard.playlist, playlistCard)
        else:
            title = "确定要删除这些项？"
            content = f"若删除这些播放列表，它们将不再位于此设备上。"
            playlistCard_list = self.checkedPlaylistCard_list[:]
            playlists = [
                playlistCard.playlist for playlistCard in playlistCard_list]
            # 取消所有歌曲卡的选中
            self.__unCheckPlaylistCards()
            # 显示删除对话框
            w = DeleteCardDialog(title, content, self.window())
            w.deleteCardSig.connect(
                lambda: self.__deleteMultiPlaylistCards(playlistCard_list, playlists))
            w.exec()

    def addSongsToPlaylist(self, playlistName: str, songInfo_list: list) -> dict:
        """ 将歌曲添加到播放列表中，返回修改后的播放列表 """
        # 直接修改播放列表卡字典中的播放列表
        index = self.getIndexByPlaylistName(playlistName)
        playlistCard_dict = self.playlistCardDict_list[index]
        playlist = playlistCard_dict["playlist"]
        # 更新播放列表
        playlist["modifiedTime"] = QDateTime.currentDateTime().toString(
            Qt.ISODate)
        playlist["songInfo_list"] = songInfo_list + playlist["songInfo_list"]
        playlistCard_dict["playlistCard"].updateWindow(playlist)
        # 更新json文件
        with open(f"app\\Playlists\\{playlistName}.json", "w", encoding="utf-8") as f:
            dump(playlist, f)
        return playlist

    def getIndexByPlaylistName(self, playlistName: str) -> int:
        """ 通过播放列表名字获取播放列表在播放列表卡字典列表中的下标 """
        for index, playlistCard_dict in enumerate(self.playlistCardDict_list):
            if playlistCard_dict["playlist"]["playlistName"] == playlistName:
                return index
        raise Exception(f'指定的播放列表"{playlistName}"不存在')

    def getIndexByPlaylistCard(self, playlistCard: PlaylistCard) -> int:
        """ 通过播放列表卡获取播放列表在播放列表卡字典列表中的下标 """
        for index, playlistCard_dict in enumerate(self.playlistCardDict_list):
            if playlistCard_dict["playlistCard"] is playlistCard:
                return index
        raise Exception(f'指定的播放列表卡"{playlistCard.playlistName}"不存在')

    def getIndexByPlaylist(self, playlist: dict) -> int:
        """ 通过播放列表获取播放列表在播放列表卡字典列表中的下标 """
        for index, playlistCard_dict in enumerate(self.playlistCardDict_list):
            if playlistCard_dict["playlist"] == playlist:
                return index
        raise Exception(f"""指定的播放列表"{playlist['playlistName']}"不存在""")

    def exitSelectionMode(self):
        """ 退出选择模式 """
        self.__unCheckPlaylistCards()

    def __connectSignalToSlot(self):
        """ 将信号连接到槽 """
        self.sortModeButton.clicked.connect(self.__showSortModeMenu)
        self.selectionModeBar.cancelButton.clicked.connect(
            self.__unCheckPlaylistCards)
        self.selectionModeBar.checkAllButton.clicked.connect(
            self.__checkAllButtonSlot)
        self.selectionModeBar.playButton.clicked.connect(
            self.__emitCheckedPlaylists)
        self.selectionModeBar.nextToPlayButton.clicked.connect(
            self.__emitCheckedPlaylists)
        self.selectionModeBar.renameButton.clicked.connect(
            self.__selectionBarRenameButtonSlot)
        self.selectionModeBar.deleteButton.clicked.connect(
            self.__selectionModeBarDeleteButtonSlot)
        self.createPlaylistButton.clicked.connect(self.createPlaylistSig)