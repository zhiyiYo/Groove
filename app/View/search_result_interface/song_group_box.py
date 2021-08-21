# coding:utf-8
from app.components.dialog_box.message_dialog import MessageDialog
from app.components.buttons.three_state_button import ThreeStatePushButton
from app.components.menu import AddToMenu, DWMMenu, DownloadMenu
from app.components.song_list_widget import BasicSongListWidget, SongCardType
from PyQt5.QtCore import QMargins, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QAction, QWidget, QPushButton


class SongGroupBox(QWidget):
    """ 歌曲分组框 """

    def __init__(self, song_type: str, parent=None):
        """
        Parameters
        ----------
        song_type: str
            歌曲类型，可以是 `'本地歌曲'` 或 `'在线歌曲'`

        parent:
            父级窗口
        """
        super().__init__(parent=parent)
        if song_type not in ['本地歌曲', '在线歌曲']:
            raise ValueError("歌曲类型必须是 '本地歌曲' 或 '在线歌曲'")

        self.songInfo_list = []
        self.titleButton = QPushButton(song_type, self)
        if song_type == '本地歌曲':
            self.songListWidget = LocalSongListWidget(self)
        else:
            self.songListWidget = OnlineSongListWidget(self)

        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1200, 500)
        self.setMinimumHeight(47)
        self.songListWidget.move(0, 57)
        self.titleButton.move(35, 0)
        self.__setQss()

    def __setQss(self):
        """ 设置层叠样式 """
        self.titleButton.setObjectName('titleButton')
        with open('app/resource/css/song_group_box.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())
        self.titleButton.adjustSize()

    def resizeEvent(self, e):
        self.songListWidget.resize(self.width(), self.songListWidget.height())

    def updateWindow(self, songInfo_list):
        """ 更新窗口 """
        if songInfo_list == self.songInfo_list:
            return
        self.songInfo_list = songInfo_list
        self.songListWidget.updateAllSongCards(self.songInfo_list)
        self.setFixedHeight(57+self.songListWidget.height())


class LocalSongListWidget(BasicSongListWidget):
    """ 本地音乐歌曲卡列表 """

    playSignal = pyqtSignal(int)                        # 将播放列表的当前歌曲切换为指定的歌曲卡
    playOneSongSig = pyqtSignal(dict)                   # 重置播放列表为指定的一首歌
    nextToPlayOneSongSig = pyqtSignal(dict)             # 将歌曲添加到下一首播放
    switchToSingerInterfaceSig = pyqtSignal(str)        # 切换到歌手界面
    switchToAlbumInterfaceSig = pyqtSignal(str, str)    # 切换到专辑界面

    def __init__(self, parent=None):
        """
        Parameters
        ----------
        parent:
            父级窗口
        """
        super().__init__(None, SongCardType.NO_CHECKBOX_SONG_CARD,
                         parent, QMargins(30, 0, 30, 0), 0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.__setQss()

    def __playButtonSlot(self, index):
        """ 歌曲卡播放按钮槽函数 """
        self.playSignal.emit(index)
        self.setCurrentIndex(index)

    def contextMenuEvent(self, e):
        """ 重写鼠标右击时间的响应函数 """
        hitIndex = self.indexAt(e.pos()).column()
        # 显示右击菜单
        if hitIndex > -1:
            contextMenu = LocalSongListContextMenu(self)
            self.__connectContextMenuSignalToSlot(contextMenu)
            contextMenu.exec(self.cursor().pos())

    def __setQss(self):
        """ 设置层叠样式 """
        with open("app/resource/css/song_tab_interface_song_list_widget.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def __showDeleteCardDialog(self):
        index = self.currentRow()
        songInfo = self.songInfo_list[index]
        title = "是否确定要删除此项？"
        content = f"""如果删除"{songInfo['songName']}"，它将不再位于此设备上。"""
        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(lambda: self.removeSongCard(index))
        w.yesSignal.connect(
            lambda: self.removeSongSignal.emit(songInfo["songPath"]))
        w.exec_()

    def __adjustHeight(self):
        """ 调整高度 """
        self.resize(self.width(), 60*len(self.songCard_list))

    def wheelEvent(self, e):
        return

    def updateAllSongCards(self, songInfo_list: list):
        """ 更新所有歌曲卡，根据给定的信息决定创建或者删除歌曲卡 """
        super().updateAllSongCards(songInfo_list, self.__connectSongCardSignalToSlot)
        self.__adjustHeight()

    def removeSongCard(self, index):
        super().removeSongCard(index)
        self.__adjustHeight()

    def clearSongCards(self):
        super().clearSongCards()
        self.__adjustHeight()

    def __connectContextMenuSignalToSlot(self, menu):
        """ 信号连接到槽 """
        menu.playAct.triggered.connect(
            lambda: self.playOneSongSig.emit(
                self.songCard_list[self.currentRow()].songInfo))
        menu.nextSongAct.triggered.connect(
            lambda: self.nextToPlayOneSongSig.emit(
                self.songCard_list[self.currentRow()].songInfo))
        menu.showPropertyAct.triggered.connect(
            self.showSongPropertyDialog)
        menu.showAlbumAct.triggered.connect(
            lambda: self.switchToAlbumInterfaceSig.emit(
                self.songCard_list[self.currentRow()].album,
                self.songCard_list[self.currentRow()].singer))
        menu.deleteAct.triggered.connect(self.__showDeleteCardDialog)

        menu.addToMenu.playingAct.triggered.connect(
            lambda: self.addSongToPlayingSignal.emit(
                self.songCard_list[self.currentRow()].songInfo))
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(
                name, [self.songCard_list[self.currentRow()].songInfo]))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(
                [self.songCard_list[self.currentRow()].songInfo]))

    def __connectSongCardSignalToSlot(self, songCard):
        """ 将歌曲卡信号连接到槽 """
        songCard.doubleClicked.connect(self.playSignal)
        songCard.playButtonClicked.connect(self.__playButtonSlot)
        songCard.addSongToPlayingSig.connect(self.addSongToPlayingSignal)
        songCard.clicked.connect(self.setCurrentIndex)
        songCard.switchToSingerInterfaceSig.connect(
            self.switchToSingerInterfaceSig)
        songCard.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterfaceSig)
        songCard.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig)
        songCard.addSongToNewCustomPlaylistSig.connect(
            lambda songInfo: self.addSongsToNewCustomPlaylistSig.emit([songInfo]))


