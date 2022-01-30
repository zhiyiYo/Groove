# coding:utf-8
from typing import List, Dict

import pinyin
from common.database.entity import Playlist, SongInfo
from common.library import Library
from components.dialog_box.message_dialog import MessageDialog
from components.dialog_box.rename_playlist_dialog import RenamePlaylistDialog
from components.layout.grid_layout import GridLayout
from PyQt5.QtCore import (QMargins, QParallelAnimationGroup, QPoint, Qt,
                          pyqtSignal, QDateTime)
from PyQt5.QtWidgets import QApplication, QWidget

from .blur_background import BlurBackground
from .playlist_card import (PlaylistCardBase, PlaylistCardFactory,
                            PlaylistCardType)


class PlaylistCardViewBase(QWidget):
    """ 播放列表卡视图 """

    playSig = pyqtSignal(list)
    nextToPlaySig = pyqtSignal(list)
    hideBlurBackgroundSig = pyqtSignal()
    renamePlaylistSig = pyqtSignal(str, str)
    deletePlaylistSig = pyqtSignal(str)
    checkedStateChanged = pyqtSignal(QWidget, bool)
    switchToPlaylistInterfaceSig = pyqtSignal(str)
    showBlurBackgroundSig = pyqtSignal(QPoint, str)
    addSongsToPlayingPlaylistSig = pyqtSignal(list)      # 添加歌曲到正在播放
    addSongsToNewCustomPlaylistSig = pyqtSignal(list)    # 添加歌曲到新的自定义的播放列表中
    addSongsToCustomPlaylistSig = pyqtSignal(str, list)  # 添加歌曲到自定义的播放列表中

    def __init__(self, library: Library, playlists: List[Playlist], cardType: PlaylistCardType, create=True, parent=None):
        """
        Parameters
        ----------
        library: Library
            歌曲库

        playlists: List[Playlist]
            专辑信息列表

        cardType: PlaylistCardType
            专辑卡类型

        create: bool
            是否直接创建歌曲卡

        parent:
            父级窗口
        """
        super().__init__(parent=parent)
        self.library = library
        self.playlists = playlists
        self.cardType = cardType
        self.playlistCards = []     # type:List[PlaylistCardBase]
        self.playlistCardMap = {}   # type:Dict[str, PlaylistCardBase]
        self.blurBackground = BlurBackground(self)
        self.hideCheckBoxAniGroup = QParallelAnimationGroup(self)
        self.hideCheckBoxAniGroup.finished.connect(self.__hideAllCheckBox)
        self.blurBackground.hide()

        self.sortMode = 'modifiedTime'

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
            lambda n: self.playSig.emit(self.__getPlaylistSongInfos(n)))
        card.nextToPlaySig.connect(
            lambda n: self.nextToPlaySig.emit(self.__getPlaylistSongInfos(n)))
        card.showBlurBackgroundSig.connect(self.__showBlurBackground)
        card.hideBlurBackgroundSig.connect(self.blurBackground.hide)
        card.renamePlaylistSig.connect(self.showRenamePlaylistDialog)
        card.deleteCardSig.connect(self.showDeleteCardDialog)
        card.checkedStateChanged.connect(self.checkedStateChanged)
        card.switchToPlaylistInterfaceSig.connect(
            self.switchToPlaylistInterfaceSig)
        card.addSongsToCustomPlaylistSig.connect(
            lambda n1, n2: self.addSongsToCustomPlaylistSig.emit(n1, self.__getPlaylistSongInfos(n2)))
        card.addSongsToNewCustomPlaylistSig.connect(
            lambda n: self.addSongsToNewCustomPlaylistSig.emit(self.__getPlaylistSongInfos(n)))
        card.addSongsToPlayingPlaylistSig.connect(
            lambda n: self.addSongsToPlayingPlaylistSig.emit(self.__getPlaylistSongInfos(n)))

    def __showBlurBackground(self, pos: QPoint, coverPath: str):
        """ 显示磨砂背景 """
        pos = self.mapFromGlobal(pos)
        self.blurBackground.setBlurPic(coverPath, 40)
        self.blurBackground.move(pos.x() - 30, pos.y() - 20)
        self.blurBackground.show()

    def showRenamePlaylistDialog(self, name: str):
        """ 显示重命名播放列表面板 """
        w = RenamePlaylistDialog(self.library, name, self.window())
        w.renamePlaylistSig.connect(self.renamePlaylistSig)
        w.exec()

    def showDeleteCardDialog(self, name: str):
        """ 显示删除一个播放列表卡对话框 """
        title = self.tr("Are you sure you want to delete this?")
        content = self.tr("If you delete") + f' "{name}" ' + \
            self.tr("it won't be on be this device anymore.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(lambda: self.deletePlaylistCard(name))
        w.yesSignal.connect(lambda: self.deletePlaylistSig.emit(name))
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
        playlist = card.playlist

        playlist.singer = playlist.singer or songInfos[0].singer
        playlist.album = playlist.album or songInfos[0].album
        playlist.count = playlist.count + len(songInfos)
        playlist.modifiedTime = QDateTime.currentDateTime().toSecsSinceEpoch()
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
                self.layout().removeWidget(card)
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
                key=lambda i: pinyin.get_initial(i.playlist.name)[0].lower(), reverse=True)

        self._removeCardsFromLayout()
        self._addCardsToLayout()


class GridPlaylistCardView(PlaylistCardViewBase):
    """ 网格布局播放列表卡视图 """

    def __init__(self, library: Library, playlists: List[Playlist], cardType: PlaylistCardType,
                 spacings=(10, 20), margins=QMargins(0, 0, 0, 0), create=True, parent=None):
        """
        Parameters
        ----------
        library: Library
            歌曲库

        playlists: List[AlbumInfo]
            专辑信息列表

        cardType: AlbumCardType
            专辑卡类型

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
        self.gridLayout = GridLayout()
        self.setLayout(self.gridLayout)
        self.gridLayout.setContentsMargins(margins)
        self.gridLayout.setHorizontalSpacing(spacings[0])
        self.gridLayout.setVerticalSpacing(spacings[1])
        self.gridLayout.setAlignment(Qt.AlignLeft)

        if create:
            self._addCardsToLayout()

    def _addCardsToLayout(self):
        """ 将所有专辑卡添加到布局 """
        for i, card in enumerate(self.playlistCards):
            row = i//self.column
            column = i-row*self.column
            self.gridLayout.addWidget(card, row, column)
            QApplication.processEvents()

    def _removeCardsFromLayout(self):
        self.gridLayout.removeAllWidgets()

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

    def resizeEvent(self, e):
        column = 1 if self.width() <= 641 else (self.width()-641)//308+2
        if self.column == column:
            return

        self.column = column
        self.gridLayout.updateColumnNum(column, 298, 288)