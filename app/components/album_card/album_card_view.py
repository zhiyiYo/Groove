# coding:utf-8
from typing import List

from common.database.entity import AlbumInfo
from common.library import Library
from common.signal_bus import signalBus
from common.thread.save_album_info_thread import SaveAlbumInfoThread
from components.dialog_box.album_info_edit_dialog import AlbumInfoEditDialog
from components.dialog_box.message_dialog import MessageDialog
from components.layout import FlowLayout, HBoxLayout
from components.widgets.label import ClickableLabel
from PyQt5.QtCore import QMargins, QParallelAnimationGroup, QPoint, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget

from .album_card import AlbumCardBase, AlbumCardFactory, AlbumCardType


class AlbumCardViewBase(QWidget):
    """ Album card view base class """

    checkedNumChanged = pyqtSignal(int, bool)              # 选中专辑卡数量改变
    checkedStateChanged = pyqtSignal(AlbumCardBase, bool)  # 专辑卡选中状态改变
    showBlurAlbumBackgroundSig = pyqtSignal(QPoint, str)   # 显示磨砂背景
    hideBlurAlbumBackgroundSig = pyqtSignal()              # 隐藏磨砂背景

    def __init__(self, library: Library, albumInfos: List[AlbumInfo], cardType: AlbumCardType, create=True, isGrouped=False, parent=None):
        """
        Parameters
        ----------
        library: Library
            song library

        albumInfos: List[AlbumInfo]
            album information list

        cardType: AlbumCardType
            album card type

        create: bool
            whether to create album card

        isGrouped: bool
            whether the view is grouped

        parent:
            parent window
        """
        super().__init__(parent=parent)
        self.library = library
        self.albumInfos = albumInfos
        self.isGrouped = isGrouped
        self.cardType = cardType
        self.albumCards = []  # type:List[AlbumCardBase]
        self.checkedAlbumCards = []  # type:List[AlbumCardBase]
        self.isInSelectionMode = False
        self.hideCheckBoxAniGroup = QParallelAnimationGroup(self)
        self.hideCheckBoxAniGroup.finished.connect(self.__hideAllCheckBox)

        if create:
            for albumInfo in self.albumInfos:
                self._createAlbumCard(albumInfo)
                QApplication.processEvents()

    def _createAlbumCard(self, albumInfo: AlbumInfo):
        """ create an alum card """
        card = AlbumCardFactory.create(self.cardType, albumInfo, self)
        self.hideCheckBoxAniGroup.addAnimation(card.hideCheckBoxAni)

        self._connectCardSignalToSlot(card)

        self.albumCards.append(card)

    def _connectCardSignalToSlot(self, card: AlbumCardBase):
        """ connect album card signal to slot """
        card.deleteCardSig.connect(self.__showDeleteCardDialog)
        card.showAlbumInfoEditDialogSig.connect(self.showAlbumInfoEditDialog)
        card.nextPlaySignal.connect(
            lambda s, a: signalBus.nextToPlaySig.emit(self.getAlbumSongInfos(s, a)))
        card.addToPlayingSignal.connect(
            lambda s, a: signalBus.addSongsToPlayingPlaylistSig.emit(self.getAlbumSongInfos(s, a)))
        card.addAlbumToCustomPlaylistSig.connect(
            lambda n, s, a: signalBus.addSongsToCustomPlaylistSig.emit(n, self.getAlbumSongInfos(s, a)))
        card.addAlbumToNewCustomPlaylistSig.connect(
            lambda s, a: signalBus.addSongsToNewCustomPlaylistSig.emit(self.getAlbumSongInfos(s, a)))
        card.checkedStateChanged.connect(self.__onAlbumCardCheckedStateChanged)
        card.showBlurAlbumBackgroundSig.connect(
            self.showBlurAlbumBackgroundSig)
        card.hideBlurAlbumBackgroundSig.connect(
            self.hideBlurAlbumBackgroundSig)

    def getAlbumSongInfos(self, singer: str, album: str):
        """ get song information of an album """
        albumInfo = self.library.albumInfoController.getAlbumInfo(
            singer, album)
        if not albumInfo:
            return []

        return albumInfo.songInfos

    def __showDeleteCardDialog(self, singer: str, album: str):
        """ show delete album card dialog box """
        title = self.tr("Are you sure you want to delete this?")
        content = self.tr("If you delete") + f' "{album}" ' + \
            self.tr("it won't be on be this device anymore.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(lambda: signalBus.removeSongSig.emit(
            [i.file for i in self.getAlbumSongInfos(singer, album)]))
        w.exec_()

    def showAlbumInfoEditDialog(self, singer: str, album: str):
        """ show album information edit dialog box """
        albumInfo = self.library.albumInfoController.getAlbumInfo(
            singer, album)
        if not albumInfo:
            return

        # create thread and dialog box
        thread = SaveAlbumInfoThread(self)
        w = AlbumInfoEditDialog(albumInfo, self.window())

        # connect signal to slot
        w.saveInfoSig.connect(thread.setAlbumInfo)
        w.saveInfoSig.connect(thread.start)
        thread.saveFinishedSignal.connect(w.onSaveComplete)
        thread.saveFinishedSignal.connect(self.__onSaveAlbumInfoFinished)

        # show dialog box
        w.setStyle(QApplication.style())
        w.exec_()

    def __hideAllCheckBox(self):
        """ hide check box of album cards """
        for albumCard in self.albumCards:
            albumCard.checkBox.hide()

    def __onSaveAlbumInfoFinished(self, oldAlbumInfo: AlbumInfo, newAlbumInfo: AlbumInfo, coverPath: str):
        """ save album information """
        self.sender().quit()
        self.sender().wait()
        self.sender().deleteLater()
        signalBus.editAlbumInfoSig.emit(oldAlbumInfo, newAlbumInfo, coverPath)

    def setAlbumCards(self, albumCards: List[AlbumCardBase]):
        """ set album cards in the view and do not generate new cards """
        raise NotImplementedError

    def _addAlbumCardsToLayout(self):
        """ add all album cards to layout """
        raise NotImplementedError

    def _removeAlbumCardsFromLayout(self):
        """ remove all album cards from layout """
        raise NotImplementedError

    def updateAllAlbumCards(self, albumInfos: List[AlbumInfo]):
        """ update all album cards """
        self._removeAlbumCardsFromLayout()

        N = len(albumInfos)
        N_ = len(self.albumCards)
        if N < N_:
            for i in range(N_ - 1, N - 1, -1):
                albumCard = self.albumCards.pop()
                self.hideCheckBoxAniGroup.takeAnimation(i)
                albumCard.deleteLater()
        elif N > N_:
            for albumInfo in albumInfos[N_:]:
                self._createAlbumCard(albumInfo)
                QApplication.processEvents()

        # update part of album cards
        self.albumInfos = albumInfos
        for i in range(min(N, N_)):
            albumInfo = albumInfos[i]
            self.albumCards[i].updateWindow(albumInfo)
            QApplication.processEvents()

        self._addAlbumCardsToLayout()
        self.setStyle(QApplication.style())
        self.adjustSize()

    def __onAlbumCardCheckedStateChanged(self, albumCard: AlbumCardBase, isChecked: bool):
        """ album card checked state changed slot """
        N0 = len(self.checkedAlbumCards)

        if albumCard not in self.checkedAlbumCards and isChecked:
            self.checkedAlbumCards.append(albumCard)
        elif albumCard in self.checkedAlbumCards and not isChecked:
            self.checkedAlbumCards.remove(albumCard)
        else:
            return

        N1 = len(self.checkedAlbumCards)

        if N0 == 0 and N1 > 0:
            self.setSelectionModeOpen(True)
        elif N1 == 0 and not self.isGrouped:
            self.setSelectionModeOpen(False)

        isAllChecked = N1 == len(self.albumCards)
        self.checkedNumChanged.emit(N1, isAllChecked)

        if self.isGrouped:
            self.checkedStateChanged.emit(albumCard, isChecked)

    def setSelectionModeOpen(self, isOpen: bool):
        """ set whether to open selection mode """
        if self.isInSelectionMode == isOpen:
            return

        self.isInSelectionMode = isOpen
        for albumCard in self.albumCards:
            albumCard.setSelectionModeOpen(isOpen)

        if not isOpen and not self.isGrouped:
            self.hideCheckBoxAniGroup.start()

    def setAllChecked(self, isChecked: bool):
        """ set the checked state of all album cards """
        for albumCard in self.albumCards:
            albumCard.setChecked(isChecked)

    def uncheckAll(self):
        """ uncheck all album cards """
        for albumCard in self.checkedAlbumCards.copy():
            albumCard.setChecked(False)

    def adjustHeight(self):
        """ adjust view height """
        raise NotImplementedError


