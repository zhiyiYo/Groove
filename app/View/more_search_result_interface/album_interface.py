# coding:utf-8
from typing import List

from common.database.entity import AlbumInfo, SongInfo
from common.library import Library
from components.album_card import (AlbumBlurBackground, AlbumCardType,
                                   GridAlbumCardView)
from components.selection_mode_interface import (AlbumSelectionModeInterface,
                                                 SelectionModeBarType)
from PyQt5.QtCore import QPoint, QFile, QMargins


class AlbumInterface(AlbumSelectionModeInterface):
    """ 专辑卡界面 """

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

        self.__setQss()
        self.__connectSignalToSlot()

    def updateWindow(self, albumInfos: List[AlbumInfo]):
        """ 更新窗口 """
        self.albumCardView.updateAllAlbumCards(albumInfos)
        self.adjustScrollHeight()

    def showEvent(self, e):
        self.albumBlurBackground.hide()
        super().showEvent(e)

    def __setQss(self):
        """ 设置层叠样式 """
        f = QFile(":/qss/album_card_interface.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

    def __showBlurAlbumBackground(self, pos: QPoint, picPath: str):
        """ 显示磨砂背景 """
        pos = self.scrollWidget.mapFromGlobal(pos)
        self.albumBlurBackground.setBlurAlbum(picPath)
        self.albumBlurBackground.move(pos.x() - 28, pos.y() - 16)
        self.albumBlurBackground.show()

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.albumCardView.showBlurAlbumBackgroundSig.connect(
            self.__showBlurAlbumBackground)
        self.albumCardView.hideBlurAlbumBackgroundSig.connect(
            self.albumBlurBackground.hide)
