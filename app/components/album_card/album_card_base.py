# coding:utf-8
from common.auto_wrap import autoWrap
from common.database.entity import AlbumInfo
from common.os_utils import getCoverPath
from common.signal_bus import signalBus
from components.buttons.blur_button import BlurButton
from components.widgets.check_box import CheckBox
from components.widgets.label import ClickableLabel, PixmapLabel
from components.widgets.menu import AddToMenu
from components.widgets.perspective_widget import PerspectiveWidget
from PyQt5.QtCore import QPoint, QPropertyAnimation, Qt, pyqtSignal
from PyQt5.QtGui import QFont, QFontMetrics, QPixmap
from PyQt5.QtWidgets import (QApplication, QGraphicsOpacityEffect, QLabel,
                             QVBoxLayout, QWidget)


class AlbumCardBase(PerspectiveWidget):
    """ Album card base class """

    deleteCardSig = pyqtSignal(str, str)                     # 删除专辑卡
    nextPlaySignal = pyqtSignal(str, str)                    # 下一首播放
    addToPlayingSignal = pyqtSignal(str, str)                # 将专辑添加到正在播放
    checkedStateChanged = pyqtSignal(QWidget, bool)          # 选中状态改变
    addAlbumToNewCustomPlaylistSig = pyqtSignal(str, str)    # 将专辑添加到新建的播放列表
    addAlbumToCustomPlaylistSig = pyqtSignal(str, str, str)  # 将专辑添加到自定义播放列表
    showAlbumInfoEditDialogSig = pyqtSignal(str, str)        # 显示专辑信息面板信号
    showBlurAlbumBackgroundSig = pyqtSignal(QPoint, str)     # 显示磨砂背景
    hideBlurAlbumBackgroundSig = pyqtSignal()                # 隐藏磨砂背景

    def __init__(self, albumInfo: AlbumInfo, parent=None):
        super().__init__(parent, True)
        self.__setAlbumInfo(albumInfo)
        self.isChecked = False
        self.isInSelectionMode = False

        self.vBoxLayout = QVBoxLayout(self)
        self.albumLabel = ClickableLabel(self.album, self)
        self.contentLabel = ClickableLabel(self.singer, self, False)
        self.albumPic = PixmapLabel(self)

        self.playButton = BlurButton(
            self,
            (30, 65),
            ":/images/album_tab_interface/Play.png",
            self.coverPath,
            self.tr('Play')
        )
        self.addToButton = BlurButton(
            self,
            (100, 65),
            ":/images/album_tab_interface/Add.png",
            self.coverPath,
            self.tr('Add to')
        )
        self.checkBox = CheckBox(self)
        self.checkBoxOpacityEffect = QGraphicsOpacityEffect(self)
        self.hideCheckBoxAni = QPropertyAnimation(
            self.checkBoxOpacityEffect, b'opacity', self)

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setFixedSize(210, 290)
        self.setAttribute(Qt.WA_StyledBackground)
        self.albumPic.setFixedSize(200, 200)
        self.contentLabel.setFixedWidth(210)
        self.albumLabel.setFixedWidth(210)
        self.playButton.move(35, 70)
        self.addToButton.move(105, 70)
        self.albumPic.setPixmap(QPixmap(self.coverPath).scaled(
            200, 200, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))

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

        # set cursor
        self.contentLabel.setCursor(Qt.PointingHandCursor)

        # initialize position of widgets
        self.__initLayout()

        # set properties and ID of widgets
        self.setObjectName("albumCard")
        self.albumLabel.setObjectName("albumLabel")
        self.contentLabel.setObjectName("contentLabel")
        self.setProperty("isChecked", "False")
        self.albumLabel.setProperty("isChecked", "False")
        self.contentLabel.setProperty("isChecked", "False")

        # connect signal to slot
        self.playButton.clicked.connect(
            lambda: signalBus.playAlbumSig.emit(self.singer, self.album))
        self.contentLabel.clicked.connect(
            lambda: signalBus.switchToSingerInterfaceSig.emit(self.singer))
        self.addToButton.clicked.connect(self.__showAddToMenu)
        self.checkBox.stateChanged.connect(self.__onCheckedStateChanged)

    def __initLayout(self):
        """ initialize layout """
        self.vBoxLayout.setContentsMargins(5, 5, 0, 0)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addWidget(self.albumPic)
        self.vBoxLayout.addSpacing(11)
        self.vBoxLayout.addWidget(self.albumLabel)
        self.vBoxLayout.addSpacing(2)
        self.vBoxLayout.addWidget(self.contentLabel)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.checkBox.move(178, 8)
        self.checkBox.hide()
        self.__adjustLabel()

    def __setAlbumInfo(self, albumInfo: AlbumInfo):
        """ set album information """
        self.albumInfo = albumInfo
        self.album = albumInfo.album
        self.singer = albumInfo.singer
        self.year = str(albumInfo.year)
        self.coverPath = getCoverPath(self.singer, self.album, 'album_big')

    def enterEvent(self, e):
        # show blur background
        albumCardPos = self.mapToGlobal(QPoint(0, 0))  # type:QPoint
        self.showBlurAlbumBackgroundSig.emit(albumCardPos, self.coverPath)

        # hide button in selection mode
        self.playButton.setHidden(self.isInSelectionMode)
        self.addToButton.setHidden(self.isInSelectionMode)

    def leaveEvent(self, e):
        self.hideBlurAlbumBackgroundSig.emit()
        self.addToButton.hide()
        self.playButton.hide()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        if e.button() == Qt.LeftButton:
            if self.isInSelectionMode:
                self.setChecked(not self.isChecked)
            else:
                signalBus.switchToAlbumInterfaceSig.emit(self.singer, self.album)

    def showAlbumInfoEditDialog(self):
        """ show album information edit dialog """
        self.showAlbumInfoEditDialogSig.emit(self.singer, self.album)

    def updateAlbumCover(self, coverPath: str):
        """ update album cover """
        self.coverPath = coverPath
        self.albumPic.setPixmap(QPixmap(self.coverPath).scaled(
            200, 200, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        self.playButton.setBlurPic(coverPath, 40)
        self.addToButton.setBlurPic(coverPath, 40)

    def updateWindow(self, albumInfo: AlbumInfo):
        """ update album card """
        if albumInfo == self.albumInfo:
            return

        self.__setAlbumInfo(albumInfo)
        self.albumPic.setPixmap(QPixmap(self.coverPath).scaled(
            200, 200, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        self.albumLabel.setText(self.album)
        self.contentLabel.setText(self.singer)
        self.playButton.setBlurPic(self.coverPath, 40)
        self.addToButton.setBlurPic(self.coverPath, 40)
        self.__adjustLabel()

    def __adjustLabel(self):
        """ adjust text of label """
        newText, isWordWrap = autoWrap(self.albumLabel.text(), 22)
        if isWordWrap:
            # add ellipsis
            index = newText.index("\n")
            fontMetrics = QFontMetrics(QFont("Microsoft YaHei", 10, 75))
            secondLineText = fontMetrics.elidedText(
                newText[index + 1:], Qt.ElideRight, 200)
            newText = newText[: index + 1] + secondLineText
            self.albumLabel.setText(newText)

        # add ellipsis to singer name
        fontMetrics = QFontMetrics(QFont("Microsoft YaHei", 10, 25))
        newSongerName = fontMetrics.elidedText(
            self.contentLabel.text(), Qt.ElideRight, 200)
        self.contentLabel.setText(newSongerName)
        self.contentLabel.adjustSize()
        self.albumLabel.adjustSize()

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

    def __showAddToMenu(self):
        """ show add to menu """
        menu = AddToMenu(parent=self)
        pos = self.mapToGlobal(QPoint(
            self.addToButton.x(), self.addToButton.y()))
        x = pos.x() + self.addToButton.width() + 5
        y = pos.y() + int(
            self.addToButton.height() / 2 - (13 + 38 * menu.actionCount()) / 2)
        menu.playingAct.triggered.connect(
            lambda: self.addToPlayingSignal.emit(self.singer, self.album))
        menu.newPlaylistAct.triggered.connect(
            lambda: self.addAlbumToNewCustomPlaylistSig.emit(self.singer, self.album))
        menu.addSongsToPlaylistSig.connect(
            lambda name: self.addAlbumToCustomPlaylistSig.emit(name, self.singer, self.album))
        menu.exec(QPoint(x, y))

    def __onCheckedStateChanged(self):
        """ check box checked state changed slot """
        self.isChecked = self.checkBox.isChecked()
        self.checkedStateChanged.emit(self, self.isChecked)

        # update text and background color
        self.setProperty("isChecked", str(self.isChecked))
        self.albumLabel.setProperty("isChecked", str(self.isChecked))
        self.contentLabel.setProperty("isChecked", str(self.isChecked))
        self.setStyle(QApplication.style())
