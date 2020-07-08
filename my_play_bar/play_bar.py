import sys
from ctypes.wintypes import HWND,MSG

from PyQt5.QtCore import Qt,QPoint
from PyQt5.QtWidgets import QApplication, QWidget,QSlider,QHBoxLayout,QLineEdit,QVBoxLayout

sys.path.append('..')
from Groove.effects.window_effect import WindowEffect
from Groove.my_play_bar.play_progress_bar import PlayProgressBar
from Groove.my_play_bar.central_button_group import CentralButtonGroup
from Groove.my_play_bar.right_widget_group import RightWidgetGroup
from Groove.my_play_bar.song_info_card import SongInfoCard
from Groove.my_play_bar.more_actions_menu import MoreActionsMenu
from Groove.flags.wm_hittest import Flags


class PlayBar(QWidget):
    """ 底部播放栏 """

    def __init__(self, songInfo, parent=None):
        super().__init__(parent)
        # 实例化窗口特效
        self.windowEffect = WindowEffect()
        self.hWnd = HWND(int(self.winId()))
        # 记录移动次数
        self.moveTime = 0
        # 实例化小部件
        self.playProgressBar = PlayProgressBar(songInfo['duration'],self)
        self.songInfoCard=SongInfoCard(songInfo,self)
        self.centralButtonGroup = CentralButtonGroup(self)
        self.rightWidgetGroup = RightWidgetGroup(self)
        self.moreActionsMenu = MoreActionsMenu(self)
        # 初始化小部件
        self.initWidget()
        self.setWidgetPos()
        self.setQss()

    def initWidget(self):
        """ 初始化小部件 """
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setFixedHeight(115)
        self.resize(1280,115)
        # 初始化亚克力背景色
        #self.setAcrylicColor('02125bC0')
        self.setAcrylicColor('143d72C0')
        # 引用小部件
        self.referenceWidgets()
        # 连接槽函数
        self.moreActionsButton.clicked.connect(self.showMoreActionsMenu)

    def setWidgetPos(self):
        """ 初始化布局 """
        self.playProgressBar.move(int(self.width() / 2 - self.playProgressBar.width() / 2), self.centralButtonGroup.height())
        self.centralButtonGroup.move(int(self.width()/2-self.centralButtonGroup.width()/2),0)
        self.rightWidgetGroup.move(self.width() - self.rightWidgetGroup.width(), 0)

    def setAcrylicColor(self,gradientColor:str):
        """ 设置亚克力效果的混合色 """
        self.windowEffect.setAcrylicEffect(self.hWnd, gradientColor)

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\playBar.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def resizeEvent(self, e):
        self.setWidgetPos()

    def showMoreActionsMenu(self):
        """ 显示更多操作菜单 """
        globalPos = self.rightWidgetGroup.mapToGlobal(self.moreActionsButton.pos())
        x = globalPos.x() + self.moreActionsButton.width() - 16
        y = int(globalPos.y() + self.moreActionsButton.height() / 2 - self.moreActionsMenu.height()/2)
        self.moreActionsMenu.show(QPoint(x, y))

    def referenceWidgets(self):
        """ 引用小部件及其方法 """
        self.randomPlayButton = self.centralButtonGroup.randomPlayButton
        self.lastSongButton = self.centralButtonGroup.lastSongButton
        self.playButton = self.centralButtonGroup.playButton
        self.nextSongButton = self.centralButtonGroup.nextSongButton
        self.loopModeButton = self.centralButtonGroup.loopModeButton
        self.progressSlider = self.playProgressBar.progressSlider
        self.volumeButton = self.rightWidgetGroup.volumeButton
        self.volumeSlider = self.rightWidgetGroup.volumeSlider
        self.smallPlayModeButton = self.rightWidgetGroup.smallPlayModeButton
        self.moreActionsButton = self.rightWidgetGroup.moreActionsButton
        # 引用方法
        self.setCurrentTime = self.playProgressBar.setCurrentTime
        self.setTotalTime = self.playProgressBar.setTotalTime


if __name__ == "__main__":
    app = QApplication(sys.argv)
    songInfo = {
        'songName': 'オオカミと少女 (狼与少女)', 'songer': 'RADWIMPS', 'duration': '3:50',
        'album': [r'resource\Album Cover\オーダーメイド\オーダーメイド.jpg']}
    demo = PlayBar(songInfo)
    demo.move(500,400)
    demo.show()
    sys.exit(app.exec_())
