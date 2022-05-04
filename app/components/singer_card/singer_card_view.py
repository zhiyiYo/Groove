# coding:utf-8
from typing import List

from common.database.entity import SingerInfo
from common.library import Library
from common.signal_bus import signalBus
from components.layout import FlowLayout, HBoxLayout
from components.widgets.label import ClickableLabel
from PyQt5.QtCore import QMargins, QParallelAnimationGroup, QPoint, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget

from .singer_card import SingerCardBase, SingerCardFactory, SingerCardType


class SingerCardViewBase(QWidget):
    """ Singer card view base class """

    checkedNumChanged = pyqtSignal(int, bool)                # 选中歌手卡数量改变
    checkedStateChanged = pyqtSignal(SingerCardBase, bool)   # 歌手卡选中状态改变
    showBlurSingerBackgroundSig = pyqtSignal(QPoint, str)    # 显示磨砂背景
    hideBlurSingerBackgroundSig = pyqtSignal()               # 隐藏磨砂背景

    def __init__(self, library: Library, singerInfos: List[SingerInfo], cardType: SingerCardType, create=True, isGrouped=False, parent=None):
        """
        Parameters
        ----------
        library: Library
            song library

        singerInfos: List[SingerInfo]
            singer information list

        cardType: SingerCardType
            singer card type

        create: bool
            whether to create singer card

        isGrouped: bool
            whether the view is grouped

        parent:
            parent window
        """
        super().__init__(parent=parent)
        self.library = library
        self.singerInfos = singerInfos
        self.isGrouped = isGrouped
        self.cardType = cardType
        self.singerCards = []  # type:List[SingerCardBase]
        self.checkedSingerCards = []  # type:List[SingerCardBase]
        self.isInSelectionMode = False
        self.hideCheckBoxAniGroup = QParallelAnimationGroup(self)
        self.hideCheckBoxAniGroup.finished.connect(self.__hideAllCheckBox)

        if create:
            for singerInfo in self.singerInfos:
                self._createSingerCard(singerInfo)
                QApplication.processEvents()

    def _createSingerCard(self, singerInfo: SingerInfo):
        """ create an singer card """
        card = SingerCardFactory.create(self.cardType, singerInfo, self)
        self.hideCheckBoxAniGroup.addAnimation(card.hideCheckBoxAni)
        self._connectCardSignalToSlot(card)
        self.singerCards.append(card)

    def _connectCardSignalToSlot(self, card: SingerCardBase):
        """ connect singer card signal to slot """
        card.playSignal.connect(
            lambda s: signalBus.playCheckedSig.emit(self.getSongInfos([s])))
        card.nextPlaySignal.connect(
            lambda s: signalBus.nextToPlaySig.emit(self.getSongInfos([s])))
        card.addToPlayingSignal.connect(
            lambda s: signalBus.addSongsToPlayingPlaylistSig.emit(self.getSongInfos([s])))
        card.addSingerToCustomPlaylistSig.connect(
            lambda n, s: signalBus.addSongsToCustomPlaylistSig.emit(n, self.getSongInfos([s])))
        card.addSingerToNewCustomPlaylistSig.connect(
            lambda s: signalBus.addSongsToNewCustomPlaylistSig.emit(self.getSongInfos([s])))
        card.checkedStateChanged.connect(self.__onSingerCardCheckedStateChanged)
        card.showBlurSingerBackgroundSig.connect(
            self.showBlurSingerBackgroundSig)
        card.hideBlurSingerBackgroundSig.connect(
            self.hideBlurSingerBackgroundSig)

    def getSongInfos(self, singers: List[str]):
        """ get song information of singers """
        return self.library.songInfoController.getSongInfosBySingers(singers)

    def __hideAllCheckBox(self):
        """ hide check box of singer cards """
        for card in self.singerCards:
            card.checkBox.hide()

    def setSingerCards(self, singerCards: List[SingerCardBase]):
        """ set singer cards in the view and do not generate new cards """
        raise NotImplementedError

    def _addSingerCardsToLayout(self):
        """ add all singer cards to layout """
        raise NotImplementedError

    def _removeSingerCardsFromLayout(self):
        """ remove all singer cards from layout """
        raise NotImplementedError

    def updateAllSingerCards(self, singerInfos: List[SingerInfo]):
        """ update all singer cards """
        self._removeSingerCardsFromLayout()

        N = len(singerInfos)
        N_ = len(self.singerCards)
        if N < N_:
            for i in range(N_ - 1, N - 1, -1):
                singerCard = self.singerCards.pop()
                self.hideCheckBoxAniGroup.takeAnimation(i)
                singerCard.deleteLater()
        elif N > N_:
            for singerInfo in singerInfos[N_:]:
                self._createSingerCard(singerInfo)
                QApplication.processEvents()

        # update part of singer cards
        self.singerInfos = singerInfos
        for i in range(min(N, N_)):
            singerInfo = singerInfos[i]
            self.singerCards[i].updateWindow(singerInfo)
            QApplication.processEvents()

        self._addSingerCardsToLayout()
        self.setStyle(QApplication.style())
        self.adjustSize()

    def __onSingerCardCheckedStateChanged(self, singerCard: SingerCardBase, isChecked: bool):
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
        elif N1 == 0 and not self.isGrouped:
            self.setSelectionModeOpen(False)

        isAllChecked = N1 == len(self.singerCards)
        self.checkedNumChanged.emit(N1, isAllChecked)

        if self.isGrouped:
            self.checkedStateChanged.emit(singerCard, isChecked)

    def setSelectionModeOpen(self, isOpen: bool):
        """ set whether to open selection mode """
        if self.isInSelectionMode == isOpen:
            return

        self.isInSelectionMode = isOpen
        for card in self.singerCards:
            card.setSelectionModeOpen(isOpen)

        if not isOpen and not self.isGrouped:
            self.hideCheckBoxAniGroup.start()

    def setAllChecked(self, isChecked: bool):
        """ set the checked state of all singer cards """
        for card in self.singerCards:
            card.setChecked(isChecked)

    def uncheckAll(self):
        """ uncheck all singer cards """
        for card in self.checkedSingerCards.copy():
            card.setChecked(False)

    def adjustHeight(self):
        """ adjust view height """
        raise NotImplementedError


