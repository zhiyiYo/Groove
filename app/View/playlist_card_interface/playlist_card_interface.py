# coding:utf-8
from common.database.entity import Playlist
from common.library import Library
from components.buttons.three_state_button import ThreeStatePushButton
from components.playlist_card import GridPlaylistCardView, PlaylistCardType
from components.selection_mode_interface import (
    PlaylistSelectionModeInterface, SelectionModeBarType)
from components.widgets.menu import AeroMenu
from PyQt5.QtCore import QFile, QMargins, QPoint, Qt, pyqtSignal
from PyQt5.QtWidgets import QAction, QLabel, QPushButton, QWidget


class PlaylistCardInterface(PlaylistSelectionModeInterface):
    """ 播放列表卡界面 """

    createPlaylistSig = pyqtSignal()

    def __init__(self, library: Library, parent=None):
        self.sortMode = "modifiedTime"
        self.library = library
        self.playlists = library.playlists

        view = GridPlaylistCardView(
            library,
            self.playlists,
            PlaylistCardType.PLAYLIST_CARD,
            margins=QMargins(15, 0, 15, 0),
        )
        super().__init__(library, view, SelectionModeBarType.PLAYLIST_CARD, parent)

        self.playlistCards = self.playlistCardView.playlistCards

        self.__createWidgets()
        self.__initWidget()

    def __createWidgets(self):
        """ 创建小部件 """
        # 创建白色遮罩
        self.whiteMask = QWidget(self)
        self.playlistLabel = QLabel(self.tr("Playlist"), self)
        self.sortModeLabel = QLabel(self.tr("Sort by:"), self)
        self.sortModeButton = QPushButton(self.tr("Date modified"), self)
        self.createPlaylistButton = ThreeStatePushButton(
            {
                "normal": ":/images/playlist_card_interface/Add_normal.png",
                "hover": ":/images/playlist_card_interface/Add_hover.png",
                "pressed": ":/images/playlist_card_interface/Add_pressed.png",
            },
            self.tr(" New playlist"),
            (19, 19),
            self,
        )

        # 创建导航标签
        self.guideLabel = QLabel(
            self.tr('There is nothing to display here. Try a different filter.'), self)

        # 创建排序菜单
        self.sortModeMenu = AeroMenu(parent=self)
        self.sortByModifiedTimeAct = QAction(
            self.tr("Date modified"), self, triggered=lambda: self.__sortPlaylist("modifiedTime"))
        self.sortByAToZAct = QAction(
            self.tr("A to Z"), self, triggered=lambda: self.__sortPlaylist("AToZ"))
        self.sortActs = [self.sortByModifiedTimeAct, self.sortByAToZAct]

        # 记录当前的排序方式
        self.currentSortAct = self.sortByModifiedTimeAct

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1270, 760)
        self.vBox.setContentsMargins(0, 175, 0, 120)
        self.guideLabel.setHidden(bool(self.playlistCards))
        self.sortModeMenu.addActions(self.sortActs)
        self.guideLabel.raise_()

        self.__setQss()
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        """ 初始化布局 """
        self.guideLabel.move(44, 196)
        self.playlistLabel.move(30, 54)
        self.createPlaylistButton.move(30, 131)
        self.sortModeLabel.move(
            self.createPlaylistButton.geometry().right()+30, 130)
        self.sortModeButton.move(self.sortModeLabel.geometry().right()+7, 130)

    def __setQss(self):
        """ 设置层叠样式 """
        self.sortModeLabel.setMinimumSize(50, 28)
        self.guideLabel.setMinimumSize(600, 40)
        self.playlistLabel.setObjectName("playlistLabel")
        self.sortModeLabel.setObjectName("sortModeLabel")
        self.sortModeButton.setObjectName("sortModeButton")
        self.createPlaylistButton.setObjectName("createPlaylistButton")
        self.sortModeMenu.setObjectName("sortModeMenu")
        self.sortModeMenu.setProperty("modeNumber", "2")
        self.guideLabel.setObjectName('guideLabel')

        f = QFile(":/qss/playlist_card_interface.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

        self.createPlaylistButton.adjustSize()
        self.sortModeLabel.adjustSize()
        self.guideLabel.adjustSize()

    def resizeEvent(self, e):
        """ 调整小部件尺寸和位置 """
        super().resizeEvent(e)
        self.whiteMask.resize(self.width() - 15, 175)

    def __sortPlaylist(self, key):
        """ 排序播放列表 """
        self.sortMode = key
        if key == "modifiedTime":
            self.sortModeButton.setText(self.tr("Date modified"))
            self.currentSortAct = self.sortByModifiedTimeAct
            self.playlistCardView.setSortMode('modifiedTime')
        else:
            self.sortModeButton.setText(self.tr("A to Z"))
            self.currentSortAct = self.sortByAToZAct
            self.playlistCardView.setSortMode('A To Z')

    def __showSortModeMenu(self):
        """ 显示排序方式菜单 """
        self.sortModeMenu.setDefaultAction(self.currentSortAct)
        index = self.sortActs.index(self.currentSortAct)
        pos = self.sender().pos()-QPoint(0, 37*index+1)
        self.sortModeMenu.exec(self.mapToGlobal(pos))

    def addPlaylistCard(self, name: str, playlist: Playlist):
        """ 添加一个播放列表卡 """
        super().addPlaylistCard(name, playlist)
        self.guideLabel.hide()

    def deletePlaylistCard(self, name: str):
        """ 删除一个播放列表卡 """
        super().deletePlaylistCard(name)
        self.guideLabel.setHidden(bool(self.playlistCards))

    def __connectSignalToSlot(self):
        """ 将信号连接到槽 """
        self.sortModeButton.clicked.connect(self.__showSortModeMenu)
        self.createPlaylistButton.clicked.connect(self.createPlaylistSig)
