# coding:utf-8
from pathlib import Path

from common.window_effect import WindowEffect
from PyQt5.QtCore import (QEasingCurve, QEvent, QFile, QPropertyAnimation,
                          QRect, Qt, pyqtSignal)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QApplication, QMenu


class AeroMenu(QMenu):
    """ Aero菜单 """

    def __init__(self, string="", parent=None):
        super().__init__(string, parent)
        # 创建窗口特效
        self.windowEffect = WindowEffect()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground | Qt.WA_StyledBackground)
        self.setObjectName("AeroMenu")
        self.setQss()

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            self.setMenuEffect()
        return QMenu.event(self, e)

    def setMenuEffect(self):
        """ 开启特效 """
        self.windowEffect.setAeroEffect(self.winId())
        self.windowEffect.addShadowEffect(self.winId())

    def setQss(self):
        """ 设置层叠样式 """
        f = QFile(":/qss/menu.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()


class AcrylicMenu(QMenu):
    """ 亚克力菜单 """

    def __init__(self, string="", parent=None, acrylicColor="e5e5e5CC"):
        super().__init__(string, parent)
        self.acrylicColor = acrylicColor
        self.windowEffect = WindowEffect()
        self.__initWidget()

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            self.windowEffect.setAcrylicEffect(
                self.winId(), self.acrylicColor, True)
        return QMenu.event(self, e)

    def __initWidget(self):
        """ 初始化菜单 """
        self.setAttribute(Qt.WA_StyledBackground)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint
        )
        self.setProperty("effect", "acrylic")
        self.setObjectName("acrylicMenu")
        self.setQss()

    def setQss(self):
        """ 设置层叠样式 """
        f = QFile(":/qss/menu.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()


class DWMMenu(QMenu):
    """ 使用 DWM 窗口阴影的菜单 """

    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        # 创建窗口特效
        self.windowEffect = WindowEffect()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setQss()

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            self.windowEffect.addShadowEffect(self.winId())
        return QMenu.event(self, e)

    def setQss(self):
        """ 设置层叠样式表 """
        f = QFile(":/qss/menu.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()


class AddToMenu(DWMMenu):
    """ 添加到菜单 """

    addSongsToPlaylistSig = pyqtSignal(str)  # 将歌曲添加到已存在的自定义播放列表
    playlistFolder = Path('cache/Playlists')

    def __init__(self, title="Add to", parent=None):
        super().__init__(title, parent)
        self.setObjectName("addToMenu")
        # 创建动作
        self.createActions()
        self.setQss()

    def createActions(self):
        """ 创建三个动作 """
        self.playingAct = QAction(
            QIcon(":/images/menu/Playing.png"), self.tr("Now playing"), self)
        self.newPlaylistAct = QAction(
            QIcon(":/images/menu/Add.png"), self.tr("New playlist"), self)

        # 根据播放列表创建动作
        playlistNames = self.__getPlaylistNames()
        self.playlistNameActs = [
            QAction(QIcon(":/images/menu/Album.png"), name, self)
            for name in playlistNames
        ]
        self.action_list = [self.playingAct,
                            self.newPlaylistAct] + self.playlistNameActs
        self.addAction(self.playingAct)
        self.addSeparator()
        self.addActions([self.newPlaylistAct] + self.playlistNameActs)

        # 将添加到播放列表的信号连接到槽函数
        for name, act in zip(playlistNames, self.playlistNameActs):
            # lambda表达式只有在执行的时候才回去寻找变量name，所以需要将name固定下来
            act.triggered.connect(
                lambda checked, playlistName=name: self.addSongsToPlaylistSig.emit(playlistName))

    def __getPlaylistNames(self):
        """ 扫描播放列表文件夹下的播放列表名字 """
        self.playlistFolder.mkdir(parents=True, exist_ok=True)
        playlists = [i.stem for i in self.playlistFolder.glob('*.json')]
        return playlists

    def actionCount(self):
        """ 返回菜单中的动作数 """
        return len(self.action_list)


class DownloadMenu(DWMMenu):
    """ 下载歌曲菜单 """

    downloadSig = pyqtSignal(str)

    def __init__(self, title="Download", parent=None):
        super().__init__(title=title, parent=parent)
        self.standardQualityAct = QAction(self.tr('Standard'), self)
        self.highQualityAct = QAction(self.tr('HQ'), self)
        self.superQualityAct = QAction(self.tr('SQ'), self)
        self.addActions(
            [self.standardQualityAct, self.highQualityAct, self.superQualityAct])
        self.standardQualityAct.triggered.connect(
            lambda: self.downloadSig.emit('Standard quality'))
        self.highQualityAct.triggered.connect(
            lambda: self.downloadSig.emit('High quality'))
        self.superQualityAct.triggered.connect(
            lambda: self.downloadSig.emit('Super quality'))
        self.setQss()


class LineEditMenu(DWMMenu):
    """ 单行输入框右击菜单 """

    def __init__(self, parent):
        super().__init__("", parent)
        self.setObjectName("lineEditMenu")
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        self.setQss()

    def createActions(self):
        # 创建动作
        self.cutAct = QAction(
            QIcon(":/images/menu/Cut.png"),
            self.tr("Cut"),
            self,
            shortcut="Ctrl+X",
            triggered=self.parent().cut,
        )
        self.copyAct = QAction(
            QIcon(":/images/menu/Copy.png"),
            self.tr("Copy"),
            self,
            shortcut="Ctrl+C",
            triggered=self.parent().copy,
        )
        self.pasteAct = QAction(
            QIcon(":/images/menu/Paste.png"),
            self.tr("Paste"),
            self,
            shortcut="Ctrl+V",
            triggered=self.parent().paste,
        )
        self.cancelAct = QAction(
            QIcon(":/images/menu/Cancel.png"),
            self.tr("Cancel"),
            self,
            shortcut="Ctrl+Z",
            triggered=self.parent().undo,
        )
        self.selectAllAct = QAction(
            self.tr("Select all"), self, shortcut="Ctrl+A", triggered=self.parent().selectAll)
        # 创建动作列表
        self.action_list = [
            self.cutAct,
            self.copyAct,
            self.pasteAct,
            self.cancelAct,
            self.selectAllAct,
        ]

    def exec_(self, pos):
        # 删除所有动作
        self.clear()
        # clear之后之前的动作已不再存在故需重新创建
        self.createActions()
        # 初始化属性
        self.setProperty("hasCancelAct", "false")

        # 访问系统剪贴板
        self.clipboard = QApplication.clipboard()

        # 根据剪贴板内容是否为text分两种情况讨论
        if self.clipboard.mimeData().hasText():
            # 再根据3种情况分类讨论
            if self.parent().text():
                self.setProperty("hasCancelAct", "true")
                if self.parent().selectedText():
                    self.addActions(self.action_list)
                else:
                    self.addActions(self.action_list[2:])
            else:
                self.addAction(self.pasteAct)
        else:
            if self.parent().text():
                self.setProperty("hasCancelAct", "true")
                if self.parent().selectedText():
                    self.addActions(
                        self.action_list[:2] + self.action_list[3:])
                else:
                    self.addActions(self.action_list[3:])
            else:
                return

        w = 130+max(self.fontMetrics().width(i.text()) for i in self.actions())
        h = len(self.actions()) * 40 + 10

        # 不能把初始的宽度设置为0px，不然会报警
        self.animation.setStartValue(QRect(pos.x(), pos.y(), 1, 1))
        self.animation.setEndValue(QRect(pos.x(), pos.y(), w, h))
        self.setStyle(QApplication.style())

        # 开始动画
        self.animation.start()
        super().exec_(pos)


class MoreActionsMenu(AeroMenu):
    """ 更多操作菜单 """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.action_list = []
        self.animation = QPropertyAnimation(self, b"geometry")
        self._createActions()
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setObjectName("moreActionsMenu")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)

    def _createActions(self):
        """ 创建动作"""
        raise NotImplementedError("该方法必须被子类实现")

    def exec(self, pos):
        h = len(self.action_list) * 38
        w = max(self.fontMetrics().width(i.text())
                for i in self.action_list) + 65
        self.animation.setStartValue(QRect(pos.x(), pos.y(), 1, h))
        self.animation.setEndValue(QRect(pos.x(), pos.y(), w, h))
        # 开始动画
        self.animation.start()
        super().exec(pos)


class PlayBarMoreActionsMenu(MoreActionsMenu):
    """ 播放栏更多操作菜单 """

    def _createActions(self):
        self.savePlayListAct = QAction(
            QIcon(":/images/menu/Add.png"), self.tr("Save as a playlist"), self)
        self.clearPlayListAct = QAction(
            QIcon(":/images/menu/Clear.png"), self.tr('Clear now playing'), self)
        self.showPlayListAct = QAction(
            QIcon(":/images/menu/Playlist.png"), self.tr("Show now playing list"), self)
        self.fullScreenAct = QAction(
            QIcon(":/images/menu/FullScreen.png"), self.tr("Go full screen"), self)
        self.action_list = [self.showPlayListAct, self.fullScreenAct,
                            self.savePlayListAct, self.clearPlayListAct]
        self.addActions(self.action_list)


class PlayingInterfaceMoreActionsMenu(MoreActionsMenu):
    """ 正在播放界面更多操作菜单 """

    lyricVisibleChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.lyricAct.setProperty('showLyric', True)
        self.lyricAct.triggered.connect(self.__onLyricActionTrigger)
        self.adjustSize()

    def __onLyricActionTrigger(self):
        """ 歌词动作槽函数 """
        isVisible = self.lyricAct.property('showLyric')
        self.lyricAct.setProperty('showLyric', not isVisible)
        self.lyricAct.setText(
            self.tr('Show lyric') if isVisible else self.tr('Hide lyric'))

        self.lyricVisibleChanged.emit(not isVisible)

    def _createActions(self):
        self.savePlayListAct = QAction(
            QIcon(":/images/menu/Add.png"), self.tr("Save as a playlist"), self)
        self.clearPlayListAct = QAction(
            QIcon(":/images/menu/Clear.png"), self.tr('Clear now playing'), self)
        self.lyricAct = QAction(
            QIcon(':/images/menu/Lyric.png'), self.tr('Hide lyric'), self)
        self.movieAct = QAction(
            QIcon(':/images/menu/Movie.png'), self.tr('Watch MV'), self)
        self.action_list = [
            self.savePlayListAct,
            self.clearPlayListAct,
            self.lyricAct,
            self.movieAct
        ]
        self.addActions(self.action_list)
