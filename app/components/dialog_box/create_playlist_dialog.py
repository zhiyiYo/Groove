# coding:utf-8
from common.database.entity import Playlist
from common.library import Library
from components.buttons.three_state_button import ThreeStateButton
from components.dialog_box.mask_dialog_base import MaskDialogBase
from components.widgets.label import ClickableLabel
from components.widgets.menu import LineEditMenu
from PyQt5.QtCore import QEvent, QFile, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QApplication, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout)


class CreatePlaylistDialog(MaskDialogBase):
    """ Create playlist dialog box """

    createPlaylistSig = pyqtSignal(str, Playlist)

    def __init__(self, library: Library, songInfos: list = None, parent=None):
        super().__init__(parent=parent)
        self.library = library
        self.songInfos = songInfos or []
        self.vBoxLayout = QVBoxLayout(self.widget)
        self.iconLabel = QLabel(self.widget)
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
        self.iconLabel.setPixmap(
            QPixmap(":/images/create_playlist_dialog/playlist.png"))

        self.__setQss()
        self.__initLayout()

        # connect signal to slot
        self.cancelLabel.clicked.connect(self.close)
        self.lineEdit.textChanged.connect(self.__isPlaylistExist)
        self.createPlaylistButton.clicked.connect(
            self.__onCreatePlaylistButtonClicked)

    def __setQss(self):
        """ set style sheet """
        self.cancelLabel.setObjectName("cancelLabel")
        f = QFile(":/qss/create_playlist_dialog.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

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
            print('Create playlist failed')
            return

        self.createPlaylistSig.emit(name, playlist)
        self.close()


class LineEdit(QLineEdit):
    """ Playlist name line edit """

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        iconPaths = {
            "normal": ":/images/create_playlist_dialog/clear_normal_50_50.png",
            "hover": ":/images/create_playlist_dialog/clear_hover_50_50.png",
            "pressed": ":/images/create_playlist_dialog/clear_pressed_50_50.png",
        }

        self.clearButton = ThreeStateButton(iconPaths, self, (50, 50))
        self.pencilPic = QLabel(self)
        self.menu = LineEditMenu(self)

        self.initWidget()
        self.__setQss()

    def initWidget(self):
        """ initialize widgets """
        self.setFixedSize(484, 70)
        self.__adjustButtonPos()
        self.textChanged.connect(self.__onTextChanged)
        self.setPlaceholderText(self.tr("Name the playlist"))

        self.clearButton.hide()
        self.clearButton.installEventFilter(self)
        self.pencilPic.setPixmap(
            QPixmap(":/images/create_playlist_dialog/pencil_50_50.png"))

        # prevent text and icon overlapping
        self.setTextMargins(
            0, 0, self.clearButton.width() + self.pencilPic.pixmap().width() + 1, 0)

    def __onTextChanged(self):
        """ 编辑框的文本改变时选择是否显示清空按钮 """
        self.clearButton.setVisible(bool(self.text()))

    def enterEvent(self, e):
        if not self.text():
            self.pencilPic.setPixmap(
                QPixmap(":/images/create_playlist_dialog/pencil_noFocus_hover_50_50.png"))

    def leaveEvent(self, e):
        if not self.text():
            self.pencilPic.setPixmap(
                QPixmap(":/images/create_playlist_dialog/pencil_noFocus_50_50.png"))

    def focusOutEvent(self, e):
        super().focusOutEvent(e)

        if not self.text():
            self.setProperty("noText", "true")
            self.setStyle(QApplication.style())

        self.clearButton.hide()
        self.pencilPic.setPixmap(
            QPixmap(":/images/create_playlist_dialog/pencil_noFocus_50_50.png"))

    def focusInEvent(self, e):
        super().focusInEvent(e)

        if self.property("noText") == "true":
            self.clear()

        self.setProperty("noText", "false")
        self.setStyle(QApplication.style())
        self.pencilPic.setPixmap(
            QPixmap(":/images/create_playlist_dialog/pencil_50_50.png"))

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            super().mousePressEvent(e)
            if self.text():
                self.clearButton.show()

    def contextMenuEvent(self, e):
        """ show context menu """
        self.menu.exec_(e.globalPos())

    def resizeEvent(self, e):
        self.__adjustButtonPos()

    def eventFilter(self, obj, e):
        """ 过滤事件 """
        if obj == self.clearButton:
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.clear()
                self.clearButton.hide()
                return True
        return super().eventFilter(obj, e)

    def __adjustButtonPos(self):
        """ adjust button position """
        self.clearButton.move(self.width() - 101, 10)
        self.pencilPic.move(self.width() - 51, 10)

    def __setQss(self):
        """ set style sheet """
        self.setObjectName("createPlaylistPanelLineEdit")

        f = QFile(":/qss/line_edit.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()
