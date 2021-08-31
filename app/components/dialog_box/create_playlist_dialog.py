# coding:utf-8
import json
import os

from components.buttons.three_state_button import ThreeStateButton
from components.dialog_box.mask_dialog_base import MaskDialogBase
from components.label import ClickableLabel
from components.menu import LineEditMenu
from PyQt5.QtCore import QDateTime, QEvent, Qt, pyqtSignal, QFile
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout


class CreatePlaylistDialog(MaskDialogBase):
    """ 创建播放列表对话框 """

    createPlaylistSig = pyqtSignal(str, dict)

    def __init__(self, songInfo_list: list = None, parent=None):
        super().__init__(parent=parent)
        self.songInfo_list = songInfo_list
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
        """ 初始化小部件 """
        self.widget.setFixedSize(586, 644)
        self.playlistExistedLabel.hide()
        self.iconLabel.setPixmap(
            QPixmap(":/images/create_playlist_dialog/playlist.png"))

        self.__setQss()
        self.__initLayout()

        # 信号连接到槽
        self.cancelLabel.clicked.connect(self.close)
        self.lineEdit.textChanged.connect(self.__isPlaylistExist)
        self.createPlaylistButton.clicked.connect(
            self.__onCreatePlaylistButtonClicked)

    def __setQss(self):
        """ 设置层叠样式 """
        self.cancelLabel.setObjectName("cancelLabel")
        f = QFile(":/qss/create_playlist_dialog.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

    def __initLayout(self):
        """ 初始化布局 """
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

    def __isPlaylistExist(self, playlistName: str) -> bool:
        """ 检测播放列表是否已经存在，如果已存在就显示提示标签 """
        os.makedirs('Playlists', exist_ok=True)

        # 扫描播放列表文件夹下的播放列表名字
        playlistNames = [
            os.path.splitext(i)[0] for i in os.listdir("Playlists")]
        isExist = playlistName in playlistNames

        # 如果播放列表名字已存在显示提示标签
        self.playlistExistedLabel.setVisible(isExist)
        self.createPlaylistButton.setEnabled(not isExist)
        return isExist

    def __onCreatePlaylistButtonClicked(self):
        """ 发出创建播放列表的信号 """
        text = self.lineEdit.text()
        playlistName = text if text else self.tr("New playlist")

        # 如果播放列表已存在，显示提示消息并直接返回
        if self.__isPlaylistExist(playlistName):
            return

        # 创建播放列表
        songInfo_list = self.songInfo_list if self.songInfo_list else []
        playlist = {
            "playlistName": playlistName,
            "songInfo_list": songInfo_list,
            "modifiedTime": QDateTime.currentDateTime().toString(Qt.ISODate),
        }
        with open(f"Playlists/{playlistName}.json", "w", encoding="utf-8") as f:
            json.dump(playlist, f)

        self.createPlaylistSig.emit(playlistName, playlist)
        self.close()


class LineEdit(QLineEdit):
    """ 编辑框 """

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        iconPath_dict = {
            "normal": ":/images/create_playlist_dialog/clear_normal_50_50.png",
            "hover": ":/images/create_playlist_dialog/clear_hover_50_50.png",
            "pressed": ":/images/create_playlist_dialog/clear_pressed_50_50.png",
        }

        # 创建小部件
        self.clearButton = ThreeStateButton(iconPath_dict, self, (50, 50))
        self.pencilPic = QLabel(self)
        self.menu = LineEditMenu(self)
        # 初始化
        self.initWidget()
        self.setQss()

    def initWidget(self):
        """ 初始化小部件 """
        self.setFixedSize(484, 70)
        self.adjustButtonPos()
        self.textChanged.connect(self.textChangedEvent)
        self.setObjectName("createPlaylistPanelLineEdit")
        self.setPlaceholderText(self.tr("Name the playlist"))
        
        # 初始化按钮
        self.clearButton.hide()
        self.clearButton.installEventFilter(self)
        self.pencilPic.setPixmap(
            QPixmap(":/images/create_playlist_dialog/pencil_50_50.png"))

        # 设置文字的外间距，防止文字和文本重叠
        self.setTextMargins(
            0, 0, self.clearButton.width() + self.pencilPic.pixmap().width() + 1, 0)

    def textChangedEvent(self):
        """ 编辑框的文本改变时选择是否显示清空按钮 """
        self.clearButton.setVisible(bool(self.text()))

    def enterEvent(self, e):
        """ 鼠标进入更新样式 """
        if not self.text():
            self.pencilPic.setPixmap(
                QPixmap(":/images/create_playlist_dialog/pencil_noFocus_hover_50_50.png"))

    def leaveEvent(self, e):
        """ 鼠标离开更新样式 """
        if not self.text():
            self.pencilPic.setPixmap(
                QPixmap(":/images/create_playlist_dialog/pencil_noFocus_50_50.png"))

    def focusOutEvent(self, e):
        """ 当焦点移到别的输入框时隐藏按钮 """
        super().focusOutEvent(e)

        if not self.text():
            self.setProperty("noText", "true")
            self.setStyle(QApplication.style())

        self.clearButton.hide()
        self.pencilPic.setPixmap(
            QPixmap(":/images/create_playlist_dialog/pencil_noFocus_50_50.png"))

    def focusInEvent(self, e):
        """ 焦点进入时更换样式并取消提示文字 """
        super().focusInEvent(e)
        # 必须有判断的一步，不然每次右击菜单执行完都会触发focusInEvent()导致菜单功能混乱
        if self.property("noText") == "true":
            self.clear()
        self.setProperty("noText", "false")
        self.setStyle(QApplication.style())
        self.pencilPic.setPixmap(
            QPixmap(":/images/create_playlist_dialog/pencil_50_50.png"))

    def mousePressEvent(self, e):
        """ 鼠标点击事件 """
        if e.button() == Qt.LeftButton:
            # 需要调用父类的鼠标点击事件，不然无法部分选中
            super().mousePressEvent(e)
            # 如果输入框中有文本，就设置为只读并显示清空按钮
            if self.text():
                self.clearButton.show()

    def contextMenuEvent(self, e):
        """ 设置右击菜单 """
        self.menu.exec_(e.globalPos())

    def resizeEvent(self, e):
        """ 调整大小的同时改变按钮位置 """
        self.adjustButtonPos()

    def eventFilter(self, obj, e):
        """ 过滤事件 """
        if obj == self.clearButton:
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.clear()
                self.clearButton.hide()
                return True
        return super().eventFilter(obj, e)

    def adjustButtonPos(self):
        """ 调整按钮的位置 """
        self.clearButton.move(self.width() - 101, 10)
        self.pencilPic.move(self.width() - 51, 10)

    def setQss(self):
        """ 设置层叠样式 """
        f = QFile(":/qss/line_edit.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()
