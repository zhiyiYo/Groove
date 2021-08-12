# coding:utf-8
from app.components.dialog_box.message_dialog import MessageDialog
from app.components.buttons.three_state_button import ThreeStatePushButton
from app.components.menu import AddToMenu, DWMMenu
from app.components.song_list_widget import BasicSongListWidget, SongCardType
from PyQt5.QtCore import QMargins, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QAction, QWidget, QPushButton


class SongGroupBox(QWidget):
    """ 歌曲分组框 """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.songInfo_list = []
        self.titleButton = QPushButton('歌曲', self)
        self.showAllButton = ThreeStatePushButton(
            {
                "normal": "app/resource/images/search_result_interface/ShowAll_normal.png",
                "hover": "app/resource/images/search_result_interface/ShowAll_hover.png",
                "pressed": "app/resource/images/search_result_interface/ShowAll_pressed.png",
            },
            '  显示全部',
            (14, 14),
            self,
        )
        self.songListWidget = SongListWidget(self)
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1200, 500)
        self.setMinimumHeight(47)
        self.songListWidget.move(0, 47)
        self.titleButton.move(37, 0)
        self.__setQss()

    def __setQss(self):
        """ 设置层叠样式 """
        self.titleButton.setObjectName('titleButton')
        self.showAllButton.setObjectName('showAllButton')
        with open('app/resource/css/song_group_box.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())
        self.titleButton.adjustSize()
        self.showAllButton.adjustSize()

    def resizeEvent(self, e):
        self.songListWidget.resize(self.width(), self.songListWidget.height())
        self.showAllButton.move(self.width()-self.showAllButton.width()-30, 0)

    def updateWindow(self, songInfo_list):
        """ 更新窗口 """
        if songInfo_list == self.songInfo_list:
            return
        # 只保留前五首
        self.songInfo_list = songInfo_list[:5]
        self.songListWidget.updateAllSongCards(self.songInfo_list)
        self.setFixedHeight(47+self.songListWidget.height())


class SongListWidget(BasicSongListWidget):
    """ 歌曲卡列表 """

    playSignal = pyqtSignal(dict)  # 将播放列表的当前歌曲切换为指定的歌曲卡
    playOneSongSig = pyqtSignal(dict)  # 重置播放列表为指定的一首歌
    nextToPlayOneSongSig = pyqtSignal(dict)
    switchToAlbumInterfaceSig = pyqtSignal(str, str)

    def __init__(self, parent):
        """
        Parameters
        ----------
        parent:
            父级窗口
        """
        super().__init__(None, SongCardType.NO_CHECKBOX_SONG_CARD,
                         parent, QMargins(30, 0, 30, 0), 0)
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.__setQss()

    def __playButtonSlot(self, index):
        """ 歌曲卡播放按钮槽函数 """
        self.playSignal.emit(self.songCard_list[index].songInfo)
        self.setCurrentIndex(index)

    def contextMenuEvent(self, e):
        """ 重写鼠标右击时间的响应函数 """
        hitIndex = self.indexAt(e.pos()).column()
        # 显示右击菜单
        if hitIndex > -1:
            contextMenu = SongCardListContextMenu(self)
            self.__connectMenuSignalToSlot(contextMenu)
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

    def __connectMenuSignalToSlot(self, contextMenu):
        """ 信号连接到槽 """
        contextMenu.playAct.triggered.connect(
            lambda: self.playOneSongSig.emit(
                self.songCard_list[self.currentRow()].songInfo))
        contextMenu.nextSongAct.triggered.connect(
            lambda: self.nextToPlayOneSongSig.emit(
                self.songCard_list[self.currentRow()].songInfo))
        # 显示属性面板
        contextMenu.showPropertyAct.triggered.connect(
            self.showSongPropertyDialog)
        # 显示专辑界面
        contextMenu.showAlbumAct.triggered.connect(
            lambda: self.switchToAlbumInterfaceSig.emit(
                self.songCard_list[self.currentRow()].album,
                self.songCard_list[self.currentRow()].songer,
            )
        )
        # 删除歌曲卡
        contextMenu.deleteAct.triggered.connect(self.__showDeleteCardDialog)
        # 将歌曲添加到正在播放列表
        contextMenu.addToMenu.playingAct.triggered.connect(
            lambda: self.addSongToPlayingSignal.emit(
                self.songCard_list[self.currentRow()].songInfo))
        # 将歌曲添加到已存在的自定义播放列表中
        contextMenu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(
                name, [self.songCard_list[self.currentRow()].songInfo]))
        # 将歌曲添加到新建的播放列表
        contextMenu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(
                [self.songCard_list[self.currentRow()].songInfo]))

    def __connectSongCardSignalToSlot(self, songCard):
        """ 将歌曲卡信号连接到槽 """
        songCard.addSongToPlayingSig.connect(self.addSongToPlayingSignal)
        songCard.doubleClicked.connect(
            lambda index: self.playSignal.emit(self.songCard_list[index].songInfo))
        songCard.playButtonClicked.connect(self.__playButtonSlot)
        songCard.clicked.connect(self.setCurrentIndex)
        songCard.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterfaceSig)
        songCard.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig)
        songCard.addSongToNewCustomPlaylistSig.connect(
            lambda songInfo: self.addSongsToNewCustomPlaylistSig.emit([songInfo]))


class SongCardListContextMenu(DWMMenu):
    """ 歌曲卡列表右击菜单 """

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
