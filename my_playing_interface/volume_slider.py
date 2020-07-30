import sys

from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QPen, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QGraphicsDropShadowEffect

from play_bar_buttons import BasicCircleButton

sys.path.append('..')
from Groove.my_widget.my_slider import Slider


class VolumeSlider(QWidget):
    """ 音量滑动条 """

    # 静音状态改变信号
    muteStateChanged = pyqtSignal(bool)
    volumeLevelChanged = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.volumeButton = VolumeButton(self)
        self.volumeSlider = Slider(Qt.Horizontal, self)
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedSize(345, 78)
        self.volumeButton.move(25, 15)
        self.volumeSlider.move(108, 25)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.__setQss()
        self.__setShadowEffect()
        # 信号连接到槽
        self.volumeButton.muteStateChanged.connect(
            lambda muteState: self.muteStateChanged.emit(muteState))
        self.volumeButton.volumeLevelChanged.connect(
            lambda volumeLevel: self.volumeLevelChanged.emit(volumeLevel))
        self.volumeSlider.valueChanged.connect(
            self.volumeButton.setVolumeLevel)

    def __setQss(self):
        """ 设置层叠样式 """
        with open(r'resource\css\volume_slider.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __setShadowEffect(self):
        """ 添加阴影 """
        self.shadowEffect = QGraphicsDropShadowEffect(self)
        self.shadowEffect.setBlurRadius(40)
        self.shadowEffect.setOffset(0, 2)
        self.setGraphicsEffect(self.shadowEffect)

    def paintEvent(self, e):
        """ 绘制背景 """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(QPen(QColor(190, 190, 190, 150)))
        painter.setBrush(QBrush(QColor(227, 227, 227)))
        painter.drawRoundedRect(self.rect(), 8, 8)


class VolumeButton(BasicCircleButton):
    """ 音量按钮 """
    # 静音状态改变信号
    muteStateChanged = pyqtSignal(bool)
    volumeLevelChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        # 按钮图标地址列表
        self.__iconPath_list = [
            r'resource\images\playing_play_bar\volume_black_level_0_47_47.png',
            r'resource\images\playing_play_bar\volume_black_level_1_47_47.png',
            r'resource\images\playing_play_bar\volume_black_level_2_47_47.png',
            r'resource\images\playing_play_bar\volume_black_level_3_47_47.png',
            r'resource\images\playing_play_bar\volume_black_level_mute_47_47.png']
        self.pixmap_list = [QPixmap(i) for i in self.__iconPath_list]
        super().__init__(self.__iconPath_list[0], parent)
        # 初始化标志位
        self.isMute = False
        self.__volumeLevel = 2

    def setVolumeLevel(self, volume):
        """ 根据音量来设置对应图标 """
        if volume == 0:
            self.updateIcon(0)
        elif 0 < volume <= 32 and self.__volumeLevel != 1:
            self.updateIcon(1)
        elif 32 < volume <= 65 and self.__volumeLevel != 2:
            self.updateIcon(2)
        elif volume > 65 and self.__volumeLevel != 3:
            self.updateIcon(3)

    def updateIcon(self, iconIndex: int):
        """ 更新图标 """
        self.__volumeLevel = iconIndex
        self.volumeLevelChanged.emit(iconIndex)
        # 静音时不更新图标
        if not self.isMute:
            self.iconPixmap = self.pixmap_list[iconIndex]
            self.update()

    def eventFilter(self, obj, e):
        """ 安装监听 """
        if obj == self:
            if e.type() in [QEvent.Enter, QEvent.Leave]:
                self.isEnter = not self.isEnter
                self.update()
            elif e.type() in [QEvent.MouseButtonPress, QEvent.MouseButtonRelease]:
                self.isPressed = not self.isPressed
                if e.type() == QEvent.MouseButtonRelease:
                    self.isMute = not self.isMute
                    self.setMute(self.isMute)
                    self.muteStateChanged.emit(self.isMute)
                self.update()
        return False

    def setMute(self, isMute):
        """ 设置静音 """
        self.isMute = isMute
        if isMute:
            self.iconPixmap = self.pixmap_list[-1]
        else:
            self.iconPixmap = self.pixmap_list[self.__volumeLevel]
        self.update()


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(500, 500)
        self.volumeSlider = VolumeSlider(self)
        self.volumeSlider.move(78, 211)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
