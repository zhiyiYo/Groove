# coding:utf-8
from common.crawler.crawler_base import SongQuality
from common.icon import Icon
from common.os_utils import getPlaylistNames
from common.style_sheet import setStyleSheet
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtWidgets import QAction, QMenu, QWidget


class Menu(QMenu):
    """ Context menu """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.playAct = QAction(self.tr('Play'), self)
        self.addToMenu = AddToMenu(self.tr('Add to'), self)
        self.removeAct = QAction(self.tr('Remove'), self)
        self.moveUpAct = QAction(self.tr('Move up'), self)
        self.moveDownAct = QAction(self.tr('Move down'), self)
        self.showAlbumAct = QAction(self.tr('Show album'), self)
        self.propertyAct = QAction(self.tr('Properties'), self)
        self.viewOnlineAct = QAction(self.tr('View online'), self)
        self.selectAct = QAction(self.tr('Select'), self)
        self.action_list = [
            self.playAct, self.removeAct, self.moveUpAct,
            self.moveDownAct, self.showAlbumAct, self.viewOnlineAct,
            self.propertyAct, self.selectAct
        ]
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.addAction(self.playAct)
        self.addMenu(self.addToMenu)
        self.addActions(self.action_list[1:-1])
        self.addSeparator()
        self.addAction(self.selectAct)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)

        self.setObjectName('playingInterfaceMenu')
        setStyleSheet(self, 'menu')


class AddToMenu(QMenu):
    """ Add to menu """

    addSongsToPlaylistSig = pyqtSignal(str)  # 将歌曲添加到已存在的自定义播放列表

    def __init__(self, title='Add to', parent=None):
        super().__init__(title, parent)

        self.playingAct = QAction(
            Icon(':/images/playing_interface/Playing_white.png'), self.tr('Now playing'), self)
        self.newPlaylistAct = QAction(
            Icon(':/images/playing_interface/Add_20_20.png'), self.tr('New playlist'), self)
        names = getPlaylistNames()
        self.playlistActs = [QAction(Icon(
            ":/images/playing_interface/Album.png"), i, self) for i in names]

        self.addAction(self.playingAct)
        self.addSeparator()
        self.addActions([self.newPlaylistAct]+self.playlistActs)

        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        for name, act in zip(names, self.playlistActs):
            act.triggered.connect(
                lambda checked, playlistName=name: self.addSongsToPlaylistSig.emit(playlistName))

        self.setObjectName('blackAddToMenu')
        setStyleSheet(self, 'menu')

    def getPopupPos(self, widget: QWidget):
        """ get suitable popup position

        Parameters
        ----------
        widget: QWidget
            the widget that triggers the pop-up menu
        """
        pos = widget.mapToGlobal(QPoint())
        x = pos.x() + widget.width() + 5
        y = pos.y() + int(widget.height() / 2 - (13 + 38 * len(self.actions())) / 2)
        return QPoint(x, y)


class DownloadMenu(QMenu):
    """ Download online music menu """

    downloadSig = pyqtSignal(SongQuality)

    def __init__(self, title="Download", parent=None):
        super().__init__(title=title, parent=parent)
        self.standardQualityAct = QAction(self.tr('Standard'), self)
        self.highQualityAct = QAction(self.tr('HQ'), self)
        self.superQualityAct = QAction(self.tr('SQ'), self)
        self.addActions(
            [self.standardQualityAct, self.highQualityAct, self.superQualityAct])

        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setObjectName('blackDownloadMenu')
        setStyleSheet(self, 'menu')

        self.standardQualityAct.triggered.connect(
            lambda: self.downloadSig.emit(SongQuality.STANDARD))
        self.highQualityAct.triggered.connect(
            lambda: self.downloadSig.emit(SongQuality.HIGH))
        self.superQualityAct.triggered.connect(
            lambda: self.downloadSig.emit(SongQuality.SUPER))