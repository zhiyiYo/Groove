# coding:utf-8
import os

from common.database.entity import SongInfo
from common.signal_bus import signalBus
from components.widgets.menu import AddToMenu
from PyQt5.QtCore import (QAbstractAnimation, QEasingCurve, QEvent,
                          QParallelAnimationGroup, QPoint, QPropertyAnimation,
                          QRect, Qt, pyqtSignal)
from PyQt5.QtGui import QFont, QFontMetrics, QMouseEvent
from PyQt5.QtWidgets import QApplication, QWidget

from .song_card_type import SongCardType
from .song_name_card import SongNameCardFactory


class BasicSongCard(QWidget):
    """ 歌曲卡基类 """

    clicked = pyqtSignal(int)
    doubleClicked = pyqtSignal(int)
    playButtonClicked = pyqtSignal(int)
    checkedStateChanged = pyqtSignal(int, bool)

    def __init__(self, songInfo: SongInfo, songCardType, parent=None):
        """ 实例化歌曲卡

        Parameters
        ----------
        songInfo: SongInfo
            歌曲信息字典

        songCardType: SongCardType
            歌曲卡类型

        parent:
            父级
        """
        super().__init__(parent)
        self.setFixedHeight(60)
        self.setSongInfo(songInfo)
        self.__resizeTime = 0
        self.__songCardType = songCardType

        # 初始化各标志位
        self.isSongExist = True
        self.isPlaying = False
        self.isSelected = False
        self.isChecked = False
        self.isInSelectionMode = False
        self.isDoubleClicked = False

        # 记录songCard对应的item的下标
        self.itemIndex = None

        # 创建歌曲名字卡
        self.songNameCard = SongNameCardFactory.create(
            songCardType, self.songName, self.track, self)

        self.__referenceWidgets()

        # 初始化小部件列表
        self.__scaleableLabelTextWidths = []  # 可拉伸的标签的文本的宽度列表
        self.__scaleableWidgetMaxWidths = []  # 可拉伸部件的最大宽度列表
        self.__dynamicStyleLabels = []
        self.__scaleableWidgets = []
        self.__clickableLabels = []
        self.__labelSpacings = []
        self.__labels = []
        self.__widgets = []  # 存放所有的小部件

        # 创建动画组和动画列表
        self.__aniGroup = QParallelAnimationGroup(self)
        self.__aniWidgets = []
        self.__deltaXs = []
        self.__anis = []

        # 安装事件过滤器
        self.installEventFilter(self)

        # 信号连接到槽
        self.playButton.clicked.connect(
            lambda: self.playButtonClicked.emit(self.itemIndex))

    def setSongInfo(self, songInfo: SongInfo):
        """ 设置歌曲信息 """
        self.songInfo = songInfo
        self.songPath = songInfo.file
        self.songName = songInfo.title
        self.singer = songInfo.singer
        self.album = songInfo.album
        self.year = str(songInfo.year or '')
        self.genre = songInfo.genre or ''
        self.track = str(songInfo.track or 0)
        self.duration = f"{int(songInfo.duration//60)}:{int(songInfo.duration%60):02}"

    def setScalableWidgets(self, widgets: list, widths: list, fixedWidth=0):
        """ 设置可随着歌曲卡的伸缩而伸缩的标签

        Parameters
        ----------
        widgets: list
            随着歌曲卡的伸缩而伸缩的小部件列表，要求第一个元素为歌名卡，后面的元素都是label

        widths: list
            与可伸缩小部件相对应的小部件初始长度列表

        fixedWidth: int
            为其他不可拉伸的小部件保留的宽度
        """
        if self.__scaleableWidgetMaxWidths:
            return

        self.__checkIsLengthEqual(widgets, widths)

        # 必须先将所有标签添加到列表中后才能调用这个函数
        if not self.__labels:
            raise Exception("必须先调用 addLabels() 将标签添加到窗口中")

        # 歌名卡默认可拉伸
        self.__scaleableWidgets = widgets
        self.__scaleableWidgetMaxWidths = widths

        # 计算初始宽度
        w = sum(widths) + sum(self.__labelSpacings) + fixedWidth
        self.resize(w, 60)

    def addLabels(self, labels: list, spacings: list):
        """ 往歌曲卡中添加除了歌曲名卡之外的标签，只能初始化一次标签列表

        Paramerter
        ----------
        labels: list
            歌名卡后的标签列表

        spacings: list
            每个标签的前置空白
        """
        if self.__labels:
            return

        self.__checkIsLengthEqual(labels, spacings)
        self.__labels = labels
        self.__labelSpacings = spacings
        self.__widgets = [self.songNameCard] + self.__labels

    def setDynamicStyleLabels(self, labels: list):
        """ 设置需要动态更新样式的标签列表 """
        self.__dynamicStyleLabels = labels

    def setClickableLabels(self, labels: list):
        """ 设置可点击的标签列表 """
        self.__clickableLabels = labels
        for label in self.__clickableLabels:
            label.setObjectName("clickableLabel")

    def setSelected(self, isSelected: bool):
        """ 设置选中状态 """
        if self.isSelected == isSelected:
            return

        self.isSelected = isSelected
        if isSelected:
            self.setWidgetState("selected-leave")
            self.setCheckBoxBtLabelState("selected")
        else:
            self.songNameCard.setWidgetHidden(True)
            self.setWidgetState("notSelected-leave")
            state = "notSelected-play" if self.isPlaying else "notSelected-notPlay"
            self.setCheckBoxBtLabelState(state)

        self.setStyle(QApplication.style())

    def setPlay(self, isPlay: bool):
        """ 设置播放状态并更新样式 """
        self.isPlaying = isPlay
        self.isSelected = isPlay

        # 判断歌曲文件是否存在
        if self.__songCardType != SongCardType.ONLINE_SONG_CARD:
            self.isSongExist = os.path.exists(self.songPath)
        else:
            self.isSongExist = True

        if isPlay:
            self.isSelected = True
            self.setCheckBoxBtLabelState("selected")
            self.setWidgetState("selected-leave")
        else:
            self.setCheckBoxBtLabelState("notSelected-notPlay")
            self.setWidgetState("notSelected-leave")

        self.songNameCard.setPlay(isPlay, self.isSongExist)
        self.setStyle(QApplication.style())

    def setCheckBoxBtLabelState(self, state: str):
        """ 设置复选框、按钮和标签动态属性

        Parameters
        ----------
        state: str
            复选框、按钮和标签的状态，可以是:
            * `notSelected-notPlay`
            * `notSelected-play`
            * `selected`
        """
        self.songNameCard.setCheckBoxBtLabelState(state, self.isSongExist)
        for label in self.__dynamicStyleLabels:
            label.setProperty("state", state)

    def setWidgetState(self, state: str):
        """ 设置按钮组窗口和自己的状态

        Parameters
        ----------
        state: str
            窗口状态，可以是:
            * `notSelected-leave`
            * `notSelected-enter`
            * `notSelected-pressed`
            * `selected-leave`
            * `selected-enter`
            * `selected-pressed`
        """
        self.songNameCard.setButtonGroupState(state)
        self.setProperty("state", state)

    def setAnimation(self, widgets: list, deltaXs: list):
        """ 设置小部件的动画

        Parameters
        ----------
        widgets: list
            需要设置动画的小部件列表

        deltaXs: list
            和 `widgets` 相对应的动画位置偏移量列表
        """
        self.__checkIsLengthEqual(widgets, deltaXs)
        self.__aniWidgets = widgets
        self.__deltaXs = deltaXs

        # 清空动画组的内容
        self.__anis.clear()
        self.__aniGroup.clear()
        self.__anis = [QPropertyAnimation(w, b"pos") for w in self.__aniWidgets]

        # 初始化动画
        for ani in self.__anis:
            ani.setDuration(400)
            ani.setEasingCurve(QEasingCurve.OutQuad)
            self.__aniGroup.addAnimation(ani)

        self._getAniTargetX()

    def _getAniTargetX(self):
        """ 计算动画的初始值 """
        self.__aniTargetXs = []
        for deltaX, widget in zip(self.__deltaXs, self.__aniWidgets):
            self.__aniTargetXs.append(deltaX + widget.x())

    def eventFilter(self, obj, e: QEvent):
        """ 安装监听 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.songNameCard.checkBox.show()
                self.songNameCard.buttonGroup.setHidden(self.isInSelectionMode)
                state = "selected-enter" if self.isSelected else "notSelected-enter"
                self.setWidgetState(state)
                self.setStyle(QApplication.style())

            elif e.type() == QEvent.Leave:
                # 不处于选择模式下时，如果歌曲卡没被选中而鼠标离开窗口就隐藏复选框和按钮组窗口
                if not self.isSelected:
                    self.songNameCard.buttonGroup.hide()
                    self.songNameCard.checkBox.setHidden(
                        not self.isInSelectionMode)

                state = "selected-leave" if self.isSelected else "notSelected-leave"
                self.setWidgetState(state)
                self.setStyle(QApplication.style())

            elif e.type() == QEvent.MouseButtonPress:
                state = "selected-pressed" if self.isSelected else "notSelected-pressed"
                if e.button() == Qt.LeftButton:
                    self.isSelected = True
                self.setWidgetState(state)
                self.setStyle(QApplication.style())

            elif e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.setWidgetState("selected-leave")
                self.setCheckBoxBtLabelState("selected")  # 鼠标松开时将设置标签为白色
                self.setStyle(QApplication.style())

            elif e.type() == QEvent.MouseButtonDblClick:
                self.isDoubleClicked = True

        return super().eventFilter(obj, e)

    def mousePressEvent(self, e):
        """ 鼠标按下时移动小部件 """
        super().mousePressEvent(e)
        # 移动小部件
        if self.__aniGroup.state() == QAbstractAnimation.Stopped:
            for dx, w in zip(self.__deltaXs, self.__aniWidgets):
                w.move(w.x() + dx, w.y())
        else:
            self.__aniGroup.stop()  # 强制停止还未结束的动画
            for x, w in zip(self.__aniTargetXs, self.__aniWidgets):
                w.move(x, w.y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        """ 鼠标松开时开始动画 """
        for ani, w, dx in zip(self.__anis, self.__aniWidgets, self.__deltaXs):
            ani.setStartValue(w.pos())
            ani.setEndValue(QPoint(w.x() - dx, w.y()))

        self.__aniGroup.start()

        if e.button() == Qt.LeftButton:
            self.clicked.emit(self.itemIndex)

        # 左键点击时才发送信号
        if self.isDoubleClicked and e.button() == Qt.LeftButton:
            self.isDoubleClicked = False
            if not self.isPlaying:
                # 发送点击信号
                self.__aniGroup.finished.connect(self.__aniFinishedSlot)

    def __aniFinishedSlot(self):
        """ 动画完成时发出双击信号 """
        self.doubleClicked.emit(self.itemIndex)
        self.__aniGroup.disconnect()

    def setClickableLabelCursor(self, cursor):
        """ 设置可点击标签的光标样式 """
        for label in self.__clickableLabels:
            label.setCursor(cursor)

    def __referenceWidgets(self):
        """ 引用小部件 """
        self.buttonGroup = self.songNameCard.buttonGroup
        self.playButton = self.songNameCard.playButton
        self.addToButton = self.songNameCard.addToButton
        self.checkBox = self.songNameCard.checkBox

    def onPlayButtonClicked(self):
        """ 播放按钮按下时更新样式 """
        self.playButtonClicked.emit(self.itemIndex)

    def _onCheckedStateChanged(self):
        """ 复选框选中状态改变对应的槽函数 """
        self.isChecked = self.checkBox.isChecked()
        self.setSelected(self.isChecked)

        # 只要点击了复选框就进入选择模式，由父级控制退出选择模式
        self.checkBox.show()
        self.setSelectionModeOpen(True)

        # 发出选中状态改变信号
        self.checkedStateChanged.emit(self.itemIndex, self.isChecked)

    def setSelectionModeOpen(self, isOpen: bool):
        """ 设置是否进入选择模式, 处于选择模式下复选框一直可见，按钮不管是否处于选择模式都不可见 """
        if self.isInSelectionMode == isOpen:
            return

        self.isInSelectionMode = isOpen

        # 设置按钮和复选框的可见性
        self.checkBox.setHidden(not isOpen)
        self.buttonGroup.setHidden(True)

    def setChecked(self, isChecked: bool):
        """ 设置歌曲卡选中状态 """
        if self.isChecked == isChecked:
            return

        self.checkBox.setChecked(isChecked)

    def updateSongCard(self, songInfo: SongInfo):
        """ 更新歌曲卡 """
        raise NotImplementedError

    def __checkIsLengthEqual(self, list_1: list, list_2: list):
        """ 检查输入的两个列表的长度是否相等，不相等则引发错误 """
        if len(list_1) != len(list_2):
            raise Exception("两个列表的长度必须一样")

    def resizeEvent(self, e):
        """ 改变窗口大小时移动标签 """
        self.__resizeTime += 1
        if self.__resizeTime > 1:
            # 分配多出来的宽度
            deltaWidth = self.width() - self.__originalWidth
            self.__originalWidth = self.width()
            equalWidth = int(deltaWidth / len(self.__scaleableWidgets))
            self.__scaleableWidgetMaxWidths = [
                i + equalWidth for i in self.__scaleableWidgetMaxWidths]
        else:
            self.__originalWidth = self.width()

        # 调整小部件宽度
        self._adjustWidgetWidth()

        # 移动标签
        x = self.songNameCard.width()
        for label, spacing in zip(self.__labels, self.__labelSpacings):
            # 如果标签是可变长度的，就将width设置为其最大可变宽度
            if label in self.__scaleableWidgets:
                index = self.__scaleableWidgets.index(label)
                width = self.__scaleableWidgetMaxWidths[index]
            else:
                width = label.width()
            label.move(x + spacing, 20)
            x = width + label.x()

        # 更新动画目标移动位置
        self._getAniTargetX()

    def _adjustWidgetWidth(self):
        """ 调整小部件宽度 """
        self.__getScaleableLabelTextWidth()
        self.songNameCard.resize(self.__scaleableWidgetMaxWidths[0], 60)
        for i in range(1, len(self.__scaleableWidgets)):
            label = self.__scaleableWidgets[i]
            w = self.__scaleableLabelTextWidths[i - 1]
            mw = self.__scaleableWidgetMaxWidths[i]
            label.setFixedWidth(min(mw, w))

    def __getScaleableLabelTextWidth(self):
        """ 计算可拉伸的标签的文本宽度 """
        fontMetrics = QFontMetrics(QFont("Microsoft YaHei", 9))
        self.__scaleableLabelTextWidths = [
            fontMetrics.width(label.text()) for label in self.__scaleableWidgets[1:]]

    def _showAddToMenu(self):
        """ 显示添加到菜单 """
        menu = AddToMenu(parent=self)
        pos = self.mapToGlobal(
            QPoint(self.addToButton.x()+self.buttonGroup.x(), 0))
        x = pos.x() + self.addToButton.width() + 5
        y = pos.y() + int(
            self.addToButton.height() / 2 - (13 + 38 * menu.actionCount()) / 2)

        menu.playingAct.triggered.connect(
            lambda: signalBus.addSongsToPlayingPlaylistSig.emit([self.songInfo]))
        menu.newPlaylistAct.triggered.connect(
            lambda: signalBus.addSongsToNewCustomPlaylistSig.emit([self.songInfo]))
        menu.addSongsToPlaylistSig.connect(
            lambda name: signalBus.addSongsToCustomPlaylistSig.emit(name, [self.songInfo]))
        menu.exec(QPoint(x, y))

    @property
    def widgets(self) -> list:
        """ 返回窗口内的所有小部件"""
        return self.__widgets

    @property
    def labels(self) -> list:
        """ 返回窗口内所有标签 """
        return self.__labels