class GridSingerCardView(SingerCardViewBase):
    """ Singer card view with grid layout """

    titleClicked = pyqtSignal()

    def __init__(self, library: Library, singerInfos: List[SingerInfo], cardType: SingerCardType,
                 spacings=(10, 20), margins=QMargins(0, 0, 0, 0), title: str = None, create=True,
                 isGrouped=False, parent=None):
        """
        Parameters
        ----------
        library: Library
            song library

        singerInfos: List[SingerInfo]
            singer information list

        cardType: SingerCardType
            singer card type

        spacings: tuple
            horizontal and vertical spacing between singer cards

        margins: QMargins
            margins of grid layout

        title: str
            title of view

        create: bool
            whether to create singer card

        isGrouped: bool
            whether the view is grouped

        parent:
            parent window
        """
        super().__init__(library, singerInfos, cardType, create, isGrouped, parent)
        self.title = title or ''
        self.titleLabel = ClickableLabel(self.title, self)

        self.flowLayout = FlowLayout(self)
        margins_ = margins + QMargins(0, 45*bool(self.title), 0, 0)
        self.flowLayout.setContentsMargins(margins_)
        self.flowLayout.setHorizontalSpacing(spacings[0])
        self.flowLayout.setVerticalSpacing(spacings[1])

        self.titleLabel.setVisible(bool(self.title))
        self.titleLabel.move(8, 6)
        self.titleLabel.clicked.connect(self.titleClicked)
        self.titleLabel.setStyleSheet(
            "font: 22px 'Segoe UI Semilight', 'Microsoft YaHei Light'; font-weight: bold; color: rgb(0, 153, 188)")
        self.titleLabel.adjustSize()

        if create:
            self._addSingerCardsToLayout()

    def _addSingerCardsToLayout(self):
        for card in self.singerCards:
            self.flowLayout.addWidget(card)
            QApplication.processEvents()

    def _removeSingerCardsFromLayout(self):
        self.flowLayout.removeAllWidgets()

    def setSingerCards(self, singerCards: List[SingerCardBase]):
        self.singerCards = singerCards
        self.singerInfos = [i.singerInfo for i in singerCards]

        self.hideCheckBoxAniGroup.clear()
        for card in self.singerCards:
            self.hideCheckBoxAniGroup.addAnimation(card.hideCheckBoxAni)
            self._connectCardSignalToSlot(card)

        self._addSingerCardsToLayout()

    def adjustHeight(self):
        h = self.flowLayout.heightForWidth(self.width())
        self.resize(self.width(), h)


class HorizonSingerCardView(SingerCardViewBase):
    """ Singer card view with horizontal box layout """

    def __init__(self, library: Library, singerInfos: List[SingerInfo], cardType: SingerCardType,
                 spacing=20, margins=QMargins(0, 0, 0, 0), create=True, isGrouped=False, parent=None):
        """
        Parameters
        ----------
        library: Library
            song library

        singerInfos: List[SingerInfo]
            singer information list

        cardType: SingerCardType
            singer card type

        spacings: tuple
            horizontal spacing between singer cards

        margins: QMargins
            margins of grid layout

        create: bool
            whether to create singer card

        isGrouped: bool
            whether the view is grouped

        parent:
            parent window
        """
        super().__init__(library, singerInfos, cardType, create, isGrouped, parent)
        self.hBoxLayout = HBoxLayout(self)
        self.hBoxLayout.setSpacing(spacing)
        self.hBoxLayout.setContentsMargins(margins)

        if create:
            self._addSingerCardsToLayout()

    def _addSingerCardsToLayout(self):
        for card in self.singerCards:
            self.hBoxLayout.addWidget(card)
            QApplication.processEvents()

    def _removeSingerCardsFromLayout(self):
        self.hBoxLayout.removeAllWidget()
