# coding:utf-8
from common.library import Library
from common.style_sheet import setStyleSheet
from components.buttons.three_state_button import ThreeStateButton
from components.dialog_box.mask_dialog_base import MaskDialogBase
from components.widgets.label import ClickableLabel, PixmapLabel
from components.widgets.menu import LineEditMenu
from PyQt5.QtCore import QEvent, QFile, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QApplication, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout)


class RenamePlaylistDialog(MaskDialogBase):
    """ Rename playlist dialog box """

    renamePlaylistSig = pyqtSignal(str, str)

    def __init__(self, library: Library, name: str, parent=None):
        super().__init__(parent=parent)
        self.oldName = name
        self.library = library
        self.vBoxLayout = QVBoxLayout(self.widget)
        self.iconLabel = PixmapLabel(self.widget)
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
        self.iconLabel.setPixmap(
            QPixmap(":/images/create_playlist_dialog/playlist.png"))
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
        setStyleSheet(self, 'rename_playlist_dialog')

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
        iconPath_dict = {
            "normal": ":/images/create_playlist_dialog/clear_normal_50_50.png",
            "hover": ":/images/create_playlist_dialog/clear_hover_50_50.png",
            "pressed": ":/images/create_playlist_dialog/clear_pressed_50_50.png",
        }

        self.clearButton = ThreeStateButton(iconPath_dict, self, (50, 50))
        self.pencilPic = PixmapLabel(self)
        self.menu = LineEditMenu(self)

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setFixedSize(484, 70)
        self.__adjustButtonPos()
        self.textChanged.connect(self.__onTextChanged)
        self.setObjectName("createPlaylistPanelLineEdit")

        self.clearButton.hide()
        self.clearButton.installEventFilter(self)
        self.pencilPic.setPixmap(
            QPixmap(":/images/create_playlist_dialog/pencil_50_50.png"))

        # prevent text and icon overlapping
        self.setTextMargins(
            0, 0, self.clearButton.width() + self.pencilPic.pixmap().width() + 1, 0)

        setStyleSheet(self, 'line_edit')

    def __onTextChanged(self):
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
        if obj is self.clearButton:
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.clear()
                self.clearButton.hide()
                return True

        return super().eventFilter(obj, e)

    def __adjustButtonPos(self):
        """ adjust button position """
        self.clearButton.move(self.width() - 101, 10)
        self.pencilPic.move(self.width() - 51, 10)