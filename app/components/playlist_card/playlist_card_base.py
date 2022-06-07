# coding:utf-8
import sys

from common.auto_wrap import autoWrap
from common.database.entity import Playlist
from common.image_utils import DominantColor, readImage
from common.os_utils import getCoverPath
from common.signal_bus import signalBus
from components.buttons.blur_button import BlurButton
from components.widgets.check_box import CheckBox
from components.widgets.menu import AddToMenu
from components.widgets.perspective_widget import PerspectiveWidget
from PIL import Image
from PIL.ImageFilter import GaussianBlur
from PyQt5.QtCore import QEvent, QPoint, QPropertyAnimation, Qt, pyqtSignal
from PyQt5.QtGui import (QBrush, QColor, QContextMenuEvent, QLinearGradient,
                         QMouseEvent, QPainter, QPixmap)
from PyQt5.QtWidgets import (QApplication, QGraphicsOpacityEffect, QLabel,
                             QVBoxLayout, QWidget)


class PlaylistCardBase(PerspectiveWidget):
    """ Playlist card base class """

    playSig = pyqtSignal(str)
    nextToPlaySig = pyqtSignal(str)
    deleteCardSig = pyqtSignal(str)
    hideBlurBackgroundSig = pyqtSignal()
    renamePlaylistSig = pyqtSignal(str)
    checkedStateChanged = pyqtSignal(QWidget, bool)
    showBlurBackgroundSig = pyqtSignal(QPoint, str)
    addSongsToPlayingPlaylistSig = pyqtSignal(str)      # 添加歌曲到正在播放
    addSongsToNewCustomPlaylistSig = pyqtSignal(str)    # 添加歌曲到新的自定义的播放列表中
    addSongsToCustomPlaylistSig = pyqtSignal(str, str)  # 添加歌曲到自定义的播放列表中

    def __init__(self, playlist: Playlist, parent=None):
        super().__init__(parent, True)
        self.isChecked = False
        self.isInSelectionMode = False
        self.__getPlaylistInfo(playlist)

        self.vBoxLayout = QVBoxLayout(self)
        self.playlistCover = PlaylistCover(self)
        self.playButton = BlurButton(
            self,
            (35, 70),
            ":/images/album_tab_interface/Play.png",
            self.coverPath,
            self.tr('Play')
        )
        self.addToButton = BlurButton(
            self,
            (105, 70),
            ":/images/album_tab_interface/Add.png",
            self.coverPath,
            self.tr('Add to')
        )
        self.nameLabel = QLabel(self.name, self)
        self.countLabel = QLabel(
            str(self.count)+self.tr(" songs"), self)

        self.checkBox = CheckBox(self, forwardTargetWidget=self.playlistCover)
        self.checkBoxOpacityEffect = QGraphicsOpacityEffect(self)
        self.hideCheckBoxAni = QPropertyAnimation(
            self.checkBoxOpacityEffect, b'opacity', self)

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setFixedSize(298, 288)
        self.setAttribute(Qt.WA_StyledBackground)

        # hide buttons and check box
        self.checkBox.hide()
        self.playButton.hide()
        self.addToButton.hide()
        self.countLabel.setMinimumWidth(200)
        self.checkBox.setFocusPolicy(Qt.NoFocus)
        self.checkBox.setGraphicsEffect(self.checkBoxOpacityEffect)
        self.playlistCover.setPlaylistCover(self.coverPath)

        # set animation
        self.hideCheckBoxAni.setStartValue(1)
        self.hideCheckBoxAni.setEndValue(0)
        self.hideCheckBoxAni.setDuration(150)

        # set properties and ID
        self.setObjectName("playlistCard")
        self.nameLabel.setObjectName("nameLabel")
        self.countLabel.setObjectName("countLabel")
        self.setProperty("isChecked", "False")
        self.nameLabel.setProperty("isChecked", "False")
        self.countLabel.setProperty("isChecked", "False")

        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        """ 初始化布局 """
        self.vBoxLayout.setContentsMargins(5, 5, 0, 0)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addWidget(self.playlistCover)
        self.vBoxLayout.addSpacing(11)
        self.vBoxLayout.addWidget(self.nameLabel)
        self.vBoxLayout.addSpacing(5)
        self.vBoxLayout.addWidget(self.countLabel)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.checkBox.move(262, 21)
        self.playButton.move(80, 68)
        self.addToButton.move(148, 68)
        self.__adjustLabel()

    def __getPlaylistInfo(self, playlist: Playlist):
        """ get playlist information """
        self.playlist = playlist
        self.name = playlist.name
        self.count = playlist.count
        singer = playlist.singer or ''
        album = playlist.album or ''
        self.coverPath = getCoverPath(singer, album, 'playlist_small')

    def __adjustLabel(self):
        """ adjust the text of label """
        newText, isWordWrap = autoWrap(self.name, 32)
        if isWordWrap:
            # 添加省略号
            index = newText.index("\n")
            fontMetrics = self.nameLabel.fontMetrics()
            secondLineText = fontMetrics.elidedText(
                newText[index + 1:], Qt.ElideRight, 288)
            newText = newText[: index + 1] + secondLineText
            self.nameLabel.setText(newText)

        self.nameLabel.adjustSize()
        self.countLabel.adjustSize()

    def enterEvent(self, e):
        # show blur background
        pos = self.mapToGlobal(QPoint(0, 0))  # type:QPoint
        self.showBlurBackgroundSig.emit(pos, self.coverPath)

        if not self.isInSelectionMode:
            self.playButton.fadeIn()
            self.addToButton.fadeIn()

    def leaveEvent(self, e):
        self.hideBlurBackgroundSig.emit()
        self.addToButton.hide()
        self.playButton.hide()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        if e.button() == Qt.LeftButton:
            if self.isInSelectionMode:
                self.setChecked(not self.isChecked)
            else:
                signalBus.switchToPlaylistInterfaceSig.emit(self.name)

    def contextMenuEvent(self, e: QContextMenuEvent):
        if sys.platform == "win32":
            return super().contextMenuEvent(e)

        event = QMouseEvent(
            QEvent.MouseButtonRelease,
            e.pos(),
            Qt.RightButton,
            Qt.RightButton,
            Qt.NoModifier
        )
        QApplication.sendEvent(self, event)
        return super().contextMenuEvent(e)

    def updateWindow(self, playlist: Playlist):
        """ update playlist card """
        self.__getPlaylistInfo(playlist)
        self.playlistCover.setPlaylistCover(self.coverPath)
        self.nameLabel.setText(self.name)
        self.countLabel.setText(str(self.count)+self.tr(" songs"))
        self.playButton.setBlurPic(self.coverPath, 40)
        self.addToButton.setBlurPic(self.coverPath, 40)
        self.__adjustLabel()

    def __onCheckedStateChanged(self):
        """ checked state changed slot """
        self.isChecked = self.checkBox.isChecked()
        self.checkedStateChanged.emit(self, self.isChecked)

        # update style
        self.setProperty("isChecked", str(self.isChecked))
        self.nameLabel.setProperty("isChecked", str(self.isChecked))
        self.countLabel.setProperty("isChecked", str(self.isChecked))
        self.setStyle(QApplication.style())

    def setChecked(self, isChecked: bool):
        """ set checked state """
        self.checkBox.setChecked(isChecked)

    def setSelectionModeOpen(self, isOpen: bool):
        """ set whether to open selection mode """
        if self.isInSelectionMode == isOpen:
            return

        if isOpen:
            self.checkBoxOpacityEffect.setOpacity(1)
            self.checkBox.show()

        self.isInSelectionMode = isOpen

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.checkBox.stateChanged.connect(self.__onCheckedStateChanged)
        self.playButton.clicked.connect(lambda: self.playSig.emit(self.name))
        self.addToButton.clicked.connect(self.__showAddToMenu)

    def __showAddToMenu(self):
        """ show add to menu """
        menu = AddToMenu(parent=self)
        pos = self.mapToGlobal(QPoint(
            self.addToButton.x(), self.addToButton.y()))
        x = pos.x() + self.addToButton.width() + 5
        y = pos.y() + int(
            self.addToButton.height() / 2 - (13 + 38 * menu.actionCount()) / 2)
        menu.playingAct.triggered.connect(
            lambda: self.addSongsToPlayingPlaylistSig.emit(self.name))
        menu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(self.name))
        menu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(name, self.name))
        menu.exec(QPoint(x, y))

    def _onSelectActionTrigerred(self):
        """ select action triggered slot """
        self.setSelectionModeOpen(True)
        self.setChecked(True)