class OnlineSongListWidget(BasicSongListWidget):
    """ 在线音乐歌曲卡列表 """

    playSignal = pyqtSignal(int)                # 将播放列表的当前歌曲切换为指定的歌曲卡
    playOneSongSig = pyqtSignal(dict)           # 重置播放列表为指定的一首歌
    nextToPlayOneSongSig = pyqtSignal(dict)     # 将歌曲添加到下一首播放
    downloadSig = pyqtSignal(dict, str)         # 下载歌曲 (songInfo, quality)

    def __init__(self, parent=None):
        """
        Parameters
        ----------
        parent:
            父级窗口
        """
        super().__init__(None, SongCardType.ONLINE_SONG_CARD,
                         parent, QMargins(30, 0, 30, 0), 0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.__setQss()

    def __playButtonSlot(self, index):
        """ 歌曲卡播放按钮槽函数 """
        self.playSignal.emit(index)
        self.setCurrentIndex(index)

    def contextMenuEvent(self, e):
        """ 重写鼠标右击时间的响应函数 """
        hitIndex = self.indexAt(e.pos()).column()
        # 显示右击菜单
        if hitIndex > -1:
            menu = OnlineSongListContextMenu(self)
            self.__connectContextMenuSignalToSlot(menu)
            menu.exec(self.cursor().pos())

    def __setQss(self):
        """ 设置层叠样式 """
        with open("app/resource/css/song_tab_interface_song_list_widget.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def __adjustHeight(self):
        """ 调整高度 """
        self.resize(self.width(), 60*len(self.songCard_list))

    def wheelEvent(self, e):
        return

    def updateAllSongCards(self, songInfo_list: list):
        """ 更新所有歌曲卡，根据给定的信息决定创建或者删除歌曲卡 """
        super().updateAllSongCards(songInfo_list, self.__connectSongCardSignalToSlot)
        self.__adjustHeight()

    def removeSongCard(self, index):
        super().removeSongCard(index)
        self.__adjustHeight()

    def clearSongCards(self):
        super().clearSongCards()
        self.__adjustHeight()

    def __connectSongCardSignalToSlot(self, songCard):
        """ 将歌曲卡信号连接到槽 """
        songCard.doubleClicked.connect(self.playSignal)
        songCard.playButtonClicked.connect(self.__playButtonSlot)
        songCard.clicked.connect(self.setCurrentIndex)
        songCard.downloadSig.connect(self.downloadSig)

    def __connectContextMenuSignalToSlot(self, menu):
        """ 将右击菜单信号连接到槽函数 """
        menu.showPropertyAct.triggered.connect(
            self.showSongPropertyDialog)
        menu.playAct.triggered.connect(lambda: self.playOneSongSig.emit(
            self.songCard_list[self.currentRow()].songInfo))
        menu.nextSongAct.triggered.connect(lambda: self.nextToPlayOneSongSig.emit(
            self.songCard_list[self.currentRow()].songInfo))
        menu.downloadMenu.downloadSig.connect(lambda quality: self.downloadSig.emit(
            self.songCard_list[self.currentRow()].songInfo, quality))


class LocalSongListContextMenu(DWMMenu):
    """ 本地音乐歌曲卡列表右击菜单 """

    def __init__(self, parent):
        super().__init__("", parent)
        # 创建主菜单动作
        self.playAct = QAction("播放", self)
        self.nextSongAct = QAction("下一首播放", self)
        self.showAlbumAct = QAction("显示专辑", self)
        self.showPropertyAct = QAction("属性", self)
        self.deleteAct = QAction("删除", self)
        # 创建菜单和子菜单
        self.addToMenu = AddToMenu("添加到", self)
        # 将动作添加到菜单中
        self.addActions([self.playAct, self.nextSongAct])
        # 将子菜单添加到主菜单
        self.addMenu(self.addToMenu)
        # 将其余动作添加到主菜单
        self.addActions(
            [self.showAlbumAct, self.showPropertyAct, self.deleteAct])


class OnlineSongListContextMenu(DWMMenu):
    """ 在线音乐歌曲卡列表右击菜单 """

    def __init__(self, parent):
        super().__init__("", parent)
        # 创建主菜单动作
        self.playAct = QAction("播放", self)
        self.nextSongAct = QAction("下一首播放", self)
        self.showPropertyAct = QAction("属性", self)
        # 创建菜单和子菜单
        self.downloadMenu = DownloadMenu(self)
        # 将动作添加到菜单中
        self.addActions([self.playAct, self.nextSongAct])
        # 将子菜单添加到主菜单
        self.addMenu(self.downloadMenu)
        # 将其余动作添加到主菜单
        self.addAction(self.showPropertyAct)
