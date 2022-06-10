# coding:utf-8
from typing import Dict, List

import pinyin
from common.database.entity import SingerInfo
from common.library import Library
from common.signal_bus import signalBus
from common.style_sheet import setStyleSheet
from common.thread.singer_avatar_downloader import SingerAvatarDownloader
from components.singer_card import (GridSingerCardView, SingerBlurBackground,
                                    SingerCard, SingerCardType)
from PyQt5.QtCore import QFile, QParallelAnimationGroup, QPoint, Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


class SingerCardView(QWidget):
    """ Singer card view """

    singerNumChanged = pyqtSignal(int)          # 歌手数改变
    checkedNumChanged = pyqtSignal(int, bool)   # 选中歌手卡数量改变

    def __init__(self, library: Library, parent=None):
        super().__init__(parent)
        self.library = library
        self.singerInfos = library.singerInfos

        self.checkedSingerCards = []  # type:List[SingerCard]
        self.singerCardViews = []  # type:List[GridSingerCardView]
        self.firstViewMap = {}

        self.isInSelectionMode = False
        self.isAllSingerCardsChecked = False
        self.sortMode = "A to Z"

        self.vBoxLayout = QVBoxLayout(self)
        self.guideLabel = QLabel(
            self.tr("There is nothing to display here. Try a different filter."), self)

        self.singerBlurBackground = SingerBlurBackground(self)
        self.hideCheckBoxAniGroup = QParallelAnimationGroup(self)
        self.singerCards = [SingerCard(i, self) for i in self.singerInfos]
        self.singerCardMap = {i.singer: i for i in self.singerCards}

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.resize(1270, 760)
        self.vBoxLayout.setSpacing(30)
        self.vBoxLayout.setContentsMargins(15, 245, 0, 120)
        self.guideLabel.move(35, 286)

        self.singerBlurBackground.hide()
        self.guideLabel.raise_()
        self.guideLabel.setHidden(bool(self.singerInfos))

        self.__setQss()
        self.sortByFirstLetter()
        self.__downloadAvatars()

        signalBus.downloadAvatarFinished.connect(
            lambda s, p: self.singerCardMap[s].updateAvatar(p))

    def __createSingerCardView(self, singerCards: List[SingerCard], title=None):
        """ create a singer card view """
        singerInfos = [i.singerInfo for i in singerCards]
        view = GridSingerCardView(
            self.library,
            singerInfos,
            SingerCardType.SINGER_CARD,
            title=title,
            create=False,
            isGrouped=True,
            parent=self
        )
        m = self.vBoxLayout.contentsMargins()
        view.setFixedWidth(self.width() - m.left() - m.right())
        view.setSingerCards(singerCards)
        view.adjustHeight()

        self.hideCheckBoxAniGroup.addAnimation(view.hideCheckBoxAniGroup)

        # connect signal to slot
        view.checkedStateChanged.connect(
            self.__onSingerCardCheckedStateChanged)
        view.showBlurSingerBackgroundSig.connect(
            self.__showBlurSingerBackground)
        view.hideBlurSingerBackgroundSig.connect(
            self.singerBlurBackground.hide)

        self.singerCardViews.append(view)
        return view

    def __setQss(self):
        """ set style sheet """
        self.guideLabel.setObjectName('guideLabel')
        setStyleSheet(self, 'singer_card_interface')
        self.guideLabel.adjustSize()

    def resizeEvent(self, e):
        """ 根据宽度调整网格的列数 """
        m = self.vBoxLayout.contentsMargins()
        w = self.width() - m.left() - m.right()

        for view in self.singerCardViews:
            view.setFixedWidth(w)
            view.adjustHeight()

    def adjustHeight(self):
        """ adjust the height of view """
        if not self.singerCardViews:
            return

        views = self.singerCardViews

        vh = sum(i.height() for i in views)
        n = len(views) - 1
        m = self.vBoxLayout.contentsMargins()
        h = vh + 30*n + m.top() + m.bottom()
        self.resize(self.width(), h)

    def __removeViewFromLayout(self):
        """ remove all views from layout """
        for view in self.singerCardViews:
            view.layout().removeAllWidgets()
            self.hideCheckBoxAniGroup.removeAnimation(
                view.hideCheckBoxAniGroup)
            view.deleteLater()

        self.singerCardViews.clear()
        self.firstViewMap.clear()

    def __addViewToLayout(self):
        """ add views to layout """
        for view in self.singerCardViews:
            self.vBoxLayout.addWidget(view, 0, Qt.AlignTop)

            # add the first view corresponding to the letter to dict
            if view.title not in self.firstViewMap:
                self.firstViewMap[view.title] = view

        self.adjustHeight()

    def sortByFirstLetter(self):
        """ sort singer cards by first letter """
        self.sortMode = "A to Z"
        self.__removeViewFromLayout()

        firstLetters = {}  # type:Dict[str, List[SingerCard]]

        for card in self.singerCards:
            letter = pinyin.get_initial(card.singer[0])[0].upper()
            letter = letter if 65 <= ord(letter) <= 90 else "..."

            if letter not in firstLetters:
                firstLetters[letter] = []

            firstLetters[letter].append(card)

        # sort group
        groupCards = sorted(firstLetters.items(), key=lambda i: i[0])

        # remove ... group to the last position
        if "..." in firstLetters:
            groupCards.append(groupCards.pop(0))

        # create views
        for letter, cards in groupCards:
            view = self.__createSingerCardView(cards, letter)
            view.titleClicked.connect(
                lambda: signalBus.showLabelNavigationInterfaceSig.emit(list(firstLetters.keys()), "grid"))

        self.__addViewToLayout()

    def __onSingerCardCheckedStateChanged(self, singerCard: SingerCard, isChecked: bool):
        """ singer card checked state changed slot """
        N0 = len(self.checkedSingerCards)

        if singerCard not in self.checkedSingerCards and isChecked:
            self.checkedSingerCards.append(singerCard)
        elif singerCard in self.checkedSingerCards and not isChecked:
            self.checkedSingerCards.remove(singerCard)
        else:
            return

        N1 = len(self.checkedSingerCards)

        if N0 == 0 and N1 > 0:
            self.setSelectionModeOpen(True)
        elif N1 == 0:
            self.setSelectionModeOpen(False)

        self.isAllSingerCardsChecked = N1 == len(self.singerCards)
        self.checkedNumChanged.emit(N1, self.isAllSingerCardsChecked)

    def setSelectionModeOpen(self, isOpen: bool):
        """ set whether to open selection mode """
        if isOpen == self.isInSelectionMode:
            return

        self.isInSelectionMode = isOpen
        for view in self.singerCardViews:
            view.setSelectionModeOpen(isOpen)

        if not isOpen:
            self.hideCheckBoxAniGroup.start()

    def uncheckAll(self):
        """ uncheck all album cards """
        for singerCard in self.checkedSingerCards.copy():
            singerCard.setChecked(False)

    def setAllChecked(self, isChecked: bool):
        """ set the checked state of all album cards """
        if self.isAllSingerCardsChecked == isChecked:
            return

        self.isAllSingerCardsChecked = isChecked
        for singerCard in self.singerCards:
            singerCard.setChecked(isChecked)

    def __showBlurSingerBackground(self, pos: QPoint, picPath: str):
        """ show blur background """
        pos = self.mapFromGlobal(pos)
        self.singerBlurBackground.setBlurAvatar(picPath)
        self.singerBlurBackground.move(pos.x() - 28, pos.y() - 16)
        self.singerBlurBackground.show()

    def updateAllSingerCards(self, singerInfos: List[SingerInfo]):
        """ update all singer cards """
        if singerInfos == self.singerInfos:
            return

        self.singerCardMap.clear()
        N = len(singerInfos)
        N_ = len(self.singerCards)
        if N < N_:
            for i in range(N_ - 1, N - 1, -1):
                singerCard = self.singerCards.pop()
                singerCard.deleteLater()
                QApplication.processEvents()
        elif N > N_:
            for singerInfo in singerInfos[N_:]:
                self.singerCards.append(SingerCard(singerInfo, self))
                QApplication.processEvents()

        self.singerInfos = singerInfos
        n = min(N_, N)
        for i in range(n):
            singerInfo = singerInfos[i]
            self.singerCards[i].updateWindow(singerInfo)
            QApplication.processEvents()

        # resort album cards
        self.singerCardMap = {i.singer: i for i in self.singerCards}
        self.sortByFirstLetter()
        self.__downloadAvatars()

        self.guideLabel.setHidden(bool(singerInfos))

        if N_ != N:
            self.singerNumChanged.emit(N)

    def getLabelY(self, label: str):
        """ get the vertical position value of speciftied label """
        view = self.firstViewMap[label]
        return view.y() - self.vBoxLayout.contentsMargins().top()

    def __downloadAvatars(self):
        """ download avatars """
        singers = []
        for v in self.singerCardViews:
            singers.extend([i.singer for i in v.singerCards])

        SingerAvatarDownloader.download(singers)