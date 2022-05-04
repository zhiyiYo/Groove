# coding:utf-8
from typing import List

from common.database.entity import SingerInfo
from common.library import Library
from components.singer_card import (HorizonSingerCardView,
                                    SingerBlurBackground, SingerCardType)
from PyQt5.QtCore import QMargins, QPoint

from .group_box import GroupBox


class SingerGroupBox(GroupBox):
    """ Singer card group box """

    qss = "singer_group_box.qss"

    def __init__(self, library: Library, parent=None):
        self.singerCardView = HorizonSingerCardView(
            library,
            [],
            SingerCardType.LOCAL_SEARCHED_SINGER_CARD,
            margins=QMargins(35, 47, 65, 0)
        )
        super().__init__(library, self.singerCardView, parent)
        self.titleButton.setText(self.tr('Singers'))
        self.titleButton.adjustSize()

        self.singerInfos = []  # type:List[SingerInfo]
        self.singerCards = self.singerCardView.singerCards
        self.singerBlurBackground = SingerBlurBackground(self)
        self.singerBlurBackground.lower()
        self.__connectSignalToSlot()

    def __showBlurSingerBackground(self, pos: QPoint, picPath: str):
        """ show blurred singer background """
        v = self.horizontalScrollBar().value()
        pos = self.singerCardView.mapFromGlobal(pos) - QPoint(v, 0)
        self.singerBlurBackground.setBlurAvatar(picPath)
        self.singerBlurBackground.move(pos.x() - 31, pos.y() - 16)
        self.singerBlurBackground.show()

    def updateWindow(self, singerInfos: List[SingerInfo]):
        """ update singer group box """
        if singerInfos == self.singerInfos:
            return

        # show mask
        self.horizontalScrollBar().setValue(0)
        self.leftMask.hide()
        self.rightMask.show()

        # update album cards
        self.singerInfos = singerInfos
        self.singerCardView.updateAllSingerCards(singerInfos)

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.singerCardView.showBlurSingerBackgroundSig.connect(
            self.__showBlurSingerBackground)
        self.singerCardView.hideBlurSingerBackgroundSig.connect(
            self.singerBlurBackground.hide)
