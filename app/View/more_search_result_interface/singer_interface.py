# coding:utf-8
from typing import List

from common.database.entity import SingerInfo
from common.library import Library
from common.style_sheet import setStyleSheet
from components.selection_mode_interface import (SelectionModeBarType,
                                                 SingerSelectionModeInterface)
from components.singer_card import (GridSingerCardView, SingerBlurBackground,
                                    SingerCardType)
from PyQt5.QtCore import QFile, QMargins, QPoint


class SingerInterface(SingerSelectionModeInterface):
    """ Singer card interface """

    def __init__(self, library: Library, parent=None):
        super().__init__(
            library,
            GridSingerCardView(library, [], SingerCardType.SINGER_CARD, margins=QMargins(30, 0, 30, 0)),
            SelectionModeBarType.SINGER_TAB,
            parent
        )
        self.vBox.setContentsMargins(0, 145, 0, 120)

        self.singerBlurBackground=SingerBlurBackground(self.scrollWidget)
        self.singerBlurBackground.lower()
        self.singerBlurBackground.hide()

        setStyleSheet(self, 'singer_card_interface')
        self.__connectSignalToSlot()

    def updateWindow(self, singerInfos: List[SingerInfo]):
        """ update window """
        self.singerCardView.updateAllSingerCards(singerInfos)
        self.adjustScrollHeight()

    def showEvent(self, e):
        self.singerBlurBackground.hide()
        super().showEvent(e)

    def __showBlurSingerBackground(self, pos: QPoint, picPath: str):
        """ show blur singer background """
        pos = self.scrollWidget.mapFromGlobal(pos)
        self.singerBlurBackground.setBlurAvatar(picPath)
        self.singerBlurBackground.move(pos.x() - 28, pos.y() - 16)
        self.singerBlurBackground.show()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.singerCardView.showBlurSingerBackgroundSig.connect(
            self.__showBlurSingerBackground)
        self.singerCardView.hideBlurSingerBackgroundSig.connect(
            self.singerBlurBackground.hide)
