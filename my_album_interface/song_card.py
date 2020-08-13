# coding:utf-8

import sys

from PyQt5.QtCore import (QAbstractAnimation, QEasingCurve, QEvent,
                          QParallelAnimationGroup, QPropertyAnimation, QRect,
                          Qt, pyqtSignal)
from PyQt5.QtGui import QFont, QFontMetrics, QMouseEvent
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

from .song_name_card import TrackNumSongNameCard
from my_widget.my_label import ClickableLabel


class SongCard(QWidget):
    """ 
    歌曲卡, 窗口的state有6种状态:
        notSelected-leave、notSelected-enter、notSelected-pressed
        selected-leave、selected-enter、selected-pressed 
    """
    clicked = pyqtSignal(int)
    doubleClicked = pyqtSignal(int)
    playButtonClicked = pyqtSignal(int)

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(parent)
        self.songInfo = songInfo
        self.__resizeTime = 0
        # 记录播放状态
        self.isPlaying = False
        self.isSelected = False
        self.isDoubleClicked = False
        self.__currentState = 'notSelected-leave'
        # 记录下每个小部件所占的最大宽度
        self.__maxSongNameCardWidth = 554
        self.__maxSongerLabelWidth = 401
        # 设置序号
        self.itemIndex = None
        # 创建小部件
        self.songNameCard = TrackNumSongNameCard(songInfo['songName'],songInfo['tracknumber'], self)
        self.songerLabel = ClickableLabel(songInfo['songer'], self)
        self.durationLabel = QLabel(songInfo['duration'], self)
        self.buttonGroup = self.songNameCard.buttonGroup
        self.playButton = self.songNameCard.playButton
        self.addToButton = self.songNameCard.addToButton
        self.__label_list = [self.songerLabel, self.durationLabel]
        # 创建动画
        self.__createAnimations()
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.__getLabelWidth()
        self.resize(1154, 60)
        self.setFixedHeight(60)
        self.songerLabel.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_StyledBackground)
        # 分配ID和属性
        self.songerLabel.setObjectName('clickableLabel')
        self.setWidgetState(self.__currentState)
        self.setCheckBoxBtLabelState('notSelected-notPlay')
        # self.__setQss()
        # 安装事件过滤器
        self.installEventFilter(self)
        # 信号连接到槽
        self.playButton.clicked.connect(self.playButtonSlot)

    def setCheckBoxBtLabelState(self, state: str):
        """ 设置复选框、按钮和标签动态属性，总共3种状态"""
        self.songNameCard.setCheckBoxBtLabelsState(state)
        self.songerLabel.setProperty('state', state)
        self.durationLabel.setProperty('state', state)

    def setWidgetState(self, state: str):
        """ 设置按钮组窗口和自己的状态，总共6种状态 """
        self.songNameCard.setButtonGroupState(state)
        self.setProperty('state', state)

    def __setQss(self):
        """ 设置层叠样式 """
        with open(r'resource\css\songTabInterfaceSongCard.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __getLabelWidth(self):
        """ 计算标签的长度 """
        fontMetrics = QFontMetrics(QFont('Microsoft YaHei', 9))
        self.songerWidth = sum([fontMetrics.width(i)
                                for i in self.songInfo['songer']])

    def resizeEvent(self, e):
        """ 改变窗口大小时移动标签 """
        # super().resizeEvent(e)
        self.__resizeTime += 1
        if self.__resizeTime == 1:
            self.originalWidth = self.width()
            width = self.width() - 131
            # 计算各个标签所占的最大宽度
            self.__maxSongNameCardWidth = int(554 / 955 * width)
            self.__maxSongerLabelWidth = int(401 / 955 * width)
            # 如果实际尺寸大于可分配尺寸，就调整大小
            self.__adjustWidgetWidth()
        elif self.__resizeTime > 1:
            deltaWidth = self.width() - self.originalWidth
            self.originalWidth = self.width()
            # 分配多出来的宽度
            fourEqualWidth = int(deltaWidth / 2)
            self.__maxSongNameCardWidth += fourEqualWidth
            self.__maxSongerLabelWidth += fourEqualWidth
            self.__adjustWidgetWidth()
        # 移动标签
        self.durationLabel.move(self.width() - 44, 20)
        self.songerLabel.move(self.__maxSongNameCardWidth + 16, 20)
        # 更新动画目标移动位置
        self.__getAniTargetX_list()

    def __adjustWidgetWidth(self):
        """ 调整小部件宽度 """
        self.songNameCard.resize(self.__maxSongNameCardWidth, 60)
        if self.songerWidth > self.__maxSongerLabelWidth:
            self.songerLabel.setFixedWidth(self.__maxSongerLabelWidth)
        else:
            self.songerLabel.setFixedWidth(self.songerWidth)

    def __createAnimations(self):
        """ 创建动画 """
        self.aniGroup = QParallelAnimationGroup(self)
        self.__deltaX_list = [13, -3, -13]
        self.__aniWidget_list = [self.songNameCard, self.songerLabel, self.durationLabel]
        self.__ani_list = [QPropertyAnimation(
            widget, b'geometry') for widget in self.__aniWidget_list]
        for ani in self.__ani_list:
            ani.setDuration(400)
            ani.setEasingCurve(QEasingCurve.OutQuad)
            self.aniGroup.addAnimation(ani)
        # 记录下移动目标位置
        self.__getAniTargetX_list()

    def __getAniTargetX_list(self):
        """ 计算动画的初始值 """
        self.__aniTargetX_list = []
        for deltaX, widget in zip(self.__deltaX_list, self.__aniWidget_list):
            self.__aniTargetX_list.append(deltaX + widget.x())

    def updateSongCard(self, songInfo):
        """ 更新歌曲卡信息 """
        self.resize(self.size())
        self.songInfo = songInfo
        self.songNameCard.setCardInfo(songInfo['songName'],songInfo['tracknumber'])
        self.songerLabel.setText(songInfo['songer'])
        self.durationLabel.setText(songInfo['duration'])
        # 调整宽度
        self.__getLabelWidth()
        songerWidth = self.songerWidth if self.songerWidth <= self.__maxSongerLabelWidth else self.__maxSongerLabelWidth
        self.songerLabel.setFixedWidth(songerWidth)

    def setPlay(self, isPlay):
        """ 设置播放状态并更新样式 """
        self.isPlaying = isPlay
        self.isSelected = isPlay
        if isPlay:
            self.isSelected = True
            self.setCheckBoxBtLabelState('selected')
            self.setWidgetState('selected-leave')
        else:
            self.setCheckBoxBtLabelState('notSelected-notPlay')
            self.setWidgetState('notSelected-leave')
        self.songNameCard.setPlay(isPlay)
        self.setStyle(QApplication.style())

    def eventFilter(self, obj, e: QEvent):
        """ 安装监听 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.songNameCard.setWidgetsHidden(False)
                state = 'selected-enter' if self.isSelected else 'notSelected-enter'
                self.setWidgetState(state)
                self.setStyle(QApplication.style())
            elif e.type() == QEvent.Leave:
                if not self.isSelected:
                    self.songNameCard.setWidgetsHidden(True)
                state = 'selected-leave' if self.isSelected else 'notSelected-leave'
                self.setWidgetState(state)
                self.setStyle(QApplication.style())
            elif e.type() == QEvent.MouseButtonPress:
                state = 'selected-pressed' if self.isSelected else 'notSelected-pressed'
                if e.button() == Qt.LeftButton:
                    self.isSelected = True
                self.setWidgetState(state)
                self.setStyle(QApplication.style())
            elif e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.setWidgetState('selected-leave')
                self.setCheckBoxBtLabelState('selected')  # 鼠标松开时将设置标签为白色
                self.setStyle(QApplication.style())
            elif e.type() == QEvent.MouseButtonDblClick:
                self.isDoubleClicked = True
        return super().eventFilter(obj, e)

    def mousePressEvent(self, e):
        """ 鼠标按下时移动小部件 """
        super().mousePressEvent(e)
        # 移动小部件
        if self.aniGroup.state() == QAbstractAnimation.Stopped:
            for deltaX, widget in zip(self.__deltaX_list, self.__aniWidget_list):
                widget.move(widget.x() + deltaX, widget.y())
        else:
            self.aniGroup.stop()    # 强制停止还未结束的动画
            for targetX, widget in zip(self.__aniTargetX_list, self.__aniWidget_list):
                widget.move(targetX, widget.y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        """ 鼠标松开时开始动画 """
        for ani, widget, deltaX in zip(self.__ani_list, self.__aniWidget_list, self.__deltaX_list):
            ani.setStartValue(
                QRect(widget.x(), widget.y(), widget.width(), widget.height()))
            ani.setEndValue(
                QRect(widget.x() - deltaX, widget.y(), widget.width(), widget.height()))
        self.aniGroup.start()
        if e.button() == Qt.LeftButton:
            self.clicked.emit(self.itemIndex)
        # 左键点击时才发送信号
        if self.isDoubleClicked and e.button() == Qt.LeftButton:
            self.isDoubleClicked = False
            if not self.isPlaying:
                self.aniGroup.finished.connect(self.__aniFinishedSlot)
        self.songNameCard.trackNumLabel.hide()

    def __aniFinishedSlot(self):
        """ 动画完成时发出双击信号 """
        self.doubleClicked.emit(self.itemIndex)
        self.aniGroup.disconnect()

    def setSelected(self, isSelected: bool):
        """ 设置选中状态 """
        self.isSelected = isSelected
        if isSelected:
            self.setWidgetState('selected-leave')
            self.setCheckBoxBtLabelState('selected')
        else:
            self.songNameCard.setWidgetsHidden(True)
            self.setWidgetState('notSelected-leave')
            state = 'notSelected-play' if self.isPlaying else 'notSelected-notPlay'
            self.setCheckBoxBtLabelState(state)
        self.setStyle(QApplication.style())

    def playButtonSlot(self):
        """ 播放按钮按下时更新样式 """
        self.playButtonClicked.emit(self.itemIndex)
