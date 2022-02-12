# coding:utf-8
from typing import List

from common.database.entity import AlbumInfo
from common.library import Library
from components.selection_mode_interface import (AlbumSelectionModeInterface,
                                                 SelectionModeBarType)

from .album_card_interface import AlbumCardView


class AlbumTabInterface(AlbumSelectionModeInterface):
    """ 专辑标签界面 """

    def __init__(self, library: Library, parent=None):
        """
        Parameters
        ----------
        library: Library
            歌曲库

        parent:
            父级窗口
        """
        super().__init__(
            library,
            AlbumCardView(library),
            SelectionModeBarType.ALBUM_TAB,
            parent
        )
        self.vBox.setContentsMargins(0, 0, 0, 0)

    def updateWindow(self, albumInfos: List[AlbumInfo]):
        """ 更新窗口 """
        self.albumCardView.updateAllAlbumCards(albumInfos)
        self.adjustScrollHeight()
        self.verticalScrollBar().setValue(0)

    def setSortMode(self, sortMode: str):
        """ 排序专辑卡

        Parameters
        ----------
        sortMode: str
            排序方式，有`Date added`、`A to Z`、`Release year` 和 `Artist` 四种
        """
        self.albumCardView.setSortMode(sortMode)
        self.adjustScrollHeight()
        self.verticalScrollBar().setValue(0)

    def scrollToLabel(self, label: str):
        """ 滚动到label指定的位置 """
        y = self.albumCardView.getLabelY(label)
        self.verticalScrollBar().setValue(y)