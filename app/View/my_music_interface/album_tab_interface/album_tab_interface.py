# coding:utf-8
from typing import List

from common.database.entity import AlbumInfo
from common.library import Library
from components.selection_mode_interface import (AlbumSelectionModeInterface,
                                                 SelectionModeBarType)

from .album_card_interface import AlbumCardView


class AlbumTabInterface(AlbumSelectionModeInterface):
    """ Album tab interface """

    def __init__(self, library: Library, parent=None):
        """
        Parameters
        ----------
        library: Library
            song library

        parent:
            parent window
        """
        super().__init__(
            library,
            AlbumCardView(library),
            SelectionModeBarType.ALBUM_TAB,
            parent
        )
        self.vBox.setContentsMargins(0, 0, 0, 0)

    def updateWindow(self, albumInfos: List[AlbumInfo]):
        """ update window """
        self.albumCardView.updateAllAlbumCards(albumInfos)
        self.adjustScrollHeight()
        self.verticalScrollBar().setValue(0)

    def setSortMode(self, sortMode: str):
        """ sort album cards

        Parameters
        ----------
        sortMode: str
            sort mode, including `Date added`, `A to Z`, `Release year` and `Artist`
        """
        self.albumCardView.setSortMode(sortMode)
        self.adjustScrollHeight()
        self.verticalScrollBar().setValue(0)

    def scrollToLabel(self, label: str):
        """ scroll to the position specified by label """
        y = self.albumCardView.getLabelY(label)
        self.verticalScrollBar().setValue(y)