# coding:utf-8
from common.database.entity import SingerInfo
from common.os_utils import getSingerAvatarPath
from common.signal_bus import signalBus
from components.buttons.blur_button import BlurButton
from components.widgets.check_box import CheckBox
from components.widgets.label import ClickableLabel
from components.widgets.menu import AddToMenu
from components.widgets.perspective_widget import PerspectiveWidget
from PyQt5.QtCore import QPoint, QPropertyAnimation, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QApplication, QGraphicsOpacityEffect, QWidget


class SingerAvatar(QWidget):
    """ Singer avatar """

    def __init__(self, singer: str, size=200, parent=None):
        """
        Parameters
        ----------
        singer: str
            singer name

        size: int
            size of avatar

        parent:
            parent window
        """
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setSinger(singer)

    def setSinger(self, singer: str):
        """ set singer

        Parameters
        ----------
        singer: str
            singer name
        """
        self.singer = singer
        self.imagePath = getSingerAvatarPath(singer)
        self.__pixmap = QPixmap(self.imagePath)
        self.update()

    def paintEvent(self, e):
        """ paint avatar """
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        w = self.width()
        painter.setPen(QPen(QColor(0, 0, 0, 25), 2))
        painter.setBrush(QBrush(self.__pixmap.scaled(
            w, w, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)))
        painter.drawRoundedRect(self.rect(), w//2, w//2)


class SingerCardBase(PerspectiveWidget):
    """ Singer card base class """

    playSignal = pyqtSignal(str)                            # 播放
    nextPlaySignal = pyqtSignal(str)                        # 下一首播放
    addToPlayingSignal = pyqtSignal(str)                    # 将歌手添加到正在播放
    checkedStateChanged = pyqtSignal(QWidget, bool)         # 选中状态改变
    addSingerToNewCustomPlaylistSig = pyqtSignal(str)       # 将歌手添加到新建的播放列表
    addSingerToCustomPlaylistSig = pyqtSignal(str, str)     # 将歌手添加到自定义播放列表
    showBlurSingerBackgroundSig = pyqtSignal(QPoint, str)   # 显示磨砂背景
    hideBlurSingerBackgroundSig = pyqtSignal()              # 隐藏磨砂背景

    def __init__(self, singerInfo: SingerInfo, parent=None):
        super().__init__(parent, True)
        self.__setSingerInfo(singerInfo)
        self.isChecked = False
        self.isInSelectionMode = False

        self.singerLabel = ClickableLabel(self.singer, self)
        self.avatar = SingerAvatar(self.singer, parent=self)
        self.playButton = BlurButton(
            self,
            (30, 65),
            ":/images/album_tab_interface/Play.png",
            self.avatar.imagePath,
            self.tr('Play')
        )
        self.addToButton = BlurButton(
            self,
            (100, 65),
            ":/images/album_tab_interface/Add.png",
            self.avatar.imagePath,
            self.tr('Add to')
        )
        self.checkBox = CheckBox(self)
        self.checkBoxOpacityEffect = QGraphicsOpacityEffect(self)
        self.hideCheckBoxAni = QPropertyAnimation(
            self.checkBoxOpacityEffect, b'opacity', self)

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setFixedSize(210, 265)
        self.setAttribute(Qt.WA_StyledBackground)
        self.singerLabel.setAlignment(Qt.AlignCenter)
        self.singerLabel.setWordWrap(True)

        # initialize layout
        self.singerLabel.setFixedWidth(210)
        self.avatar.move(5, 5)
        self.playButton.move(35, 70)
        self.addToButton.move(105, 70)
        self.singerLabel.move(0, 215)
        self.checkBox.move(178, 8)

        # add opacity effect to check box
        self.checkBox.setFocusPolicy(Qt.NoFocus)
        self.checkBox.setGraphicsEffect(self.checkBoxOpacityEffect)

        # hide buttons
        self.playButton.hide()
        self.addToButton.hide()

        # set animation
        self.hideCheckBoxAni.setStartValue(1)
        self.hideCheckBoxAni.setEndValue(0)
        self.hideCheckBoxAni.setDuration(150)
        self.checkBox.hide()

        # set properties and ID of widgets
        self.setObjectName("singerCard")
        self.singerLabel.setObjectName("singerLabel")
        self.setProperty("isChecked", "False")
        self.singerLabel.setProperty("isChecked", "False")

        # connect signal to slot
        self.playButton.clicked.connect(lambda: self.playSignal.emit(self.singer))
        self.singerLabel.clicked.connect(
            lambda: signalBus.switchToSingerInterfaceSig.emit(self.singer))
        self.addToButton.clicked.connect(self.__showAddToMenu)
        self.checkBox.stateChanged.connect(self.__onCheckedStateChanged)

    def __setSingerInfo(self, singerInfo: SingerInfo):
        """ set singer information """
        self.singerInfo = singerInfo
        self.singer = self.singerInfo.singer

    def __showAddToMenu(self):
        """ show add to menu """
        menu = AddToMenu(parent=self)
        pos = self.mapToGlobal(QPoint(
            self.addToButton.x(), self.addToButton.y()))
        x = pos.x() + self.addToButton.width() + 5
        y = pos.y() + int(
            self.addToButton.height() / 2 - (13 + 38 * menu.actionCount()) / 2)
        menu.playingAct.triggered.connect(
            lambda: self.addToPlayingSignal.emit(self.singer))
        menu.newPlaylistAct.triggered.connect(
            lambda: self.addSingerToNewCustomPlaylistSig.emit(self.singer))
        menu.addSongsToPlaylistSig.connect(
            lambda name: self.addSingerToCustomPlaylistSig.emit(name, self.singer))
        menu.exec(QPoint(x, y))

    def __onCheckedStateChanged(self):
        """ check box checked state changed slot """
        self.isChecked = self.checkBox.isChecked()
        self.checkedStateChanged.emit(self, self.isChecked)

        # update text and background color
        self.setProperty("isChecked", str(self.isChecked))
        self.singerLabel.setProperty("isChecked", str(self.isChecked))
        self.setStyle(QApplication.style())

    def enterEvent(self, e):
        # show blur background
        pos = self.mapToGlobal(QPoint(0, 0))  # type:QPoint
        self.showBlurSingerBackgroundSig.emit(pos, self.avatar.imagePath)

        # hide button in selection mode
        self.playButton.setHidden(self.isInSelectionMode)
        self.addToButton.setHidden(self.isInSelectionMode)

    def leaveEvent(self, e):
        self.hideBlurSingerBackgroundSig.emit()
        self.addToButton.hide()
        self.playButton.hide()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        if e.button() == Qt.LeftButton:
            if self.isInSelectionMode:
                self.setChecked(not self.isChecked)
            else:
                signalBus.switchToSingerInterfaceSig.emit(self.singer)

    def updateWindow(self, singerInfo: SingerInfo):
        """ update singer card """
        if singerInfo == self.singerInfo:
            return

        self.__setSingerInfo(singerInfo)
        self.avatar.setSinger(self.singer)
        self.singerLabel.setText(self.singer)
        self.playButton.setBlurPic(self.avatar.imagePath, 40)
        self.addToButton.setBlurPic(self.avatar.imagePath, 40)

    def setChecked(self, isChecked: bool):
        """ set the checked state """
        self.checkBox.setChecked(isChecked)

    def setSelectionModeOpen(self, isOpen: bool):
        """ set whether to open selection mode """
        if self.isInSelectionMode == isOpen:
            return

        if isOpen:
            self.checkBoxOpacityEffect.setOpacity(1)
            self.checkBox.show()

        self.isInSelectionMode = isOpen

    def _onSelectActionTriggered(self):
        """ select action triggered slot """
        self.setSelectionModeOpen(True)
        self.setChecked(True)
