# coding:utf-8
from common.database.entity import Playlist
from common.library import Library
from common.style_sheet import setStyleSheet
from common.icon import getIconColor, drawSvgIcon
from components.buttons.three_state_button import ThreeStateButton
from components.dialog_box.mask_dialog_base import MaskDialogBase
from components.widgets.label import ClickableLabel, PixmapLabel
from components.widgets.menu import LineEditMenu
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QBrush, QColor, QPainter, QPixmap, QLinearGradient
from PyQt5.QtWidgets import (QApplication, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QWidget)
from PyQt5.QtSvg import QSvgWidget


class CreatePlaylistDialog(MaskDialogBase):
    """ Create playlist dialog box """

    createPlaylistSig = pyqtSignal(str, Playlist)

    def __init__(self, library: Library, songInfos: list = None, parent=None):
        super().__init__(parent=parent)
        self.library = library
        self.songInfos = songInfos or []
        self.vBoxLayout = QVBoxLayout(self.widget)
        self.iconLabel = PlaylistIcon(self.widget)
        self.lineEdit = LineEdit(parent=self.widget)
        self.cancelLabel = ClickableLabel(self.tr("Cancel"), self.widget)
        self.yourCreationLabel = QLabel(self.tr("Created by you"), self.widget)
        self.createPlaylistButton = QPushButton(
            self.tr('Create playlist'), self.widget)
        self.playlistExistedLabel = QLabel(
            self.tr("This name already exists. Please try a different name."), self.widget)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.widget.setFixedSize(586, 644)
        self.playlistExistedLabel.hide()

        self.__setQss()
        self.__initLayout()

        # connect signal to slot
        self.cancelLabel.clicked.connect(self.close)
        self.lineEdit.textChanged.connect(self.__isPlaylistExist)
        self.lineEdit.returnPressed.connect(
            self.__onCreatePlaylistButtonClicked)
        self.createPlaylistButton.clicked.connect(
            self.__onCreatePlaylistButtonClicked)

    def __setQss(self):
        """ set style sheet """
        self.cancelLabel.setObjectName("cancelLabel")
        setStyleSheet(self, 'playlist_dialog')

    def __initLayout(self):
        """ initialize layout """
        self.vBoxLayout.setContentsMargins(0, 74, 0, 0)
        self.vBoxLayout.setSpacing(0)
        args = (0, Qt.AlignHCenter)
        self.vBoxLayout.addWidget(self.iconLabel, *args)
        self.vBoxLayout.addSpacing(25)
        self.vBoxLayout.addWidget(self.lineEdit, *args)
        self.vBoxLayout.addSpacing(20)
        self.vBoxLayout.addWidget(self.yourCreationLabel, *args)
        self.vBoxLayout.addSpacing(23)
        self.vBoxLayout.addWidget(self.playlistExistedLabel, *args)
        self.vBoxLayout.addSpacing(38)
        self.vBoxLayout.addWidget(self.createPlaylistButton, *args)
        self.vBoxLayout.addSpacing(28)
        self.vBoxLayout.addWidget(self.cancelLabel, *args)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

    def __isPlaylistExist(self, name: str) -> bool:
        """ check if the playlist already exists """
        names = [i.name for i in self.library.playlistController.getAllPlaylists()]
        isExist = name in names

        # show hint label if playlist already exists
        self.playlistExistedLabel.setVisible(isExist)
        self.createPlaylistButton.setEnabled(not isExist)

        return isExist

    def __onCreatePlaylistButtonClicked(self):
        """ create playlist """
        text = self.lineEdit.text().strip()
        name = text if text else self.tr("New playlist")

        if self.__isPlaylistExist(name):
            return

        # add playlist to database
        playlist = Playlist(name=name, songInfos=self.songInfos)
        if not self.library.playlistController.create(playlist):
            return

        self.createPlaylistSig.emit(name, playlist)
        self.close()


