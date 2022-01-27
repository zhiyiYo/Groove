# coding:utf-8
from copy import deepcopy

from common.database.entity import AlbumInfo, SongInfo
from common.os_utils import getCoverPath
from common.thread.save_album_info_thread import SaveAlbumInfoThread
from components.dialog_box.album_info_edit_dialog import AlbumInfoEditDialog
from components.widgets.menu import AddToMenu
from components.widgets.scroll_area import ScrollArea
from PyQt5.QtCore import QFile, QPoint, Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget

from .album_info_bar import AlbumInfoBar
from .selection_mode_bar import SelectionModeBar
from .song_list_widget import SongListWidget


class AlbumInterface(ScrollArea):
    """ 专辑界面 """

    songCardPlaySig = pyqtSignal(int)                    # 在当前播放列表中播放这首歌
    playAlbumSignal = pyqtSignal(str, str)               # 播放整张专辑
    playOneSongCardSig = pyqtSignal(SongInfo)            # 将播放列表重置为一首歌
    playCheckedCardsSig = pyqtSignal(list)               # 播放选中的歌曲卡
    nextToPlayOneSongSig = pyqtSignal(SongInfo)          # 下一首播放一首歌
    addOneSongToPlayingSig = pyqtSignal(SongInfo)        # 添加一首歌到正在播放
    editSongInfoSignal = pyqtSignal(SongInfo, SongInfo)  # 编辑歌曲信息信号
    selectionModeStateChanged = pyqtSignal(bool)         # 进入/退出 选择模式
    switchToSingerInterfaceSig = pyqtSignal(str)         # 切换到歌手界面
    nextToPlayCheckedCardsSig = pyqtSignal(list)         # 将选中的多首歌添加到下一首播放
    addSongsToPlayingPlaylistSig = pyqtSignal(list)      # 添加歌曲到正在播放
    addSongsToNewCustomPlaylistSig = pyqtSignal(list)    # 添加歌曲到新建播放列表
    addSongsToCustomPlaylistSig = pyqtSignal(str, list)  # 添加歌曲到自定义的播放列表中
    editAlbumInfoSignal = pyqtSignal(AlbumInfo, AlbumInfo, str)  # 编辑专辑信息

    def __init__(self, albumInfo: AlbumInfo = None, parent=None):
        """
        Parameters
        ----------
        albumInfo: AlbumInfo
            专辑信息

        parent:
            父级窗口
        """
        super().__init__(parent)
        self.__getInfo(albumInfo)
        self.scrollWidget = QWidget(self)
        self.vBox = QVBoxLayout(self.scrollWidget)
        self.songListWidget = SongListWidget(self.songInfos, self)
        self.albumInfoBar = AlbumInfoBar(self.albumInfo, self)
        self.selectionModeBar = SelectionModeBar(self)
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1230, 900)
        self.setWidget(self.scrollWidget)
        self.selectionModeBar.hide()
        self.songListWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 设置布局
        self.vBox.setContentsMargins(0, 430, 0, 0)
        self.vBox.addWidget(self.songListWidget)
        # 设置层叠样式
        self.__setQss()
        # 信号连接到槽
        self.__connectSignalToSlot()

    def __getInfo(self, albumInfo: AlbumInfo):
        """ 获取信息 """
        self.albumInfo = albumInfo if albumInfo else AlbumInfo()
        self.songInfos = self.albumInfo.songInfos
        self.album = self.albumInfo.album
        self.singer = self.albumInfo.singer
        self.year = self.albumInfo.year
        self.genre = self.albumInfo.genre

    def __setQss(self):
        """ 设置层叠样式 """
        self.setObjectName("albumInterface")
        self.scrollWidget.setObjectName("scrollWidget")
        f = QFile(":/qss/album_interface.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

    def updateWindow(self, albumInfo: AlbumInfo):
        """ 更新窗口 """
        if albumInfo == self.albumInfo:
            return

        self.verticalScrollBar().setValue(0)
        self.__getInfo(albumInfo)
        self.albumInfoBar.updateWindow(self.albumInfo)
        self.songListWidget.updateAllSongCards(self.songInfos)
        self.scrollWidget.resize(
            self.width(), self.songListWidget.height()+430)

    def resizeEvent(self, e):
        """ 改变尺寸时改变小部件大小 """
        super().resizeEvent(e)
        self.albumInfoBar.resize(self.width(), self.albumInfoBar.height())
        self.songListWidget.resize(self.width(), self.songListWidget.height())
        self.scrollWidget.resize(
            self.width(), self.songListWidget.height()+430)
        self.selectionModeBar.resize(
            self.width(), self.selectionModeBar.height())
        self.selectionModeBar.move(
            0, self.height() - self.selectionModeBar.height())

    # TODO:使用数据库
    def updateOneSongCard(self, oldSongInfo: SongInfo, newSongInfo: SongInfo):
        """ 更新一个歌曲卡

        Parameters
        ----------
        oldSongInfo: SongInfo
            旧的歌曲信息

        newSongInfo: SongInfo
            更新后的歌曲信息
        """
        if oldSongInfo not in self.songInfos:
            return

        # 如果新的歌曲信息的"专辑名.歌手"不变，则更新歌曲卡信息，否则将其移除
        newKey = newSongInfo.get("album", "")+"."+newSongInfo.get("singer", "")
        oldKey = oldSongInfo.get("album", "")+"."+oldSongInfo.get("singer", "")

        if newKey == oldKey:
            self.songListWidget.updateOneSongCard(newSongInfo, False)
        else:
            index = self.songListWidget.index(oldSongInfo)
            self.songListWidget.removeSongCard(index)

        self.__sortSongCardsByTrackNum()
        self.albumInfo.songInfos = self.songListWidget.songInfos
        self.songInfos = self.songListWidget.songInfos

    def __showAlbumInfoEditDialog(self):
        """ 显示专辑信息编辑对话框 """
        # 创建线程和对话框
        thread = SaveAlbumInfoThread(self)
        w = AlbumInfoEditDialog(self.albumInfo, self.window())

        # 信号连接到槽
        w.saveInfoSig.connect(thread.setAlbumInfo)
        w.saveInfoSig.connect(thread.start)
        thread.saveFinishedSignal.connect(w.onSaveComplete)
        thread.saveFinishedSignal.connect(self.__onSaveAlbumInfoFinished)

        # 显示对话框
        w.setStyle(QApplication.style())
        w.exec_()

    def __onSelectionModeStateChanged(self, isOpen: bool):
        """ 选择状态改变对应的槽函数 """
        self.selectionModeBar.setHidden(not isOpen)
        self.selectionModeStateChanged.emit(isOpen)

    def __sortSongCardsByTrackNum(self):
        """ 以曲序为基准排序歌曲卡 """
        self.songListWidget.sortSongCardByTrackNum()
        self.albumInfo.songInfos= self.songListWidget.songInfos
        self.songInfos = self.songListWidget.songInfos

    def __onEditSongInfo(self, oldSongInfo: AlbumInfo, newSongInfo: AlbumInfo):
        self.__sortSongCardsByTrackNum()
        index = self.songInfos.index(newSongInfo)

        # 更新封面
        if newSongInfo.get('coverPath'):
            coverPath = getCoverPath(newSongInfo['coverName'], 'album_big')
            oldCoverPath = self.albumInfoBar.coverPath
            if oldCoverPath.startswith(':') or (index == 0 and oldCoverPath != coverPath):
                self.albumInfo['coverPath'] = coverPath

        # 更新专辑信息
        for i, songInfo in enumerate(self.albumInfo["songInfos"]):
            if songInfo.file == newSongInfo.file:
                self.albumInfo["songInfos"][i] = newSongInfo.copy()
                self.albumInfo["genre"] = self.albumInfo["songInfos"][0]["genre"]

        self.albumInfoBar.updateWindow(self.albumInfo)
        self.editSongInfoSignal.emit(oldSongInfo, newSongInfo)

    def __onSaveAlbumInfoFinished(self, oldAlbumInfo: AlbumInfo, newAlbumInfo: AlbumInfo, coverPath: str):
        """ 保存专辑信息 """
        # 删除线程
        self.sender().quit()
        self.sender().wait()
        self.sender().deleteLater()

        # 更新窗口
        albumInfo = deepcopy(newAlbumInfo)
        songInfos = albumInfo["songInfos"]
        oldKey = oldAlbumInfo["album"]+'.'+oldAlbumInfo["singer"]
        for songInfo in songInfos.copy():
            newKey = songInfo.get('album', '')+'.'+songInfo.get('singer', '')
            if newKey != oldKey:
                songInfos.remove(songInfo)

        # 在只修改了封面的情况下必须强制更新专辑信息栏
        self.albumInfoBar.updateWindow(albumInfo)
        self.updateWindow(albumInfo)
        self.__sortSongCardsByTrackNum()
        self.editAlbumInfoSignal.emit(oldAlbumInfo, newAlbumInfo, coverPath)

    def __unCheckSongCards(self):
        """ 取消已选中歌曲卡的选中状态并更新按钮图标 """
        self.songListWidget.unCheckSongCards()
        # 更新按钮的图标为全选
        self.selectionModeBar.checkAllButton.setCheckedState(True)

    def __emitPlaylist(self):
        """ 发送歌曲界面选中的播放列表 """
        playlist = [i.songInfo for i in self.songListWidget.checkedSongCards]
        self.__unCheckSongCards()

        if self.sender() == self.selectionModeBar.playButton:
            self.playCheckedCardsSig.emit(playlist)
        elif self.sender() == self.selectionModeBar.nextToPlayButton:
            self.nextToPlayCheckedCardsSig.emit(playlist)

    def __editSongCardInfo(self):
        """ 编辑歌曲卡信息 """
        songCard = self.songListWidget.checkedSongCards[0]
        self.__unCheckSongCards()
        self.songListWidget.showSongInfoEditDialog(songCard)

    def __selectAllButtonSlot(self):
        """ 歌曲卡全选/取消全选 """
        isChecked = not self.songListWidget.isAllSongCardsChecked
        self.songListWidget.setAllSongCardCheckedState(isChecked)
        self.selectionModeBar.checkAllButton.setCheckedState(isChecked)

    def __showCheckedSongCardProperty(self):
        """ 显示选中的歌曲卡的属性 """
        songInfo = self.songListWidget.checkedSongCards[0].songInfo
        self.__unCheckSongCards()
        self.songListWidget.showSongPropertyDialog(songInfo)

    def __onCheckedCardNumChanged(self, num):
        """ 选中的卡数量发生改变时刷新选择栏 """
        self.selectionModeBar.setPartButtonHidden(num > 1)

    def exitSelectionMode(self):
        """ 退出选择模式 """
        self.__unCheckSongCards()

    def __showAddToMenu(self):
        """ 显示添加到菜单 """
        # 初始化菜单动作触发标志
        menu = AddToMenu(parent=self)

        # 计算菜单弹出位置
        pos = self.selectionModeBar.mapToGlobal(
            QPoint(self.selectionModeBar.addToButton.x(), 0))
        x = pos.x() + self.selectionModeBar.addToButton.width() + 5
        y = pos.y() + self.selectionModeBar.addToButton.height() // 2 - \
            (13 + 38 * menu.actionCount()) // 2

        # 获取选中的歌曲信息列表
        for act in menu.action_list:
            act.triggered.connect(self.exitSelectionMode)
        songInfos = [
            i.songInfo for i in self.songListWidget.checkedSongCards]
        menu.playingAct.triggered.connect(
            lambda: self.addSongsToPlayingPlaylistSig.emit(songInfos))
        menu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(name, songInfos))
        menu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(songInfos))
        menu.exec(QPoint(x, y))

    def __onScrollBarValueChanged(self, value):
        """ 滚动时改变专辑信息栏高度 """
        h = 385 - value
        if h > 155:
            self.albumInfoBar.resize(self.albumInfoBar.width(), h)

    def setCurrentIndex(self, index: int):
        """ 设置当前播放歌曲 """
        self.songListWidget.setPlay(index)

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        # 专辑信息栏信号
        self.albumInfoBar.playAllButton.clicked.connect(
            lambda: self.playAlbumSignal.emit(self.singer, self.album))
        self.albumInfoBar.editInfoButton.clicked.connect(
            self.__showAlbumInfoEditDialog)
        self.albumInfoBar.showSingerButton.clicked.connect(
            lambda: self.switchToSingerInterfaceSig.emit(self.singer))
        self.albumInfoBar.addToPlayingPlaylistSig.connect(
            lambda: self.addSongsToPlayingPlaylistSig.emit(self.songInfos))
        self.albumInfoBar.addToNewCustomPlaylistSig.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(self.songInfos))
        self.albumInfoBar.addToCustomPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(name, self.songInfos))
        self.albumInfoBar.action_list[-2].triggered.connect(
            self.__showAlbumInfoEditDialog)

        # 歌曲列表信号
        self.songListWidget.playSignal.connect(self.songCardPlaySig)
        self.songListWidget.playOneSongSig.connect(self.playOneSongCardSig)
        self.songListWidget.editSongInfoSignal.connect(self.__onEditSongInfo)
        self.songListWidget.nextToPlayOneSongSig.connect(
            self.nextToPlayOneSongSig)
        self.songListWidget.addSongToPlayingSignal.connect(
            self.addOneSongToPlayingSig)
        self.songListWidget.selectionModeStateChanged.connect(
            self.__onSelectionModeStateChanged)
        self.songListWidget.checkedSongCardNumChanged.connect(
            self.__onCheckedCardNumChanged)
        self.songListWidget.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig)
        self.songListWidget.addSongsToNewCustomPlaylistSig.connect(
            self.addSongsToNewCustomPlaylistSig)
        self.songListWidget.isAllCheckedChanged.connect(
            lambda x: self.selectionModeBar.checkAllButton.setCheckedState(not x))
        self.songListWidget.switchToSingerInterfaceSig.connect(
            self.switchToSingerInterfaceSig)

        # 选择栏信号连接到槽函数
        self.selectionModeBar.cancelButton.clicked.connect(
            self.__unCheckSongCards)
        self.selectionModeBar.playButton.clicked.connect(self.__emitPlaylist)
        self.selectionModeBar.nextToPlayButton.clicked.connect(
            self.__emitPlaylist)
        self.selectionModeBar.editInfoButton.clicked.connect(
            self.__editSongCardInfo)
        self.selectionModeBar.propertyButton.clicked.connect(
            self.__showCheckedSongCardProperty)
        self.selectionModeBar.checkAllButton.clicked.connect(
            self.__selectAllButtonSlot)
        self.selectionModeBar.addToButton.clicked.connect(self.__showAddToMenu)

        # 将滚动信号连接到槽函数
        self.verticalScrollBar().valueChanged.connect(self.__onScrollBarValueChanged)