class PlaylistCover(QWidget):
    """ Playlist cover """

    def __init__(self, parent=None, picPath: str = ""):
        super().__init__(parent)
        self.setFixedSize(288, 196)
        self.__blurPix = None
        self.__playlistCoverPix = None
        self.coverPath = ''
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setPlaylistCover(picPath)

    def setPlaylistCover(self, picPath: str):
        """ set playlist cover """
        if picPath == self.coverPath:
            return

        # blur cover
        self.coverPath = picPath
        img = readImage(picPath).resize((288, 288)).crop((0, 46, 288, 242))
        self.__blurPix = img.filter(GaussianBlur(40)).toqpixmap()
        self.__playlistCoverPix = QPixmap(picPath).scaled(
            135, 135, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)  # type:QPixmap

        # get dominant color of cover
        self.dominantRgb = DominantColor.getDominantColor(picPath)
        self.update()

    def paintEvent(self, e):
        """ paint playlist card """
        super().paintEvent(e)
        if not self.__blurPix:
            return

        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)

        # paint blurred cover
        painter.drawPixmap(0, 0, self.__blurPix)

        # paint dominant color
        gradientColor = QLinearGradient(0, self.height(), 0, 0)
        gradientColor.setColorAt(0, QColor(*self.dominantRgb, 128))
        gradientColor.setColorAt(1, QColor(*self.dominantRgb, 10))
        painter.setBrush(QBrush(gradientColor))
        painter.drawRect(self.rect())

        # paint cover
        painter.drawPixmap(76, 31, self.__playlistCoverPix)

        # paint line
        painter.setBrush(QBrush(QColor(*self.dominantRgb, 100)))
        painter.drawRect(96, 21, self.width() - 192, 5)
        painter.setBrush(QBrush(QColor(*self.dominantRgb, 210)))
        painter.drawRect(86, 26, self.width() - 172, 5)
