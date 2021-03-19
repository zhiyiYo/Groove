# coding:utf-8

from copy import deepcopy

from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QThread
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPalette

from app.components.menu import AddToMenu
from app.common.object.save_info_object import SaveInfoObject
from app.components.dialog_box.album_info_edit_panel import AlbumInfoEditPanel

from .album_info_bar import AlbumInfoBar
from .selection_mode_bar import SelectionModeBar
from .song_card_list_widget import SongCardListWidget


class AlbumInterface(QWidget):
    """ 专辑界面 """

    songCardPlaySig = pyqtSignal(int)  # 在当前播放列表中播放这首歌
    playAlbumSignal = pyqtSignal(list)  # 播放整张专辑
    playOneSongCardSig = pyqtSignal(dict)  # 将播放列表重置为一首歌
    playCheckedCardsSig = pyqtSignal(list)  # 播放选中的歌曲卡
    nextToPlayOneSongSig = pyqtSignal(dict)  # 下一首播放一首歌
    addOneSongToPlayingSig = pyqtSignal(dict)  # 添加一首歌到正在播放
    saveAlbumInfoSig = pyqtSignal(dict, dict)
    selectionModeStateChanged = pyqtSignal(bool)
    nextToPlayCheckedCardsSig = pyqtSignal(list)  # 将选中的多首歌添加到下一首播放
    addSongsToPlayingPlaylistSig = pyqtSignal(list)  # 添加歌曲到正在播放
    addSongsToNewCustomPlaylistSig = pyqtSignal(list)  # 添加歌曲到新建播放列表
    addSongsToCustomPlaylistSig = pyqtSignal(str, list)  # 添加歌曲到自定义的播放列表中

    def __init__(self, albumInfo: dict, parent=None):
        super().__init__(parent)
        self.albumInfo = deepcopy(albumInfo)
        self.songInfo_list = albumInfo.get("songInfo_list")  # type:list
        # 创建小部件
        self.songListWidget = SongCardListWidget(self.songInfo_list, self)
        self.albumInfoBar = AlbumInfoBar(albumInfo, self)
        self.selectionModeBar = SelectionModeBar(self)
        # 创建线程
        self.saveAlbumInfoObject = SaveInfoObject()
        self.saveInfoThread = QThread(self.parent())
        self.saveAlbumInfoObject.moveToThread(self.saveInfoThread)
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1230, 900)
        self.setAutoFillBackground(True)
        self.selectionModeBar.hide()
        self.songListWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 设置背景色
        palette = QPalette()
        palette.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(palette)
        # 信号连接到槽
        self.__connectSignalToSlot()

    def updateWindow(self, albumInfo: dict):
        """ 更新窗口 """
        if albumInfo == self.albumInfo:
            return
        self.albumInfoBar.updateWindow(albumInfo)
        self.albumInfo = albumInfo if albumInfo else {}
        self.songInfo_list = albumInfo.get("songInfo_list")
        self.songListWidget.updateAllSongCards(self.songInfo_list)
        self.songListWidget.resize(self.size())

    def resizeEvent(self, e):
        """ 改变尺寸时改变小部件大小 """
        super().resizeEvent(e)
        self.albumInfoBar.resize(self.width(), self.albumInfoBar.height())
        self.songListWidget.resize(self.size())
        self.selectionModeBar.resize(self.width(), self.selectionModeBar.height())
        self.selectionModeBar.move(0, self.height() - self.selectionModeBar.height())

    def updateOneSongCard(self, oldSongInfo: dict, newSongInfo):
        """ 更新一个歌曲卡 """
        # 不将歌曲信息写入json文件
        self.songListWidget.updateOneSongCard(oldSongInfo, newSongInfo, False)
        self.albumInfo["songInfo_list"] = self.songListWidget.songInfo_list

    def __showAlbumInfoEditPanel(self):
        """ 显示专辑信息编辑面板 """
        oldAlbumInfo = deepcopy(self.albumInfo)
        infoEditPanel = AlbumInfoEditPanel(deepcopy(self.albumInfo), self.window())
        infoEditPanel.saveInfoSig.connect(
            lambda newAlbumInfo: self.__saveAlbumInfoSlot(oldAlbumInfo, newAlbumInfo)
        )
        self.saveAlbumInfoObject.saveCompleteSig.connect(infoEditPanel.saveCompleteSlot)
        self.saveAlbumInfoObject.saveErrorSig.connect(infoEditPanel.saveErrorSlot)
        infoEditPanel.setStyle(QApplication.style())
        infoEditPanel.exec_()
        self.saveAlbumInfoObject.disconnect()

    def __selectionModeStateChangedSlot(self, isOpenSelectionMode: bool):
        """ 选择状态改变对应的槽函数 """
        self.selectionModeBar.setHidden(not isOpenSelectionMode)
        self.selectionModeStateChanged.emit(isOpenSelectionMode)

    def __sortSongCardsByTrackNum(self):
        """ 以曲序为基准排序歌曲卡 """
        self.songListWidget.sortSongCardByTrackNum()
        self.albumInfo["songInfo_list"] = self.songListWidget.songInfo_list
        self.songInfo_list = self.songListWidget.songInfo_list

    def __saveAlbumInfoSlot(self, oldAlbumInfo: dict, newAlbumInfo: dict):
        """ 保存专辑信息 """
        self.saveAlbumInfoObject.saveAlbumInfoSlot(newAlbumInfo["songInfo_list"])
        newAlbumInfo_copy = deepcopy(newAlbumInfo)
        self.updateWindow(newAlbumInfo)
        # 如果只更改了专辑封面需要直接刷新信息栏
        self.albumInfoBar.updateWindow(newAlbumInfo)
        self.__sortSongCardsByTrackNum()
        self.saveAlbumInfoSig.emit(oldAlbumInfo, newAlbumInfo_copy)

    def __unCheckSongCards(self):
        """ 取消已选中歌曲卡的选中状态并更新按钮图标 """
        self.songListWidget.unCheckSongCards()
        # 更新按钮的图标为全选
        self.selectionModeBar.checkAllButton.setCheckedState(True)

    def __emitPlaylist(self):
        """ 发送歌曲界面选中的播放列表 """
        playlist = [
            songCard.songInfo for songCard in self.songListWidget.checkedSongCard_list
        ]
        self.__unCheckSongCards()
        if self.sender() == self.selectionModeBar.playButton:
            self.playCheckedCardsSig.emit(playlist)
        elif self.sender() == self.selectionModeBar.nextToPlayButton:
            self.nextToPlayCheckedCardsSig.emit(playlist)

    def __editSongCardInfo(self):
        """ 编辑歌曲卡信息 """
        songCard = self.songListWidget.checkedSongCard_list[0]
        self.__unCheckSongCards()
        self.songListWidget.showSongInfoEditPanel(songCard)

    def __selectAllButtonSlot(self):
        """ 歌曲卡全选/取消全选 """
        isChecked = not self.songListWidget.isAllSongCardsChecked
        self.songListWidget.setAllSongCardCheckedState(isChecked)
        self.selectionModeBar.checkAllButton.setCheckedState(isChecked)

    def __showCheckedSongCardProperty(self):
        """ 显示选中的歌曲卡的属性 """
        songInfo = self.songListWidget.checkedSongCard_list[0].songInfo
        self.__unCheckSongCards()
        self.songListWidget.showPropertyPanel(songInfo)

    def __checkedCardNumChangedSlot(self, num):
        """ 选中的卡数量发生改变时刷新选择栏 """
        self.selectionModeBar.setPartButtonHidden(num > 1)

    def exitSelectionMode(self):
        """ 退出选择模式 """
        self.__unCheckSongCards()

    def __showAddToMenu(self):
        """ 显示添加到菜单 """
        # 初始化菜单动作触发标志
        self.__actionTriggeredFlag = False
        addToMenu = AddToMenu(parent=self)
        # 计算菜单弹出位置
        addToGlobalPos = self.selectionModeBar.mapToGlobal(QPoint(0, 0)) + QPoint(
            self.selectionModeBar.addToButton.x(), 0
        )
        x = addToGlobalPos.x() + self.selectionModeBar.addToButton.width() + 5
        y = addToGlobalPos.y() + int(
            self.selectionModeBar.addToButton.height() / 2
            - (13 + 38 * addToMenu.actionCount()) / 2
        )
        # 获取选中的歌曲信息列表
        songInfo_list = [
            songCard.songInfo for songCard in self.songListWidget.checkedSongCard_list
        ]
        addToMenu.playingAct.triggered.connect(
            lambda: self.addSongsToPlayingPlaylistSig.emit(songInfo_list)
        )
        addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(name, songInfo_list)
        )
        addToMenu.newPlayList.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(songInfo_list)
        )
        for act in addToMenu.action_list:
            act.triggered.connect(self.__addToMenuTriggeredSlot)
        addToMenu.exec(QPoint(x, y))
        # 如果动作有被触发就退出选择模式
        if self.__actionTriggeredFlag:
            self.__unCheckSongCards()

    def __addToMenuTriggeredSlot(self):
        """ 添加到菜单上的动作被触发时标志位置位 """
        self.__actionTriggeredFlag = True

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        # 专辑信息栏信号
        self.albumInfoBar.playAllBt.clicked.connect(
            lambda: self.playAlbumSignal.emit(self.songInfo_list)
        )
        self.albumInfoBar.addToPlayingPlaylistSig.connect(
            lambda: self.addSongsToPlayingPlaylistSig.emit(self.songInfo_list)
        )
        self.albumInfoBar.editInfoBt.clicked.connect(self.__showAlbumInfoEditPanel)
        self.albumInfoBar.addToNewCustomPlaylistSig.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(self.songInfo_list)
        )
        self.albumInfoBar.addToCustomPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(name, self.songInfo_list)
        )
        self.albumInfoBar.editInfoSig.connect(self.__showAlbumInfoEditPanel)
        # 歌曲列表信号
        self.songListWidget.playSignal.connect(self.songCardPlaySig)
        self.songListWidget.playOneSongSig.connect(self.playOneSongCardSig)
        self.songListWidget.nextToPlayOneSongSig.connect(self.nextToPlayOneSongSig)
        self.songListWidget.addSongToPlayingSignal.connect(self.addOneSongToPlayingSig)
        self.songListWidget.selectionModeStateChanged.connect(
            self.__selectionModeStateChangedSlot
        )
        self.songListWidget.checkedSongCardNumChanged.connect(
            self.__checkedCardNumChangedSlot
        )
        self.songListWidget.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig
        )
        self.songListWidget.addSongsToNewCustomPlaylistSig.connect(
            self.addSongsToNewCustomPlaylistSig
        )
        # 选择栏信号连接到槽函数
        self.selectionModeBar.cancelButton.clicked.connect(self.__unCheckSongCards)
        self.selectionModeBar.playButton.clicked.connect(self.__emitPlaylist)
        self.selectionModeBar.nextToPlayButton.clicked.connect(self.__emitPlaylist)
        self.selectionModeBar.editInfoButton.clicked.connect(self.__editSongCardInfo)
        self.selectionModeBar.propertyButton.clicked.connect(
            self.__showCheckedSongCardProperty
        )
        self.selectionModeBar.checkAllButton.clicked.connect(self.__selectAllButtonSlot)
        self.selectionModeBar.addToButton.clicked.connect(self.__showAddToMenu)

