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

    checkedNumChanged = pyqtSignal(int, bool)                # 选中专辑卡数量改变
    checkedStateChanged = pyqtSignal(SingerCardBase, bool)   # 专辑卡选中状态改变
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
            whether to create album card

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

    
