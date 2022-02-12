# coding:utf-8
from typing import List, Tuple

from common.database.entity import Playlist, SongInfo
from common.library import Library
from common.signal_bus import signalBus
from PyQt5.QtCore import QFile, QPoint, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget

from ..album_card import AlbumCardViewBase
from ..dialog_box.message_dialog import MessageDialog
from ..playlist_card import PlaylistCardViewBase
from ..song_list_widget import BasicSongListWidget
from ..widgets.menu import AddToMenu
from ..widgets.scroll_area import ScrollArea
from .bar import SelectionModeBarFactory, SelectionModeBarType


class SelectionModeViewBase(QWidget):
    """ 选择模式视图基类 """

    checkedNumChanged = pyqtSignal(int, bool)

    def setAllChecked(self, isChecked: bool):
        """ 设置所有部件的选中状态 """
        raise NotImplementedError

    def uncheckAll(self):
        """ 所有已处于选中状态的部件的选中状态 """
        raise NotImplementedError


class SelectionModeInterface(ScrollArea):
    """ 选择模式界面 """

    def __init__(self, barType: SelectionModeBarType, parent=None):
        """
        Parameters
        ----------
        barType: SelectionModeBarType
            选择模式栏类型

        parent:
            父级窗口
        """
        super().__init__(parent=parent)
        self.view = None
        self.isInSelectionMode = False
        self.scrollWidget = QWidget(self)
        self.vBox = QVBoxLayout(self.scrollWidget)
        self.selectionModeBar = SelectionModeBarFactory.create(barType, self)

        self.setWidget(self.scrollWidget)
        self.scrollWidget.setObjectName("scrollWidget")
        self.selectionModeBar.hide()
        self._setQss()

    def setView(self, view: SelectionModeViewBase):
        """ 设置视图 """
        if self.view:
            return

        self.view = view
        self.view.setParent(self.scrollWidget)
        self.vBox.addWidget(view)
        self._connectSignalToSlot()

    def resizeEvent(self, e):
        self.selectionModeBar.resize(
            self.width(), self.selectionModeBar.height())
        self.selectionModeBar.move(
            0, self.height()-self.selectionModeBar.height())

    def adjustScrollHeight(self):
        """ 调整滚动部件的高度 """
        m = self.vBox.contentsMargins()
        h = self.view.height() + m.top() + m.bottom()
        self.scrollWidget.resize(self.width(), h)

    def _setQss(self):
        """ 设置层叠样式 """
        f = QFile(":/qss/selection_mode_interface.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

    def exitSelectionMode(self):
        """ 退出选择模式 """
        self._onCancel()

    def _getCheckedSongInfos(self) -> List[SongInfo]:
        """ 获取选中的歌曲信息列表 """
        raise NotImplementedError

    def _getCheckedSinger(self) -> str:
        """ 获取选中的部件的歌手 """
        raise NotImplementedError

    def _getCheckedAlbum(self) -> Tuple[str, str]:
        """ 获取选中的专辑 """
        raise NotImplementedError

    def _onCheckedNumChanged(self, n: int, isAllChecked: bool):
        """ 选中的部件数量改变槽函数 """
        if n > 0 and not self.isInSelectionMode:
            self.isInSelectionMode = True
            signalBus.selectionModeStateChanged.emit(True)
        elif n == 0 and self.isInSelectionMode:
            self.isInSelectionMode = False
            signalBus.selectionModeStateChanged.emit(False)

        self.selectionModeBar.setVisible(self.isInSelectionMode)
        self.selectionModeBar.setPartButtonHidden(n > 1)
        self.selectionModeBar.checkAllButton.setCheckedState(not isAllChecked)
        self.selectionModeBar.move(
            0, self.height()-self.selectionModeBar.height())

    def _onCancel(self):
        """ 选择模式栏取消信号槽函数 """
        self.view.uncheckAll()
        self.selectionModeBar.checkAllButton.setCheckedState(True)

    def _onPlay(self):
        """ 选择模式栏播放信号槽函数 """
        signalBus.playCheckedSig.emit(self._getCheckedSongInfos())

    def _onNextToPlay(self):
        """ 选择模式栏下一首播放信号槽函数 """
        signalBus.nextToPlaySig.emit(self._getCheckedSongInfos())

    def _onAddTo(self):
        """ 选择模式栏添加到信号槽函数 """
        menu = AddToMenu(parent=self)

        # 获取选中的歌曲信息列表
        for act in menu.action_list:
            act.triggered.connect(self.exitSelectionMode)

        songInfos = self._getCheckedSongInfos()
        menu.playingAct.triggered.connect(
            lambda: signalBus.addSongsToPlayingPlaylistSig.emit(songInfos))
        menu.addSongsToPlaylistSig.connect(
            lambda name: signalBus.addSongsToCustomPlaylistSig.emit(name, songInfos))
        menu.newPlaylistAct.triggered.connect(
            lambda: signalBus.addSongsToNewCustomPlaylistSig.emit(songInfos))

        pos = self.selectionModeBar.mapToGlobal(
            QPoint(self.selectionModeBar.addToButton.x(), 0))
        x = pos.x() + self.selectionModeBar.addToButton.width() + 5
        y = pos.y() + int(self.selectionModeBar.addToButton.height() /
                          2 - (13 + 38 * menu.actionCount()) / 2)
        menu.exec(QPoint(x, y))

    def _onSinger(self):
        """ 选择模式栏歌手信号槽函数 """
        singer = self._getCheckedSinger()
        self.exitSelectionMode()
        signalBus.switchToSingerInterfaceSig.emit(singer)

    def _onAlbum(self):
        """ 选择模式栏专辑信号槽函数 """
        singer, album = self._getCheckedAlbum()
        self.exitSelectionMode()
        signalBus.switchToAlbumInterfaceSig.emit(singer, album)

    def _onProperty(self):
        """ 选择模式栏属性信号槽函数 """
        raise NotImplementedError

    def _onEditInfo(self):
        """ 选择模式栏编辑信号槽函数 """
        raise NotImplementedError

    def _onPinToStart(self):
        """ 选择模式栏固定到开始菜单信号槽函数 """
        raise NotImplementedError

    def _onRename(self):
        """ 选择模式栏重命名信号槽函数 """
        raise NotImplementedError

    def _onMoveUp(self):
        """ 选择模式栏向上移动信号槽函数 """
        raise NotImplementedError

    def _onMoveDown(self):
        """ 选择模式栏向下移动信号槽函数 """
        raise NotImplementedError

    def _onDelete(self):
        """ 选择模式栏删除信号槽函数 """
        raise NotImplementedError

    def _onCheckAll(self, isCheck: bool):
        """ 选择模式栏全选/取消全选信号槽函数 """
        self.view.setAllChecked(isCheck)

    def _connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.view.checkedNumChanged.connect(self._onCheckedNumChanged)
        self.selectionModeBar.cancelSig.connect(self._onCancel)
        self.selectionModeBar.playSig.connect(self._onPlay)
        self.selectionModeBar.nextToPlaySig.connect(self._onNextToPlay)
        self.selectionModeBar.addToSig.connect(self._onAddTo)
        self.selectionModeBar.singerSig.connect(self._onSinger)
        self.selectionModeBar.albumSig.connect(self._onAlbum)
        self.selectionModeBar.propertySig.connect(self._onProperty)
        self.selectionModeBar.editInfoSig.connect(self._onEditInfo)
        self.selectionModeBar.pinToStartSig.connect(self._onPinToStart)
        self.selectionModeBar.renameSig.connect(self._onRename)
        self.selectionModeBar.moveUpSig.connect(self._onMoveUp)
        self.selectionModeBar.moveDownSig.connect(self._onMoveDown)
        self.selectionModeBar.deleteSig.connect(self._onDelete)
        self.selectionModeBar.checkAllSig.connect(self._onCheckAll)


class SongSelectionModeInterface(SelectionModeInterface):
    """ 歌曲选择模式界面 """

    def __init__(self, songListWidget: BasicSongListWidget, barType: SelectionModeBarType, parent=None):
        """
        Parameters
        ----------
        songListWidget: BasicSongListWidget
            歌曲列表控件

        barType: SelectionModeBarType
            选择模式栏类型

        parent:
            父级窗口
        """
        super().__init__(barType, parent)
        self.songListWidget = songListWidget
        self.songListWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setView(songListWidget)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.songListWidget.resize(self.width(), self.songListWidget.height())
        self.adjustScrollHeight()

    def _getCheckedSongInfos(self) -> List[SongInfo]:
        return [i.songInfo for i in self.songListWidget.checkedSongCards]

    def _getCheckedAlbum(self) -> Tuple[str, str]:
        songCard = self.songListWidget.checkedSongCards[0]
        return songCard.singer, songCard.album

    def _getCheckedSinger(self) -> str:
        return self.songListWidget.checkedSongCards[0].singer

    def _onProperty(self):
        songInfo = self._getCheckedSongInfos()[0]
        self.exitSelectionMode()
        self.songListWidget.showSongPropertyDialog(songInfo)

    def _onEditInfo(self):
        songInfo = self._getCheckedSongInfos()[0]
        self.exitSelectionMode()
        self.songListWidget.showSongInfoEditDialog(songInfo)

    def _onDelete(self):
        if len(self.songListWidget.checkedSongCards) > 1:
            title = self.tr("Are you sure you want to delete these?")
            content = self.tr(
                "If you delete these songs, they won't be on be this device anymore.")
        else:
            name = self.songListWidget.checkedSongCards[0].songName
            title = self.tr("Are you sure you want to delete this?")
            content = self.tr("If you delete") + f' "{name}" ' + \
                self.tr("it won't be on be this device anymore.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(self.__onDeleteConfirmed)
        w.exec()

    def __onDeleteConfirmed(self):
        """ 确定删除槽函数 """
        songPaths = [i.songPath for i in self.songListWidget.checkedSongCards]

        for songCard in self.songListWidget.checkedSongCards.copy():
            songCard.setChecked(False)
            self.songListWidget.removeSongCard(songCard.itemIndex)

        signalBus.removeSongSig.emit(songPaths)


class AlbumSelectionModeInterface(SelectionModeInterface):
    """ 专辑选择模式界面 """

    def __init__(self, library: Library, view: AlbumCardViewBase, barType: SelectionModeBarType, parent=None):
        """
        Parameters
        ----------
        library: Library
            歌曲库

        view: AlbumCardViewBase
            专辑卡视图

        barType: SelectionModeBarType
            选择模式栏类型

        parent:
            父级窗口
        """
        super().__init__(barType, parent)
        self.library = library
        self.albumCardView = view
        self.vBox.setSizeConstraint(QVBoxLayout.SetFixedSize)
        self.setView(view)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def adjustScrollHeight(self):
        """ 调整滚动部件的高度 """
        self.scrollWidget.adjustSize()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        m = self.vBox.contentsMargins()
        w = self.width() - m.left() - m.right()
        self.albumCardView.setFixedWidth(w)
        self.albumCardView.adjustHeight()
        self.adjustScrollHeight()

    def _getCheckedSongInfos(self) -> List[SongInfo]:
        singers = []
        albums = []
        for albumCard in self.albumCardView.checkedAlbumCards:
            singers.append(albumCard.singer)
            albums.append(albumCard.album)

        songInfos = self.library.songInfoController.getSongInfosBySingerAlbum(
            singers, albums)

        return songInfos

    def _getCheckedAlbum(self) -> Tuple[str, str]:
        card = self.albumCardView.checkedAlbumCards[0]
        return card.singer, card.album

    def _getCheckedSinger(self) -> str:
        return self.albumCardView.checkedAlbumCards[0].singer

    def _onEditInfo(self):
        singer, album = self._getCheckedAlbum()
        self.exitSelectionMode()
        self.albumCardView.showAlbumInfoEditDialog(singer, album)

    def _onDelete(self):
        if len(self.albumCardView.checkedAlbumCards) > 1:
            title = self.tr("Are you sure you want to delete these?")
            content = self.tr(
                "If you delete these albums, they won't be on be this device anymore.")
        else:
            name = self.albumCardView.checkedAlbumCards[0].album
            title = self.tr("Are you sure you want to delete this?")
            content = self.tr("If you delete") + f' "{name}" ' + \
                self.tr("it won't be on be this device anymore.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(self.__onDeleteConfirmed)
        w.exec()

    def __onDeleteConfirmed(self):
        """ 确认删除槽函数 """
        songInfos = self._getCheckedSongInfos()
        songPaths = [i.file for i in songInfos]
        self.exitSelectionMode()
        signalBus.removeSongSig.emit(songPaths)


class PlaylistSelectionModeInterface(SelectionModeInterface):
    """ 播放列表选择模式界面 """

    def __init__(self, library: Library, view: PlaylistCardViewBase, barType: SelectionModeBarType, parent=None):
        """
        Parameters
        ----------
        library: Library
            歌曲库

        view: PlaylistCardViewBase
            播放列表卡视图

        barType: SelectionModeBarType
            选择模式栏类型

        parent:
            父级窗口
        """
        super().__init__(barType, parent)
        self.library = library
        self.playlistCardView = view
        self.playlists = library.playlists
        self.playlistCards = self.playlistCardView.playlistCards
        self.vBox.setSizeConstraint(QVBoxLayout.SetFixedSize)
        self.setView(view)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def adjustScrollHeight(self):
        self.scrollWidget.adjustSize()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        m = self.vBox.contentsMargins()
        w = self.width() - m.left() - m.right()
        self.playlistCardView.setFixedWidth(w)
        self.playlistCardView.adjustHeight()
        self.adjustScrollHeight()

    def _getCheckedSongInfos(self) -> List[SongInfo]:
        names = [i.name for i in self.playlistCardView.checkedPlaylistCards]
        songInfos = []
        for playlist in self.library.playlistController.getPlaylists(names):
            songInfos.extend(playlist.songInfos)

        return songInfos

    def _onRename(self):
        card = self.playlistCardView.checkedPlaylistCards[0]
        self.exitSelectionMode()
        self.playlistCardView.showRenamePlaylistDialog(card.playlist.name)

    def _onDelete(self):
        if len(self.playlistCardView.checkedPlaylistCards) == 1:
            card = self.playlistCardView.checkedPlaylistCards[0]
            self.exitSelectionMode()
            self.playlistCardView.showDeleteCardDialog(card.name)
        else:
            title = self.tr("Are you sure you want to delete these?")
            content = self.tr(
                "If you delete these playlists, they won't be on be this device anymore.")
            names = [i.name for i in self.playlistCardView.checkedPlaylistCards]

            self.exitSelectionMode()

            # 显示删除对话框
            w = MessageDialog(title, content, self.window())
            w.yesSignal.connect(lambda: self.__onDeleteConfirmed(names))
            w.exec()

    def __onDeleteConfirmed(self, names: List[str]):
        """ 删除多个播放列表卡 """
        for name in names:
            signalBus.deletePlaylistSig.emit(name)

    def addPlaylistCard(self, name: str, playlist: Playlist):
        """ 添加一个播放列表卡 """
        self.playlists.append(playlist)
        self.playlistCardView.updateAllCards(self.playlists)

    def renamePlaylist(self, old: str, new: str):
        """ 重命名播放列表 """
        self.playlistCardView.renamePlaylistCard(old, new)

    def deletePlaylistCard(self, name: str):
        """ 删除一个播放列表卡 """
        self.playlistCardView.deletePlaylistCard(name)

    def addSongsToPlaylist(self, name: str, songInfos: List[SongInfo]) -> Playlist:
        """ 将歌曲添加到播放列表 """
        if not songInfos:
            return

        self.playlistCardView.addSongsToPlaylistCard(name, songInfos)

    def removeSongsFromPlaylist(self, name: str, songInfos: List[SongInfo]):
        """ 移除一个播放列表中的歌曲 """
        self.playlistCardView.removeSongsFromPlaylistCard(name, songInfos)
