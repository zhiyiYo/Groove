# coding:utf-8
from copy import deepcopy
from typing import Dict, List

import pinyin
from common.database.entity import AlbumInfo, SongInfo
from common.meta_data.reader import AlbumCoverReader
from common.os_utils import getCoverPath
from common.thread.save_album_info_thread import SaveAlbumInfoThread
from components.album_card import AlbumBlurBackground, AlbumCard
from components.dialog_box.album_info_edit_dialog import AlbumInfoEditDialog
from components.dialog_box.message_dialog import MessageDialog
from components.widgets.group_box import GroupBox
from components.layout.grid_layout import GridLayout
from components.widgets.scroll_area import ScrollArea
from PyQt5.QtCore import (QFile, QParallelAnimationGroup, QPoint,
                          QPropertyAnimation, Qt, pyqtSignal)
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


class AlbumCardInterface(ScrollArea):
    """ 定义一个专辑卡视图 """

    playSignal = pyqtSignal(str, str)                           # 播放专辑
    deleteAlbumSig = pyqtSignal(str, str)                       # 删除(多张)专辑
    nextPlaySignal = pyqtSignal(str, str)                       # 下一首播放专辑
    albumNumChanged = pyqtSignal(int)                           # 专辑数改变
    isAllCheckedChanged = pyqtSignal(bool)                      # 专辑卡全部选中改变
    addAlbumToPlayingSignal = pyqtSignal(str, str)              # 将专辑添加到正在播放
    selectionModeStateChanged = pyqtSignal(bool)                # 进入/退出 选择模式
    checkedAlbumCardNumChanged = pyqtSignal(int)                # 选中的专辑卡数量改变
    switchToSingerInterfaceSig = pyqtSignal(str)                # 切换到歌手界面
    switchToAlbumInterfaceSig = pyqtSignal(str, str)            # 切换到专辑界面
    editAlbumInfoSignal = pyqtSignal(dict, dict, str)           # 完成专辑信息编辑
    addAlbumToNewCustomPlaylistSig = pyqtSignal(str, str)       # 将专辑添加到新建的播放列表
    addAlbumToCustomPlaylistSig = pyqtSignal(str, str, str)     # 专辑添加到已存在的播放列表
    showLabelNavigationInterfaceSig = pyqtSignal(list, str)     # 显示标签导航界面

    def __init__(self, albumInfos: List[AlbumInfo], parent=None):
        super().__init__(parent)
        self.albumInfos = albumInfos

        # 初始化网格的列数
        self.columnNum = 1
        self.albumCards = []  # type:List[AlbumCard]
        self.checkedAlbumCards = []  # type:List[AlbumCard]
        self.groupInfos = []
        self.groupBoxMap = {}  # 记录首字母或年份及其对应的第一个分组框

        # 由键值对 "albumName.singer":albumCard组成的字典，albumInfo 是引用
        self.albumCardMap = {}  # type:Dict[str, AlbumCard]
        # TODO:使用数据库移除这个字典
        self.albumInfoMap = {}  # type:Dict[str, dict]

        # 初始化标志位
        self.isInSelectionMode = False
        self.isAllAlbumCardsChecked = False

        # 当前排序方式
        self.sortMode = "Date added"    # type:str
        self.__sortFunctions = {
            "Date added": self.sortByAddTime,
            "A to Z": self.sortByFirstLetter,
            "Release year": self.sortByYear,
            "Artist": self.sortBySinger
        }

        # 分组标签列表
        self.groupTitle_list = []

        # 实例化滚动部件的竖直布局
        self.scrollWidgetVBoxLayout = QVBoxLayout()

        # 实例化滚动区域和滚动区域的窗口
        self.__createGuideLabel()
        self.scrollWidget = QWidget()
        self.albumBlurBackground = AlbumBlurBackground(self.scrollWidget)

        # 创建专辑卡并将其添加到布局中
        self.__createAlbumCards()
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1270, 760)
        self.albumBlurBackground.hide()
        self.guideLabel.raise_()
        self.guideLabel.setHidden(bool(self.albumCards))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollWidget.setObjectName("scrollWidget")
        self.__connectSignalToSlot()
        self.__initLayout()
        self.__setQss()

    def __createGuideLabel(self):
        """ 创建导航标签 """
        self.guideLabel = QLabel(
            self.tr("There is nothing to display here. Try a different filter."), self)
        self.guideLabel.setStyleSheet(
            "color: black; font: 25px 'Segoe UI','Microsoft YaHei'")
        self.guideLabel.adjustSize()
        self.guideLabel.move(35, 286)

    def __createAlbumCards(self):
        """ 将专辑卡添加到窗口中 """
        self.hideCheckBoxAniGroup = QParallelAnimationGroup(self)
        self.hideCheckBoxAnis = []
        for albumInfo in self.albumInfos:
            self.__createOneAlbumCard(albumInfo)
            QApplication.processEvents()

    def __createOneAlbumCard(self, albumInfo: AlbumInfo):
        """ 创建一个专辑卡 """
        card = AlbumCard(albumInfo, self)
        hideCheckBoxAni = QPropertyAnimation(
            card.checkBoxOpacityEffect, b"opacity")
        self.hideCheckBoxAniGroup.addAnimation(hideCheckBoxAni)
        self.hideCheckBoxAnis.append(hideCheckBoxAni)

        # 将含有专辑卡及其信息的字典插入列表
        self.albumCards.append(card)
        key = albumInfo.album + "." + albumInfo.singer
        self.albumCardMap[key] = card
        self.albumInfoMap[key] = albumInfo

        # 专辑卡信号连接到槽函数
        card.playSignal.connect(self.playSignal)
        card.nextPlaySignal.connect(self.nextPlaySignal)
        card.deleteCardSig.connect(self.__showDeleteOneCardDialog)
        card.addToPlayingSignal.connect(self.addAlbumToPlayingSignal)
        card.switchToAlbumInterfaceSig.connect(self.switchToAlbumInterfaceSig)
        card.checkedStateChanged.connect(self.__onAlbumCardCheckedStateChanged)
        card.showBlurAlbumBackgroundSig.connect(self.__showBlurAlbumBackground)
        card.hideBlurAlbumBackgroundSig.connect(self.albumBlurBackground.hide)
        card.showAlbumInfoEditDialogSig.connect(self.__showAlbumInfoEditDialog)
        card.addAlbumToCustomPlaylistSig.connect(
            self.addAlbumToCustomPlaylistSig)
        card.addAlbumToNewCustomPlaylistSig.connect(
            self.addAlbumToNewCustomPlaylistSig)
        card.switchToSingerInterfaceSig.connect(
            self.switchToSingerInterfaceSig)

    def __connectSignalToSlot(self):
        """ 将信号连接到槽函数 """
        self.hideCheckBoxAniGroup.finished.connect(self.__hideAllCheckBox)

    def __initLayout(self):
        """ 初始化布局 """
        # 按照添加时间分组
        self.sortByAddTime()
        self.scrollWidgetVBoxLayout.setSpacing(30)

        # 顶部留出工具栏的位置
        self.scrollWidgetVBoxLayout.setContentsMargins(10, 245, 0, 120)
        self.scrollWidget.setLayout(self.scrollWidgetVBoxLayout)
        self.setWidget(self.scrollWidget)

    def resizeEvent(self, event):
        """ 根据宽度调整网格的列数 """
        super().resizeEvent(event)
        column = 2 if self.width() <= 690 else (self.width()-690)//220+3
        if self.columnNum == column:
            return

        self.columnNum = column
        for groupInfo in self.groupInfos:
            gridLayout = groupInfo["gridLayout"]  # type:GridLayout
            gridLayout.updateColumnNum(column, 210, 290)

        self.__adjustScrollWidgetSize()

    def __adjustScrollWidgetSize(self):
        """ 调整滚动部件的高度 """
        rowCount = sum(i["gridLayout"].rowCount() for i in self.groupInfos)
        containerCount = len(self.groupInfos)
        self.scrollWidget.resize(
            self.width(),
            310 * rowCount
            + 60 * containerCount * (self.sortMode != "Date added")
            + 120
            + 245,
        )

    def __removeContainerFromVBoxLayout(self):
        """ 从竖直布局中移除专辑卡容器 """
        for groupInfo in self.groupInfos:
            groupInfo["gridLayout"].removeAllWidgets()
            self.scrollWidgetVBoxLayout.removeWidget(
                groupInfo["container"])
            groupInfo["container"].deleteLater()
            groupInfo["gridLayout"].deleteLater()

        self.groupInfos = []

    def __addContainterToVBoxLayout(self):
        """ 将当前的分组添加到箱式布局中 """
        for groupInfo in self.groupInfos:
            self.scrollWidgetVBoxLayout.addWidget(
                groupInfo["container"], 0, Qt.AlignTop)

    def __addAlbumCardToGridLayout(self):
        """ 将专辑卡添加到每一个网格布局中 """
        for groupInfo in self.groupInfos:
            for index, albumCard in enumerate(groupInfo["albumCards"]):
                row = index // self.columnNum
                column = index - row * self.columnNum
                groupInfo["gridLayout"].addWidget(albumCard, row, column)

            groupInfo["gridLayout"].setAlignment(Qt.AlignLeft)

    def sortByAddTime(self):
        """ 按照添加时间分组 """
        self.sortMode = "Date added"

        # 创建一个包含所有歌曲卡的网格布局
        container = QWidget()
        gridLayout = GridLayout()
        gridLayout.setVerticalSpacing(20)
        gridLayout.setHorizontalSpacing(10)
        container.setLayout(gridLayout)

        # 清空分组标签列表
        self.groupTitle_list.clear()
        # 从竖直布局中移除小部件
        self.__removeContainerFromVBoxLayout()
        # 构造一个包含布局和小部件列表字典的列表
        self.groupInfos = [{
            "container": container,
            "gridLayout": gridLayout,
            "albumCards": self.albumCards,
        }]

        # 将专辑卡添加到布局中
        self.__addAlbumCardToGridLayout()
        self.__addContainterToVBoxLayout()
        self.__adjustScrollWidgetSize()

    def sortByFirstLetter(self):
        """ 按照专辑名的首字母进行分组排序 """
        self.sortMode = "A to Z"

        # 将专辑卡从旧布局中移除
        self.__removeContainerFromVBoxLayout()
        self.groupTitle_list.clear()

        # 创建分组
        firstLetters = []

        # 将专辑卡添加到分组中
        for card in self.albumCards:
            letter = pinyin.get_initial(card.album[0])[0].upper()
            letter = letter if 65 <= ord(letter) <= 90 else "..."

            # 如果首字母属于不在列表中就将创建分组(仅限于A-Z和...)
            if letter not in firstLetters:
                firstLetters.append(letter)
                group = GroupBox(letter)
                gridLayout = GridLayout()
                group.setLayout(gridLayout)
                gridLayout.setVerticalSpacing(20)
                gridLayout.setHorizontalSpacing(10)
                self.groupInfos.append({
                    "container": group,
                    "firstLetter": letter,
                    "gridLayout": gridLayout,
                    "albumCards": [],
                })
                self.groupTitle_list.append(group.title())

            # 将专辑卡添加到分组中
            index = firstLetters.index(letter)
            self.groupInfos[index]["albumCards"].append(card)

        # 排序列表
        self.groupInfos.sort(key=lambda i: i["firstLetter"])

        # 将...分组移到最后
        if "..." in firstLetters:
            unique_group = self.groupInfos.pop(0)
            self.groupInfos.append(unique_group)

        # 将专辑卡添加到网格布局中并将容器添加到竖直布局中
        self.__addAlbumCardToGridLayout()
        self.__addContainterToVBoxLayout()
        self.__adjustScrollWidgetSize()
        self.__getFirstLetterFirstGroupBox()
        self.__connectGroupBoxSigToSlot("letterGridLayout")

    def sortByYear(self):
        """ 按照专辑的年份进行分组排序 """
        self.sortMode = "Release year"
        self.groupTitle_list.clear()
        self.groupBoxMap.clear()

        # 将专辑卡从旧布局中移除
        self.__removeContainerFromVBoxLayout()

        # 创建分组
        years = []

        # 将专辑加到分组中
        for card in self.albumCards:
            year = card.year
            year = self.tr("Unknown") if year == '' else year

            # 如果年份不在年份列表中就创建分组
            if year not in years:
                years.append(year)

                # 实例化分组和网格布局
                group = GroupBox(year)
                gridLayout = GridLayout()
                group.setLayout(gridLayout)
                gridLayout.setVerticalSpacing(20)
                gridLayout.setHorizontalSpacing(10)
                self.groupInfos.append({
                    "year": year,
                    "container": group,
                    "albumCards": [],
                    "gridLayout": gridLayout,
                })
                self.groupTitle_list.append(group.title())
                self.groupBoxMap[year] = group

            # 将专辑卡添加到分组中
            index = years.index(year)
            self.groupInfos[index]["albumCards"].append(card)

        # 按照年份从进到远排序
        self.groupTitle_list.sort(reverse=True)
        self.groupInfos.sort(key=lambda i: i["year"], reverse=True)

        # 检测是否含有未知分组,有的话将其移到最后一个
        if self.tr("Unknown") in years:
            unique_group = self.groupInfos.pop(0)
            self.groupInfos.append(unique_group)

        # 将专辑加到分组的网格布局中
        self.__addAlbumCardToGridLayout()
        self.__addContainterToVBoxLayout()
        self.__adjustScrollWidgetSize()
        self.__connectGroupBoxSigToSlot("listLayout")

    def sortBySinger(self):
        """ 按照专辑的专辑进行分组排序 """
        self.sortMode = "Artist"

        # 将专辑卡从旧布局中移除
        self.groupTitle_list.clear()
        self.__removeContainerFromVBoxLayout()

        # 创建列表
        singers = []

        # 将专辑加到分组中
        for card in self.albumCards:
            singer = card.singer

            if singer not in singers:
                singers.append(singer)
                group = GroupBox(singer)
                gridLayout = GridLayout()
                group.setLayout(gridLayout)
                gridLayout.setVerticalSpacing(20)
                gridLayout.setHorizontalSpacing(10)
                self.groupInfos.append({
                    "singer": singer,
                    "container": group,
                    "albumCards": [],
                    "gridLayout": gridLayout,
                })
                # 点击分组的标题时显示导航界面
                self.groupTitle_list.append(group.title())

            # 将专辑卡添加到分组中
            index = singers.index(singer)
            self.groupInfos[index]["albumCards"].append(card)

        # 排序列表
        self.groupInfos.sort(
            key=lambda i: pinyin.get_initial(i["singer"])[0].lower())

        # 将专辑加到分组的网格布局中
        self.__addAlbumCardToGridLayout()
        self.__addContainterToVBoxLayout()
        self.__adjustScrollWidgetSize()
        self.__getFirstLetterFirstGroupBox()
        self.__connectGroupBoxSigToSlot("letterGridLayout")

    def __setQss(self):
        """ 设置层叠样式 """
        f = QFile(":/qss/album_card_interface.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

    def findAlbumCardByAlbumInfo(self, albumInfo: AlbumInfo) -> AlbumCard:
        """ 通过专辑信息查找专辑卡，没找到则返回 None """
        album = albumInfo.album
        singer = albumInfo.singer
        return self.findAlbumCardByName(album, singer)

    def findAlbumCardByName(self, albumName: str, singerName: str) -> AlbumCard:
        """ 通过专辑和歌手名字查找专辑卡，没找到则返回 None """
        key = f'{albumName}.{singerName}'
        albumCard = self.albumCardMap.get(key, None)
        return albumCard

    # TODO:移除寻找专辑信息的函数
    def findAlbumInfoByName(self, albumName: str, singerName: str) -> dict:
        """ 通过专辑和歌手名字查找专辑信息，没找到则返回 None """
        key = f'{albumName}.{singerName}'
        albumInfo = self.albumInfoMap.get(key, {})
        return albumInfo

    def __onAlbumCardCheckedStateChanged(self, albumCard: AlbumCard, isChecked: bool):
        """ 专辑卡选中状态改变对应的槽函数 """
        # 如果专辑信息不在选中的专辑信息列表中且对应的专辑卡变为选中状态就将专辑信息添加到列表中
        if albumCard not in self.checkedAlbumCards and isChecked:
            self.checkedAlbumCards.append(albumCard)
            self.checkedAlbumCardNumChanged.emit(
                len(self.checkedAlbumCards))

        # 如果专辑信息已经在列表中且该专辑卡变为非选中状态就弹出该专辑信息
        elif albumCard in self.checkedAlbumCards and not isChecked:
            self.checkedAlbumCards.pop(
                self.checkedAlbumCards.index(albumCard))
            self.checkedAlbumCardNumChanged.emit(len(self.checkedAlbumCards))

        # 检查是否全部专辑卡选中改变
        isAllChecked = len(self.checkedAlbumCards) == len(self.albumCards)
        if isAllChecked != self.isAllAlbumCardsChecked:
            self.isAllAlbumCardsChecked = isAllChecked
            self.isAllCheckedChanged.emit(isAllChecked)

        # 如果先前不处于选择模式那么这次发生选中状态改变就进入选择模式
        if not self.isInSelectionMode:
            self.__setAllAlbumCardSelectionModeOpen(True)
            self.selectionModeStateChanged.emit(True)
            self.isInSelectionMode = True
        elif not self.checkedAlbumCards:
            self.__setAllAlbumCardSelectionModeOpen(False)
            self.selectionModeStateChanged.emit(False)
            self.isInSelectionMode = False

    def __setAllAlbumCardSelectionModeOpen(self, isOpen: bool):
        """ 设置所有专辑卡是否进入选择模式 """
        for albumCard in self.albumCards:
            albumCard.setSelectionModeOpen(isOpen)

        # 退出选择模式时开启隐藏所有复选框的动画
        if not isOpen:
            self.__startHideCheckBoxAni()

    def __startHideCheckBoxAni(self):
        """ 开始隐藏复选框动画 """
        for ani in self.hideCheckBoxAnis:
            ani.setStartValue(1)
            ani.setEndValue(0)
            ani.setDuration(140)

        self.hideCheckBoxAniGroup.start()

    def __hideAllCheckBox(self):
        """ 隐藏所有复选框 """
        for albumCard in self.albumCards:
            albumCard.checkBox.hide()

    def unCheckAlbumCards(self):
        """ 取消所有已处于选中状态的专辑卡的选中状态 """
        for albumCard in self.checkedAlbumCards.copy():
            albumCard.setChecked(False)

    def setAllAlbumCardCheckedState(self, isAllChecked: bool):
        """ 设置所有的专辑卡checked状态 """
        if self.isAllAlbumCardsChecked == isAllChecked:
            return

        self.isAllAlbumCardsChecked = isAllChecked
        for albumCard in self.albumCards:
            albumCard.setChecked(isAllChecked)

    def __showBlurAlbumBackground(self, pos: QPoint, picPath: str):
        """ 显示磨砂背景 """
        pos = self.scrollWidget.mapFromGlobal(pos)
        self.albumBlurBackground.setBlurAlbum(picPath)
        self.albumBlurBackground.move(pos.x() - 28, pos.y() - 16)
        self.albumBlurBackground.show()

    # TODO:使用数据库来更新
    def updateOneSongInfo(self, oldSongInfo: SongInfo, newSongInfo: SongInfo):
        """ 更新一首歌的信息 """
        newKey = newSongInfo.album + "." + newSongInfo.singer
        oldKey = oldSongInfo.album + "." + oldSongInfo.singer
        albumInfos = deepcopy(self.albumInfos)
        oldAlbumInfo = self.albumInfoMap[oldKey]
        oldIndex = albumInfos.index(oldAlbumInfo)

        if newKey in self.albumInfoMap.keys():
            albumInfo = self.albumInfoMap[newKey]
            newIndex = self.albumInfos.index(albumInfo)
            albumInfo = albumInfos[newIndex]

            # 不增加/删除专辑，直接更新某张专辑的信息
            if oldKey == newKey:
                for i, songInfo in enumerate(albumInfo.songInfos):
                    if songInfo.file == newSongInfo.file:
                        albumInfo.songInfos[i] = newSongInfo.copy()
                        albumInfo["genre"] = albumInfo.songInfos[0]["genre"]
                        self.__sortOneAlbum(albumInfo)
                        break

                # 更新封面
                if newSongInfo.get('coverPath'):
                    coverPath = getCoverPath(
                        newSongInfo['coverName'], 'album_big')
                    oldCoverPath = albumInfo['coverPath']
                    if oldCoverPath.startswith(':') or (
                            len(albumInfo['songInfos']) == 1 and oldCoverPath != coverPath):
                        albumInfo['coverPath'] = coverPath

            # 删除旧专辑中的一首歌，并在某张专辑中添加一首歌
            else:
                albumInfos[newIndex].songInfos.append(newSongInfo)
                self.__sortOneAlbum(albumInfos[newIndex])
                oldAlbumInfo = albumInfos[oldIndex]
                oldAlbumInfo.songInfos.remove(oldSongInfo)
                if not oldAlbumInfo.songInfos:
                    albumInfos.remove(oldAlbumInfo)

        else:
            # 增加一张新专辑，如果旧专辑变成空的就将其移除
            oldAlbumInfo = albumInfos[oldIndex]
            oldAlbumInfo.songInfos.remove(oldSongInfo)
            if not oldAlbumInfo.songInfos:
                albumInfos.remove(oldAlbumInfo)
            albumInfos.insert(0, self.__getAlbumInfoByOneSong(newSongInfo))

        self.updateAllAlbumCards(albumInfos)

    # TODO:使用数据库来更新
    def updateOneAlbumInfo(self, oldAlbumInfo: AlbumInfo, newAlbumInfo: AlbumInfo, coverPath: str):
        """ 更新一张专辑信息 """
        oldSongInfos = oldAlbumInfo.songInfos
        newSongInfos = newAlbumInfo.songInfos
        albumInfos = deepcopy(self.albumInfos)
        albumInfoMap = deepcopy(self.albumInfoMap)

        # 更新当前专辑卡封面
        if coverPath:
            key = oldAlbumInfo.album+'.'+oldAlbumInfo.singer
            self.albumCardMap[key].updateAlbumCover(coverPath)

        # 更新所有专辑卡
        for oldSongInfo, newSongInfo in zip(oldSongInfos, newSongInfos):
            newKey = newSongInfo.album + "." + newSongInfo.singer
            oldKey = oldSongInfo.album + "." + oldSongInfo.singer

            if newKey in albumInfoMap.keys():
                # 不增加/删除专辑，直接更新某张专辑的信息
                albumInfo = albumInfoMap[newKey]
                newIndex = albumInfos.index(albumInfo)
                if oldKey == newKey:
                    for i, songInfo in enumerate(albumInfo.songInfos):
                        if songInfo.file == newSongInfo.file:
                            albumInfo.songInfos[i] = newSongInfo.copy()
                            albumInfo["genre"] = albumInfo.songInfos[0]["genre"]
                            self.__sortOneAlbum(albumInfo)
                            albumInfos[newIndex] = albumInfo
                            albumInfoMap[newKey] = albumInfo
                            break

                # 删除旧专辑中的一首歌，并在某张专辑中添加一首歌
                else:
                    albumInfos[newIndex].songInfos.append(
                        newSongInfo)
                    self.__sortOneAlbum(albumInfos[newIndex])
                    albumInfoMap[newKey] = albumInfos[newIndex]

                    index = albumInfos.index(oldAlbumInfo)
                    oldAlbumInfo = albumInfos[index]
                    oldAlbumInfo.songInfos.remove(oldSongInfo)
                    albumInfoMap[oldKey] = oldAlbumInfo
                    if not oldAlbumInfo.songInfos:
                        albumInfos.remove(oldAlbumInfo)
                        albumInfoMap.pop(oldKey)

            else:
                # 增加一张新专辑，如果旧专辑变成空的就将其移除
                index = albumInfos.index(oldAlbumInfo)
                oldAlbumInfo = albumInfos[index]
                oldAlbumInfo.songInfos.remove(oldSongInfo)
                albumInfoMap[oldKey] = oldAlbumInfo
                if not oldAlbumInfo.songInfos:
                    albumInfos.remove(oldAlbumInfo)
                    albumInfoMap.pop(oldKey)

                albumInfo = self.__getAlbumInfoByOneSong(newSongInfo)
                albumInfoMap[newKey] = albumInfo
                albumInfos.insert(0, albumInfo)

        self.updateAllAlbumCards(albumInfos)

    def updateAllAlbumCards(self, albumInfos: List[AlbumInfo]):
        """ 更新所有专辑卡 """
        if albumInfos == self.albumInfos:
            return

        # 将专辑卡从布局中移除
        self.__removeContainerFromVBoxLayout()

        # 根据具体情况增减专辑卡
        N = len(albumInfos)
        N_ = len(self.albumCards)
        if N < N_:
            # 删除部分专辑卡
            for i in range(N_ - 1, N - 1, -1):
                albumCard = self.albumCards.pop()
                self.hideCheckBoxAnis.pop()
                self.hideCheckBoxAniGroup.takeAnimation(i)
                albumCard.deleteLater()
                QApplication.processEvents()
        elif N > N_:
            # 新增部分专辑卡
            for albumInfo in albumInfos[N_:]:
                self.__createOneAlbumCard(albumInfo)
                QApplication.processEvents()

        # 更新部分专辑卡
        self.albumInfos = albumInfos
        n = min(N_, N)
        for i in range(n):
            albumInfo = albumInfos[i]
            self.albumCards[i].updateWindow(albumInfo)
            QApplication.processEvents()

        # 重新排序专辑卡
        self.__sortFunctions[self.sortMode]()

        # 根据当前专辑卡数决定是否显示导航标签
        self.guideLabel.setHidden(bool(albumInfos))

        # 更新 "专辑名.歌手名"：专辑卡 字典
        self.albumCardMap.clear()
        self.albumInfoMap.clear()
        for albumCard, albumInfo in zip(self.albumCards, albumInfos):
            key = albumInfo["album"] + "." + albumInfo["singer"]
            self.albumCardMap[key] = albumCard
            self.albumInfoMap[key] = albumInfo

        if N_ != N:
            self.albumNumChanged.emit(N)

    def setSortMode(self, sortMode: str):
        """ 排序专辑卡

        Parameters
        ----------
        sortMode: str
            排序方式，有`Date added`、`A to Z`、`Release year` 和 `Artist` 四种
        """
        if self.sortMode == sortMode:
            return

        self.albumBlurBackground.hide()
        self.__sortFunctions[sortMode]()

    def __showDeleteOneCardDialog(self, singer: str, album: str):
        """ 显示删除一个专辑卡的对话框 """
        title = self.tr("Are you sure you want to delete this?")
        content = self.tr("If you delete") + f' "{album}" ' + \
            self.tr("it won't be on be this device anymore.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(lambda: self.deleteAlbumSig.emit(singer, album))
        w.exec_()

    def __connectGroupBoxSigToSlot(self, layout):
        """ 分组框信号连接到槽函数 """
        for groupInfo in self.groupInfos:
            groupInfo["container"].titleClicked.connect(
                lambda: self.showLabelNavigationInterfaceSig.emit(self.groupTitle_list, layout))

    def scrollToLabel(self, label: str):
        """ 滚动到label指定的位置 """
        group = self.groupBoxMap[label]
        self.verticalScrollBar().setValue(group.y() - 245)

    def __getFirstLetterFirstGroupBox(self):
        """ 获取首字母对应的第一个分组框 """
        letters = []
        self.groupBoxMap.clear()
        for groupInfo in self.groupInfos:
            group = groupInfo["container"]
            letter = pinyin.get_initial(group.title())[0].upper()
            letter = "..." if not 65 <= ord(letter) <= 90 else letter

            # 将字母对应的第一个分组框添加到字典中
            if letter not in letters:
                letters.append(letter)
                self.groupBoxMap[letter] = group

    # TODO:使用数据库
    def __showAlbumInfoEditDialog(self, albumInfo: AlbumInfo):
        """ 显示专辑信息编辑界面信号 """
        # 创建线程和对话框
        thread = SaveAlbumInfoThread(self)
        w = AlbumInfoEditDialog(albumInfo, self.window())

        # 信号连接到槽
        w.saveInfoSig.connect(thread.setAlbumInfo)
        w.saveInfoSig.connect(thread.start)
        thread.saveFinishedSignal.connect(w.onSaveComplete)
        thread.saveFinishedSignal.connect(self.__onSaveAlbumInfoFinished)

        # 显示对话框
        w.setStyle(QApplication.style())
        w.exec_()

    def __onSaveAlbumInfoFinished(self, oldAlbumInfo: dict, newAlbumInfo: dict, coverPath):
        """ 保存专辑信息槽函数 """
        # 删除线程
        self.sender().quit()
        self.sender().wait()
        self.sender().deleteLater()

        # TODO:更新所有专辑卡并发送信号
        self.updateOneAlbumInfo(oldAlbumInfo, newAlbumInfo, coverPath)
        # self.editAlbumInfoSignal.emit(oldAlbumInfo, newAlbumInfo, coverPath)

    @staticmethod
    def __getAlbumInfoByOneSong(songInfo: dict):
        """ 从一首歌创建一个专辑信息 """
        album = songInfo["album"]
        singer = songInfo["singer"]
        coverName = songInfo["coverName"]
        AlbumCoverReader.getAlbumCover(songInfo)
        coverPath = getCoverPath(coverName, 'album_big')
        albumInfo = {
            "album": album,
            "singer": singer,
            "genre": songInfo["genre"],
            "year": songInfo["year"],
            "songInfos": [songInfo.copy()],
            "modifiedTime": songInfo["createTime"],
            "coverPath": coverPath,
            "coverName": coverName,
        }
        return albumInfo

    def __sortOneAlbum(self, albumInfo: AlbumInfo):
        """ 根据曲序就地排序一张专辑中的歌曲列表 """
        albumInfo.songInfos.sort(key=lambda i: i.track)

    # TODO:使用数据库删除
    def deleteSongs(self, songPaths: list):
        """ 删除歌曲 """
        albumInfos = deepcopy(self.albumInfos)
        for albumInfo in albumInfos.copy():
            songInfos = albumInfo["songInfos"]

            for songInfo in songInfos.copy():
                if songInfo["songPath"] in songPaths:
                    songInfos.remove(songInfo)

            # 如果专辑变成空专辑，就将其从专辑列表中移除
            if not songInfos:
                albumInfos.remove(albumInfo)

        # 更新窗口
        self.updateAllAlbumCards(albumInfos)

    def deleteAlbums(self, albums: List[str]):
        """ 删除专辑 """
        albumInfos = deepcopy(self.albumInfos)

        for albumInfo in albumInfos.copy():
            if albumInfo.album in albums:
                albumInfos.remove(albumInfo)

        self.updateAllAlbumCards(albumInfos)
