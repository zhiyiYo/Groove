import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget

from play_bar_buttons import (BasicCircleButton, PlayButton, PullUpArrow,
                              SelectableButton, TwoStateButton, VolumeButton, FillScreenButton)
from volume_slider import VolumeSlider
from play_progress_bar import PlayProgressBar

class PlayBar(QWidget):
    """ 播放栏 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建小部件
        self.__createWidget()
        # 初始化
        self.__initWidget()

    def __createWidget(self):
        """ 创建小部件 """
        self.playButton = PlayButton(self)
        self.volumeButton = VolumeButton(self)
        self.volumeSlider = VolumeSlider(self.window())
        self.fillScreenButton = FillScreenButton(self)
        self.playProgressBar = PlayProgressBar('3:10',parent=self)
        self.pullUpArrowButton = PullUpArrow(
            r'resource\images\playing_play_bar\上拉箭头_27_27.png', self)
        self.lastSongButton = BasicCircleButton(
            r'resource\images\playing_play_bar\lastSong_47_47.png', self)
        self.nextSongButton = BasicCircleButton(
            r'resource\images\playing_play_bar\nextSong_47_47.png', self)
        self.randomPlayButton = SelectableButton(
            [r'resource\images\playing_play_bar\randomPlay_47_47.png'], self)
        self.loopModeButton = SelectableButton(
            [r'resource\images\playing_play_bar\列表循环_47_47.png',
             r'resource\images\playing_play_bar\单曲循环_47_47.png'], self)
        self.moreActionsButton = BasicCircleButton(
            r'resource\images\playing_play_bar\更多操作_47_47.png', self)
        self.showPlaylistButton = BasicCircleButton(
            r'resource\images\playing_play_bar\显示播放列表_47_47.png', self)
        self.smallPlayModeButton = BasicCircleButton(
            r'resource\images\playing_play_bar\最小模式播放_47_47.png', self)

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedHeight(193)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.lastSongButton.move(17, 85)
        self.playButton.move(77, 85)
        self.nextSongButton.move(137, 85)
        self.randomPlayButton.move(197, 85)
        self.loopModeButton.move(257, 85)
        self.volumeButton.move(317, 85)
        self.moreActionsButton.move(387, 85)
        self.volumeSlider.hide()
        self.playProgressBar.move(0, 45)
        self.__moveButtons()
        # 信号连接到槽
        self.volumeButton.clicked.connect(self.__showVolumeSlider)
        self.volumeSlider.muteStateChanged.connect(
            lambda muteState: self.volumeButton.setMute(muteState))
        self.volumeSlider.volumeLevelChanged.connect(
            lambda volumeLevel: self.volumeButton.updateIcon(volumeLevel))

    def __showVolumeSlider(self):
        """ 显示音量滑动条 """
        if self.parent():
            self.volumeSlider.move(self.window().geometry().x() + 166,
                                   self.window().geometry().y() + self.y())
        else:
            self.volumeSlider.move(
                self.geometry().x() + 166, self.geometry().y())
        self.volumeSlider.show()

    def __moveButtons(self):
        """ 移动按钮 """
        self.pullUpArrowButton.move(
            int(self.width()/2-self.pullUpArrowButton.width()/2), 165)
        self.fillScreenButton.move(self.width() - 64, 85)
        self.smallPlayModeButton.move(self.width() - 124, 85)
        self.showPlaylistButton.move(self.width() - 184, 85)

    def resizeEvent(self, e):
        """ 改变尺寸时移动按钮 """
        super().resizeEvent(e)
        self.playProgressBar.resize(self.width(), 38)
        self.__moveButtons()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = PlayBar()
    demo.show()
    sys.exit(app.exec_())
