# coding:utf-8
import os
from copy import deepcopy
from typing import Dict, List

from common.crawler.kuwo_music_crawler import KuWoMusicCrawler
from common.thread.get_singer_avatar_thread import GetSingerAvatarThread
from common.thread.save_album_info_thread import SaveAlbumInfoThread
from components.album_card import AlbumBlurBackground
from components.album_card import AlbumCard as AlbumCardBase
from components.buttons.three_state_button import ThreeStateButton
from components.dialog_box.album_info_edit_dialog import AlbumInfoEditDialog
from components.dialog_box.message_dialog import MessageDialog
from components.layout.grid_layout import GridLayout
from components.menu import AddToMenu, DWMMenu
from components.scroll_area import ScrollArea
from PyQt5.QtCore import (QFile, QParallelAnimationGroup, QPoint,
                          QPropertyAnimation, Qt, pyqtSignal)
from PyQt5.QtWidgets import QAction, QApplication, QLabel, QWidget

from .selection_mode_bar import SelectionModeBar
from .singer_info_bar import SingerInfoBar


class SingerInterface(ScrollArea):
    """ 歌手界面 """

    playSig = pyqtSignal(list)                                  # 播放信号
    nextToPlaySig = pyqtSignal(list)                            # 下一首播放
    deleteAlbumSig = pyqtSignal(list)                           # 删除专辑
    selectionModeStateChanged = pyqtSignal(bool)                # 进入/退出选择模式
    switchToAlbumInterfaceSig = pyqtSignal(str, str)            # 切换到专辑界面
    editAlbumInfoSignal = pyqtSignal(dict, dict, str)           # 编辑专辑信息
    addSongsToPlayingPlaylistSig = pyqtSignal(list)             # 将歌曲添加到正在播放
    addSongsToNewCustomPlaylistSig = pyqtSignal(list)           # 将专辑添加到新建的播放列表
    addSongsToCustomPlaylistSig = pyqtSignal(str, list)         # 专辑添加到已存在的播放列表

    def __init__(self, singerInfo: dict = None, parent=None):
        """
        Parameters
        ----------
        singerInfo: dict
            歌手信息

        parent:
            父级
        """
        super().__init__(parent=parent)
        self.__getInfo(singerInfo)
        self.columnNum = 1
        self.isInSelectionMode = False
        self.isAllAlbumCardsChecked = False
        self.albumCard_list = []            # type:List[AlbumCard]
        self.checkedAlbumCard_list = []     # type:List[AlbumCard]
        self.hideCheckBoxAni_list = []      # type:List[QPropertyAnimation]
        self.albumName2AlbumInfo_dict = {}  # type:Dict[str, dict]
        self.albumName2AlbumCard_dict = {}  # type:Dict[str, AlbumCard]
        self.crawler = KuWoMusicCrawler()
        self.getAvatarThread = GetSingerAvatarThread(self)

        # 创建小部件
        self.scrollWidget = QWidget(self)
        self.selectionModeBar = SelectionModeBar(self)
        self.singerInfoBar = SingerInfoBar(self.singerInfo, self)
        self.hideCheckBoxAniGroup = QParallelAnimationGroup(self)
        self.gridLayout = GridLayout(self.scrollWidget)
        self.albumBlurBackground = AlbumBlurBackground(self.scrollWidget)
        self.inYourMusicLabel = QLabel(
            self.tr('In your music'), self.scrollWidget)
        self.playButton = ThreeStateButton(
            {
                "normal": ":/images/singer_interface//Play_normal.png",
                "hover": ":/images/singer_interface//Play_hover.png",
                "pressed": ":/images/singer_interface//Play_pressed.png",
            },
            self.scrollWidget,
            (20, 20)
        )

        # 创建专辑卡
        self.__setQss()
        for albumInfo in self.albumInfo_list:
            self.__createOneAlbumCard(albumInfo)

        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setWidget(self.scrollWidget)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 设置布局
        self.gridLayout.setContentsMargins(30, 456, 30, 116)
        self.gridLayout.setVerticalSpacing(10)
        self.gridLayout.setHorizontalSpacing(10)
        self.__addAlbumCardsToLayout()

        self.inYourMusicLabel.move(30, 412)
        self.playButton.move(185, 419)
        self.selectionModeBar.hide()
        self.__connectSignalToSlot()
        self.resize(1200, 900)

    def __createOneAlbumCard(self, albumInfo):
        """ 创建一个专辑卡 """
        albumName = albumInfo.get("album", self.tr('Unknown album'))
        albumCard = AlbumCard(albumInfo, self.scrollWidget)
        ani = QPropertyAnimation(albumCard.checkBoxOpacityEffect, b'opacity')
        self.hideCheckBoxAniGroup.addAnimation(ani)
        self.hideCheckBoxAni_list.append(ani)
        self.albumCard_list.append(albumCard)
        self.albumName2AlbumInfo_dict[albumName] = albumInfo
        self.albumName2AlbumCard_dict[albumName] = albumCard

        # 信号连接到槽
        albumCard.playSignal.connect(self.playSig)
        albumCard.nextPlaySignal.connect(self.nextToPlaySig)
        albumCard.deleteCardSig.connect(self.__showDeleteOneCardDialog)
        albumCard.addToPlayingSignal.connect(self.addSongsToPlayingPlaylistSig)
        albumCard.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterfaceSig)
        albumCard.checkedStateChanged.connect(
            self.__onAlbumCardCheckedStateChanged)
        albumCard.showBlurAlbumBackgroundSig.connect(
            self.__showBlurAlbumBackground)
        albumCard.hideBlurAlbumBackgroundSig.connect(
            self.albumBlurBackground.hide)
        albumCard.addAlbumToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig)
        albumCard.addAlbumToNewCustomPlaylistSig.connect(
            self.addSongsToNewCustomPlaylistSig)
        albumCard.showAlbumInfoEditDialogSig.connect(
            self.__showAlbumInfoEditDialog)

    def __playAllSongs(self):
        """ 播放歌手的所有歌曲 """
        songInfo_list = []
        for albumInfo in self.albumInfo_list:
            songInfo_list.extend(albumInfo.get('songInfo_list', []))

        self.playSig.emit(songInfo_list)

    def __addSongsToPlayingPlaylist(self):
        """ 将歌曲添加到正在播放列表 """
        songInfo_list = []
        for albumInfo in self.albumInfo_list:
            songInfo_list.extend(albumInfo.get('songInfo_list', []))

        self.addSongsToPlayingPlaylistSig.emit(songInfo_list)

    def __addSongsToCustomPlaylist(self, playlistName: str):
        """ 将歌曲添加到正在播放列表 """
        songInfo_list = []
        for albumInfo in self.albumInfo_list:
            songInfo_list.extend(albumInfo.get('songInfo_list', []))

        self.addSongsToCustomPlaylistSig.emit(playlistName, songInfo_list)

    def __addSongsToNewCustomPlaylist(self):
        """ 将歌曲添加到正在播放列表 """
        songInfo_list = []
        for albumInfo in self.albumInfo_list:
            songInfo_list.extend(albumInfo.get('songInfo_list', []))

        self.addSongsToNewCustomPlaylistSig.emit(songInfo_list)

    def __addAlbumCardsToLayout(self):
        """ 将专辑卡添加到布局中 """
        self.gridLayout.removeAllWidgets()
        for i, card in enumerate(self.albumCard_list):
            row = i//self.columnNum
            column = i-self.columnNum*row
            self.gridLayout.addWidget(card, row, column, Qt.AlignLeft)

        self.scrollWidget.resize(
            self.width(), 456 + self.gridLayout.rowCount() * 300 + 120)

    def resizeEvent(self, e):
        self.singerInfoBar.resize(self.width(), self.singerInfoBar.height())
        self.selectionModeBar.resize(
            self.width(), self.selectionModeBar.height())
        self.selectionModeBar.move(
            0, self.height()-self.selectionModeBar.height())

        column = 1 if self.width() < 480 else 2+(self.width()-480)//220
        if column == self.columnNum:
            return

        self.columnNum = column
        self.gridLayout.updateColumnNum(column, 210, 290)
        self.scrollWidget.resize(
            self.width(), 456 + self.gridLayout.rowCount() * 300 + 120)

    def __getInfo(self, singerInfo: dict):
        """ 获取信息 """
        self.singerInfo = deepcopy(singerInfo) if singerInfo else {}
        self.genre = self.singerInfo.get('genre', self.tr('Unknown genre'))
        self.singer = self.singerInfo.get('singer', self.tr('Unknown artist'))
        self.albumInfo_list = self.singerInfo.get('albumInfo_list', [])

    def __setQss(self):
        """ 设置层叠样式 """
        self.scrollWidget.setObjectName('scrollWidget')
        self.inYourMusicLabel.setObjectName('inYourMusicLabel')

        f = QFile(":/qss/singer_interface.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

        self.inYourMusicLabel.adjustSize()

    def __onSelectionModeBarDeleteButtonClicked(self):
        """ 选择模式栏删除按钮点击槽函数 """
        if len(self.checkedAlbumCard_list) > 1:
            title = self.tr("Are you sure you want to delete these?")
            content = self.tr(
                "If you delete these albums, they won't be on be this device anymore.")
        else:
            name = self.checkedAlbumCard_list[0].albumName
            title = self.tr("Are you sure you want to delete this?")
            content = self.tr("If you delete") + f' "{name}" ' + \
                self.tr("it won't be on be this device anymore.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(self.__onDeleteAlbumsYesButtonClicked)
        w.exec()

    def __onDeleteAlbumsYesButtonClicked(self):
        """ 专辑界面选择模式栏删除按钮点击槽函数 """
        albumNames = []
        songPaths = []
        for albumCard in self.checkedAlbumCard_list.copy():
            albumNames.append(albumCard.albumName)
            songPaths.extend([i["songPath"] for i in albumCard.songInfo_list])
            albumCard.setChecked(False)

        self.deleteAlbums(albumNames)
        self.deleteAlbumSig.emit(songPaths)

    def __showDeleteOneCardDialog(self, albumName: str):
        """ 显示删除一个专辑卡的对话框 """
        songPaths = [i["songPath"] for i in self.sender().songInfo_list]
        title = self.tr("Are you sure you want to delete this?")
        content = self.tr("If you delete") + f' "{albumName}" ' + \
            self.tr("it won't be on be this device anymore.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(lambda: self.deleteAlbums([albumName]))
        w.yesSignal.connect(lambda: self.deleteAlbumSig.emit(songPaths))
        w.exec_()

    def deleteAlbums(self, albumNames: list):
        """ 删除专辑 """
        albumInfo_list = deepcopy(self.albumInfo_list)

        for albumInfo in albumInfo_list.copy():
            if albumInfo["album"] in albumNames:
                albumInfo_list.remove(albumInfo)

        self.__updateAllAlbumCards(albumInfo_list)

    def __showBlurAlbumBackground(self, pos: QPoint, picPath: str):
        """ 显示磨砂背景 """
        pos = self.scrollWidget.mapFromGlobal(pos)
        self.albumBlurBackground.setBlurAlbum(picPath)
        self.albumBlurBackground.move(pos.x() - 28, pos.y() - 16)
        self.albumBlurBackground.show()

    def __onAlbumCardCheckedStateChanged(self, albumCard, isChecked: bool):
        """ 专辑卡选中状态改变对应的槽函数 """
        # 如果专辑信息不在选中的专辑信息列表中且对应的专辑卡变为选中状态就将专辑信息添加到列表中
        if albumCard not in self.checkedAlbumCard_list and isChecked:
            self.checkedAlbumCard_list.append(albumCard)

        # 如果专辑信息已经在列表中且该专辑卡变为非选中状态就弹出该专辑信息
        elif albumCard in self.checkedAlbumCard_list and not isChecked:
            self.checkedAlbumCard_list.pop(
                self.checkedAlbumCard_list.index(albumCard))

        self.selectionModeBar.setPartButtonHidden(
            len(self.checkedAlbumCard_list) > 1)
        self.selectionModeBar.move(
            0, self.height()-self.selectionModeBar.height())

        # 检查是否全部专辑卡选中改变
        isAllChecked = (len(self.checkedAlbumCard_list)
                        == len(self.albumCard_list))
        if isAllChecked != self.isAllAlbumCardsChecked:
            self.isAllAlbumCardsChecked = isAllChecked
            self.selectionModeBar.checkAllButton.setCheckedState(
                not isAllChecked)

        # 如果先前不处于选择模式那么这次发生选中状态改变就进入选择模式
        if not self.isInSelectionMode:
            self.__setAllAlbumCardSelectionModeOpen(True)
            self.selectionModeStateChanged.emit(True)
            self.isInSelectionMode = True
        elif not self.checkedAlbumCard_list:
            self.__setAllAlbumCardSelectionModeOpen(False)
            self.selectionModeStateChanged.emit(False)
            self.isInSelectionMode = False

    def __setAllAlbumCardSelectionModeOpen(self, isOpen: bool):
        """ 设置所有专辑卡是否进入选择模式 """
        self.selectionModeBar.setVisible(isOpen)
        for albumCard in self.albumCard_list:
            albumCard.setSelectionModeOpen(isOpen)

        # 退出选择模式时开启隐藏所有复选框的动画
        if not isOpen:
            self.__startHideCheckBoxAni()

    def __startHideCheckBoxAni(self):
        """ 开始隐藏复选框动画 """
        for ani in self.hideCheckBoxAni_list:
            ani.setStartValue(1)
            ani.setEndValue(0)
            ani.setDuration(140)
        self.hideCheckBoxAniGroup.start()

    def __hideAllCheckBox(self):
        """ 隐藏所有复选框 """
        for albumCard in self.albumCard_list:
            albumCard.checkBox.hide()

    def __onScrollBarValueChanged(self, value):
        """ 滚动时改变专辑信息栏高度 """
        h = 385 - value
        if h > 155:
            self.singerInfoBar.resize(self.width(), h)

    def __showAlbumInfoEditDialog(self, albumInfo: dict):
        """ 显示专辑信息编辑界面信号 """
        # 创建线程和对话框
        thread = SaveAlbumInfoThread(self)
        w = AlbumInfoEditDialog(albumInfo, self.window())

        # 信号连接到槽
        w.saveInfoSig.connect(thread.setAlbumInfo)
        w.saveInfoSig.connect(thread.start)
        thread.saveFinishedSignal.connect(w.onSaveComplete)
        thread.saveFinishedSignal.connect(self.__onSaveAlbumInfoFinished)

        # 显示对话框
        w.setStyle(QApplication.style())
        w.exec_()

    def __onSaveAlbumInfoFinished(self, oldAlbumInfo: dict, newAlbumInfo: dict, coverPath):
        """ 保存专辑信息槽函数 """
        # 删除线程
        self.sender().quit()
        self.sender().wait()
        self.sender().deleteLater()

        # 发送信号
        self.editAlbumInfoSignal.emit(oldAlbumInfo, newAlbumInfo, coverPath)

    def __getSingerAvatar(self, singer: str):
        """ 获取歌手头像 """
        path = f'singer_avatar/{singer}.jpg'
        if not os.path.exists(path):
            self.singerInfoBar.coverLabel.hide()
            self.getAvatarThread.singer = singer
            self.getAvatarThread.start()

    def __onDownloadAvatarFinished(self, avatarPath: str):
        """ 下载歌手头像完成 """
        self.singerInfoBar.coverLabel.show()
        if os.path.exists(avatarPath):
            self.singerInfoBar.updateCover(avatarPath)

    def updateWindow(self, singerInfo: dict):
        """ 更新窗口 """
        if self.singerInfo == singerInfo:
            return
        self.__getSingerAvatar(singerInfo.get(
            'singer', self.tr('Unknown artist')))
        self.__updateAllAlbumCards(singerInfo.get('albumInfo_list', []))
        self.__getInfo(singerInfo)
        self.singerInfoBar.updateWindow(self.singerInfo)

    def showEvent(self, e):
        self.verticalScrollBar().setValue(0)
        self.albumBlurBackground.hide()
        super().showEvent(e)

    def __updateAllAlbumCards(self, albumInfo_list: list):
        """ 更新所有专辑卡 """
        # 根据具体情况增减专辑卡
        newCardNum = len(albumInfo_list)
        oldCardNum = len(self.albumCard_list)
        if newCardNum < oldCardNum:
            # 删除部分专辑卡
            for i in range(oldCardNum - 1, newCardNum - 1, -1):
                albumCard = self.albumCard_list.pop()
                self.hideCheckBoxAni_list.pop()
                self.hideCheckBoxAniGroup.takeAnimation(i)
                albumCard.deleteLater()
        elif newCardNum > oldCardNum:
            # 新增部分专辑卡
            for albumInfo in albumInfo_list[oldCardNum:]:
                self.__createOneAlbumCard(albumInfo)
                QApplication.processEvents()

        # 更新部分专辑卡
        self.albumInfo_list = albumInfo_list
        n = oldCardNum if oldCardNum < newCardNum else newCardNum
        for i in range(n):
            albumInfo = albumInfo_list[i]
            self.albumCard_list[i].updateWindow(albumInfo)
            QApplication.processEvents()

        # 将专辑卡添加到布局中
        self.__addAlbumCardsToLayout()
        self.setStyle(QApplication.style())

        # 更新字典
        for albumCard, albumInfo in zip(self.albumCard_list, albumInfo_list):
            album = albumInfo["album"]
            self.albumName2AlbumCard_dict[album] = albumCard
            self.albumName2AlbumInfo_dict[album] = albumInfo

    def __onSelectionModeBarPlayButtonClicked(self):
        """ 选择模式栏播放/下一首播放按钮槽函数 """
        songInfo_list = []
        for albumCard in self.checkedAlbumCard_list:
            songInfo_list.extend(albumCard.albumInfo["songInfo_list"])
        self.__unCheckAlbumCards()

        if self.sender() is self.selectionModeBar.playButton:
            self.playSig.emit(songInfo_list)
        elif self.sender() is self.selectionModeBar.nextToPlayButton:
            self.nextToPlaySig.emit(songInfo_list)

    def __unCheckAlbumCards(self):
        """ 取消选中所有专辑卡 """
        self.selectionModeBar.checkAllButton.setCheckedState(True)
        checkedCards = self.checkedAlbumCard_list.copy()
        for albumCard in checkedCards:
            albumCard.setChecked(False)

    def __showAddToMenu(self):
        """ 显示添加到菜单 """
        menu = AddToMenu(parent=self)
        addToButton = self.sender()

        # 获取选中的播放列表
        songInfo_list = []
        for albumCard in self.checkedAlbumCard_list:
            songInfo_list.extend(albumCard.songInfo_list)

        # 计算菜单弹出位置
        pos = self.selectionModeBar.mapToGlobal(addToButton.pos())
        x = pos.x() + addToButton.width() + 5
        y = pos.y() + int(
            addToButton.height() / 2 - (13 + 38 * menu.actionCount()) / 2)

        # 信号连接到槽
        for act in menu.action_list:
            act.triggered.connect(self.exitSelectionMode)
        menu.playingAct.triggered.connect(
            lambda: self.addSongsToPlayingPlaylistSig.emit(songInfo_list))
        menu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(songInfo_list))
        menu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(name, songInfo_list))
        menu.exec(QPoint(x, y))

    def exitSelectionMode(self):
        """ 退出选择模式 """
        self.__unCheckAlbumCards()

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        # 播放全部按钮槽函数
        self.playButton.clicked.connect(self.__playAllSongs)

        # 动画完成隐藏复选框
        self.hideCheckBoxAniGroup.finished.connect(self.__hideAllCheckBox)

        # 将滚动信号连接到槽函数
        self.verticalScrollBar().valueChanged.connect(self.__onScrollBarValueChanged)

        # 将歌手信息栏信号连接到槽函数
        self.singerInfoBar.playAllButton.clicked.connect(self.__playAllSongs)
        self.singerInfoBar.addSongsToPlayingPlaylistSig.connect(
            self.__addSongsToPlayingPlaylist)
        self.singerInfoBar.addSongsToNewCustomPlaylistSig.connect(
            self.__addSongsToNewCustomPlaylist)
        self.singerInfoBar.addSongsToCustomPlaylistSig.connect(
            self.__addSongsToCustomPlaylist)

        # 将选择模式栏信号连接到槽函数
        self.selectionModeBar.playButton.clicked.connect(
            self.__onSelectionModeBarPlayButtonClicked)
        self.selectionModeBar.nextToPlayButton.clicked.connect(
            self.__onSelectionModeBarPlayButtonClicked)
        self.selectionModeBar.deleteButton.clicked.connect(
            self.__onSelectionModeBarDeleteButtonClicked)
        self.selectionModeBar.addToButton.clicked.connect(self.__showAddToMenu)

        # 将歌手头像下载线程信号连接到槽
        self.getAvatarThread.downloadFinished.connect(
            self.__onDownloadAvatarFinished)


class AlbumCard(AlbumCardBase):
    """ 专辑卡 """

    def __init__(self, albumInfo: dict, parent):
        super().__init__(albumInfo, parent)
        self.contentLabel.setText(self.year)
        self.contentLabel.setCursor(Qt.ArrowCursor)
        self.contentLabel.isSendEventToParent = True

    def updateWindow(self, newAlbumInfo: dict):
        super().updateWindow(newAlbumInfo)
        self.contentLabel.setText(self.year)

    def contextMenuEvent(self, e):
        """ 显示右击菜单 """
        menu = AlbumCardContextMenu(parent=self)
        menu.playAct.triggered.connect(
            lambda: self.playSignal.emit(self.songInfo_list))
        menu.nextToPlayAct.triggered.connect(
            lambda: self.nextPlaySignal.emit(self.songInfo_list))
        menu.addToMenu.playingAct.triggered.connect(
            lambda: self.addToPlayingSignal.emit(self.songInfo_list))
        menu.editInfoAct.triggered.connect(self.showAlbumInfoEditDialog)
        menu.selectAct.triggered.connect(self.__selectActSlot)
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addAlbumToCustomPlaylistSig.emit(name, self.songInfo_list))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: self.addAlbumToNewCustomPlaylistSig.emit(self.songInfo_list))
        menu.deleteAct.triggered.connect(
            lambda: self.deleteCardSig.emit(self.albumName))
        menu.exec(e.globalPos())


class AlbumCardContextMenu(DWMMenu):
    """ 专辑卡右击菜单"""

    def __init__(self, parent):
        super().__init__("", parent)
        # 创建动作
        self.__createActions()
        self.setObjectName("albumCardContextMenu")
        self.setQss()

    def __createActions(self):
        """ 创建动作 """
        # 创建动作
        self.playAct = QAction(self.tr("Play"), self)
        self.selectAct = QAction(self.tr("Select"), self)
        self.nextToPlayAct = QAction(self.tr("Play next"), self)
        self.pinToStartMenuAct = QAction(self.tr('Pin to Start'), self)
        self.deleteAct = QAction(self.tr("Delete"), self)
        self.editInfoAct = QAction(self.tr("Edit info"), self)
        self.addToMenu = AddToMenu(self.tr("Add to"), self)

        # 添加动作到菜单
        self.addActions([self.playAct, self.nextToPlayAct])
        # 将子菜单添加到主菜单
        self.addMenu(self.addToMenu)
        self.addActions(
            [self.pinToStartMenuAct, self.editInfoAct, self.deleteAct])
        self.addSeparator()
        self.addAction(self.selectAct)
