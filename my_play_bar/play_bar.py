import sys
from ctypes.wintypes import HWND

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget,QSlider,QHBoxLayout,QLineEdit,QVBoxLayout

sys.path.append('..')
from Groove.effects.window_effect import WindowEffect
from Groove.my_play_bar.play_progress_bar import PlayProgressBar
from Groove.my_play_bar.central_button_group import CentralButtonGroup
from Groove.my_play_bar.right_widget_group import RightWidgetGroup
from Groove.my_play_bar.song_info_card import SongInfoCard


class PlayBar(QWidget):
    """ 底部播放栏 """

    def __init__(self, songInfo, parent=None):
        super().__init__(parent)
        # 实例化窗口特效
        self.windowEffect = WindowEffect()
        self.hWnd = HWND(int(self.winId()))

        # 实例化小部件
        self.songInfoCard=SongInfoCard(songInfo,self)
        self.playProgressBar = PlayProgressBar(self)
        self.centralButtonGroup = CentralButtonGroup(self)
        self.rightWidgetGroup = RightWidgetGroup(self)

        # 初始化小部件
        self.initWidget()
        self.setWidgetPos()
        self.setQss()

    def initWidget(self):
        """ 初始化小部件 """
        self.setWindowFlags(Qt.Window|Qt.FramelessWindowHint)
        self.setFixedHeight(115)
        self.resize(1180,115)
        # 设置亚克力背景色
        self.setAcrylicColor('a93436C0')
        
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    songInfo = {
        'songName': 'オーダーメイド (定制品)', 'songer': 'RADWIMPS',
        'album': [r'resource\Album Cover\オーダーメイド\オーダーメイド.jpg']}
    demo = Demo(songInfo)
    demo.show()
    demo.playBar.show()

    sys.exit(app.exec_())
