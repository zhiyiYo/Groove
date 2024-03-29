# coding:utf-8
from typing import List

from common.database.entity import AlbumInfo
from common.library import Library
from common.style_sheet import setStyleSheet
from components.album_card import (AlbumBlurBackground, AlbumCardType,
                                   GridAlbumCardView)
from components.selection_mode_interface import (AlbumSelectionModeInterface,
                                                 SelectionModeBarType)
from PyQt5.QtCore import QFile, QMargins, QPoint


class AlbumInterface(AlbumSelectionModeInterface):
    """ Album card interface """

    def __init__(self, library: Library, parent=None):
        super().__init__(
            library,
            GridAlbumCardView(library, [], AlbumCardType.ALBUM_CARD, margins=QMargins(30, 0, 30, 0)),
            SelectionModeBarType.ALBUM_TAB,
            parent
        )
        self.vBox.setContentsMargins(0, 145, 0, 120)

        self.albumBlurBackground = AlbumBlurBackground(self.scrollWidget)
        self.albumBlurBackground.lower()
        self.albumBlurBackground.hide()

        setStyleSheet(self, 'album_card_interface')
        self.__connectSignalToSlot()

    def updateWindow(self, albumInfos: List[AlbumInfo]):
        """ update window """
        self.albumCardView.updateAllAlbumCards(albumInfos)
        self.adjustScrollHeight()

    def showEvent(self, e):
        self.albumBlurBackground.hide()
        super().showEvent(e)

    def __showBlurAlbumBackground(self, pos: QPoint, picPath: str):
        """ show blur album background """
        pos = self.scrollWidget.mapFromGlobal(pos)
        self.albumBlurBackground.setBlurAlbum(picPath)
        self.albumBlurBackground.move(pos.x() - 28, pos.y() - 16)
        self.albumBlurBackground.show()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.albumCardView.showBlurAlbumBackgroundSig.connect(
            self.__showBlurAlbumBackground)
        self.albumCardView.hideBlurAlbumBackgroundSig.connect(
            self.albumBlurBackground.hide)
