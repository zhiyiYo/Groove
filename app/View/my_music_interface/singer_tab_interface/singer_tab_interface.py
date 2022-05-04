# coding:utf-8
from typing import List

from common.database.entity import SingerInfo
from common.library import Library
from components.selection_mode_interface import (SelectionModeBarType,
                                                 SingerSelectionModeInterface)

from .singer_card_interface import SingerCardView


class SingerTabInterface(SingerSelectionModeInterface):
    """ Singer tab interface """

    def __init__(self, library: Library, parent=None):
        super().__init__(
            library,
            SingerCardView(library),
            SelectionModeBarType.SINGER_TAB,
            parent
        )
        self.vBox.setContentsMargins(0, 0, 0, 0)

    def updateWindow(self, singerInfos: List[SingerInfo]):
        """ update window """
        self.singerCardView.updateAllSingerCards(singerInfos)
        self.adjustScrollHeight()
        self.verticalScrollBar().setValue(0)

    def scrollToLabel(self, label: str):
        """ scroll to the position specified by label """
        y = self.singerCardView.getLabelY(label)
        self.verticalScrollBar().setValue(y)
