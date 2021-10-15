# coding:utf-8

"""
按钮优先级：单曲循环>随机播放>列表循环/顺序播放：
    处于单曲循环播放状态时，按下随机播放按钮，记录下随机按钮的按下状态，但不改变播放模式；
    当循环模式按钮的状态不是单曲循环时，如果随机播放按下或者已经按下，切换为随机播放模式;
    如果取消随机播放，恢复之前的循环模式;
    随机播放的按钮没有按下时，根据循环模式按钮的状态决定播放方式
"""

from PyQt5.QtCore import QEvent, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtMultimedia import QMediaPlaylist


class PlayButton(QToolButton):
    """ 控制播放和暂停的按钮 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置标志位
        self.isPlaying = False
        self.isEnter = False
        self.isPressed = False
        # 设置图标
        self.iconPath_list = [
            ':/images/play_bar/Play.png', ':/images/play_bar/Pause.png']
        self.setFixedSize(65, 65)
        self.setStyleSheet(
            "QToolButton{border:none;margin:0;background:transparent}")
        self.installEventFilter(self)

    def setPlay(self, play: bool = True):
        """ 根据播放状态设置按钮图标 """
        self.isPlaying = play
        self.update()

    def eventFilter(self, obj, e):
        """ 按钮按下时更换按钮 """
        if obj == self and self.isEnabled():
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.isPlaying = not self.isPlaying
                self.isPressed = False
                self.update()
                return False
            if e.type() == QEvent.MouseButtonPress and e.button() == Qt.LeftButton:
                self.isPressed = True
                self.update()
                return False
        return super().eventFilter(obj, e)

    def enterEvent(self, e):
        """ 鼠标进入时更新背景 """
        self.isEnter = True
        self.update()

    def leaveEvent(self, e):
        """ 鼠标离开时更新背景 """
        self.isEnter = False
        self.update()

    def paintEvent(self, e):
        """ 绘制按钮 """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        if self.isPressed:
            painter.setPen(QPen(QColor(255, 255, 255, 120), 2))
            painter.drawEllipse(1, 1, 62, 62)
        elif self.isEnter:
            # enter时绘制一个双色圆环
            painter.setPen(QPen(QColor(255, 255, 255, 18)))
            painter.drawEllipse(1, 1, 62, 62)
            # 绘制深色背景
            painter.setBrush(QBrush(QColor(0, 0, 0, 50)))
            painter.drawEllipse(2, 2, 61, 61)
            painter.setPen(QPen(QColor(0, 0, 0, 39)))
            painter.drawEllipse(1, 1, 63, 63)
        else:
            # normal时绘制一个宽度为2，alpha=50的单色圆环
            painter.setPen(QPen(QColor(255, 255, 255, 50), 2))
            painter.drawEllipse(1, 1, 62, 62)
        # 绘制图标
        if not self.isPressed:
            iconPix = QPixmap(self.iconPath_list[self.isPlaying])
            painter.drawPixmap(1, 1, 63, 63, iconPix)
        else:
            iconPix = QPixmap(self.iconPath_list[self.isPlaying]).scaled(
                58, 58, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(3, 3, 59, 59, iconPix)


class RandomPlayButton(QToolButton):
    """ 随机播放按钮 """

    randomPlayChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置标志位
        self.isSelected = False
        self.isPressed = False
        self.isEnter = False
        self.setFixedSize(47, 47)
        self.setStyleSheet(
            "QToolButton{border:none;margin:0;background:transparent}")
        self.installEventFilter(self)

    def setRandomPlay(self, isRandomPlay: bool):
        """ 设置随机播放状态 """
        if isRandomPlay == self.isSelected:
            return
        self.isSelected = isRandomPlay
        self.update()

    def eventFilter(self, obj, e):
        """ 按钮按下时更换按钮 """
        if obj == self:
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.isSelected = not self.isSelected
                self.isPressed = False
                self.update()
                self.randomPlayChanged.emit(self.isSelected)
                return False
            if e.type() == QEvent.MouseButtonPress and e.button() == Qt.LeftButton:
                self.isPressed = True
                self.update()
                return False
        return super().eventFilter(obj, e)

    def enterEvent(self, e):
        """ 鼠标进入时更新背景 """
        self.isEnter = True
        self.update()

    def leaveEvent(self, e):
        """ 鼠标离开时更新背景 """
        self.isEnter = False
        self.update()

    def paintEvent(self, e):
        """ 绘制背景 """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        self.image = QPixmap(':/images/play_bar/Shuffle.png')
        if self.isSelected:
            bgBrush = QBrush(QColor(0, 0, 0, 106))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
        if self.isPressed:
            painter.setPen(QPen(QColor(0, 0, 0, 45)))
            bgBrush = QBrush(QColor(0, 0, 0, 45))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
            self.image = self.image.scaled(
                44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(2, 2, 44, 44, self.image)
        elif self.isEnter:
            # 设置画笔
            painter.setPen(QPen(QColor(0, 0, 0, 38)))
            bgBrush = QBrush(QColor(0, 0, 0, 26))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
        # 绘制图标
        if not self.isPressed:
            painter.setPen(Qt.NoPen)
            painter.drawPixmap(1, 1, 45, 45, self.image)


class BasicButton(QToolButton):
    """ 基本圆形按钮 """

    def __init__(self, icon_path, parent=None):
        super().__init__(parent)
        # 设置标志位
        self.isEnter = False
        self.isPressed = False
        self.icon_path = icon_path
        self.setFixedSize(47, 47)

    def enterEvent(self, e):
        """ 鼠标进入时更新背景 """
        self.isEnter = True
        self.update()

    def leaveEvent(self, e):
        """ 鼠标离开时更新背景 """
        self.isEnter = False
        self.update()

    def mousePressEvent(self, e):
        """ 鼠标按下更新背景 """
        super().mousePressEvent(e)
        self.isPressed = True
        self.update()

    def mouseReleaseEvent(self, e):
        """ 鼠标按下更新背景 """
        self.isPressed = False
        self.update()
        super().mouseReleaseEvent(e)

    def paintEvent(self, e):
        """ 绘制背景 """
        image = QPixmap(self.icon_path)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        # 设置画笔
        painter.setPen(Qt.NoPen)
        if self.isPressed:
            bgBrush = QBrush(QColor(0, 0, 0, 45))
            painter.setBrush(bgBrush)
            painter.drawEllipse(2, 2, 42, 42)
            image = image.scaled(
                43, 43, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        elif self.isEnter:
            painter.setPen(QPen(QColor(0, 0, 0, 38)))
            bgBrush = QBrush(QColor(0, 0, 0, 26))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
        painter.setPen(Qt.NoPen)
        # 绘制背景图
        if not self.isPressed:
            painter.drawPixmap(1, 1, 45, 45, image)
        else:
            painter.drawPixmap(2, 2, 42, 42, image)


class LoopModeButton(QToolButton):
    """ 循环播放模式按钮 """

    loopModeChanged = pyqtSignal(QMediaPlaylist.PlaybackMode)

    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置标志位
        self.isEnter = False
        self.isPressed = False
        # 设置点击次数以及对应的循环模式和的图标
        self.clickedTime = 0
        self.loopMode = QMediaPlaylist.Sequential
        self.__loopMode_list = [QMediaPlaylist.Sequential,
                                QMediaPlaylist.Loop, QMediaPlaylist.CurrentItemInLoop]

        self.__iconPath_list = [':/images/play_bar/RepeatAll.png',
                                ':/images/play_bar/RepeatAll.png',
                                ':/images/play_bar/RepeatOne.png']
        self.setFixedSize(47, 47)
        self.installEventFilter(self)

    def setLoopMode(self, loopMode: QMediaPlaylist.PlaybackMode):
        """ 设置循环模式 """
        self.loopMode = loopMode
        self.clickedTime = self.__loopMode_list.index(loopMode)
        self.update()

    def eventFilter(self, obj, e):
        """ 按钮按下时更换图标 """
        if obj == self:
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.clickedTime = (self.clickedTime + 1) % 3
                self.loopMode = self.__loopMode_list[self.clickedTime]
                self.update()
                self.loopModeChanged.emit(self.loopMode)
                return False
        return super().eventFilter(obj, e)

    def enterEvent(self, e):
        """ 鼠标进入时更新背景 """
        self.isEnter = True
        self.update()

    def leaveEvent(self, e):
        """ 鼠标离开时更新背景 """
        self.isEnter = False
        self.update()

    def mousePressEvent(self, e):
        """ 鼠标按下更新背景 """
        super().mousePressEvent(e)
        self.isPressed = True
        self.update()

    def mouseReleaseEvent(self, e):
        """ 鼠标按下更新背景 """
        super().mouseReleaseEvent(e)
        self.isPressed = False
        self.update()

    def paintEvent(self, e):
        """ 绘制背景 """
        self.image = QPixmap(self.__iconPath_list[self.clickedTime])
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        # 设置画笔
        painter.setPen(Qt.NoPen)
        # 绘制背景色
        if self.clickedTime != 0:
            brush = QBrush(QColor(0, 0, 0, 106))
            painter.setBrush(brush)
            painter.drawEllipse(1, 1, 44, 44)
        if self.isPressed:
            painter.setPen(QPen(QColor(0, 0, 0, 45)))
            bgBrush = QBrush(QColor(0, 0, 0, 45))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
            self.image = self.image.scaled(
                44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(2, 2, 44, 44, self.image)
        elif self.isEnter and self.clickedTime == 0:
            painter.setPen(QPen(QColor(0, 0, 0, 38)))
            bgBrush = QBrush(QColor(0, 0, 0, 26))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)

        # 绘制背景图
        painter.setPen(Qt.NoPen)
        # 绘制图标
        if not self.isPressed:
            painter.setPen(Qt.NoPen)
            painter.drawPixmap(1, 1, 45, 45, self.image)


class VolumeButton(QToolButton):
    """ 音量按钮 """

    muteStateChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置标志位
        self.isEnter = False
        self.isPressed = False
        self.isMute = False
        # 当前音量等级及其各个图标地址
        self.currentVolumeLevel = 1
        self.__iconPath_list = [
            ':/images/play_bar/Volume0.png',
            ':/images/play_bar/Volume1.png',
            ':/images/play_bar/Volume2.png',
            ':/images/play_bar/Volume3.png',
            ':/images/play_bar/Volumex.png']
        self.pixmap_list = [QPixmap(i) for i in self.__iconPath_list]
        self.iconPixmap = self.pixmap_list[1]
        self.setFixedSize(47, 47)

    def mousePressEvent(self, e):
        """ 鼠标按下更新背景 """
        super().mousePressEvent(e)
        self.isPressed = True
        self.update()

    def mouseReleaseEvent(self, e):
        """ 鼠标松开更新背景 """
        super().mouseReleaseEvent(e)
        self.isPressed = False
        self.setMute(not self.isMute)
        self.update()
        self.muteStateChanged.emit(self.isMute)

    def enterEvent(self, e):
        """ 鼠标进入时更新背景 """
        self.isEnter = True
        self.update()

    def leaveEvent(self, e):
        """ 鼠标离开时更新背景 """
        self.isEnter = False
        self.update()

    def paintEvent(self, e):
        """ 绘制背景 """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        # 设置画笔和背景图
        painter.setPen(Qt.NoPen)
        if self.isPressed:
            bgBrush = QBrush(QColor(0, 0, 0, 45))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
            iconPixmap = self.iconPixmap.scaled(
                44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(1, 1, 44, 44, iconPixmap)
        elif self.isEnter:
            # 设置画笔
            painter.setPen(QPen(QColor(0, 0, 0, 38)))
            bgBrush = QBrush(QColor(0, 0, 0, 26))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
        # 绘制背景图
        if not self.isPressed:
            painter.setPen(Qt.NoPen)
            brush = QBrush(self.iconPixmap)
            painter.setBrush(brush)
            painter.drawEllipse(1, 1, 45, 45)

    def setMute(self, isMute: bool):
        """ 设置静音状态 """
        if isMute == self.isMute:
            return
        self.isMute = isMute
        index = -1 if isMute else self.currentVolumeLevel
        self.iconPixmap = self.pixmap_list[index]
        self.update()

    def setVolumeLevel(self, volume):
        """ 根据音量来设置图标 """
        if volume == 0:
            self.__updateIcon(0)
        elif volume <= 32 and self.currentVolumeLevel != 1:
            self.__updateIcon(1)
        elif 33 <= volume <= 65 and self.currentVolumeLevel != 2:
            self.__updateIcon(2)
        elif volume > 65 and self.currentVolumeLevel != 3:
            self.__updateIcon(3)

    def __updateIcon(self, iconIndex):
        """ 更新图标 """
        self.currentVolumeLevel = iconIndex
        if not self.isMute:
            self.iconPixmap = self.pixmap_list[iconIndex]
            self.update()
