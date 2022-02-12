# coding:utf-8
from typing import Dict, List

import pinyin
from common.database.entity import AlbumInfo, SongInfo
from common.library import Library
from common.signal_bus import signalBus
from components.album_card import (AlbumBlurBackground, AlbumCard,
                                   AlbumCardType, GridAlbumCardView)
from PyQt5.QtCore import (QFile, QParallelAnimationGroup, QPoint, QSize, Qt,
                          pyqtSignal)
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


class AlbumCardView(QWidget):
    """ 定义一个专辑卡视图 """

    albumNumChanged = pyqtSignal(int)                           # 专辑数改变
    checkedNumChanged = pyqtSignal(int, bool)                   # 选中专辑卡数量改变

    def __init__(self, library: Library, parent=None):
        super().__init__(parent)
        self.library = library
        self.albumInfos = library.albumInfos

        self.checkedAlbumCards = []  # type:List[AlbumCard]
        self.albumCardViews = []  # type:List[GridAlbumCardView]
        self.firstViewMap = {}

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

        self.vBoxLayout = QVBoxLayout(self)

        self.guideLabel = QLabel(
            self.tr("There is nothing to display here. Try a different filter."), self)

        # 磨砂背景
        self.albumBlurBackground = AlbumBlurBackground(self)

        # 创建专辑卡
        self.hideCheckBoxAniGroup = QParallelAnimationGroup(self)
        self.albumCards = [AlbumCard(i, self) for i in self.albumInfos]

        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1270, 760)
        self.vBoxLayout.setSpacing(30)
        self.vBoxLayout.setContentsMargins(15, 245, 0, 120)
        self.guideLabel.move(35, 286)

        self.albumBlurBackground.hide()
        self.guideLabel.raise_()
        self.guideLabel.setHidden(bool(self.albumInfos))

        self.__setQss()
        self.sortByAddTime()

    def __createAlbumCardView(self, albumCards: List[AlbumCard], title=None):
        """ 创建一个专辑卡视图 """
        albumInfos = [i.albumInfo for i in albumCards]
        view = GridAlbumCardView(
            self.library,
            albumInfos,
            AlbumCardType.ALBUM_CARD,
            title=title,
            create=False,
            isGrouped=True,
            parent=self
        )
        m = self.vBoxLayout.contentsMargins()
        view.setFixedWidth(self.width() - m.left() - m.right())
        view.setAlbumCards(albumCards)
        view.adjustHeight()

        self.hideCheckBoxAniGroup.addAnimation(view.hideCheckBoxAniGroup)

        # 专辑卡信号连接到槽函数
        view.checkedStateChanged.connect(self.__onAlbumCardCheckedStateChanged)
        view.showBlurAlbumBackgroundSig.connect(self.__showBlurAlbumBackground)
        view.hideBlurAlbumBackgroundSig.connect(self.albumBlurBackground.hide)

        self.albumCardViews.append(view)
        return view

    def resizeEvent(self, e):
        """ 根据宽度调整网格的列数 """
        m = self.vBoxLayout.contentsMargins()
        w = self.width() - m.left() - m.right()

        for view in self.albumCardViews:
            view.setFixedWidth(w)
            view.adjustHeight()

        # self.adjustHeight()

    def adjustHeight(self):
        """ 调整滚动部件的高度 """
        if not self.albumCardViews:
            return

        views = self.albumCardViews

        vh = sum(i.height() for i in views)
        n = len(views) - 1
        m = self.vBoxLayout.contentsMargins()
        h = vh + 30*n + m.top() + m.bottom()
        self.resize(self.width(), h)

    def __removeViewFromLayout(self):
        """ 从竖直布局中移除专辑卡视图 """
        for view in self.albumCardViews:
            view.layout().removeAllWidgets()
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

        self.adjustHeight()

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
            view.titleClicked.connect(
                lambda: signalBus.showLabelNavigationInterfaceSig.emit(list(firstLetters.keys()), "grid"))

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
            view.titleClicked.connect(
                lambda: signalBus.showLabelNavigationInterfaceSig.emit(years, "list"))

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
        groupCards = sorted(
            singers.items(), key=lambda i: pinyin.get_initial(i[0])[0].lower())

        # 创建视图
        for singer, cards in groupCards:
            view = self.__createAlbumCardView(cards, singer)
            view.titleClicked.connect(
                lambda: signalBus.showLabelNavigationInterfaceSig.emit(list(singers.keys()), "grid"))

        self.__addViewToLayout()

    def __setQss(self):
        """ 设置层叠样式 """
        self.guideLabel.setObjectName('guideLabel')

        f = QFile(":/qss/album_card_interface.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

        self.guideLabel.adjustSize()

    def __onAlbumCardCheckedStateChanged(self, albumCard: AlbumCard, isChecked: bool):
        """ 专辑卡选中状态改变对应的槽函数 """
        N0 = len(self.checkedAlbumCards)

        if albumCard not in self.checkedAlbumCards and isChecked:
            self.checkedAlbumCards.append(albumCard)
        elif albumCard in self.checkedAlbumCards and not isChecked:
            self.checkedAlbumCards.remove(albumCard)
        else:
            return

        N1 = len(self.checkedAlbumCards)

        if N0 == 0 and N1 > 0:
            self.setSelectionModeOpen(True)
        elif N1 == 0:
            self.setSelectionModeOpen(False)

        isAllChecked = N1 == len(self.albumCards)
        self.checkedNumChanged.emit(N1, isAllChecked)

    def setSelectionModeOpen(self, isOpen: bool):
        """ 设置所有专辑卡是否进入选择模式 """
        if isOpen == self.isInSelectionMode:
            return

        self.isInSelectionMode = isOpen
        for view in self.albumCardViews:
            view.setSelectionModeOpen(isOpen)

        if not isOpen:
            self.hideCheckBoxAniGroup.start()

    def uncheckAll(self):
        """ 取消所有已处于选中状态的专辑卡的选中状态 """
        for albumCard in self.checkedAlbumCards.copy():
            albumCard.setChecked(False)

    def setAllChecked(self, isChecked: bool):
        """ 设置所有的专辑卡checked状态 """
        if self.isAllAlbumCardsChecked == isChecked:
            return

        self.isAllAlbumCardsChecked = isChecked
        for albumCard in self.albumCards:
            albumCard.setChecked(isChecked)

    def __showBlurAlbumBackground(self, pos: QPoint, picPath: str):
        """ 显示磨砂背景 """
        pos = self.mapFromGlobal(pos)
        self.albumBlurBackground.setBlurAlbum(picPath)
        self.albumBlurBackground.move(pos.x() - 28, pos.y() - 16)
        self.albumBlurBackground.show()

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

        if N_ != N:
            self.albumNumChanged.emit(N)

    def getLabelY(self, label: str):
        """ 滚动到label指定的位置 """
        view = self.firstViewMap[label]
        return view.y() - self.vBoxLayout.contentsMargins().top()

    def showAlbumInfoEditDialog(self, singer: str, album: str):
        """ 显示专辑信息编辑界面信号 """
        self.albumCardViews[0].showAlbumInfoEditDialog(singer, album)
