# coding:utf-8

import json
from os import rename

from PyQt5.QtCore import Qt, pyqtSignal, QDateTime
from PyQt5.QtWidgets import QLabel

from .basic_playlist_panel import BasicPlaylistPanel
from app.components.dialog_box.sub_panel_frame import SubPanelFrame


class RenamePlaylistPanel(SubPanelFrame):
    """ 选择歌曲文件夹面板 """

    def __init__(self, oldPlaylist: dict, parent=None):
        super().__init__(parent)
        # 实例化子属性面板
        self.__subRenamePlaylistPanel = SubRenamePlaylistPanel(oldPlaylist, self)
        self.renamePlaylistSig = self.__subRenamePlaylistPanel.renamePlaylistSig
        # 初始化
        self.showMask()
        self.__setSubWindowPos()
        self.__subRenamePlaylistPanel.resizeSig.connect(self.__setSubWindowPos)

    def __setSubWindowPos(self):
        """ 设置子窗口的位置 """
        self.__subRenamePlaylistPanel.move(
            int(self.width() / 2 - self.__subRenamePlaylistPanel.width() / 2),
            int(self.height() / 2 - self.__subRenamePlaylistPanel.height() / 2),
        )


class SubRenamePlaylistPanel(BasicPlaylistPanel):
    """ 子重命名播放列表面板 """

    resizeSig = pyqtSignal()
    renamePlaylistSig = pyqtSignal(dict, dict)

    def __init__(self, oldPlaylist: dict, parent=None):
        super().__init__(parent)
        self.oldPlaylist = oldPlaylist
        self.oldPlaylistName = oldPlaylist["playlistName"]  # type:str
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化 """
        self.resize(586, 594)
        self.setAttribute(Qt.WA_StyledBackground)
        # 先禁用按钮
        self.button.setText("重命名")
        self.button.setEnabled(False)
        self.lineEdit.setText(self.oldPlaylistName)
        self.lineEdit.selectAll()
        # 设置层叠样式
        self._setQss()
        self.__initLayout()
        # 信号连接到槽函数
        self.lineEdit.textChanged.connect(self.__lineEditTextChangedSlot)
        self.button.clicked.connect(self.__renamePlaylistButtonSlot)

    def __initLayout(self):
        """ 初始化布局 """
        self.iconPic.move(188, 74)
        self.lineEdit.move(52, 309)
        self.playlistExistedLabel.move(152, 405)
        self.cancelLabel.move(276, self.height() - 74)
        self.button.move(137, self.height() - 103 - self.button.height())

    def __lineEditTextChangedSlot(self, playlistName: str):
        """ 单行输入框中的播放列表名字改变对应的槽函数 """
        self.button.setEnabled(
            not (playlistName in ["", self.oldPlaylistName, "       命名此播放列表"])
        )
        # 如果播放列表名已存在，显示提示标签
        if (
            self._isPlaylistExist(playlistName)
            and self.height() != 627
            and playlistName != self.oldPlaylistName
        ):
            self.resize(586, 627)
            self.resizeSig.emit()
            self.__initLayout()
            self.playlistExistedLabel.show()
        elif not self._isPlaylistExist(playlistName) and self.height() == 627:
            self.resize(586, 594)
            self.resizeSig.emit()
            self.__initLayout()
            self.playlistExistedLabel.hide()

    def __renamePlaylistButtonSlot(self):
        """ 重命名播放列表 """
        playlistName = self.lineEdit.text()
        if self._isPlaylistExist(playlistName):
            return
        # 创建新播放列表并写入json文件
        newPlaylist = {
            "playlistName": playlistName,
            "songInfo_list": self.oldPlaylist["songInfo_list"],
            "modifiedTime": QDateTime.currentDateTime().toString(Qt.ISODate),
        }
        with open(
            f"app\\Playlists\\{self.oldPlaylistName}.json", "w", encoding="utf-8"
        ) as f:
            json.dump(newPlaylist, f)
        # 重命名文件
        rename(
            f"app\\Playlists\\{self.oldPlaylistName}.json",
            f"app\\Playlists\\{playlistName}.json",
        )
        # 发送信号
        self.renamePlaylistSig.emit(self.oldPlaylist, newPlaylist)
        self.parent().deleteLater()

    def _isPlaylistExist(self, playlistName):
        """ 检查播放列表名字是否已存在 """
        isExist = super()._isPlaylistExist(playlistName)
        self.playlistExistedLabel.hide()
        return isExist
