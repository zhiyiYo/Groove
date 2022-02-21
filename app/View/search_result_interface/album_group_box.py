# coding:utf-8
from typing import List

from common.database.entity import AlbumInfo
from common.library import Library
from components.album_card import (AlbumBlurBackground, AlbumCardType,
                                   HorizonAlbumCardView)
from PyQt5.QtCore import QMargins, QPoint

from .group_box import GroupBox


class AlbumGroupBox(GroupBox):
    """ Album card group box """

    qss = 'album_group_box.qss'

    def __init__(self, library: Library, parent=None):
        self.albumCardView = HorizonAlbumCardView(
            library,
            [],
            AlbumCardType.LOCAL_SEARCHED_ALBUM_CARD,
            margins=QMargins(35, 47, 65, 0)
        )
        super().__init__(library, self.albumCardView, parent)
        self.titleButton.setText(self.tr('Albums'))
        self.titleButton.adjustSize()

        self.albumInfos = []  # type:List[AlbumInfo]
        self.albumCards = self.albumCardView.albumCards
        self.albumBlurBackground = AlbumBlurBackground(self)
        self.albumBlurBackground.lower()
        self.__connectSignalToSlot()

    def __showBlurAlbumBackground(self, pos: QPoint, picPath: str):
        """ show blurred album background """
        v = self.horizontalScrollBar().value()
        pos = self.albumCardView.mapFromGlobal(pos) - QPoint(v, 0)
        self.albumBlurBackground.setBlurAlbum(picPath)
        self.albumBlurBackground.move(pos.x() - 31, pos.y() - 16)
        self.albumBlurBackground.show()

    def updateWindow(self, albumInfos: List[AlbumInfo]):
        """ update album group box """
        if albumInfos == self.albumInfos:
            return

        # show mask
        self.horizontalScrollBar().setValue(0)
        self.leftMask.hide()
        self.rightMask.show()

        # update album cards
        self.albumInfos = albumInfos
        self.albumCardView.updateAllAlbumCards(albumInfos)

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.albumCardView.showBlurAlbumBackgroundSig.connect(
            self.__showBlurAlbumBackground)
        self.albumCardView.hideBlurAlbumBackgroundSig.connect(
            self.albumBlurBackground.hide)
