# coding:utf-8

from typing import List, Dict

import pinyin
from my_widget.my_grid_layout import GridLayout
from my_widget.my_groupBox import GroupBox
from my_widget.my_scrollArea import ScrollArea
from PyQt5.QtCore import (QParallelAnimationGroup, QPoint, QPropertyAnimation,
                          Qt, pyqtSignal, QThread)
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QScrollBar

from .album_card import AlbumCard
from .album_blur_background import AlbumBlurBackground
from my_dialog_box.delete_card_panel import DeleteCardPanel
from my_object.save_info_object import SaveInfoObject


class AlbumCardViewer(QWidget):
    """ 定义一个专辑卡视图 """

    playSignal = pyqtSignal(list)
    nextPlaySignal = pyqtSignal(list)
    albumNumChanged = pyqtSignal(int)
    saveAlbumInfoSig = pyqtSignal(dict, dict)
    addAlbumToPlayingSignal = pyqtSignal(list)  # 将专辑添加到正在播放
    switchToAlbumInterfaceSig = pyqtSignal(dict)
    selectionModeStateChanged = pyqtSignal(bool)
    checkedAlbumCardNumChanged = pyqtSignal(int)
    addAlbumToNewCustomPlaylistSig = pyqtSignal(list)  # 将专辑添加到新建的播放列表
    addAlbumToCustomPlaylistSig = pyqtSignal(str, list)  # 将专辑添加到已存在的自定义播放列表
    showLabelNavigationInterfaceSig = pyqtSignal(list, str)  # 显示标签导航界面

    def __init__(self, albumInfo_list: list, parent=None):
        super().__init__(parent)
        self.albumInfo_list = albumInfo_list
        # 初始化网格的列数
        self.columnNum = 1
        self.albumCard_list = []  # type:List[AlbumCard]
        self.albumCardDict_list = []
        self.checkedAlbumCard_list = []
        self.currentGroupDict_list = []
        self.groupTitle_dict = {}  # 记录首字母或年份及其对应的第一个分组
        # 由键值对 "albumName.songer":albumCard组成的字典
        self.albumSonger2AlbumCard_dict = {}  # type:Dict[str,AlbumCard]
        # 初始化标志位
        self.isInSelectionMode = False
        self.isAllAlbumCardsChecked = False
        # 设置当前排序方式
        self.sortMode = '添加时间'
        # 分组标签列表
        self.groupTitle_list = []
        # 实例化滚动部件的竖直布局
        self.scrollWidgetVBoxLayout = QVBoxLayout()
        # 实例化滚动区域和滚动区域的窗口
        self.__createGuideLabel()
        self.scrollArea = ScrollArea(self)
        self.scrollWidget = QWidget()
        self.albumBlurBackground = AlbumBlurBackground(self.scrollWidget)
        # 创建专辑卡并将其添加到布局中
        self.__createAlbumCards()
        # 创建线程
        self.saveAlbumInfoObject = SaveInfoObject()
        self.saveInfoThread = QThread(self.parent())
        self.saveAlbumInfoObject.moveToThread(self.saveInfoThread)
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
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollWidget.setObjectName('scrollWidget')
        self.__connectSignalToSlot()
        self.__initLayout()
        self.__setQss()

    def __createGuideLabel(self):
        """ 创建导航标签 """
        self.guideLabel = QLabel('这里没有可显示的内容。请尝试其他筛选器。', self)
        self.guideLabel.setStyleSheet(
            "color: black; font: 25px 'Microsoft YaHei'")
        self.guideLabel.resize(500, 26)
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
            albumCard.checkBoxOpacityEffect, b'opacity')
        self.hideCheckBoxAniGroup.addAnimation(hideCheckBoxAni)
        self.hideCheckBoxAni_list.append(hideCheckBoxAni)
        # 将含有专辑卡及其信息的字典插入列表
        album = albumInfo['album']
        self.albumCard_list.append(albumCard)
        self.albumCardDict_list.append({
            'albumCard': albumCard,
            'albumName': album,
            'year': albumInfo['year'][:4],
            'songer': albumInfo['songer'],
            'firstLetter': pinyin.get_initial(album[0])[0].upper()
        })
        self.albumSonger2AlbumCard_dict[albumInfo['album'] +
                                        '.' + albumInfo['songer']] = albumCard
        # 专辑卡信号连接到槽函数
        albumCard.playSignal.connect(self.playSignal)
        albumCard.nextPlaySignal.connect(self.nextPlaySignal)
        albumCard.saveAlbumInfoSig.connect(self.__saveAlbumInfoSlot)
        albumCard.deleteCardSig.connect(self.showDeleteOneCardPanel)
        albumCard.addToPlayingSignal.connect(
            self.addAlbumToPlayingSignal)
        albumCard.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterfaceSig)
        albumCard.checkedStateChanged.connect(
            self.__albumCardCheckedStateChangedSlot)
        albumCard.showBlurAlbumBackgroundSig.connect(
            self.__showBlurAlbumBackground)
        albumCard.hideBlurAlbumBackgroundSig.connect(
            self.albumBlurBackground.hide)
        albumCard.addAlbumToCustomPlaylistSig.connect(
            self.addAlbumToCustomPlaylistSig)
        albumCard.addAlbumToNewCustomPlaylistSig.connect(
            self.addAlbumToNewCustomPlaylistSig)
        albumCard.showAlbumInfoEditPanelSig.connect(
            self.__showAlbumInfoEditPanelSlot)

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
        self.scrollArea.setWidget(self.scrollWidget)

    def resizeEvent(self, event):
        """ 根据宽度调整网格的列数 """
        super().resizeEvent(event)
        self.scrollArea.resize(self.size())
        # 如果第一次超过1337就调整网格的列数
        if self.width() >= 1790 and self.columnNum != 8:
            self.__updateColumnNum(8)
        if 1570 <= self.width() < 1790 and self.columnNum != 7:
            self.__updateColumnNum(7)
        elif 1350 <= self.width() < 1570 and self.columnNum != 6:
            self.__updateColumnNum(6)
        elif 1130 < self.width() < 1350 and self.columnNum != 5:
            self.__updateColumnNum(5)
        elif 910 < self.width() <= 1130 and self.columnNum != 4:
            self.__updateColumnNum(4)
        elif 690 < self.width() <= 910:
            self.__updateColumnNum(3)
        elif self.width() <= 690:
            self.__updateColumnNum(2)
        # 调整滚动条
        self.scrollArea.verticalScrollBar().move(-1, 40)
        self.scrollArea.verticalScrollBar().resize(
            self.scrollArea.verticalScrollBar().width(), self.height() - 156)

    def __updateColumnNum(self, columnNum: int):
        """ 更新网格列数 """
        self.columnNum = columnNum
        for currentGroup_dict in self.currentGroupDict_list:
            gridLayout = currentGroup_dict['gridLayout']  # type:GridLayout
            gridLayout.updateColumnNum(columnNum, 210, 290)
        self.__adjustScrollWidgetSize()

    def __adjustScrollWidgetSize(self):
        """ 调整滚动部件的高度 """
        rowCount = sum([
            currentGroup_dict['gridLayout'].rowCount()
            for currentGroup_dict in self.currentGroupDict_list
        ])
        containerCount = len(self.currentGroupDict_list)
        self.scrollWidget.resize(
            self.width(), 310 * rowCount + 60 * containerCount * (self.sortMode != '添加日期') + 120 + 245)

    def __removeContainerFromVBoxLayout(self):
        """ 从竖直布局中移除专辑卡容器 """
        for currentGroup_dict in self.currentGroupDict_list:
            # 将专辑卡从每个网格布局中移除
            currentGroup_dict['gridLayout'].removeAllWidgets()
            self.scrollWidgetVBoxLayout.removeWidget(
                currentGroup_dict['container'])
            currentGroup_dict['container'].deleteLater()
            currentGroup_dict['gridLayout'].deleteLater()
        self.currentGroupDict_list = []

    def __addContainterToVBoxLayout(self):
        """ 将当前的分组添加到箱式布局中 """
        for currentGroup_dict in self.currentGroupDict_list:
            self.scrollWidgetVBoxLayout.addWidget(
                currentGroup_dict['container'], 0, Qt.AlignTop)

    def __addAlbumCardToGridLayout(self):
        """ 将专辑卡添加到每一个网格布局中 """
        for currentGroup_dict in self.currentGroupDict_list:
            for index, albumCard in enumerate(currentGroup_dict['albumCard_list']):
                row = index // self.columnNum
                column = index - row * self.columnNum
                currentGroup_dict['gridLayout'].addWidget(
                    albumCard, row, column)
            currentGroup_dict['gridLayout'].setAlignment(Qt.AlignLeft)

    def sortByAddTime(self):
        """ 按照添加时间分组 """
        self.sortMode = '添加时间'
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
        self.addTimeGroup_list = [{
            'container': container,
            'gridLayout': gridLayout,
            'albumCard_list': self.albumCard_list
        }]
        # 创建一个对当前分组列表引用的列表
        self.currentGroupDict_list = self.addTimeGroup_list
        # 将专辑卡添加到布局中
        self.__addAlbumCardToGridLayout()
        self.__addContainterToVBoxLayout()
        self.__adjustScrollWidgetSize()

    def sortByFirstLetter(self):
        """ 按照专辑名的首字母进行分组排序 """
        self.sortMode = 'A到Z'
        # 将专辑卡从旧布局中移除
        self.__removeContainerFromVBoxLayout()
        self.groupTitle_list.clear()
        # 创建分组
        firstLetter_list = []
        self.firsetLetterGroupDict_list = []
        # 将专辑卡添加到分组中
        for albumCard_dict in self.albumCardDict_list:
            # 获取专辑卡的专辑名首字母(有可能不是字母)
            firstLetter = albumCard_dict['firstLetter']
            firstLetter = firstLetter if 65 <= ord(
                firstLetter) <= 90 else '...'
            # 如果首字母属于不在列表中就将创建分组(仅限于A-Z和...)
            if firstLetter not in firstLetter_list:
                # firstLetter_list的首字母顺序和firsetLetterGroupDict_list保持一致
                firstLetter_list.append(firstLetter)
                group = GroupBox(firstLetter)
                gridLayout = GridLayout()
                group.setLayout(gridLayout)
                gridLayout.setVerticalSpacing(20)
                gridLayout.setHorizontalSpacing(10)
                self.firsetLetterGroupDict_list.append({
                    'container': group,
                    'firstLetter': firstLetter,
                    'gridLayout': gridLayout,
                    'albumCard_list': []
                })
                self.groupTitle_list.append(group.title())
            # 将专辑卡添加到分组中
            index = firstLetter_list.index(firstLetter)
            self.firsetLetterGroupDict_list[index]['albumCard_list'].append(
                albumCard_dict['albumCard'])
        # 排序列表
        self.firsetLetterGroupDict_list.sort(
            key=lambda item: item['firstLetter'])
        # 将...分组移到最后
        if '...' in firstLetter_list:
            unique_group = self.firsetLetterGroupDict_list.pop(0)
            self.firsetLetterGroupDict_list.append(unique_group)
        # 将专辑加到分组的网格布局中
        self.currentGroupDict_list = self.firsetLetterGroupDict_list
        # 将专辑卡添加到网格布局中并将容器添加到竖直布局中
        self.__addAlbumCardToGridLayout()
        self.__addContainterToVBoxLayout()
        self.__adjustScrollWidgetSize()
        self.__getFirstLetterFirstGroupBox()
        self.__connectGroupBoxSigToSlot('letterGridLayout')

    def sortByYear(self):
        """ 按照专辑的年份进行分组排序 """
        self.sortMode = '发行年份'
        self.groupTitle_list.clear()
        self.groupTitle_dict.clear()
        # 将专辑卡从旧布局中移除
        self.__removeContainerFromVBoxLayout()
        # 创建分组
        year_list = []
        self.yearGroupDict_list = []
        # 将专辑加到分组中
        for albumCard_dict in self.albumCardDict_list:
            year = albumCard_dict['year']
            year = '未知' if year == '未知年份' else year
            # 如果年份不在年份列表中就创建分组
            if year not in year_list:
                year_list.append(year)
                # 实例化分组和网格布局
                group = GroupBox(year)
                gridLayout = GridLayout()
                group.setLayout(gridLayout)
                gridLayout.setVerticalSpacing(20)
                gridLayout.setHorizontalSpacing(10)
                self.yearGroupDict_list.append({
                    'year': year,
                    'container': group,
                    'albumCard_list': [],
                    'gridLayout': gridLayout
                })
                self.groupTitle_list.append(group.title())
                self.groupTitle_dict[year] = group
            # 将专辑卡添加到分组中
            index = year_list.index(year)
            self.yearGroupDict_list[index]['albumCard_list'].append(
                albumCard_dict['albumCard'])
        # 按照年份从进到远排序
        self.groupTitle_list.sort(reverse=True)
        self.yearGroupDict_list.sort(
            key=lambda item: item['year'], reverse=True)
        # 检测是否含有未知分组,有的话将其移到最后一个
        if '未知' in year_list:
            unique_group = self.yearGroupDict_list.pop(0)
            self.yearGroupDict_list.append(unique_group)
        # 将专辑加到分组的网格布局中
        self.currentGroupDict_list = self.yearGroupDict_list
        self.__addAlbumCardToGridLayout()
        self.__addContainterToVBoxLayout()
        self.__adjustScrollWidgetSize()
        self.__connectGroupBoxSigToSlot('listLayout')

    def sortBySonger(self):
        """ 按照专辑的专辑进行分组排序 """
        self.sortMode = '歌手'
        # 将专辑卡从旧布局中移除
        self.groupTitle_list.clear()
        self.__removeContainerFromVBoxLayout()
        # 创建列表
        songer_list = []
        self.songerGroupDict_list = []
        # 将专辑加到分组中
        for albumCard_dict in self.albumCardDict_list:
            songer = albumCard_dict['songer']
            if songer not in songer_list:
                songer_list.append(songer)
                group = GroupBox(songer)
                gridLayout = GridLayout()
                group.setLayout(gridLayout)
                gridLayout.setVerticalSpacing(20)
                gridLayout.setHorizontalSpacing(10)
                self.songerGroupDict_list.append({
                    'songer': songer,
                    'container': group,
                    'albumCard_list': [],
                    'gridLayout': gridLayout
                })
                # 点击分组的标题时显示导航界面
                self.groupTitle_list.append(group.title())
            # 将专辑卡添加到分组中
            index = songer_list.index(songer)
            self.songerGroupDict_list[index]['albumCard_list'].append(
                albumCard_dict['albumCard'])
        # 排序列表
        self.songerGroupDict_list.sort(
            key=lambda item: pinyin.get_initial(item['songer'])[0].lower())
        # 将专辑加到分组的网格布局中
        self.currentGroupDict_list = self.songerGroupDict_list
        self.__addAlbumCardToGridLayout()
        self.__addContainterToVBoxLayout()
        self.__adjustScrollWidgetSize()
        self.__getFirstLetterFirstGroupBox()
        self.__connectGroupBoxSigToSlot('letterGridLayout')

    def __setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\albumCardViewer.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def findAlbumCardByAlbumInfo(self, albumInfo: dict) -> AlbumCard:
        """ 通过albumInfo获取对AlbumCard实例的引用 """
        return self.albumCard_list[self.albumInfo_list.index(albumInfo)]

    def findAlbumCardByName(self, albumName: str, songerName: str) -> AlbumCard:
        """ 通过名字查找专辑卡 """
        albumCard = self.albumSonger2AlbumCard_dict.get(
            albumName+'.'+songerName, None)
        return albumCard

    def __albumCardCheckedStateChangedSlot(self, albumCard: AlbumCard, isChecked: bool):
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
        # 如果先前不处于选择模式那么这次发生选中状态改变就进入选择模式
        if not self.isInSelectionMode:
            # 所有专辑卡进入选择模式
            self.__setAllAlbumCardSelectionModeOpen(True)
            # 发送信号要求主窗口隐藏播放栏
            self.selectionModeStateChanged.emit(True)
            # 更新标志位
            self.isInSelectionMode = True
        else:
            if not self.checkedAlbumCard_list:
                # 所有专辑卡退出选择模式
                self.__setAllAlbumCardSelectionModeOpen(False)
                # 发送信号要求主窗口显示播放栏
                self.selectionModeStateChanged.emit(False)
                # 更新标志位
                self.isInSelectionMode = False

    def __setAllAlbumCardSelectionModeOpen(self, isOpenSelectionMode: bool):
        """ 设置所有专辑卡是否进入选择模式 """
        for albumCard in self.albumCard_list:
            albumCard.setSelectionModeOpen(isOpenSelectionMode)
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
        self.albumBlurBackground.move(pos.x() - 31, pos.y() - 16)
        self.albumBlurBackground.show()

    def updateOneAlbumCardSongInfo(self, newSongInfo: dict):
        """ 更新一个专辑卡的一首歌的信息 """
        key = newSongInfo['album']+'.'+newSongInfo['songer']
        if key in self.albumSonger2AlbumCard_dict.keys():
            albumInfo = self.albumSonger2AlbumCard_dict[key].albumInfo
            for i, songInfo in enumerate(albumInfo['songInfo_list']):
                if songInfo['songPath'] == newSongInfo['songPath']:
                    albumInfo['songInfo_list'][i] = newSongInfo.copy()
                    return albumInfo
        return {}

    def updateAllAlbumCards(self, albumInfo_list: list):
        """ 更新所有专辑卡 """
        oldAlbumInfo_list = [
            albumCard.albumInfo for albumCard in self.albumCard_list]
        if albumInfo_list == oldAlbumInfo_list:
            return
        # 将专辑卡从布局中移除
        self.__removeContainerFromVBoxLayout()
        # 根据具体情况增减专辑卡
        newCardNum = len(albumInfo_list)
        oldCardNum = len(self.albumCard_list)
        deltaNum = newCardNum - oldCardNum
        if deltaNum < 0:
            for i in range(oldCardNum - 1, newCardNum - 1, -1):
                albumCard = self.albumCard_list.pop()
                self.hideCheckBoxAni_list.pop()
                self.albumCardDict_list.pop()
                self.hideCheckBoxAniGroup.takeAnimation(i)
                albumCard.deleteLater()
        elif deltaNum > 0:
            for albumInfo in albumInfo_list[oldCardNum:]:
                self.__createOneAlbumCard(albumInfo)
                QApplication.processEvents()
        # 更新部分专辑卡
        self.albumInfo_list = albumInfo_list
        iterRange = range(oldCardNum) if deltaNum > 0 else range(newCardNum)
        for i in iterRange:
            albumInfo = albumInfo_list[i]
            album = albumInfo['album']
            self.albumCard_list[i].updateWindow(albumInfo)
            QApplication.processEvents()
            self.albumCardDict_list[i] = {
                'albumCard': self.albumCard_list[i],
                'albumName': album,
                'year': albumInfo['year'][:4],
                'songer': albumInfo['songer'],
                'firstLetter': pinyin.get_initial(album)[0].upper()
            }
        # 重新排序专辑卡
        self.setSortMode(self.sortMode)
        # 根据当前专辑卡数决定是否显示导航标签
        self.guideLabel.setHidden(bool(albumInfo_list))
        # 更新 "专辑名.歌手名"：专辑卡 字典
        self.albumSonger2AlbumCard_dict = {}
        for albumCard in self.albumCard_list:
            albumInfo = albumCard.albumInfo
            self.albumSonger2AlbumCard_dict[albumInfo['album'] +
                                            '.'+albumInfo['songer']] = albumCard
        if deltaNum != 0:
            self.albumNumChanged.emit(newCardNum)

    def setSortMode(self, sortMode: str):
        """ 排序专辑卡 """
        self.sortMode = sortMode
        if sortMode == '添加时间':
            self.sortByAddTime()
        elif sortMode == 'A到Z':
            self.sortByFirstLetter()
        elif sortMode == '发行年份':
            self.sortByYear()
        elif sortMode == '歌手':
            self.sortBySonger()
        else:
            raise Exception(f'排序依据"{sortMode}"不存在')

    def showDeleteOneCardPanel(self, albumInfo: dict):
        """ 显示删除一个专辑卡的对话框 """
        title = '是否确定要删除此项？'
        content = f"""如果删除"{albumInfo['album']}"，它将不再位于此设备上。"""
        deleteCardPanel = DeleteCardPanel(title, content, self.window())
        deleteCardPanel.deleteCardSig.connect(
            lambda: self.__deleteAlbumCards([albumInfo]))
        deleteCardPanel.exec_()

    def showDeleteMultiAlbumCardPanel(self, albumInfo_list: list):
        """ 显示删除多个专辑卡的对话框 """
        title = '确定要删除这些项？'
        content = "如果你删除这些专辑，它们将不再位于此设备上。"
        deleteCardPanel = DeleteCardPanel(title, content, self.window())
        deleteCardPanel.deleteCardSig.connect(
            lambda: self.__deleteAlbumCards(albumInfo_list))
        deleteCardPanel.exec()

    def __deleteAlbumCards(self, albumInfo_list: list):
        """ 删除一个专辑卡 """
        for albumInfo in albumInfo_list:
            self.albumInfo_list.remove(albumInfo)
        self.updateAllAlbumCards(self.albumInfo_list)

    def __connectGroupBoxSigToSlot(self, layout):
        """ 分组框信号连接到槽函数 """
        for group_dict in self.currentGroupDict_list:
            group_dict['container'].titleClicked.connect(
                lambda: self.showLabelNavigationInterfaceSig.emit(self.groupTitle_list, layout))

    def scrollToLabel(self, label: str):
        """ 滚动到label指定的位置 """
        group = self.groupTitle_dict[label]
        self.scrollArea.verticalScrollBar().setValue(group.y() - 245)

    def __getFirstLetterFirstGroupBox(self):
        """ 获取首字母对应的第一个分组框 """
        letter_list = []
        self.groupTitle_dict.clear()
        for group_dict in self.currentGroupDict_list:
            group = group_dict['container']
            letter = pinyin.get_initial(group.title())[0].upper()
            letter = '...' if not 65 <= ord(letter) <= 90 else letter
            # 将字母对应的第一个分组框添加到字典中
            if letter not in letter_list:
                letter_list.append(letter)
                self.groupTitle_dict[letter] = group

    def __showAlbumInfoEditPanelSlot(self, albumInfoEditPanel):
        """ 显示专辑信息编辑界面信号 """
        self.saveAlbumInfoObject.saveErrorSig.connect(
            albumInfoEditPanel.saveErrorSlot)
        self.saveAlbumInfoObject.saveCompleteSig.connect(
            albumInfoEditPanel.saveCompleteSlot)

    def __saveAlbumInfoSlot(self, oldAlbumInfo: dict, newAlbumInfo: dict):
        """ 保存专辑信息槽函数 """
        # 更新字典
        self.albumSonger2AlbumCard_dict.pop(
            oldAlbumInfo['album']+'.'+oldAlbumInfo['songer'])
        self.albumSonger2AlbumCard_dict[newAlbumInfo['album']+'.'+newAlbumInfo['songer']] = self.sender(
        )
        self.saveAlbumInfoObject.saveAlbumInfoSlot(
            newAlbumInfo['songInfo_list'])
        self.saveAlbumInfoSig.emit(oldAlbumInfo, newAlbumInfo)
        # self.saveAlbumInfoObject.disconnect()
