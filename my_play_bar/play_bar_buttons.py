#coding:utf-8

""" 
按钮优先级：单曲循环>随机播放>列表循环/顺序播放：
    处于单曲循环播放状态时，按下随机播放按钮，记录下随机按钮的按下状态，但不改变播放模式；
    当循环模式按钮的状态不是单曲循环时，如果随机播放按下或者已经按下，切换为随机播放模式;
    如果取消随机播放，恢复之前的循环模式;
    随机播放的按钮没有按下时，根据循环模式按钮的状态决定播放方式
"""

import sys

from PyQt5.QtCore import QEvent, QSize, Qt
from PyQt5.QtGui import QBrush, QColor, QEnterEvent, QIcon, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QApplication, QToolButton, QWidget
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
        if obj == self:
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
        """ 绘制背景 """
        # super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        # 设置描边画笔
        pen = QPen(QColor(255, 255, 255, 100))
        pen.setWidth(2)
        # 设置画笔
        painter.setPen(pen)
        painter.drawEllipse(1, 1, 62, 62)
        # 设置背景图
        painter.setPen(Qt.NoPen)
        if not self.isPlaying:
            self.image = QPixmap(r'resource\images\playBar\播放_63_63.png')
        else:
            self.image = QPixmap(r'resource\images\playBar\暂停_63_63.png')
        # 绘制背景
        if self.isPressed:
            self.image.scaled(58, 58, Qt.KeepAspectRatio,
                              Qt.SmoothTransformation)
            painter.drawPixmap(2, 2, 59, 59, self.image)
        elif self.isEnter:
            painter.setPen(QPen(QColor(101, 106, 116, 180)))
            bgBrush = QBrush(QColor(73, 76, 84, 70))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 62, 62)
        # 绘制背景图
        if not self.isPressed:
            brush = QBrush(self.image)
            painter.setBrush(brush)
            painter.drawEllipse(1, 1, 63, 63)


