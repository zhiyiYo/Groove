# coding:utf-8
from typing import Dict, List

import pinyin
from common.database.entity import AlbumInfo, SongInfo
from common.library import Library
from components.album_card import (AlbumBlurBackground, AlbumCard,
                                   AlbumCardType, GridAlbumCardView)
from components.widgets.scroll_area import ScrollArea
from PyQt5.QtCore import QFile, QParallelAnimationGroup, QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


class AlbumCardInterface(ScrollArea):
    """ 定义一个专辑卡视图 """

    playSignal = pyqtSignal(str, str)                           # 播放专辑
    nextPlaySignal = pyqtSignal(list)                           # 下一首播放专辑
    albumNumChanged = pyqtSignal(int)                           # 专辑数改变
    deleteAlbumSig = pyqtSignal(str, str)                       # 删除专辑
    isAllCheckedChanged = pyqtSignal(bool)                      # 专辑卡全部选中改变
    addAlbumToPlayingSignal = pyqtSignal(list)                  # 将专辑添加到正在播放
    selectionModeStateChanged = pyqtSignal(bool)                # 进入/退出 选择模式
    checkedAlbumCardNumChanged = pyqtSignal(int)                # 选中的专辑卡数量改变
    switchToSingerInterfaceSig = pyqtSignal(str)                # 切换到歌手界面
    switchToAlbumInterfaceSig = pyqtSignal(str, str)            # 切换到专辑界面
    addAlbumToNewCustomPlaylistSig = pyqtSignal(list)           # 将专辑添加到新建的播放列表
    addAlbumToCustomPlaylistSig = pyqtSignal(str, list)         # 专辑添加到已存在的播放列表
    showLabelNavigationInterfaceSig = pyqtSignal(list, str)     # 显示标签导航界面
    editAlbumInfoSignal = pyqtSignal(AlbumInfo, AlbumInfo, str)  # 完成专辑信息编辑

    def __init__(self, library: Library, parent=None):
        super().__init__(parent)
        self.library = library
        self.albumInfos = library.albumInfos

        self.checkedAlbumCards = []  # type:List[AlbumCard]
        self.albumCardViews = []  # type:List[GridAlbumCardView]
        self.firstViewMap = {}

        # 由键值对 "albumName.singer":albumCard组成的字典，albumInfo 是引用
        self.albumCardMap = {}  # type:Dict[str, AlbumCard]
        # TODO:使用数据库移除这个字典
        self.albumInfoMap = {}  # type:Dict[str, dict]

        # 初始化标志位
        self.isInSelectionMode = False
        self.isAllAlbumCardsChecked = False

        # 当前排序方式
        self.sortMode = "Date added"
        self.__sortFunctions = {
            "Date added": self.sortByAddTime,
            "A to Z": self.sortByFirstLetter,
            "Release year": self.sortByYear,
            "Artist": self.sortBySinger
        }

        # 滚动部件
        self.scrollWidget = QWidget()
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)

        self.guideLabel = QLabel(
            self.tr("There is nothing to display here. Try a different filter."), self)

        # 磨砂背景
        self.albumBlurBackground = AlbumBlurBackground(self.scrollWidget)

        # 创建专辑卡
        self.hideCheckBoxAniGroup = QParallelAnimationGroup(self)
        self.albumCards = [AlbumCard(i, self) for i in self.albumInfos]
        self.sortByAddTime()

        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1270, 760)
        self.setWidget(self.scrollWidget)
        self.vBoxLayout.setSpacing(30)
        self.vBoxLayout.setContentsMargins(15, 245, 0, 120)
        self.guideLabel.move(35, 286)

        self.albumBlurBackground.hide()
        self.guideLabel.raise_()
        self.guideLabel.setHidden(bool(self.albumInfos))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.__setQss()

    def __createAlbumCardView(self, albumCards: List[AlbumCard], title=None):
        """ 创建一个专辑卡视图 """
        albumInfos = [i.albumInfo for i in albumCards]
        view = GridAlbumCardView(
            self.library, albumInfos, AlbumCardType.ALBUM_CARD, title=title, create=False, parent=self)
        view.setAlbumCards(albumCards)

        self.hideCheckBoxAniGroup.addAnimation(view.hideCheckBoxAniGroup)

        # 专辑卡信号连接到槽函数
        view.playSig.connect(self.playSignal)
        view.nextPlaySig.connect(self.nextPlaySignal)
        view.deleteAlbumSig.connect(self.deleteAlbumSig)
        view.addAlbumToPlayingSig.connect(self.addAlbumToPlayingSignal)
        view.switchToAlbumInterfaceSig.connect(self.switchToAlbumInterfaceSig)
        view.checkedStateChanged.connect(self.__onAlbumCardCheckedStateChanged)
        view.showBlurAlbumBackgroundSig.connect(self.__showBlurAlbumBackground)
        view.hideBlurAlbumBackgroundSig.connect(self.albumBlurBackground.hide)
        view.addAlbumToCustomPlaylistSig.connect(
            self.addAlbumToCustomPlaylistSig)
        view.addAlbumToNewCustomPlaylistSig.connect(
            self.addAlbumToNewCustomPlaylistSig)
        view.switchToSingerInterfaceSig.connect(
            self.switchToSingerInterfaceSig)

        self.albumCardViews.append(view)
        return view

    def resizeEvent(self, e):
        """ 根据宽度调整网格的列数 """
        for view in self.albumCardViews:
            view.setFixedWidth(self.width() - 15)

        self.__adjustHeight()

    def __adjustHeight(self):
        """ 调整滚动部件的高度 """
        r = sum(i.gridLayout.rowCount() for i in self.albumCardViews)
        n = len(self.albumCardViews)
        self.scrollWidget.resize(
            self.width(),
            310*r + 60*n*(self.sortMode != "Date added") + 120 + 245
        )

    def __removeViewFromLayout(self):
        """ 从竖直布局中移除专辑卡视图 """
        for view in self.albumCardViews:
            view.gridLayout.removeAllWidgets()
            self.hideCheckBoxAniGroup.removeAnimation(
                view.hideCheckBoxAniGroup)
            view.deleteLater()

        self.albumCardViews.clear()
        self.firstViewMap.clear()

    def __addViewToLayout(self):
        """ 将视图添加到竖直布局中 """
        for view in self.albumCardViews:
            self.vBoxLayout.addWidget(view, 0, Qt.AlignTop)

            title = view.title
            if self.sortMode == 'Artist':
                title = pinyin.get_initial(title)[0].upper()
                title = "..." if not 65 <= ord(title) <= 90 else title

            # 将字母对应的第一个视图添加到字典中
            if title not in self.firstViewMap:
                self.firstViewMap[title] = view

        QApplication.sendEvent(self, QResizeEvent(self.size(), self.size()))
        QApplication.processEvents()
        self.verticalScrollBar().setValue(0)
        self.__adjustHeight()

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

    def sortByAddTime(self):
        """ 按照添加时间分组 """
        self.sortMode = "Date added"
        self.__removeViewFromLayout()
        self.__createAlbumCardView(self.albumCards)
        self.__addViewToLayout()

    def sortByFirstLetter(self):
        """ 按照专辑名的首字母进行分组排序 """
        self.sortMode = "A to Z"

        self.__removeViewFromLayout()

        # 创建分组
        firstLetters = {}  # type:Dict[str, List[AlbumCard]]

        # 将专辑卡添加到分组中
        for card in self.albumCards:
            letter = pinyin.get_initial(card.album[0])[0].upper()
            letter = letter if 65 <= ord(letter) <= 90 else "..."

            # 如果首字母属于不在列表中就将创建分组(仅限于A-Z和...)
            if letter not in firstLetters:
                firstLetters[letter] = []

            firstLetters[letter].append(card)

        # 排序分组
        groupCards = sorted(firstLetters.items(), key=lambda i: i[0])

        # 将...分组移到最后
        if "..." in firstLetters:
            groupCards.append(groupCards.pop(0))

        # 创建视图
        for letter, cards in groupCards:
            view = self.__createAlbumCardView(cards, letter)
            view.titleClicked.connect(lambda: self.showLabelNavigationInterfaceSig.emit(
                list(firstLetters.keys()), "grid"))

        self.__addViewToLayout()

    def sortByYear(self):
        """ 按照专辑的年份进行分组排序 """
        self.sortMode = "Release year"
        self.__removeViewFromLayout()

        years = {}  # type:Dict[str, List[AlbumCard]]

        for card in self.albumCards:
            year = card.year if card.year else self.tr('Unknown')

            if year not in years:
                years[year] = []

            years[year].append(card)

        # 按照年份从进到远排序
        groupCards = sorted(years.items(), key=lambda i: i[0], reverse=True)
        years = sorted(years.keys(), reverse=True)

        if self.tr("Unknown") in years:
            groupCards.append(groupCards.pop(0))

        # 创建视图
        for year, cards in groupCards:
            view = self.__createAlbumCardView(cards, year)
            view.titleClicked.connect(lambda: self.showLabelNavigationInterfaceSig.emit(
                years, "list"))

        self.__addViewToLayout()

    def sortBySinger(self):
        """ 按照专辑的专辑进行分组排序 """
        self.sortMode = "Artist"
        self.__removeViewFromLayout()

        singers = {}  # type:Dict[str, List[AlbumCard]]

        for card in self.albumCards:
            singer = card.singer

            if singer not in singers:
                singers[singer] = []

            # 将专辑卡添加到分组中
            singers[singer].append(card)

        # 排序分组
        groupCards = sorted(singers.items(), key=lambda i: i[0])

        # 创建视图
        for singer, cards in groupCards:
            view = self.__createAlbumCardView(cards, singer)
            view.titleClicked.connect(lambda: self.showLabelNavigationInterfaceSig.emit(
                list(singers.keys()), "grid"))

        self.__addViewToLayout()

    def __setQss(self):
        """ 设置层叠样式 """
        self.scrollWidget.setObjectName("scrollWidget")
        self.guideLabel.setObjectName('guideLabel')

        f = QFile(":/qss/album_card_interface.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

        self.guideLabel.adjustSize()

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
            self.hideCheckBoxAniGroup.start()

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

    # TODO:使用数据库来更新
    def updateOneAlbumInfo(self, oldAlbumInfo: AlbumInfo, newAlbumInfo: AlbumInfo, coverPath: str):
        """ 更新一张专辑信息 """

    def updateAllAlbumCards(self, albumInfos: List[AlbumInfo]):
        """ 更新所有专辑卡 """
        if albumInfos == self.albumInfos:
            return

        # 根据具体情况增减专辑卡
        N = len(albumInfos)
        N_ = len(self.albumCards)
        if N < N_:
            # 删除部分专辑卡
            for i in range(N_ - 1, N - 1, -1):
                albumCard = self.albumCards.pop()
                albumCard.deleteLater()
                QApplication.processEvents()
        elif N > N_:
            # 新增部分专辑卡
            for albumInfo in albumInfos[N_:]:
                self.albumCards.append(AlbumCard(albumInfo, self))
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

    def scrollToLabel(self, label: str):
        """ 滚动到label指定的位置 """
        view = self.firstViewMap[label]
        self.verticalScrollBar().setValue(view.y() - 245)

    # TODO:使用数据库删除
    def deleteSongs(self, songPaths: list):
        """ 删除歌曲 """

    def deleteAlbums(self, albums: List[str]):
        """ 删除专辑 """
