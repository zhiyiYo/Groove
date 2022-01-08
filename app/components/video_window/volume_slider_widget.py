# coding:utf-8
from components.buttons.circle_button import CircleButton
from components.widgets.slider import Slider
from PyQt5.QtCore import QEvent, QFile, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel


class VolumeSliderWidget(QWidget):
    """ 音量滑动条 """

    muteStateChanged = pyqtSignal(bool)
    volumeLevelChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.volumeButton = VolumeButton(self)
        self.volumeSlider = Slider(Qt.Horizontal, self)
        self.volumeLabel = QLabel('100', self)
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedSize(345, 78)
        self.volumeButton.move(25, 15)
        self.volumeSlider.move(90, 25)
        self.volumeSlider.setSingleStep(1)
        self.volumeSlider.setRange(0, 100)
        self.volumeLabel.move(300, 28)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.__setQss()
        self.__connectSignalToSlot()

    def __setQss(self):
        """ 设置层叠样式 """
        self.volumeSlider.setObjectName('volumeSlider')

        f = QFile(":/qss/volume_slider_widget.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

    def paintEvent(self, e):
        """ 绘制背景 """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(25, 25, 25)))
        painter.setBrush(QBrush(QColor(31, 31, 31)))
        painter.drawRoundedRect(self.rect(), 10, 10)

    def setVolume(self, volume: int):
        """ 设置音量 """
        self.volumeSlider.setValue(volume)
        self.__onVolumeChanged(volume)

    def __onVolumeChanged(self, volume: int):
        """ 音量改变槽函数 """
        self.volumeButton.setVolumeLevel(volume)
        self.volumeLabel.setText(str(volume))
        self.volumeLabel.adjustSize()

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.volumeSlider.valueChanged.connect(self.__onVolumeChanged)
        self.volumeButton.muteStateChanged.connect(self.muteStateChanged)
        self.volumeButton.volumeLevelChanged.connect(self.volumeLevelChanged)


class VolumeButton(CircleButton):
    """ 音量按钮 """

    # 静音状态改变信号
    muteStateChanged = pyqtSignal(bool)
    volumeLevelChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        # 按钮图标地址列表
        self.__iconPath_list = [
            ":/images/video_window/Volume0.png",
            ":/images/video_window/Volume1.png",
            ":/images/video_window/Volume2.png",
            ":/images/video_window/Volume3.png",
            ":/images/video_window/Volumex.png",
        ]
        self.pixmap_list = [QPixmap(i) for i in self.__iconPath_list]
        super().__init__(self.__iconPath_list[0], parent)
        # 初始化标志位
        self.isMute = False
        self.__volumeLevel = 0

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
                    self.setMute(not self.isMute)
                    self.muteStateChanged.emit(self.isMute)
                self.update()
        return False

    def setMute(self, isMute: bool):
        """ 设置静音 """
        if self.isMute == isMute:
            return
        self.isMute = isMute
        index = -1 if isMute else self.__volumeLevel
        self.iconPixmap = self.pixmap_list[index]
        self.update()