class RandomPlayButton(QToolButton):
    """ 随机播放按钮 """

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

    def eventFilter(self, obj, e):
        """ 按钮按下时更换按钮 """
        if obj == self:
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.isSelected = not self.isSelected
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
        """ 绘制背景 """
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        self.image = QPixmap(r'resource\images\playBar\随机播放_45_45.png')
        if self.isSelected:
            bgBrush = QBrush(QColor(73, 76, 84, 120))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
        if self.isPressed:
            painter.setPen(QPen(QColor(101, 106, 116, 80)))
            bgBrush = QBrush(QColor(73, 76, 84, 110))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
            self.image = self.image.scaled(44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(1,1,44,44,self.image)
        elif self.isEnter:
            # 设置画笔
            painter.setPen(QPen(QColor(101, 106, 116, 180)))
            bgBrush = QBrush(QColor(73, 76, 84, 80))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
        # 绘制背景图
        if not self.isPressed:
            painter.setPen(Qt.NoPen)
            brush = QBrush(self.image)
            painter.setBrush(brush)
            painter.drawEllipse(1, 1, 45, 45)


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
        super().mouseReleaseEvent(e)
        self.isPressed = False
        self.update()

    def paintEvent(self, e):
        """ 绘制背景 """
        self.image = QPixmap(self.icon_path)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        # 设置画笔
        painter.setPen(Qt.NoPen)
        if self.isPressed:
            bgBrush = QBrush(QColor(73, 76, 84, 100))
            painter.setBrush(bgBrush)
            painter.drawEllipse(2, 2, 42, 42)
            self.image = self.image.scaled(
                43, 43, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        elif self.isEnter:
            painter.setPen(QPen(QColor(101, 106, 116, 180)))
            bgBrush = QBrush(QColor(73, 76, 84, 70))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
        painter.setPen(Qt.NoPen)
        # 绘制背景图
        if not self.isPressed:
            painter.drawPixmap(1, 1, 45, 45, self.image)
        else:
            painter.drawPixmap(2, 2, 42, 42, self.image)


class LastSongButton(BasicButton):
    """ 播放上一首按钮 """

    def __init__(self, parent=None):
        self.icon_path = r'resource\images\playBar\上一首_45_45.png'
        super().__init__(self.icon_path, parent)


class NextSongButton(BasicButton):
    """ 播放下一首按钮 """

    def __init__(self, parent=None):
        self.icon_path = r'resource\images\playBar\下一首_45_45.png'
        super().__init__(self.icon_path, parent)


class LoopModeButton(QToolButton):
    """ 循环播放模式按钮 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置进入标志位
        self.isEnter = False
        # 设置点击次数以及对应的循环模式和的图标
        self.clickedTime = 0
        self.loopMode = QMediaPlaylist.Sequential
        self.__loopMode_list = [QMediaPlaylist.Sequential,
                                QMediaPlaylist.Loop, QMediaPlaylist.CurrentItemInLoop]

        self.__iconPath_list = [r'resource\images\playBar\循环播放_45_45.png',
                                r'resource\images\playBar\循环播放_45_45.png',
                                r'resource\images\playBar\单曲循环_45_45.png']
        self.setFixedSize(47, 47)
        self.installEventFilter(self)

    def eventFilter(self, obj, e):
        """ 按钮按下时更换图标 """
        if obj == self:
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.clickedTime = (self.clickedTime + 1) % 3
                self.loopMode = self.__loopMode_list[self.clickedTime]
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
        painter.setRenderHint(QPainter.Antialiasing, True)
        # 设置画笔
        painter.setPen(Qt.NoPen)
        if self.isEnter and self.clickedTime == 0:
            painter.setPen(QPen(QColor(101, 106, 116, 180)))
            bgBrush = QBrush(QColor(73, 76, 84, 80))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
        # 绘制背景色
        if self.clickedTime != 0:
            brush = QBrush(QColor(73, 76, 84, 120))
            painter.setBrush(brush)
            painter.drawEllipse(1, 1, 44, 44)
        # 绘制背景图
        painter.setPen(Qt.NoPen)
        self.image = QPixmap(self.__iconPath_list[self.clickedTime])
        brush = QBrush(self.image)
        painter.setBrush(brush)
        painter.drawEllipse(1, 1, 45, 45)


class VolumeButton(QToolButton):
    """ 音量按钮 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置标志位
        self.isEnter = False
        self.isSelected = False
        self.isPressed = False
        # 当前音量等级及其各个图标地址
        self.currentVolumeLevel = 1
        self.__iconPath_list = [r'resource\images\playBar\音量按钮_无_45_45.png',
                                r'resource\images\playBar\音量按钮_低_45_45.png',
                                r'resource\images\playBar\音量按钮_中_45_45.png',
                                r'resource\images\playBar\音量按钮_高_45_45.png',
                                r'resource\images\playBar\音量按钮_静音_45_45.png']
        self.setFixedSize(47, 47)
        # self.installEventFilter(self)

    def mousePressEvent(self, e):
        """ 鼠标按下更新背景 """
        super().mousePressEvent(e)
        self.isPressed = True
        self.update()

    def mouseReleaseEvent(self, e):
        """ 鼠标按下更新背景 """
        super().mouseReleaseEvent(e)
        self.isPressed = False
        self.isSelected = not self.isSelected
        self.update()

    def eventFilter(self, obj, e):
        """ 按钮按下时变为静音图标 """
        if obj == self:
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.isSelected = not self.isSelected
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
        # 设置画笔和背景图
        painter.setPen(Qt.NoPen)
        self.image = QPixmap(self.__iconPath_list[self.currentVolumeLevel])
        if self.isSelected:
            # 如果被按下就换成静音按钮
            self.image = QPixmap(self.__iconPath_list[-1])
        if self.isPressed:
            bgBrush = QBrush(QColor(73, 76, 84, 90))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
            self.image = self.image.scaled(
                44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(1,1,44,44,self.image)
        elif self.isEnter:
            # 设置画笔
            painter.setPen(QPen(QColor(101, 106, 116, 180)))
            bgBrush = QBrush(QColor(73, 76, 84, 70))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
        # 绘制背景图
        if not self.isPressed:
            painter.setPen(Qt.NoPen)
            brush = QBrush(self.image)
            painter.setBrush(brush)
            painter.drawEllipse(1, 1, 45, 45)

    def setVolumeLevel(self, volumeLevel):
        """ 根据音量大小的不同来更换图标 """
        if self.currentVolumeLevel != volumeLevel:
            self.currentVolumeLevel = volumeLevel
            self.update()


class SmallPlayModeButton(BasicButton):
    """ 最小播放模式按钮 """

    def __init__(self, parent=None):
        self.icon_path = r'resource\images\playBar\最小播放模式_45_45.png'
        super().__init__(self.icon_path, parent)


class MoreActionsButton(BasicButton):
    """ 最小化播放按钮 """

    def __init__(self, parent=None):
        self.icon_path = r'resource\images\playBar\更多操作_45_45.png'
        super().__init__(self.icon_path, parent)
