# coding:utf-8
import json
import os

from app.components.buttons.three_state_button import ThreeStateButton
from app.components.dialog_box.mask_dialog_base import MaskDialogBase
from app.components.label import ClickableLabel
from app.components.menu import LineEditMenu
from PyQt5.QtCore import QDateTime, QEvent, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton


class RenamePlaylistDialog(MaskDialogBase):
    """ 创建播放列表对话框 """

    renamePlaylistSig = pyqtSignal(dict, dict)

    def __init__(self, oldPlaylist: dict, parent=None):
        super().__init__(parent=parent)
        self.oldPlaylist = oldPlaylist
        self.oldPlaylistName = oldPlaylist["playlistName"]  # type:str
        self.iconLabel = QLabel(self.widget)
        self.lineEdit = LineEdit(self.oldPlaylistName, self.widget)
        self.cancelLabel = ClickableLabel("取消", self.widget)
        self.renamePlaylistButton = QPushButton('重命名', self.widget)
        self.playlistExistedLabel = QLabel("此名称已经存在。请尝试其他名称。", self.widget)
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.widget.setFixedSize(586, 594)
        self.renamePlaylistButton.setEnabled(False)
        self.playlistExistedLabel.hide()
        self.lineEdit.selectAll()
        self.iconLabel.setPixmap(
            QPixmap("app/resource/images/createPlaylistPanel/playList_icon.png"))
        self.__setQss()
        self.__initLayout()
        # 信号连接到槽
        self.cancelLabel.clicked.connect(self.close)
        self.lineEdit.textChanged.connect(self.__onLineEditTextChanged)
        self.renamePlaylistButton.clicked.connect(
            self.__onRenamePlaylistButtonClicked)

    def __setQss(self):
        """ 设置层叠样式 """
        self.cancelLabel.setObjectName("cancelLabel")
        with open("app/resource/css/rename_playlist_dialog.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def __initLayout(self):
        """ 初始化布局 """
        self.renamePlaylistButton.adjustSize()
        self.lineEdit.move(52, 309)
        self.iconLabel.move(188, 74)
        self.playlistExistedLabel.move(152, 405)
        self.cancelLabel.move(276, self.widget.height()-74)
        self.renamePlaylistButton.move(self.widget.width()//2-self.renamePlaylistButton.width()//2,
                                       self.widget.height() - 103 - self.renamePlaylistButton.height())

    def __isPlaylistExist(self, playlistName: str) -> bool:
        """ 检测播放列表是否已经存在，如果已存在就显示提示标签 """
        os.makedirs('app/Playlists', exist_ok=True)
        # 扫描播放列表文件夹下的播放列表名字
        playlistNames = [os.path.splitext(i)[0]
                         for i in os.listdir("app/Playlists")]
        isExist = playlistName in playlistNames
        # 如果播放列表名字禁用按钮
        self.playlistExistedLabel.hide()
        self.playlistExistedLabel.setVisible(isExist)
        self.renamePlaylistButton.setEnabled(not isExist)
        return isExist

    def __onRenamePlaylistButtonClicked(self):
        """ 重命名播放列表按钮点击槽函数 """
        playlistName = self.lineEdit.text()
        if self.__isPlaylistExist(playlistName):
            return
        # 创建新播放列表并写入json文件
        newPlaylist = {
            "playlistName": playlistName,
            "songInfo_list": self.oldPlaylist["songInfo_list"],
            "modifiedTime": QDateTime.currentDateTime().toString(Qt.ISODate),
        }
        with open(f"app/Playlists/{self.oldPlaylistName}.json", "w", encoding="utf-8") as f:
            json.dump(newPlaylist, f)
        # 重命名文件
        os.rename(f"app/Playlists/{self.oldPlaylistName}.json",
                  f"app/Playlists/{playlistName}.json")
        # 发送信号
        self.renamePlaylistSig.emit(self.oldPlaylist, newPlaylist)
        self.close()

    def __onLineEditTextChanged(self, playlistName: str):
        """ 单行输入框中的播放列表名字改变对应的槽函数 """
        self.renamePlaylistButton.setEnabled(
            not (playlistName in ["", self.oldPlaylistName, "       命名此播放列表"])
        )
        # 如果播放列表名已存在，显示提示标签
        if self.__isPlaylistExist(playlistName) and self.widget.height() != 627 and playlistName != self.oldPlaylistName:
            self.widget.setFixedSize(586, 627)
            self.__initLayout()
            self.playlistExistedLabel.show()
        elif not self.__isPlaylistExist(playlistName) and self.widget.height() == 627:
            self.widget.setFixedSize(586, 594)
            self.__initLayout()
            self.playlistExistedLabel.hide()


class LineEdit(QLineEdit):
    """ 编辑框 """

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        iconPath_dict = {
            "normal": r"app\resource\images\createPlaylistPanel\清空按钮_normal_50_50.png",
            "hover": r"app\resource\images\createPlaylistPanel\清空按钮_hover_50_50.png",
            "pressed": r"app\resource\images\createPlaylistPanel\清空按钮_pressed_50_50.png",
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
        # 初始化按钮
        self.clearButton.hide()
        self.clearButton.installEventFilter(self)
        self.pencilPic.setPixmap(
            QPixmap(r"app\resource\images\createPlaylistPanel\pencil_50_50.png")
        )
        # 设置文字的外间距，防止文字和文本重叠
        self.setTextMargins(
            0, 0, self.clearButton.width() + self.pencilPic.pixmap().width() + 1, 0
        )

    def textChangedEvent(self):
        """ 编辑框的文本改变时选择是否显示清空按钮 """
        if self.text():
            self.clearButton.show()
        else:
            self.clearButton.hide()

    def enterEvent(self, e):
        """ 鼠标进入更新样式 """
        if self.property("noText") == "true":
            self.pencilPic.setPixmap(
                QPixmap(
                    r"app\resource\images\createPlaylistPanel\pencil_noFocus_hover_50_50.png"
                )
            )

    def leaveEvent(self, e):
        """ 鼠标离开更新样式 """
        if self.property("noText") == "true":
            self.pencilPic.setPixmap(
                QPixmap(
                    r"app\resource\images\createPlaylistPanel\pencil_noFocus_50_50.png"
                )
            )

    def focusOutEvent(self, e):
        """ 当焦点移到别的输入框时隐藏按钮 """
        super().focusOutEvent(e)
        if not self.text():
            self.setProperty("noText", "true")
            self.setStyle(QApplication.style())
            self.setText("       命名此播放列表")
        self.clearButton.hide()
        self.pencilPic.setPixmap(
            QPixmap(
                r"app\resource\images\createPlaylistPanel\pencil_noFocus_50_50.png")
        )

    def focusInEvent(self, e):
        """ 焦点进入时更换样式并取消提示文字 """
        super().focusInEvent(e)
        # 必须有判断的一步，不然每次右击菜单执行完都会触发focusInEvent()导致菜单功能混乱
        if self.property("noText") == "true":
            self.clear()
        self.setProperty("noText", "false")
        self.setStyle(QApplication.style())
        self.pencilPic.setPixmap(
            QPixmap(r"app\resource\images\createPlaylistPanel\pencil_50_50.png")
        )

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
        with open("app/resource/css/line_edit.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())
