# coding:utf-8

import json

from app.my_dialog_box.sub_panel_frame import SubPanelFrame
from PyQt5.QtCore import QDateTime, Qt, pyqtSignal
from PyQt5.QtWidgets import QLabel

from .basic_playlist_panel import BasicPlaylistPanel


class CreatePlaylistPanel(SubPanelFrame):
    """ 创建播放列表面板 """

    def __init__(self, parent=None, songInfo_list: list = None):
        super().__init__(parent)
        # 实例化子属性面板
        self.__subCreatePlaylistPanel = SubCreatePlaylistPanel(
            self, songInfo_list)
        self.createPlaylistSig = self.__subCreatePlaylistPanel.createPlaylistSig
        # 初始化
        self.showMask()
        self.__setSubWindowPos()

    def __setSubWindowPos(self):
        """ 设置子窗口的位置 """
        self.__subCreatePlaylistPanel.move(
            int(self.width() / 2 - self.__subCreatePlaylistPanel.width() / 2),
            int(self.height() / 2 - self.__subCreatePlaylistPanel.height() / 2))


class SubCreatePlaylistPanel(BasicPlaylistPanel):
    """ 创建播放列表子面板 """
    createPlaylistSig = pyqtSignal(dict)

    def __init__(self, parent=None, songInfo_list: list = None):
        super().__init__(parent)
        self.songInfo_list = songInfo_list
        # 创建小部件
        self.yourCreationLabel = QLabel('您创建的', self)
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedSize(586, 644)
        self.setAttribute(Qt.WA_StyledBackground)
        self.button.setText('创建播放列表')
        # 设置层叠样式
        self._setQss()
        self.__initLayout()
        # 信号连接到槽函数
        self.lineEdit.textChanged.connect(self._isPlaylistExist)
        self.button.clicked.connect(self.__createPlaylistButtonSlot)

    def __initLayout(self):
        """ 初始化布局 """
        self.iconPic.move(188, 74)
        self.button.move(137, 496)
        self.lineEdit.move(52, 309)
        self.cancelLabel.move(276, 570)
        self.yourCreationLabel.move(255, 398)
        self.playlistExistedLabel.move(152, 440)

    def __createPlaylistButtonSlot(self):
        """ 发出创建播放列表的信号 """
        if self.lineEdit.text() and self.lineEdit.text() != '       命名此播放列表':
            playlistName = self.lineEdit.text()
        else:
            playlistName = '新的播放列表'
        # 如果播放列表已存在，显示提示消息并直接返回
        if self._isPlaylistExist(playlistName):
            return
        # 创建播放列表
        songInfo_list = self.songInfo_list if self.songInfo_list else []
        playlist = {'playlistName': playlistName,
                    'songInfo_list': songInfo_list,
                    'modifiedTime': QDateTime.currentDateTime().toString(Qt.ISODate)}
        with open(f'app\\Playlists\\{playlistName}.json', 'w', encoding='utf-8') as f:
            json.dump(playlist, f)
        self.createPlaylistSig.emit(playlist)
        self.parent().deleteLater()
