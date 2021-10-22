# coding:utf-8
from copy import deepcopy
from typing import Dict, List

import pinyin
from common.meta_data_getter import AlbumCoverGetter
from common.os_utils import getCoverPath
from common.thread.save_album_info_thread import SaveAlbumInfoThread
from components.album_card import AlbumBlurBackground, AlbumCard
from components.dialog_box.album_info_edit_dialog import AlbumInfoEditDialog
from components.dialog_box.message_dialog import MessageDialog
from components.group_box import GroupBox
from components.layout.grid_layout import GridLayout
from components.scroll_area import ScrollArea
from PyQt5.QtCore import (QFile, QParallelAnimationGroup, QPoint,
                          QPropertyAnimation, Qt, pyqtSignal)
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


class AlbumCardInterface(ScrollArea):
    """ 定义一个专辑卡视图 """

    playSignal = pyqtSignal(list)                               # 播放专辑
    deleteAlbumSig = pyqtSignal(list)                           # 删除(多张)专辑
    nextPlaySignal = pyqtSignal(list)                           # 下一首播放专辑
    albumNumChanged = pyqtSignal(int)                           # 专辑数改变
    isAllCheckedChanged = pyqtSignal(bool)                      # 专辑卡全部选中改变
    addAlbumToPlayingSignal = pyqtSignal(list)                  # 将专辑添加到正在播放
    selectionModeStateChanged = pyqtSignal(bool)                # 进入/退出 选择模式
    checkedAlbumCardNumChanged = pyqtSignal(int)                # 选中的专辑卡数量改变
    switchToSingerInterfaceSig = pyqtSignal(str)                # 切换到歌手界面
    switchToAlbumInterfaceSig = pyqtSignal(str, str)            # 切换到专辑界面
    editAlbumInfoSignal = pyqtSignal(dict, dict, str)           # 完成专辑信息编辑
    addAlbumToNewCustomPlaylistSig = pyqtSignal(list)           # 将专辑添加到新建的播放列表
    addAlbumToCustomPlaylistSig = pyqtSignal(str, list)         # 专辑添加到已存在的播放列表
    showLabelNavigationInterfaceSig = pyqtSignal(list, str)     # 显示标签导航界面

    def __init__(self, albumInfo_list: list, parent=None):
        super().__init__(parent)
        self.albumInfo_list = albumInfo_list
        # 初始化网格的列数
        self.columnNum = 1
        self.albumCard_list = []  # type:List[AlbumCard]
        self.albumCardInfo_list = []
        self.checkedAlbumCard_list = []  # type:List[AlbumCard]
        self.currentGroupInfo_list = []
        self.groupTitle_dict = {}  # 记录首字母或年份及其对应的第一个分组
        # 由键值对 "albumName.singer":albumCard组成的字典，albumInfo 是引用
        self.albumSinger2AlbumCard_dict = {}  # type:Dict[str, AlbumCard]
        self.albumSinger2AlbumInfo_dict = {}  # type:Dict[str, dict]
        # 初始化标志位
        self.isInSelectionMode = False
        self.isAllAlbumCardsChecked = False
        # 设置当前排序方式
        self.sortMode = "Date added"    # type:str
        self.__sortFunctions = {
            "Date added": self.sortByAddTime,
            "A to Z": self.sortByFirstLetter,
            "Release year": self.sortByYear,
            "Artist": self.sortBySonger
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
        # 初始化小部件
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1270, 760)
        # 隐藏磨砂背景
        self.albumBlurBackground.hide()
        # 设置导航标签的可见性
        self.guideLabel.raise_()
        self.guideLabel.setHidden(bool(self.albumCard_list))
        # 初始化滚动条
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
        # 创建并行动画组
        self.hideCheckBoxAniGroup = QParallelAnimationGroup(self)
        self.hideCheckBoxAni_list = []
        for albumInfo in self.albumInfo_list:
            self.__createOneAlbumCard(albumInfo)

    def __createOneAlbumCard(self, albumInfo: dict):
        """ 创建一个专辑卡 """
        # 实例化专辑卡和动画
        albumCard = AlbumCard(albumInfo, self)
        # 创建动画
        hideCheckBoxAni = QPropertyAnimation(
            albumCard.checkBoxOpacityEffect, b"opacity")
        self.hideCheckBoxAniGroup.addAnimation(hideCheckBoxAni)
        self.hideCheckBoxAni_list.append(hideCheckBoxAni)
        # 将含有专辑卡及其信息的字典插入列表
        album = albumInfo["album"]
        self.albumCard_list.append(albumCard)
        self.albumCardInfo_list.append(
            {
                "albumCard": albumCard,
                "albumName": album,
                "year": albumInfo["year"][:4],
                "singer": albumInfo["singer"],
                "firstLetter": pinyin.get_initial(album[0])[0].upper(),
            }
        )
        key = albumInfo["album"] + "." + albumInfo["singer"]
        self.albumSinger2AlbumCard_dict[key] = albumCard
        self.albumSinger2AlbumInfo_dict[key] = albumInfo
        # 专辑卡信号连接到槽函数
        albumCard.playSignal.connect(self.playSignal)
        albumCard.nextPlaySignal.connect(self.nextPlaySignal)
        albumCard.deleteCardSig.connect(self.__showDeleteOneCardDialog)
        albumCard.addToPlayingSignal.connect(self.addAlbumToPlayingSignal)
        albumCard.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterfaceSig)
        albumCard.switchToSingerInterfaceSig.connect(
            self.switchToSingerInterfaceSig)
        albumCard.checkedStateChanged.connect(
            self.__onAlbumCardCheckedStateChanged)
        albumCard.showBlurAlbumBackgroundSig.connect(
            self.__showBlurAlbumBackground)
        albumCard.hideBlurAlbumBackgroundSig.connect(
            self.albumBlurBackground.hide)
        albumCard.addAlbumToCustomPlaylistSig.connect(
            self.addAlbumToCustomPlaylistSig)
        albumCard.addAlbumToNewCustomPlaylistSig.connect(
            self.addAlbumToNewCustomPlaylistSig)
        albumCard.showAlbumInfoEditDialogSig.connect(
            self.__showAlbumInfoEditDialog)

    def __connectSignalToSlot(self):
        """ 将信号连接到槽函数 """
        # 动画完成隐藏复选框
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
        for currentGroup_dict in self.currentGroupInfo_list:
            gridLayout = currentGroup_dict["gridLayout"]  # type:GridLayout
            gridLayout.updateColumnNum(column, 210, 290)
        self.__adjustScrollWidgetSize()

    def __adjustScrollWidgetSize(self):
        """ 调整滚动部件的高度 """
        rowCount = sum(
            [
                currentGroup_dict["gridLayout"].rowCount()
                for currentGroup_dict in self.currentGroupInfo_list
            ]
        )
        containerCount = len(self.currentGroupInfo_list)
        self.scrollWidget.resize(
            self.width(),
            310 * rowCount
            + 60 * containerCount * (self.sortMode != "Date added")
            + 120
            + 245,
        )

    def __removeContainerFromVBoxLayout(self):
        """ 从竖直布局中移除专辑卡容器 """
        for currentGroup_dict in self.currentGroupInfo_list:
            # 将专辑卡从每个网格布局中移除
            currentGroup_dict["gridLayout"].removeAllWidgets()
            self.scrollWidgetVBoxLayout.removeWidget(
                currentGroup_dict["container"])
            currentGroup_dict["container"].deleteLater()
            currentGroup_dict["gridLayout"].deleteLater()
        self.currentGroupInfo_list = []

    def __addContainterToVBoxLayout(self):
        """ 将当前的分组添加到箱式布局中 """
        for currentGroup_dict in self.currentGroupInfo_list:
            self.scrollWidgetVBoxLayout.addWidget(
                currentGroup_dict["container"], 0, Qt.AlignTop)

    def __addAlbumCardToGridLayout(self):
        """ 将专辑卡添加到每一个网格布局中 """
        for currentGroup_dict in self.currentGroupInfo_list:
            for index, albumCard in enumerate(currentGroup_dict["albumCard_list"]):
                row = index // self.columnNum
                column = index - row * self.columnNum
                currentGroup_dict["gridLayout"].addWidget(
                    albumCard, row, column)
            currentGroup_dict["gridLayout"].setAlignment(Qt.AlignLeft)

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
        self.addTimeGroupInfo_list = [
            {
                "container": container,
                "gridLayout": gridLayout,
                "albumCard_list": self.albumCard_list,
            }
        ]
        # 创建一个对当前分组列表引用的列表
        self.currentGroupInfo_list = self.addTimeGroupInfo_list
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
        firstLetter_list = []
        self.firsetLetterGroupInfo_list = []
        # 将专辑卡添加到分组中
        for albumCard_dict in self.albumCardInfo_list:
            # 获取专辑卡的专辑名首字母(有可能不是字母)
            firstLetter = albumCard_dict["firstLetter"]
            firstLetter = firstLetter if 65 <= ord(
                firstLetter) <= 90 else "..."
            # 如果首字母属于不在列表中就将创建分组(仅限于A-Z和...)
            if firstLetter not in firstLetter_list:
                # firstLetter_list的首字母顺序和firsetLetterGroupInfo_list保持一致
                firstLetter_list.append(firstLetter)
                group = GroupBox(firstLetter)
                gridLayout = GridLayout()
                group.setLayout(gridLayout)
                gridLayout.setVerticalSpacing(20)
                gridLayout.setHorizontalSpacing(10)
                self.firsetLetterGroupInfo_list.append(
                    {
                        "container": group,
                        "firstLetter": firstLetter,
                        "gridLayout": gridLayout,
                        "albumCard_list": [],
                    }
                )
                self.groupTitle_list.append(group.title())
            # 将专辑卡添加到分组中
            index = firstLetter_list.index(firstLetter)
            self.firsetLetterGroupInfo_list[index]["albumCard_list"].append(
                albumCard_dict["albumCard"]
            )
        # 排序列表
        self.firsetLetterGroupInfo_list.sort(
            key=lambda item: item["firstLetter"])
        # 将...分组移到最后
        if "..." in firstLetter_list:
            unique_group = self.firsetLetterGroupInfo_list.pop(0)
            self.firsetLetterGroupInfo_list.append(unique_group)
        # 将专辑加到分组的网格布局中
        self.currentGroupInfo_list = self.firsetLetterGroupInfo_list
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
        self.groupTitle_dict.clear()
        # 将专辑卡从旧布局中移除
        self.__removeContainerFromVBoxLayout()
        # 创建分组
        year_list = []
        self.yearGroupInfo_list = []
        # 将专辑加到分组中
        for albumCard_dict in self.albumCardInfo_list:
            year = albumCard_dict["year"]
            year = self.tr("Unknown") if year == '' else year

            # 如果年份不在年份列表中就创建分组
            if year not in year_list:
                year_list.append(year)

                # 实例化分组和网格布局
                group = GroupBox(year)
                gridLayout = GridLayout()
                group.setLayout(gridLayout)
                gridLayout.setVerticalSpacing(20)
                gridLayout.setHorizontalSpacing(10)
                self.yearGroupInfo_list.append(
                    {
                        "year": year,
                        "container": group,
                        "albumCard_list": [],
                        "gridLayout": gridLayout,
                    }
                )
                self.groupTitle_list.append(group.title())
                self.groupTitle_dict[year] = group

            # 将专辑卡添加到分组中
            index = year_list.index(year)
            self.yearGroupInfo_list[index]["albumCard_list"].append(
                albumCard_dict["albumCard"])

        # 按照年份从进到远排序
        self.groupTitle_list.sort(reverse=True)
        self.yearGroupInfo_list.sort(
            key=lambda item: item["year"], reverse=True)

        # 检测是否含有未知分组,有的话将其移到最后一个
        if self.tr("Unknown") in year_list:
            unique_group = self.yearGroupInfo_list.pop(0)
            self.yearGroupInfo_list.append(unique_group)

        # 将专辑加到分组的网格布局中
        self.currentGroupInfo_list = self.yearGroupInfo_list
        self.__addAlbumCardToGridLayout()
        self.__addContainterToVBoxLayout()
        self.__adjustScrollWidgetSize()
        self.__connectGroupBoxSigToSlot("listLayout")

    def sortBySonger(self):
        """ 按照专辑的专辑进行分组排序 """
        self.sortMode = "Artist"
        # 将专辑卡从旧布局中移除
        self.groupTitle_list.clear()
        self.__removeContainerFromVBoxLayout()
        # 创建列表
        singer_list = []
        self.singerGroupInfo_list = []
        # 将专辑加到分组中
        for albumCard_dict in self.albumCardInfo_list:
            singer = albumCard_dict["singer"]
            if singer not in singer_list:
                singer_list.append(singer)
                group = GroupBox(singer)
                gridLayout = GridLayout()
                group.setLayout(gridLayout)
                gridLayout.setVerticalSpacing(20)
                gridLayout.setHorizontalSpacing(10)
                self.singerGroupInfo_list.append(
                    {
                        "singer": singer,
                        "container": group,
                        "albumCard_list": [],
                        "gridLayout": gridLayout,
                    }
                )
                # 点击分组的标题时显示导航界面
                self.groupTitle_list.append(group.title())
            # 将专辑卡添加到分组中
            index = singer_list.index(singer)
            self.singerGroupInfo_list[index]["albumCard_list"].append(
                albumCard_dict["albumCard"])
        # 排序列表
        self.singerGroupInfo_list.sort(
            key=lambda item: pinyin.get_initial(item["singer"])[0].lower())
        # 将专辑加到分组的网格布局中
        self.currentGroupInfo_list = self.singerGroupInfo_list
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

    def findAlbumCardByAlbumInfo(self, albumInfo: dict) -> AlbumCard:
        """ 通过专辑信息查找专辑卡，没找到则返回 None """
        album = albumInfo.get("album", "")
        singer = albumInfo.get("singer")
        return self.findAlbumCardByName(album, singer)

    def findAlbumCardByName(self, albumName: str, singerName: str) -> AlbumCard:
        """ 通过专辑和歌手名字查找专辑卡，没找到则返回 None """
        key = f'{albumName}.{singerName}'
        albumCard = self.albumSinger2AlbumCard_dict.get(key, None)
        return albumCard

    def findAlbumInfoByName(self, albumName: str, singerName: str) -> dict:
        """ 通过专辑和歌手名字查找专辑信息，没找到则返回 None """
        key = f'{albumName}.{singerName}'
        albumInfo = self.albumSinger2AlbumInfo_dict.get(key, {})
        return albumInfo

    def __onAlbumCardCheckedStateChanged(self, albumCard: AlbumCard, isChecked: bool):
        """ 专辑卡选中状态改变对应的槽函数 """
        # 如果专辑信息不在选中的专辑信息列表中且对应的专辑卡变为选中状态就将专辑信息添加到列表中
        if albumCard not in self.checkedAlbumCard_list and isChecked:
            self.checkedAlbumCard_list.append(albumCard)
            self.checkedAlbumCardNumChanged.emit(
                len(self.checkedAlbumCard_list))
        # 如果专辑信息已经在列表中且该专辑卡变为非选中状态就弹出该专辑信息
        elif albumCard in self.checkedAlbumCard_list and not isChecked:
            self.checkedAlbumCard_list.pop(
                self.checkedAlbumCard_list.index(albumCard))
            self.checkedAlbumCardNumChanged.emit(
                len(self.checkedAlbumCard_list))

        # 检查是否全部专辑卡选中改变
        isAllChecked = (len(self.checkedAlbumCard_list)
                        == len(self.albumCard_list))
        if isAllChecked != self.isAllAlbumCardsChecked:
            self.isAllAlbumCardsChecked = isAllChecked
            self.isAllCheckedChanged.emit(isAllChecked)

        # 如果先前不处于选择模式那么这次发生选中状态改变就进入选择模式
        if not self.isInSelectionMode:
            self.__setAllAlbumCardSelectionModeOpen(True)
            self.selectionModeStateChanged.emit(True)
            self.isInSelectionMode = True
        elif not self.checkedAlbumCard_list:
            self.__setAllAlbumCardSelectionModeOpen(False)
            self.selectionModeStateChanged.emit(False)
            self.isInSelectionMode = False

    def __setAllAlbumCardSelectionModeOpen(self, isOpen: bool):
        """ 设置所有专辑卡是否进入选择模式 """
        for albumCard in self.albumCard_list:
            albumCard.setSelectionModeOpen(isOpen)
        # 退出选择模式时开启隐藏所有复选框的动画
        if not isOpen:
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
        for albumCard in self.albumCard_list:
            albumCard.checkBox.hide()

    def unCheckAlbumCards(self):
        """ 取消所有已处于选中状态的专辑卡的选中状态 """
        checkedAlbumCard_list_copy = self.checkedAlbumCard_list.copy()
        for albumCard in checkedAlbumCard_list_copy:
            albumCard.setChecked(False)

    def setAllAlbumCardCheckedState(self, isAllChecked: bool):
        """ 设置所有的专辑卡checked状态 """
        if self.isAllAlbumCardsChecked == isAllChecked:
            return
        self.isAllAlbumCardsChecked = isAllChecked
        for albumCard in self.albumCard_list:
            albumCard.setChecked(isAllChecked)

    def __showBlurAlbumBackground(self, pos: QPoint, picPath: str):
        """ 显示磨砂背景 """
        # 将全局坐标转为窗口坐标
        pos = self.scrollWidget.mapFromGlobal(pos)
        self.albumBlurBackground.setBlurAlbum(picPath)
        self.albumBlurBackground.move(pos.x() - 28, pos.y() - 16)
        self.albumBlurBackground.show()

    def updateOneSongInfo(self, oldSongInfo: dict, newSongInfo: dict):
        """ 更新一首歌的信息 """
        newKey = newSongInfo["album"] + "." + newSongInfo["singer"]
        oldKey = oldSongInfo["album"] + "." + oldSongInfo["singer"]
        albumInfo_list = deepcopy(self.albumInfo_list)
        oldAlbumInfo = self.albumSinger2AlbumInfo_dict[oldKey]
        oldIndex = albumInfo_list.index(oldAlbumInfo)

        if newKey in self.albumSinger2AlbumInfo_dict.keys():
            albumInfo = self.albumSinger2AlbumInfo_dict[newKey]
            newIndex = self.albumInfo_list.index(albumInfo)
            albumInfo = albumInfo_list[newIndex]

            # 不增加/删除专辑，直接更新某张专辑的信息
            if oldKey == newKey:
                for i, songInfo in enumerate(albumInfo["songInfo_list"]):
                    if songInfo["songPath"] == newSongInfo["songPath"]:
                        albumInfo["songInfo_list"][i] = newSongInfo.copy()
                        albumInfo["genre"] = albumInfo["songInfo_list"][0]["genre"]
                        self.__sortOneAlbum(albumInfo)
                        break

            # 删除旧专辑中的一首歌，并在某张专辑中添加一首歌
            else:
                albumInfo_list[newIndex]["songInfo_list"].append(newSongInfo)
                self.__sortOneAlbum(albumInfo_list[newIndex])
                oldAlbumInfo = albumInfo_list[oldIndex]
                oldAlbumInfo["songInfo_list"].remove(oldSongInfo)
                if not oldAlbumInfo["songInfo_list"]:
                    albumInfo_list.remove(oldAlbumInfo)

        else:
            # 增加一张新专辑，如果旧专辑变成空的就将其移除
            oldAlbumInfo = albumInfo_list[oldIndex]
            oldAlbumInfo["songInfo_list"].remove(oldSongInfo)
            if not oldAlbumInfo["songInfo_list"]:
                albumInfo_list.remove(oldAlbumInfo)
            albumInfo_list.insert(0, self.__getAlbumInfoByOneSong(newSongInfo))

        self.updateAllAlbumCards(albumInfo_list)

    def updateOneAlbumInfo(self, oldAlbumInfo: dict, newAlbumInfo: dict, coverPath: str):
        """ 更新一张专辑信息 """
        oldSongInfo_list = oldAlbumInfo["songInfo_list"]
        newSongInfo_list = newAlbumInfo["songInfo_list"]
        albumInfo_list = deepcopy(self.albumInfo_list)
        albumSinger2AlbumInfo_dict = deepcopy(self.albumSinger2AlbumInfo_dict)

        # 更新当前专辑卡封面
        if coverPath:
            key = oldAlbumInfo["album"]+'.'+oldAlbumInfo["singer"]
            self.albumSinger2AlbumCard_dict[key].updateAlbumCover(coverPath)

        # 更新所有专辑卡
        for oldSongInfo, newSongInfo in zip(oldSongInfo_list, newSongInfo_list):
            newKey = newSongInfo["album"] + "." + newSongInfo["singer"]
            oldKey = oldSongInfo["album"] + "." + oldSongInfo["singer"]

            if newKey in albumSinger2AlbumInfo_dict.keys():
                # 不增加/删除专辑，直接更新某张专辑的信息
                albumInfo = albumSinger2AlbumInfo_dict[newKey]
                newIndex = albumInfo_list.index(albumInfo)
                if oldKey == newKey:
                    for i, songInfo in enumerate(albumInfo["songInfo_list"]):
                        if songInfo["songPath"] == newSongInfo["songPath"]:
                            albumInfo["songInfo_list"][i] = newSongInfo.copy()
                            albumInfo["genre"] = albumInfo["songInfo_list"][0]["genre"]
                            self.__sortOneAlbum(albumInfo)
                            albumInfo_list[newIndex] = albumInfo
                            albumSinger2AlbumInfo_dict[newKey] = albumInfo
                            break

                # 删除旧专辑中的一首歌，并在某张专辑中添加一首歌
                else:
                    albumInfo_list[newIndex]["songInfo_list"].append(
                        newSongInfo)
                    self.__sortOneAlbum(albumInfo_list[newIndex])
                    albumSinger2AlbumInfo_dict[newKey] = albumInfo_list[newIndex]

                    index = albumInfo_list.index(oldAlbumInfo)
                    oldAlbumInfo = albumInfo_list[index]
                    oldAlbumInfo["songInfo_list"].remove(oldSongInfo)
                    albumSinger2AlbumInfo_dict[oldKey] = oldAlbumInfo
                    if not oldAlbumInfo["songInfo_list"]:
                        albumInfo_list.remove(oldAlbumInfo)
                        albumSinger2AlbumInfo_dict.pop(oldKey)

            else:
                # 增加一张新专辑，如果旧专辑变成空的就将其移除
                index = albumInfo_list.index(oldAlbumInfo)
                oldAlbumInfo = albumInfo_list[index]
                oldAlbumInfo["songInfo_list"].remove(oldSongInfo)
                albumSinger2AlbumInfo_dict[oldKey] = oldAlbumInfo
                if not oldAlbumInfo["songInfo_list"]:
                    albumInfo_list.remove(oldAlbumInfo)
                    albumSinger2AlbumInfo_dict.pop(oldKey)

                albumInfo = self.__getAlbumInfoByOneSong(newSongInfo)
                albumSinger2AlbumInfo_dict[newKey] = albumInfo
                albumInfo_list.insert(0, albumInfo)

        self.updateAllAlbumCards(albumInfo_list)

    def updateAllAlbumCards(self, albumInfo_list: list):
        """ 更新所有专辑卡 """
        if albumInfo_list == self.albumInfo_list:
            return

        # 将专辑卡从布局中移除
        self.__removeContainerFromVBoxLayout()

        # 根据具体情况增减专辑卡
        newCardNum = len(albumInfo_list)
        oldCardNum = len(self.albumCard_list)
        if newCardNum < oldCardNum:
            # 删除部分专辑卡
            for i in range(oldCardNum - 1, newCardNum - 1, -1):
                albumCard = self.albumCard_list.pop()
                self.hideCheckBoxAni_list.pop()
                self.albumCardInfo_list.pop()
                self.hideCheckBoxAniGroup.takeAnimation(i)
                albumCard.deleteLater()
        elif newCardNum > oldCardNum:
            # 新增部分专辑卡
            for albumInfo in albumInfo_list[oldCardNum:]:
                self.__createOneAlbumCard(albumInfo)
                QApplication.processEvents()

        # 更新部分专辑卡
        self.albumInfo_list = albumInfo_list
        n = oldCardNum if oldCardNum < newCardNum else newCardNum
        for i in range(n):
            albumInfo = albumInfo_list[i]
            album = albumInfo["album"]
            self.albumCard_list[i].updateWindow(albumInfo)
            QApplication.processEvents()
            self.albumCardInfo_list[i] = {
                "albumCard": self.albumCard_list[i],
                "albumName": album,
                "year": albumInfo["year"][:4],
                "singer": albumInfo["singer"],
                "firstLetter": pinyin.get_initial(album)[0].upper(),
            }

        # 重新排序专辑卡
        self.__sortFunctions[self.sortMode]()

        # 根据当前专辑卡数决定是否显示导航标签
        self.guideLabel.setHidden(bool(albumInfo_list))

        # 更新 "专辑名.歌手名"：专辑卡 字典
        self.albumSinger2AlbumCard_dict.clear()
        self.albumSinger2AlbumInfo_dict.clear()
        for albumCard, albumInfo in zip(self.albumCard_list, albumInfo_list):
            key = albumInfo["album"] + "." + albumInfo["singer"]
            self.albumSinger2AlbumCard_dict[key] = albumCard
            self.albumSinger2AlbumInfo_dict[key] = albumInfo

        if oldCardNum != newCardNum:
            self.albumNumChanged.emit(newCardNum)

    def setSortMode(self, sortMode: str):
        """ 排序专辑卡

        Parameters
        ----------
        sortMode: str
            排序方式，有`Date added`、`A to Z`、`Release year` 和 `Artist` 四种
        """
        if self.sortMode == sortMode:
            return
        self.__sortFunctions[sortMode]()

    def __showDeleteOneCardDialog(self, albumName: str):
        """ 显示删除一个专辑卡的对话框 """
        songPaths = [i["songPath"] for i in self.sender().songInfo_list]
        title = self.tr("Are you sure you want to delete this?")
        content = self.tr("If you delete") + f' "{albumName}" ' + \
            self.tr("it won't be on be this device anymore.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(lambda: self.deleteAlbums([albumName]))
        w.yesSignal.connect(lambda: self.deleteAlbumSig.emit(songPaths))
        w.exec_()

    def __connectGroupBoxSigToSlot(self, layout):
        """ 分组框信号连接到槽函数 """
        for group_dict in self.currentGroupInfo_list:
            group_dict["container"].titleClicked.connect(
                lambda: self.showLabelNavigationInterfaceSig.emit(self.groupTitle_list, layout))

    def scrollToLabel(self, label: str):
        """ 滚动到label指定的位置 """
        group = self.groupTitle_dict[label]
        self.verticalScrollBar().setValue(group.y() - 245)

    def __getFirstLetterFirstGroupBox(self):
        """ 获取首字母对应的第一个分组框 """
        letter_list = []
        self.groupTitle_dict.clear()
        for group_dict in self.currentGroupInfo_list:
            group = group_dict["container"]
            letter = pinyin.get_initial(group.title())[0].upper()
            letter = "..." if not 65 <= ord(letter) <= 90 else letter
            # 将字母对应的第一个分组框添加到字典中
            if letter not in letter_list:
                letter_list.append(letter)
                self.groupTitle_dict[letter] = group

    def __showAlbumInfoEditDialog(self, albumInfo: dict):
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

        # 更新所有专辑卡并发送信号
        self.updateOneAlbumInfo(oldAlbumInfo, newAlbumInfo, coverPath)
        self.editAlbumInfoSignal.emit(oldAlbumInfo, newAlbumInfo, coverPath)

    @staticmethod
    def __getAlbumInfoByOneSong(songInfo: dict):
        """ 从一首歌创建一个专辑信息 """
        album = songInfo["album"]
        singer = songInfo["singer"]
        coverName = songInfo["coverName"]
        AlbumCoverGetter.getOneAlbumCover(songInfo)
        coverPath = getCoverPath(coverName, 'album_big')
        albumInfo = {
            "album": album,
            "singer": singer,
            "genre": songInfo["genre"],
            "year": songInfo["year"],
            "songInfo_list": [songInfo.copy()],
            "modifiedTime": songInfo["createTime"],
            "coverPath": coverPath,
            "coverName": coverName,
        }
        return albumInfo

    def __sortOneAlbum(self, albumInfo: dict):
        """ 根据曲序就地排序一张专辑中的歌曲列表 """
        albumInfo["songInfo_list"].sort(key=self.__getTrackNum)

    def __getTrackNum(self, songInfo: dict) -> int:
        """ 根据歌曲信息获取曲目 """
        trackNum = songInfo["tracknumber"]  # type:str
        # 处理m4a
        if not trackNum[0].isnumeric():
            return eval(trackNum)[0]
        return int(trackNum)

    def deleteSongs(self, songPaths: list):
        """ 删除歌曲 """
        albumInfo_list = deepcopy(self.albumInfo_list)
        for albumInfo in albumInfo_list.copy():
            songInfo_list = albumInfo["songInfo_list"]

            for songInfo in songInfo_list.copy():
                if songInfo["songPath"] in songPaths:
                    songInfo_list.remove(songInfo)

            # 如果专辑变成空专辑，就将其从专辑列表中移除
            if not songInfo_list:
                albumInfo_list.remove(albumInfo)

        # 更新窗口
        self.updateAllAlbumCards(albumInfo_list)

    def deleteAlbums(self, albumNames: list):
        """ 删除专辑 """
        albumInfo_list = deepcopy(self.albumInfo_list)

        for albumInfo in albumInfo_list.copy():
            if albumInfo["album"] in albumNames:
                albumInfo_list.remove(albumInfo)

        self.updateAllAlbumCards(albumInfo_list)
