# coding:utf-8
from typing import Dict, List

import pinyin
from common.database.entity import Playlist, SongInfo
from common.library import Library
from common.signal_bus import signalBus
from components.dialog_box.message_dialog import MessageDialog
from components.dialog_box.rename_playlist_dialog import RenamePlaylistDialog
from components.layout import GridLayout, HBoxLayout, FlowLayout
from components.layout.h_box_layout import HBoxLayout
from PyQt5.QtCore import (QMargins, QParallelAnimationGroup, QPoint, Qt,
                          pyqtSignal)
from PyQt5.QtWidgets import QApplication, QWidget

from .blur_background import BlurBackground
from .playlist_card import (PlaylistCardBase, PlaylistCardFactory,
                            PlaylistCardType)


class PlaylistCardViewBase(QWidget):
    """ 播放列表卡视图 """

    checkedNumChanged = pyqtSignal(int, bool)

    def __init__(self, library: Library, playlists: List[Playlist], cardType: PlaylistCardType, create=True, parent=None):
        """
        Parameters
        ----------
        library: Library
            歌曲库

        playlists: List[Playlist]
            播放列表信息列表

        cardType: PlaylistCardType
            播放列表卡类型

        create: bool
            是否直接创建歌曲卡

        parent:
            父级窗口
        """
        super().__init__(parent=parent)
        self.library = library
        self.playlists = playlists
        self.cardType = cardType
        self.playlistCards = []         # type:List[PlaylistCardBase]
        self.playlistCardMap = {}       # type:Dict[str, PlaylistCardBase]
        self.checkedPlaylistCards = []  # type:List[PlaylistCardBase]
        self.blurBackground = BlurBackground(self)
        self.hideCheckBoxAniGroup = QParallelAnimationGroup(self)
        self.hideCheckBoxAniGroup.finished.connect(self.__hideAllCheckBox)
        self.blurBackground.hide()

        self.sortMode = 'modifiedTime'
        self.isInSelectionMode = False

        if create:
            for platlist in self.playlists:
                self._createAlbumCard(platlist)
                QApplication.processEvents()

    def _createAlbumCard(self, platlist: Playlist):
        """ 创建一个专辑卡 """
        card = PlaylistCardFactory.create(self.cardType, platlist, self)
        self.hideCheckBoxAniGroup.addAnimation(card.hideCheckBoxAni)

        # 信号连接到槽
        self._connectCardSignalToSlot(card)

        self.playlistCards.append(card)
        self.playlistCardMap[platlist.name] = card

    def _connectCardSignalToSlot(self, card: PlaylistCardBase):
        """ 将专辑卡信号连接到槽函数 """
        card.playSig.connect(
            lambda n: signalBus.playCheckedSig.emit(self.__getPlaylistSongInfos(n)))
        card.nextToPlaySig.connect(
            lambda n: signalBus.nextToPlaySig.emit(self.__getPlaylistSongInfos(n)))
        card.showBlurBackgroundSig.connect(self.__showBlurBackground)
        card.hideBlurBackgroundSig.connect(self.blurBackground.hide)
        card.renamePlaylistSig.connect(self.showRenamePlaylistDialog)
        card.deleteCardSig.connect(self.showDeleteCardDialog)
        card.checkedStateChanged.connect(self.__onPlaylistCardCheckedStateChanged)
        card.addSongsToCustomPlaylistSig.connect(
            lambda n1, n2: signalBus.addSongsToCustomPlaylistSig.emit(n1, self.__getPlaylistSongInfos(n2)))
        card.addSongsToNewCustomPlaylistSig.connect(
            lambda n: signalBus.addSongsToNewCustomPlaylistSig.emit(self.__getPlaylistSongInfos(n)))
        card.addSongsToPlayingPlaylistSig.connect(
            lambda n: signalBus.addSongsToPlayingPlaylistSig.emit(self.__getPlaylistSongInfos(n)))

    def __showBlurBackground(self, pos: QPoint, coverPath: str):
        """ 显示磨砂背景 """
        pos = self.mapFromGlobal(pos)
        self.blurBackground.setBlurPic(coverPath, 40)
        self.blurBackground.move(pos.x() - 30, pos.y() - 20)
        self.blurBackground.show()

    def showRenamePlaylistDialog(self, name: str):
        """ 显示重命名播放列表面板 """
        w = RenamePlaylistDialog(self.library, name, self.window())
        w.renamePlaylistSig.connect(signalBus.renamePlaylistSig)
        w.exec()

    def showDeleteCardDialog(self, name: str):
        """ 显示删除一个播放列表卡对话框 """
        title = self.tr("Are you sure you want to delete this?")
        content = self.tr("If you delete") + f' "{name}" ' + \
            self.tr("it won't be on be this device anymore.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(lambda: signalBus.deletePlaylistSig.emit(name))
        w.exec()

    def __getPlaylistSongInfos(self, name: str):
        """ 获取一个播放列表的歌曲信息 """
        playlist = self.library.playlistController.getPlaylist(name)
        if not playlist:
            return []

        return playlist.songInfos

    def __hideAllCheckBox(self):
        """ 隐藏所有复选框 """
        for card in self.playlistCards:
            card.checkBox.hide()

    def renamePlaylistCard(self, old: str, new: str):
        """ 重命名播放列表卡 """
        success = self.library.playlistController.rename(old, new)
        if not success:
            return

        card = self.playlistCardMap.pop(old)
        card.playlist.name = new
        card.updateWindow(card.playlist)
        self.playlistCardMap[new] = card
        self.setSortMode(self.sortMode)

    def addSongsToPlaylistCard(self, name: str, songInfos: List[SongInfo]):
        """ 向播放列表卡添加歌曲 """
        success = self.library.playlistController.addSongs(name, songInfos)
        if not success:
            return

        card = self.playlistCardMap[name]
        index = self.playlistCards.index(card)
        playlist = self.library.playlistController.getPlaylist(name)
        self.playlists[index] = playlist
        card.updateWindow(playlist)

    def removeSongsFromPlaylistCard(self, name: str, songInfos: List[SongInfo]):
        """ 移除一个播放列表中的歌曲 """
        success = self.library.playlistController.removeSongs(name, songInfos)
        if not success:
            return

        card = self.playlistCardMap[name]
        playlist = self.library.playlistController.getPlaylist(name)
        card.updateWindow(playlist)

    def deletePlaylistCard(self, name: str):
        """ 删除一个播放列表卡 """
        success = self.library.playlistController.delete(name)
        if not success:
            return

        card = self.playlistCardMap.pop(name)
        self.layout().removeWidget(card)
        index = self.playlistCards.index(card)
        self.playlistCards.pop(index)
        self.hideCheckBoxAniGroup.takeAnimation(index)
        self.playlists.remove(card.playlist)
        card.deleteLater()

        self.adjustSize()

    def setPlaylistCards(self, playlistCards: List[PlaylistCardBase]):
        """ 设置视图中的专辑卡，不生成新的专辑卡 """
        raise NotImplementedError

    def _addCardsToLayout(self):
        """ 将所有播放列表卡加到布局中 """
        raise NotImplementedError

    def _removeCardsFromLayout(self):
        """ 将所有播放列表卡从布局中移除 """
        raise NotImplementedError

    def updateAllCards(self, playlists: List[Playlist]):
        """ 更新所有播放列表卡 """
        self._removeCardsFromLayout()

        N = len(playlists)
        N_ = len(self.playlistCards)
        if N < N_:
            for i in range(N_ - 1, N - 1, -1):
                card = self.playlistCards.pop()
                self.playlistCardMap.pop(card.name)
                self.hideCheckBoxAniGroup.takeAnimation(i)
                card.deleteLater()
        elif N > N_:
            for playlist in playlists[N_:]:
                self._createAlbumCard(playlist)
                QApplication.processEvents()

        # 更新部分专辑卡
        self.playlists = playlists
        for i in range(min(N, N_)):
            playlist = playlists[i]
            self.playlistCards[i].updateWindow(playlist)
            QApplication.processEvents()

        # 将专辑卡添加到布局中
        self._addCardsToLayout()
        self.setStyle(QApplication.style())
        self.adjustSize()

    def setSortMode(self, mode: str):
        """ 设置专辑卡的排序模式

        Parameters
        ----------
        mode: str
            排序依据，可以是 `A To Z` 或者 `modifiedTime`

        reverse: bool
            是否降序
        """
        self.sortMode = mode
        self._removeCardsFromLayout()

        if mode == 'modifiedTime':
            self.playlistCards.sort(key=lambda i: i.playlist[mode])
        else:
            self.playlistCards.sort(
                key=lambda i: pinyin.get_initial(i.playlist.name)[0].lower())

        self._removeCardsFromLayout()
        self._addCardsToLayout()

    def __onPlaylistCardCheckedStateChanged(self, card: PlaylistCardBase, isChecked: bool):
        """ 播放列表卡选中状态改变槽函数 """
        N0 = len(self.checkedPlaylistCards)

        if card not in self.checkedPlaylistCards and isChecked:
            self.checkedPlaylistCards.append(card)
        elif card in self.checkedPlaylistCards and not isChecked:
            self.checkedPlaylistCards.remove(card)
        else:
            return

        N1 = len(self.checkedPlaylistCards)

        if N0 == 0 and N1 > 0:
            self.setSelectionModeOpen(True)
        elif N1 == 0:
            self.setSelectionModeOpen(False)

        isAllChecked = N1 == len(self.playlistCards)
        self.checkedNumChanged.emit(N1, isAllChecked)

    def setSelectionModeOpen(self, isOpen: bool):
        """ 设置所有播放列表卡是否进入选择模式 """
        if self.isInSelectionMode == isOpen:
            return

        self.isInSelectionMode = isOpen
        for card in self.playlistCards:
            card.setSelectionModeOpen(isOpen)

        if not isOpen:
            self.hideCheckBoxAniGroup.start()

    def setAllChecked(self, isChecked: bool):
        """ 设置所有播放列表卡的选中状态 """
        for card in self.playlistCards:
            card.setChecked(isChecked)

    def uncheckAll(self):
        """ 取消所有已处于选中状态的播放列表卡的选中状态 """
        for card in self.checkedPlaylistCards.copy():
            card.setChecked(False)

    def adjustHeight(self):
        """ 调整高度 """
        raise NotADirectoryError


class GridPlaylistCardView(PlaylistCardViewBase):
    """ 网格布局播放列表卡视图 """

    def __init__(self, library: Library, playlists: List[Playlist], cardType: PlaylistCardType,
                 spacings=(10, 20), margins=QMargins(0, 0, 0, 0), create=True, parent=None):
        """
        Parameters
        ----------
        library: Library
            歌曲库

        playlists: List[Playlist]
            播放列表列表

        cardType: PlaylistCardType
            播放列表卡类型

        spacings: tuple
            专辑卡的水平和垂直间距

        margins: QMargins
            网格布局的外边距

        create: bool
            是否立即创建专辑卡

        parent:
            父级窗口
        """
        super().__init__(library, playlists, cardType, create, parent)
        self.column = 3
        self.flowLayout = FlowLayout(self)
        self.flowLayout.setContentsMargins(margins)
        self.flowLayout.setHorizontalSpacing(spacings[0])
        self.flowLayout.setVerticalSpacing(spacings[1])

        if create:
            self._addCardsToLayout()

    def _addCardsToLayout(self):
        """ 将所有专辑卡添加到布局 """
        for card in self.playlistCards:
            self.flowLayout.addWidget(card)
            QApplication.processEvents()

    def _removeCardsFromLayout(self):
        self.flowLayout.removeAllWidgets()

    def setPlaylistCards(self, playlistCards: List[PlaylistCardBase]):
        self.playlistCards.clear()
        self.playlistCards.extend(playlistCards)
        self.playlists = [i.playlist for i in playlistCards]
        self.playlistCardMap = {i.name: i for i in self.playlistCards}

        self.hideCheckBoxAniGroup.clear()
        for card in self.playlistCards:
            self.hideCheckBoxAniGroup.addAnimation(card.hideCheckBoxAni)
            self._connectCardSignalToSlot(card)

        self._addCardsToLayout()

    def adjustHeight(self):
        """ 调整高度 """
        h = self.flowLayout.heightForWidth(self.width())
        self.resize(self.width(), h)


class HorizonPlaylistCardView(PlaylistCardViewBase):
    """ 水平播放列表卡视图 """

    def __init__(self, library: Library, playlists: List[Playlist], cardType: PlaylistCardType,
                 spacing=20, margins=QMargins(0, 0, 0, 0), create=True, parent=None):
        """
        Parameters
        ----------
        library: Library
            歌曲库

        playlists: List[Playlist]
            播放列表列表

        cardType: PlaylistCardType
            播放列表卡类型

        spacing: int
            专辑卡的水平间距

        margins: QMargins
            网格布局的外边距

        create: bool
            是否立即创建专辑卡

        parent:
            父级窗口
        """
        super().__init__(library, playlists, cardType, create, parent)
        self.hBoxLayout = HBoxLayout(self)
        self.hBoxLayout.setSpacing(spacing)
        self.hBoxLayout.setContentsMargins(margins)

        if create:
            self._addCardsToLayout()

    def _addCardsToLayout(self):
        """ 将所有专辑卡添加到布局 """
        for card in self.playlistCards:
            self.hBoxLayout.addWidget(card)
            QApplication.processEvents()

    def _removeCardsFromLayout(self):
        """ 将所有播放列表卡从布局中移除 """
        self.hBoxLayout.removeAllWidget()