class RenamePlaylistDialog(MaskDialogBase):
    """ Rename playlist dialog box """

    renamePlaylistSig = pyqtSignal(str, str)

    def __init__(self, library: Library, name: str, parent=None):
        super().__init__(parent=parent)
        self.oldName = name
        self.library = library
        self.vBoxLayout = QVBoxLayout(self.widget)
        self.iconLabel = PlaylistIcon(self.widget)
        self.lineEdit = LineEdit(self.oldName, self.widget)
        self.cancelLabel = ClickableLabel(self.tr("Cancel"), self.widget)
        self.renamePlaylistButton = QPushButton(self.tr('Rename'), self.widget)
        self.playlistExistedLabel = QLabel(
            self.tr("This name already exists. Please try a different name."), self.widget)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.widget.setFixedSize(586, 594)
        self.renamePlaylistButton.setEnabled(False)
        self.playlistExistedLabel.hide()
        self.lineEdit.selectAll()
        self.__setQss()
        self.__initLayout()

        # connect signal to slot
        self.cancelLabel.clicked.connect(self.close)
        self.lineEdit.textChanged.connect(self.__onLineEditTextChanged)
        self.lineEdit.returnPressed.connect(
            self.__onRenamePlaylistButtonClicked)
        self.renamePlaylistButton.clicked.connect(
            self.__onRenamePlaylistButtonClicked)

    def __setQss(self):
        """ set style sheet """
        self.cancelLabel.setObjectName("cancelLabel")
        setStyleSheet(self, 'playlist_dialog')

    def __initLayout(self):
        """ 初始化布局 """
        self.vBoxLayout.setContentsMargins(0, 74, 0, 0)
        self.vBoxLayout.setSpacing(0)
        args = (0, Qt.AlignHCenter)
        self.vBoxLayout.addWidget(self.iconLabel, *args)
        self.vBoxLayout.addSpacing(25)
        self.vBoxLayout.addWidget(self.lineEdit, *args)
        self.vBoxLayout.addSpacing(25)
        self.vBoxLayout.addWidget(self.playlistExistedLabel, *args)
        self.vBoxLayout.addSpacing(20)
        self.vBoxLayout.addWidget(self.renamePlaylistButton, *args)
        self.vBoxLayout.addSpacing(28)
        self.vBoxLayout.addWidget(self.cancelLabel, *args)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

    def __isPlaylistExist(self, name: str) -> bool:
        """ detect if the playlist exists """
        names = [i.name for i in self.library.playlistController.getAllPlaylists()]
        return name in names

    def __onRenamePlaylistButtonClicked(self):
        """ rename button clicked slot """
        name = self.lineEdit.text().strip()
        if self.__isPlaylistExist(name):
            return

        self.renamePlaylistSig.emit(self.oldName, name)
        self.close()

    def __onLineEditTextChanged(self, name: str):
        """ line edit text changed slot """
        name = name.strip()

        # disable button if the playlist exists
        isExist = self.__isPlaylistExist(name)
        isDisabled = name in ["", self.oldName]
        self.renamePlaylistButton.setDisabled(isDisabled or isExist)

        if isExist and name != self.oldName:
            self.playlistExistedLabel.show()
        elif not isExist:
            self.playlistExistedLabel.hide()


class LineEdit(QLineEdit):
    """ Playlist name line edit """

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.iconFolder = ":/images/playlist_dialog"
        self.color = getIconColor()
        iconPaths = {
            "normal": f"{self.iconFolder}/Clear_{self.color}.svg",
            "hover": f"{self.iconFolder}/Clear_green.svg",
            "pressed": f"{self.iconFolder}/Clear_white.svg",
        }

        self.clearButton = ThreeStateButton(iconPaths, self, (50, 50), (18, 18))
        self.pencilIcon = QSvgWidget(self)
        self.menu = LineEditMenu(self)

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setFixedSize(484, 70)
        self.setProperty("noText", not bool(self.text()))
        self.setPlaceholderText(self.tr("Name the playlist"))
        self.__adjustButtonPos()

        self.clearButton.hide()
        self.pencilIcon.setFixedSize(24, 24)
        self.pencilIcon.load(f"{self.iconFolder}/Pen_{self.color}.svg")
        self.pencilIcon.setCursor(Qt.ArrowCursor)

        # prevent text and icon overlapping
        self.setTextMargins(
            0, 0, self.clearButton.width() + self.pencilIcon.width() + 1, 0)

        self.clearButton.clicked.connect(self.__clearText)
        self.textChanged.connect(
            lambda t: self.clearButton.setVisible(bool(t)))

    def __clearText(self):
        self.clear()
        self.clearButton.hide()

    def enterEvent(self, e):
        if not self.text():
            self.pencilIcon.load(f"{self.iconFolder}/Pen_{self.color}_noFocus_hover.svg")

    def leaveEvent(self, e):
        if not self.text():
            self.pencilIcon.load(f"{self.iconFolder}/Pen_{self.color}_noFocus.svg")

    def focusOutEvent(self, e):
        super().focusOutEvent(e)

        self.setProperty("noText", not bool(self.text()))
        self.setStyle(QApplication.style())

        self.clearButton.hide()
        self.pencilIcon.load(f"{self.iconFolder}/Pen_{self.color}_noFocus.svg")

    def focusInEvent(self, e):
        super().focusInEvent(e)
        self.clearButton.setVisible(bool(self.text()))

        self.setProperty("noText", not bool(self.text()))
        self.setStyle(QApplication.style())

        self.pencilIcon.load(f"{self.iconFolder}/Pen_{self.color}.svg")

    def contextMenuEvent(self, e):
        self.menu.exec_(e.globalPos())

    def resizeEvent(self, e):
        self.__adjustButtonPos()

    def __adjustButtonPos(self):
        """ adjust button position """
        self.clearButton.move(self.width() - 101, 10)
        self.pencilIcon.move(self.width() - 37, 24)


class PlaylistIcon(QWidget):
    """ Playlist icon """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(210, 210)
        self.iconPath = ":/images/playlist_dialog/Playlist.svg"

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)

        # draw background color
        gradientColor = QLinearGradient(0, 0, 0, self.height())
        gradientColor.setColorAt(0, QColor(0, 107, 131))
        gradientColor.setColorAt(1, QColor(0, 153, 188))
        painter.setBrush(QBrush(gradientColor))
        painter.drawRoundedRect(self.rect(), 8, 8)

        # draw icon
        drawSvgIcon(self.iconPath, painter, QRect(82, 82, 46, 46))