class GridAlbumCardView(AlbumCardViewBase):
    """ Album card view with grid layout """

    titleClicked = pyqtSignal()

    def __init__(self, library: Library, albumInfos: List[AlbumInfo], cardType: AlbumCardType,
                 spacings=(10, 20), margins=QMargins(0, 0, 0, 0), title: str = None, create=True,
                 isGrouped=False, parent=None):
        """
        Parameters
        ----------
        library: Library
            song library

        albumInfos: List[AlbumInfo]
            album information list

        cardType: AlbumCardType
            album card type

        spacings: tuple
            horizontal and vertical spacing between album cards

        margins: QMargins
            margins of grid layout

        title: str
            title of view

        create: bool
            whether to create album card

        isGrouped: bool
            whether the view is grouped

        parent:
            parent window
        """
        super().__init__(library, albumInfos, cardType, create, isGrouped, parent)
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
            self._addAlbumCardsToLayout()

    def _addAlbumCardsToLayout(self):
        for card in self.albumCards:
            self.flowLayout.addWidget(card)
            QApplication.processEvents()

    def _removeAlbumCardsFromLayout(self):
        self.flowLayout.removeAllWidgets()

    def setAlbumCards(self, albumCards: List[AlbumCardBase]):
        self.albumCards = albumCards
        self.albumInfos = [i.albumInfo for i in albumCards]

        self.hideCheckBoxAniGroup.clear()
        for card in self.albumCards:
            self.hideCheckBoxAniGroup.addAnimation(card.hideCheckBoxAni)
            self._connectCardSignalToSlot(card)

        self._addAlbumCardsToLayout()

    def adjustHeight(self):
        h = self.flowLayout.heightForWidth(self.width())
        self.resize(self.width(), h)


class HorizonAlbumCardView(AlbumCardViewBase):
    """ Album card view with horizontal box layout """

    def __init__(self, library: Library, albumInfos: List[AlbumInfo], cardType: AlbumCardType,
                 spacing=20, margins=QMargins(0, 0, 0, 0), create=True, isGrouped=False, parent=None):
        """
        Parameters
        ----------
        library: Library
            song library

        albumInfos: List[AlbumInfo]
            album information list

        cardType: AlbumCardType
            album card type

        spacings: tuple
            horizontal spacing between album cards

        margins: QMargins
            margins of grid layout

        create: bool
            whether to create album card

        isGrouped: bool
            whether the view is grouped

        parent:
            parent window
        """
        super().__init__(library, albumInfos, cardType, create, isGrouped, parent)
        self.hBoxLayout = HBoxLayout(self)
        self.hBoxLayout.setSpacing(spacing)
        self.hBoxLayout.setContentsMargins(margins)

        if create:
            self._addAlbumCardsToLayout()

    def _addAlbumCardsToLayout(self):
        for card in self.albumCards:
            self.hBoxLayout.addWidget(card)
            QApplication.processEvents()

    def _removeAlbumCardsFromLayout(self):
        self.hBoxLayout.removeAllWidget()
