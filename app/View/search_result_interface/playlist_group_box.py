# coding:utf-8
from copy import deepcopy
from typing import Dict, List

from common.os_utils import moveToTrash
from components.buttons.three_state_button import ThreeStatePushButton
from components.dialog_box.message_dialog import MessageDialog
from components.dialog_box.rename_playlist_dialog import RenamePlaylistDialog
from components.layout.h_box_layout import HBoxLayout
from components.widgets.menu import AddToMenu, DWMMenu
from components.playlist_card import BlurBackground
from components.playlist_card import PlaylistCard as PlaylistCardBase
from PyQt5.QtCore import (QEasingCurve, QFile, QParallelAnimationGroup, QPoint,
                          QPropertyAnimation, QSize, Qt, pyqtSignal)
from PyQt5.QtGui import QContextMenuEvent, QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QGraphicsOpacityEffect,
                             QPushButton, QScrollArea, QToolButton,
                             QWidget)


class PlaylistGroupBox(QScrollArea):
    """ 播放列表分组框 """

    playSig = pyqtSignal(list)                           # 播放自定义播放列表
    nextToPlaySig = pyqtSignal(list)                     # 下一首播放自定义播放列表
    deletePlaylistSig = pyqtSignal(str)                  # 删除播放列表
    renamePlaylistSig = pyqtSignal(dict, dict)           # 重命名播放列表
    switchToPlaylistInterfaceSig = pyqtSignal(str)       # 切换到播放列表界面
    addSongsToPlayingPlaylistSig = pyqtSignal(list)      # 添加歌曲到正在播放
    addSongsToNewCustomPlaylistSig = pyqtSignal(list)    # 添加歌曲到新的自定义的播放列表中
    addSongsToCustomPlaylistSig = pyqtSignal(str, list)  # 添加歌曲到自定义的播放列表中

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.playlists = {}
        self.playlistCard_list = []  # type:List[PlaylistCard]
        self.playlistName2Card_dict = {}  # type:Dict[str, PlaylistCard]
        self.titleButton = QPushButton(self.tr('Playlists'), self)
        self.scrollRightButton = QToolButton(self)
        self.scrollLeftButton = QToolButton(self)
        self.opacityAniGroup = QParallelAnimationGroup(self)
        self.leftOpacityEffect = QGraphicsOpacityEffect(self)
        self.rightOpacityEffect = QGraphicsOpacityEffect(self)
        self.leftOpacityAni = QPropertyAnimation(
            self.leftOpacityEffect, b'opacity', self)
        self.rightOpacityAni = QPropertyAnimation(
            self.rightOpacityEffect, b'opacity', self)
        self.scrollAni = QPropertyAnimation(
            self.horizontalScrollBar(), b'value', self)
        self.scrollWidget = QWidget(self)
        self.hBox = HBoxLayout(self.scrollWidget)
        self.blurBackground = BlurBackground(self.scrollWidget)
        self.leftMask = QWidget(self)
        self.rightMask = QWidget(self)
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedHeight(343)
        self.setWidget(self.scrollWidget)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollLeftButton.raise_()
        self.scrollRightButton.raise_()
        self.blurBackground.lower()
        self.hBox.setSpacing(20)
        self.hBox.setContentsMargins(35, 47, 65, 0)
        self.__setQss()
        self.titleButton.move(37, 0)
        self.leftMask.move(0, 47)
        self.leftMask.resize(35, 296)
        self.rightMask.resize(65, 296)
        self.scrollLeftButton.move(35, 42)
        self.scrollLeftButton.setFixedSize(25, 301)
        self.scrollRightButton.setFixedSize(25, 301)
        self.scrollLeftButton.setIconSize(QSize(15, 15))
        self.scrollRightButton.setIconSize(QSize(15, 15))
        self.scrollLeftButton.setIcon(
            QIcon(':/images/search_result_interface/ChevronLeft.png'))
        self.scrollRightButton.setIcon(
            QIcon(':/images/search_result_interface/ChevronRight.png'))
        self.scrollLeftButton.setGraphicsEffect(self.leftOpacityEffect)
        self.scrollRightButton.setGraphicsEffect(self.rightOpacityEffect)
        self.scrollLeftButton.hide()
        self.scrollRightButton.hide()
        self.leftMask.hide()
        self.resize(1200, 343)
        # 信号连接到槽
        self.horizontalScrollBar().valueChanged.connect(self.__onScrollHorizon)
        self.scrollLeftButton.clicked.connect(self.__onScrollLeftButtonClicked)
        self.scrollRightButton.clicked.connect(
            self.__onScrollRightButtonClicked)

    def __setQss(self):
        """ 设置层叠样式 """
        self.leftMask.setObjectName('leftMask')
        self.rightMask.setObjectName('rightMask')
        self.titleButton.setObjectName('titleButton')

        f = QFile(":/qss/playlist_group_box.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

        self.titleButton.adjustSize()

    def resizeEvent(self, e):
        self.rightMask.move(self.width()-65, 47)
        self.scrollRightButton.move(self.width()-90, 42)
        self.scrollWidget.resize(self.scrollWidget.width(), self.height())

    def __onScrollHorizon(self, value):
        """ 水平滚动槽函数 """
        self.leftMask.setHidden(value == 0)
        self.rightMask.setHidden(value == self.horizontalScrollBar().maximum())
        self.scrollLeftButton.setHidden(value == 0)
        self.scrollRightButton.setHidden(
            value == self.horizontalScrollBar().maximum())

    def __onScrollRightButtonClicked(self):
        """ 向右滚动按钮点击槽函数 """
        v = self.horizontalScrollBar().value()
        self.scrollAni.setStartValue(v)
        self.scrollAni.setEndValue(
            min(v+868, self.horizontalScrollBar().maximum()))
        self.scrollAni.setDuration(450)
        self.scrollAni.setEasingCurve(QEasingCurve.OutQuad)
        self.scrollAni.start()

    def __onScrollLeftButtonClicked(self):
        """ 向左滚动按钮点击槽函数 """
        v = self.horizontalScrollBar().value()
        self.scrollAni.setStartValue(v)
        self.scrollAni.setEndValue(max(v-868, 0))
        self.scrollAni.setDuration(450)
        self.scrollAni.setEasingCurve(QEasingCurve.OutQuad)
        self.scrollAni.start()

    def __showBlurBackground(self, pos: QPoint, picPath: str):
        """ 显示磨砂背景 """
        # 将全局坐标转为窗口坐标
        pos = self.scrollWidget.mapFromGlobal(pos)
        self.blurBackground.setBlurPic(picPath, 40)
        self.blurBackground.move(pos.x() - 35, pos.y() - 20)
        self.blurBackground.show()

    def __showRenamePlaylistDialog(self, oldPlaylist: dict):
        """ 显示重命名播放列表面板 """
        w = RenamePlaylistDialog(oldPlaylist, self.window())
        w.renamePlaylistSig.connect(self.renamePlaylistSig)
        w.exec()

    def renamePlaylist(self, oldPlaylist: dict, newPlaylist: dict):
        """ 重命名播放列表 """
        oldName = oldPlaylist["playlistName"]
        newName = newPlaylist["playlistName"]

        # 更新播放列表卡
        playlistCard = self.playlistName2Card_dict.pop(oldName)
        playlistCard.updateWindow(newPlaylist)

        # 更新字典和列表
        self.playlistName2Card_dict[newName] = playlistCard
        self.playlists[newName] = newPlaylist
        self.playlists.pop(oldName)

    def __showDeleteCardDialog(self, playlistName: str):
        """ 显示删除播放列表卡对话框 """
        title = self.tr("Are you sure you want to delete this?")
        content = self.tr("If you delete") + f' "{playlistName}" ' + \
            self.tr("it won't be on be this device anymore.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(lambda: self.deleteOnePlaylistCard(playlistName))
        w.yesSignal.connect(lambda: self.deletePlaylistSig.emit(playlistName))
        w.exec()

    def deleteOnePlaylistCard(self, playlistName: str):
        """ 删除一个播放列表卡 """
        playlistCard = self.playlistName2Card_dict[playlistName]

        # 从布局中移除播放列表卡
        self.hBox.removeWidget(playlistCard)

        # 从列表中弹出小部件
        self.playlistCard_list.remove(playlistCard)

        # 更新字典
        self.playlists.pop(playlistName)
        self.playlistName2Card_dict.pop(playlistName)

        # 删除播放列表卡和播放列表文件
        playlistCard.deleteLater()
        moveToTrash(f'cache/Playlists/{playlistName}.json')

    def deleteSongs(self, songPaths: list):
        """ 从各个播放列表中删除歌曲 """
        for name, playlist in self.playlists.items():
            songInfo_list = playlist["songInfo_list"]
            playlistCard = self.playlistName2Card_dict[name]

            for songInfo in songInfo_list.copy():
                if songInfo['songPath'] in songPaths:
                    songInfo_list.remove(songInfo)

            playlistCard.updateWindow(playlist)
            self.savePlaylist(playlist)

    def enterEvent(self, e):
        """ 进入窗口时显示滚动按钮 """
        if self.horizontalScrollBar().maximum() == 0:
            return

        # 移除之前的动画
        if self.opacityAniGroup.indexOfAnimation(self.leftOpacityAni) >= 0:
            self.opacityAniGroup.removeAnimation(self.leftOpacityAni)
        if self.opacityAniGroup.indexOfAnimation(self.rightOpacityAni) >= 0:
            self.opacityAniGroup.removeAnimation(self.rightOpacityAni)

        v = self.horizontalScrollBar().value()
        if v != 0:
            self.scrollLeftButton.show()
            self.leftOpacityAni.setStartValue(0)
            self.leftOpacityAni.setEndValue(1)
            self.leftOpacityAni.setDuration(200)
            self.opacityAniGroup.addAnimation(self.leftOpacityAni)

        if v != self.horizontalScrollBar().maximum():
            self.scrollRightButton.show()
            self.rightOpacityAni.setStartValue(0)
            self.rightOpacityAni.setEndValue(1)
            self.rightOpacityAni.setDuration(200)
            self.opacityAniGroup.addAnimation(self.rightOpacityAni)

        self.opacityAniGroup.start()

    def leaveEvent(self, e):
        """ 离开窗口是隐藏滚动按钮 """
        if self.horizontalScrollBar().maximum() == 0:
            return

        # 移除之前的动画
        if self.opacityAniGroup.indexOfAnimation(self.leftOpacityAni) >= 0:
            self.opacityAniGroup.removeAnimation(self.leftOpacityAni)
        if self.opacityAniGroup.indexOfAnimation(self.rightOpacityAni) >= 0:
            self.opacityAniGroup.removeAnimation(self.rightOpacityAni)

        if self.scrollLeftButton.isVisible():
            self.leftOpacityAni.setStartValue(1)
            self.leftOpacityAni.setEndValue(0)
            self.leftOpacityAni.setDuration(200)
            self.opacityAniGroup.addAnimation(self.leftOpacityAni)

        if self.scrollRightButton.isVisible():
            self.rightOpacityAni.setStartValue(1)
            self.rightOpacityAni.setEndValue(0)
            self.leftOpacityAni.setDuration(200)
            self.opacityAniGroup.addAnimation(self.rightOpacityAni)

        self.opacityAniGroup.start()

    def __createOnePlaylistCard(self, playlistName: str, playlist: dict):
        """ 创建一个播放列表卡 """
        playlistCard = PlaylistCard(playlist, self)
        self.playlistCard_list.append(playlistCard)
        self.playlistName2Card_dict[playlistName] = playlistCard
        self.hBox.addWidget(playlistCard)

        # 信号连接到槽
        playlistCard.playSig.connect(self.playSig)
        playlistCard.nextToPlaySig.connect(self.nextToPlaySig)
        playlistCard.showBlurBackgroundSig.connect(self.__showBlurBackground)
        playlistCard.hideBlurBackgroundSig.connect(self.blurBackground.hide)
        playlistCard.renamePlaylistSig.connect(self.__showRenamePlaylistDialog)
        playlistCard.deleteCardSig.connect(self.__showDeleteCardDialog)
        playlistCard.switchToPlaylistInterfaceSig.connect(
            self.switchToPlaylistInterfaceSig)
        playlistCard.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig)
        playlistCard.addSongsToNewCustomPlaylistSig.connect(
            self.addSongsToNewCustomPlaylistSig)
        playlistCard.addSongsToPlayingPlaylistSig.connect(
            self.addSongsToPlayingPlaylistSig)

    def updateWindow(self, playlists: dict):
        """ 更新窗口 """
        if playlists == self.playlists:
            return

        # 显示遮罩
        self.horizontalScrollBar().setValue(0)
        self.leftMask.hide()
        self.rightMask.show()

        # 根据具体情况增减专辑卡
        newCardNum = len(playlists.keys())
        oldCardNum = len(self.playlistCard_list)
        if newCardNum < oldCardNum:
            # 删除部分播放列表卡
            for i in range(oldCardNum - 1, newCardNum - 1, -1):
                playlistCard = self.playlistCard_list.pop()
                self.hBox.removeWidget(playlistCard)
                playlistCard.deleteLater()
        elif newCardNum > oldCardNum:
            # 新增部分播放列表卡
            for name, playlist in list(playlists.items())[oldCardNum:]:
                self.__createOnePlaylistCard(name, playlist)
                QApplication.processEvents()

        self.scrollWidget.adjustSize()

        # 更新部分播放列表卡
        self.playlists = deepcopy(playlists)
        n = oldCardNum if oldCardNum < newCardNum else newCardNum
        for i, playlist in enumerate(list(playlists.values())[:n]):
            self.playlistCard_list[i].updateWindow(playlist)
            QApplication.processEvents()

        self.setStyle(QApplication.style())


class PlaylistCard(PlaylistCardBase):
    """ 播放列表卡 """

    def contextMenuEvent(self, e: QContextMenuEvent):
        menu = PlaylistCardContextMenu(self)
        menu.playAct.triggered.connect(
            lambda: self.playSig.emit(self.songInfo_list))
        menu.nextToPlayAct.triggered.connect(
            lambda: self.nextToPlaySig.emit(self.songInfo_list))
        menu.deleteAct.triggered.connect(
            lambda: self.deleteCardSig.emit(self.playlistName))
        menu.renameAct.triggered.connect(
            lambda: self.renamePlaylistSig.emit(self.playlist))
        menu.addToMenu.playingAct.triggered.connect(
            lambda: self.addSongsToPlayingPlaylistSig.emit(self.songInfo_list))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(self.songInfo_list))
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(name, self.songInfo_list))
        menu.exec(e.globalPos())


class PlaylistCardContextMenu(DWMMenu):
    """ 播放列表卡右击菜单"""

    def __init__(self, parent):
        super().__init__("", parent)
        self.__createActions()
        self.setObjectName("playlistCardContextMenu")
        self.setQss()

    def __createActions(self):
        """ 创建动作 """
        self.playAct = QAction(self.tr("Play"), self)
        self.nextToPlayAct = QAction(self.tr("Play next"), self)
        self.addToMenu = AddToMenu(self.tr("Add to"), self)
        self.renameAct = QAction(self.tr("Rename"), self)
        self.pinToStartMenuAct = QAction(self.tr('Pin to Start'), self)
        self.deleteAct = QAction(self.tr("Delete"), self)

        # 添加动作到菜单
        self.addActions([self.playAct, self.nextToPlayAct])
        # 将子菜单添加到主菜单
        self.addMenu(self.addToMenu)
        self.addActions(
            [self.renameAct, self.pinToStartMenuAct, self.deleteAct])
