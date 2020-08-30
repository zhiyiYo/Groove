# coding:utf-8

import sys

from PyQt5.QtCore import (QAbstractAnimation, QEasingCurve, QEvent,
                          QParallelAnimationGroup, QPropertyAnimation, QRect,
                          Qt, pyqtSignal)
from PyQt5.QtGui import QFont, QFontMetrics, QMouseEvent
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

from .song_card_sub_unit import SongNameCard
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
    checkedStateChanged = pyqtSignal(int, bool)
    switchToAlbumInterfaceSig = pyqtSignal(str, str)  # 发送专辑名和歌手名

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(parent)
        self.__getInfo(songInfo)
        self.__resizeTime = 0
        # 初始化各标志位
        self.isPlaying = False
        self.isSelected = False
        self.isChecked = False
        self.isInSelectionMode = False
        self.isDoubleClicked = False
        self.__currentState = 'notSelected-leave'
        # 记录下每个小部件所占的最大宽度
        self.__maxSongNameCardWidth = 326
        self.__maxSongerLabelWidth = 191
        self.__maxAlbumLabelWidth = 191
        self.__maxTconLabelWidth = 178
        # 记录songCard对应的item的下标
        self.itemIndex = None
        # 创建小部件
        self.songNameCard = SongNameCard(self.songName, self)
        self.songerLabel = ClickableLabel(self.songer, self, False)
        self.albumLabel = ClickableLabel(self.album, self, False)
        self.yearLabel = QLabel(self.year, self)
        self.tconLabel = QLabel(self.tcon, self)
        self.durationLabel = QLabel(self.duration, self)
        self.buttonGroup = self.songNameCard.buttonGroup
        self.playButton = self.songNameCard.playButton
        self.addToButton = self.songNameCard.addToButton
        self.__label_list = [self.songerLabel, self.albumLabel,
                             self.yearLabel, self.tconLabel, self.durationLabel]
        # 创建动画
        self.__createAnimations()
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.__getLabelWidth()
        self.resize(1154, 60)
        self.resize(1154, 60)
        self.setFixedHeight(60)
        self.albumLabel.setCursor(Qt.PointingHandCursor)
        self.songerLabel.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_StyledBackground)
        # 分配ID和属性
        self.albumLabel.setObjectName('clickableLabel')
        self.songerLabel.setObjectName('clickableLabel')
        self.setWidgetState(self.__currentState)
        self.setCheckBoxBtLabelState('notSelected-notPlay')
        # 安装事件过滤器
        self.installEventFilter(self)
        # 信号连接到槽
        self.__connectSignalToSlot()

    def setCheckBoxBtLabelState(self, state: str):
        """ 设置复选框、按钮和标签动态属性，总共3种状态"""
        self.songNameCard.setCheckBoxBtLabelState(state)
        self.songerLabel.setProperty('state', state)
        self.albumLabel.setProperty('state', state)
        self.yearLabel.setProperty('state', state)
        self.tconLabel.setProperty('state', state)
        self.durationLabel.setProperty('state', state)

    def setWidgetState(self, state: str):
        """ 设置按钮组窗口和自己的状态，总共6种状态 """
        self.songNameCard.setButtonGroupState(state)
        self.setProperty('state', state)

    def __getLabelWidth(self):
        """ 计算标签的长度 """
        fontMetrics = QFontMetrics(QFont('Microsoft YaHei', 9))
        self.songerWidth = sum([fontMetrics.width(i)
                                for i in self.songInfo['songer']])
        self.albumWidth = sum([fontMetrics.width(i)
                               for i in self.songInfo['album']])
        self.tconWidth = sum([fontMetrics.width(i)
                              for i in self.songInfo['tcon']])

    def resizeEvent(self, e):
        """ 改变窗口大小时移动标签 """
        # super().resizeEvent(e)
        self.__resizeTime += 1
        if self.__resizeTime == 1:
            self.originalWidth = self.width()
            width = self.width() - 246
            # 计算各个标签所占的最大宽度
            self.__maxSongNameCardWidth = int(326 / 886 * width)
            self.__maxSongerLabelWidth = int(191 / 886 * width)
            self.__maxAlbumLabelWidth = self.__maxSongerLabelWidth
            self.__maxTconLabelWidth = int(178 / 886 * width)
            # 如果实际尺寸大于可分配尺寸，就调整大小
            self.__adjustWidgetWidth()
        elif self.__resizeTime > 1:
            deltaWidth = self.width() - self.originalWidth
            self.originalWidth = self.width()
            # 分配多出来的宽度
            fourEqualWidth = int(deltaWidth / 4)
            self.__maxSongNameCardWidth += fourEqualWidth
            self.__maxSongerLabelWidth += fourEqualWidth
            self.__maxAlbumLabelWidth += fourEqualWidth
            self.__maxTconLabelWidth += (deltaWidth - 3 * fourEqualWidth)
            self.__adjustWidgetWidth()
        # 移动标签
        self.durationLabel.move(self.width() - 45, 20)
        self.tconLabel.move(
            self.durationLabel.x()-70-self.__maxTconLabelWidth, 20)
        self.yearLabel.move(self.tconLabel.x() - 78, 20)
        self.songerLabel.move(self.__maxSongNameCardWidth + 32, 20)
        self.albumLabel.move(self.songerLabel.x() +
                             self.__maxSongerLabelWidth + 16, 20)
        # 更新动画目标移动位置
        self.__getAniTargetX_list()

    def __adjustWidgetWidth(self):
        """ 调整小部件宽度 """
        self.songNameCard.resize(self.__maxSongNameCardWidth, 60)
        if self.songerWidth > self.__maxSongerLabelWidth:
            self.songerLabel.setFixedWidth(self.__maxSongerLabelWidth)
        else:
            self.songerLabel.setFixedWidth(self.songerWidth)
        if self.albumWidth > self.__maxAlbumLabelWidth:
            self.albumLabel.setFixedWidth(self.__maxAlbumLabelWidth)
        else:
            self.albumLabel.setFixedWidth(self.albumWidth)
        if self.tconWidth > self.__maxTconLabelWidth:
            self.tconLabel.setFixedWidth(self.__maxTconLabelWidth)
        else:
            self.tconLabel.setFixedWidth(self.tconWidth)

    def __createAnimations(self):
        """ 创建动画 """
        self.aniGroup = QParallelAnimationGroup(self)
        self.__deltaX_list = [13, 6, -3, -6, -8, -13]
        self.__aniWidget_list = [self.songNameCard, self.songerLabel, self.albumLabel,
                                 self.yearLabel, self.tconLabel, self.durationLabel]
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

    def updateSongCard(self, songInfo: dict):
        """ 更新歌曲卡信息 """
        self.resize(self.size())
        self.__getInfo(songInfo)
        self.songNameCard.setSongName(self.songName)
        self.songerLabel.setText(self.songer)
        self.albumLabel.setText(self.album)
        self.yearLabel.setText(self.year)
        self.tconLabel.setText(self.tcon)
        self.durationLabel.setText(self.duration)
        # 调整宽度
        self.__getLabelWidth()
        songerWidth = self.songerWidth if self.songerWidth <= self.__maxSongerLabelWidth else self.__maxSongerLabelWidth
        albumWidth = self.albumWidth if self.albumWidth <= self.__maxAlbumLabelWidth else self.__maxAlbumLabelWidth
        tconWidth = self.tconWidth if self.tconWidth <= self.__maxTconLabelWidth else self.__maxTconLabelWidth
        self.songerLabel.setFixedWidth(songerWidth)
        self.albumLabel.setFixedWidth(albumWidth)
        self.tconLabel.setFixedWidth(tconWidth)

    def __getInfo(self, songInfo: dict):
        """ 从歌曲信息字典中获取信息 """
        self.songInfo = songInfo
        self.songName = songInfo.get('songName', '未知歌曲')  # type:str
        self.songer = songInfo.get('songer', '未知歌手')     # type:str
        self.album = songInfo.get('album', ['未知专辑'])[0]  # type:str
        self.year = songInfo.get('year', '未知年份')         # type:str
        self.tcon = songInfo.get('tcon', '未知流派')         # type:str
        self.duration = songInfo.get('duration', '0:00')    # type:str

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
                self.songNameCard.checkBox.show()
                self.songNameCard.buttonGroup.setHidden(self.isInSelectionMode)
                state = 'selected-enter' if self.isSelected else 'notSelected-enter'
                self.setWidgetState(state)
                self.setStyle(QApplication.style())
            elif e.type() == QEvent.Leave:
                # 不处于选择模式下时，如果歌曲卡没被选中而鼠标离开窗口就隐藏复选框和按钮组窗口
                if not self.isSelected:
                    self.songNameCard.buttonGroup.hide()
                    self.songNameCard.checkBox.setHidden(
                        not self.isInSelectionMode)
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
                # 发送点击信号
                self.aniGroup.finished.connect(self.__aniFinishedSlot)

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
            self.songNameCard.setWidgetHidden(True)
            self.setWidgetState('notSelected-leave')
            state = 'notSelected-play' if self.isPlaying else 'notSelected-notPlay'
            self.setCheckBoxBtLabelState(state)
        self.setStyle(QApplication.style())

    def playButtonSlot(self):
        """ 播放按钮按下时更新样式 """
        self.playButtonClicked.emit(self.itemIndex)

    def setChecked(self, isChecked: bool):
        """ 设置歌曲卡选中状态 """
        self.songNameCard.checkBox.setChecked(isChecked)

    def checkedStateChangedSlot(self):
        """ 复选框选中状态改变对应的槽函数 """
        self.isChecked = self.songNameCard.checkBox.isChecked()
        self.setSelected(self.isChecked)
        # 只要点击了复选框就进入选择模式，由父级控制退出选择模式
        self.songNameCard.checkBox.show()
        self.setSelectionModeOpen(True)
        # 发出选中状态改变信号
        self.checkedStateChanged.emit(self.itemIndex, self.isChecked)

    def setSelectionModeOpen(self, isOpenSelectionMode: bool):
        """ 设置是否进入选择模式, 处于选择模式下复选框一直可见，按钮不管是否处于选择模式都不可见 """
        if self.isInSelectionMode == isOpenSelectionMode:
            return
        # 更新标志位
        self.isInSelectionMode = isOpenSelectionMode
        # 设置按钮和复选框的可见性
        self.songNameCard.checkBox.setHidden(not isOpenSelectionMode)
        self.songNameCard.buttonGroup.setHidden(True)

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.playButton.clicked.connect(self.playButtonSlot)
        self.albumLabel.clicked.connect(
            lambda: self.switchToAlbumInterfaceSig.emit(
                self.album, self.songer))
        self.songNameCard.checkBox.stateChanged.connect(
            self.checkedStateChangedSlot)
