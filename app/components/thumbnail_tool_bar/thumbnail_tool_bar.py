# coding:utf-8

from PyQt5.QtGui import QIcon
from PyQt5.QtWinExtras import QWinThumbnailToolBar, QWinThumbnailToolButton


class ThumbnailPlayButton(QWinThumbnailToolButton):
    """ 缩略图任务栏的播放/暂停按钮 """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setPlay(False)

    def setPlay(self, isPlay: bool):
        """ 根据播放状态设置图标和提示条 """
        self.isPlaying = isPlay
        if self.isPlaying:
            self.setToolTip("暂停")
            self.setIcon(
                QIcon(r"app/resource/images/thumbnail_tool_bar/播放_32_32_2.png")
            )
        else:
            self.setToolTip("播放")
            self.setIcon(
                QIcon(r"app/resource/images/thumbnail_tool_bar/暂停_32_32_2.png")
            )


class ThumbnailToolBar(QWinThumbnailToolBar):
    """ 缩略图任务栏 """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.playButton = ThumbnailPlayButton(self)
        self.lastSongButton = QWinThumbnailToolButton(self)
        self.nextSongButton = QWinThumbnailToolButton(self)
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        # 设置图标和提示条
        self.lastSongButton.setToolTip("上一首")
        self.nextSongButton.setToolTip("下一首")
        self.lastSongButton.setIcon(
            QIcon(r"app/resource/images/thumbnail_tool_bar/上一首_32_32_2.png")
        )
        self.nextSongButton.setIcon(
            QIcon(r"app/resource/images/thumbnail_tool_bar/下一首_32_32_2.png")
        )
        # 将按钮添加到任务栏
        self.addButton(self.lastSongButton)
        self.addButton(self.playButton)
        self.addButton(self.nextSongButton)
        # 禁用所有按钮
        # self.setButtonsEnabled(False)

    def setButtonsEnabled(self, isEnable: bool):
        """ 设置按钮的启用与否 """
        for button in self.buttons():
            button.setEnabled(isEnable)
