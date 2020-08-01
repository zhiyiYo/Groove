import sys

from PyQt5.QtCore import (QAbstractAnimation, QEasingCurve, QEvent,
                          QParallelAnimationGroup, QPropertyAnimation, QRect,
                          Qt, pyqtSignal)
from PyQt5.QtGui import QFont, QFontMetrics, QMouseEvent
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

from .song_card_sub_unit import SongNameCard
from my_widget.my_label import ClickableLabel


class SongCard(QWidget):
    """ 歌曲卡 """
    clicked = pyqtSignal(int)

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(parent)
        self.songInfo = songInfo
        self.__resizeTime = 0
        # 记录播放状态
        self.isPlaying = False
        self.__currentState = 'leave-notPlay'
        # 记录下每个小部件所占的最大宽度
        self.__maxSongNameCardWidth = 0
        self.__maxSongerLabelWidth = 0
        self.__maxAlbumLabelWidth = 0
        # 记录songCard对应的item的下标
        self.itemIndex = None
        # 创建小部件
        self.songNameCard = SongNameCard(songInfo['songName'], self)
        self.songerLabel = ClickableLabel(songInfo['songer'], self)
        self.albumLabel = ClickableLabel(songInfo['album'][0], self)
        self.yearLabel = QLabel(songInfo['year'], self)
        self.durationLabel = QLabel(songInfo['duration'], self)
        self.buttonGroup = self.songNameCard.buttonGroup
        self.playButton = self.songNameCard.playButton
        self.addToButton = self.songNameCard.addToButton
        self.__label_list = [self.songerLabel, self.albumLabel,
                             self.yearLabel, self.durationLabel]
        # 创建动画
        self.__createAnimations()
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.__getLabelWidth()
        self.resize(1200, 60)
        self.setFixedHeight(60)
        self.albumLabel.setCursor(Qt.PointingHandCursor)
        self.songerLabel.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_StyledBackground)
        # 分配ID和属性
        self.setObjectName('songCard')
        self.albumLabel.setObjectName('clickableLabel')
        self.songerLabel.setObjectName('clickableLabel')
        self.setDynamicProperty(self.__currentState)
        self.__setQss()
        # 安装事件过滤器
        self.installEventFilter(self)

    def __setQss(self):
        """ 设置层叠样式 """
        with open(r'resource\css\playInterfaceSongCard.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __getLabelWidth(self):
        """ 计算标签的长度 """
        fontMetrics = QFontMetrics(QFont('Microsoft YaHei', 10))
        self.songerWidth = sum([fontMetrics.width(i)
                                for i in self.songInfo['songer']])
        self.albumWidth = sum([fontMetrics.width(i)
                               for i in self.songInfo['album']])

    def setDynamicProperty(self, state: str):
        """ 设置动态属性，总共4状态，分别为enter-notPlay、enter-play、leave-notPlay、leave-play """
        self.yearLabel.setProperty('state', state)
        self.albumLabel.setProperty('state', state)
        self.songerLabel.setProperty('state', state)
        self.durationLabel.setProperty('state', state)
        if state.endswith('play'):
            self.isPlaying = True
            self.songNameCard.setPlay(True)
        if state.startswith('enter'):
            self.setProperty('state', 'hover')
            self.songNameCard.buttonGroup.setProperty('state', 'hover')
        else:
            self.setProperty('state', 'leave')
            self.songNameCard.buttonGroup.setProperty('state', 'leave')
        self.setStyle(QApplication.style())

    def resizeEvent(self, e):
        """ 改变窗口大小时移动标签 """
        # super().resizeEvent(e)
        self.__resizeTime += 1
        if self.__resizeTime == 1:
            self.originalWidth = self.width()
            width = self.width() - 246
            # 计算各个标签所占的最大宽度
            self.__maxSongNameCardWidth = int(42 / 99 * width)
            self.__maxSongerLabelWidth = int(
                (width - self.__maxSongNameCardWidth) / 2)
            self.__maxAlbumLabelWidth = self.__maxSongerLabelWidth
            # 如果实际尺寸大于可分配尺寸，就调整大小
            self.__adjustWidgetWidth()
        elif self.__resizeTime > 1:
            deltaWidth = self.width() - self.originalWidth
            self.originalWidth = self.width()
            # 分配多出来的宽度
            threeEqualWidth = int(deltaWidth / 3)
            self.__maxSongNameCardWidth += threeEqualWidth
            self.__maxSongerLabelWidth += threeEqualWidth
            self.__maxAlbumLabelWidth += (deltaWidth-2*threeEqualWidth)
            self.__adjustWidgetWidth()
        # 移动标签
        self.durationLabel.move(self.width() - 45, 20)
        self.yearLabel.move(self.width() - 190, 20)
        self.songerLabel.move(self.__maxSongNameCardWidth + 26, 20)
        self.albumLabel.move(self.songerLabel.x() +
                             self.__maxSongerLabelWidth + 15, 20)
        # 更新动画目标移动位置
        self.__getAniTargetX_list()

    def eventFilter(self, obj, e: QEvent):
        """ 更新样式 """
        if obj == self:
            if e.type() in [QEvent.Enter, QEvent.MouseButtonRelease]:
                self.songNameCard.setWidgetHidden(False)
                state = 'enter-play' if self.isPlaying else 'enter-notPlay'
                self.setDynamicProperty(state)
            elif e.type() == QEvent.Leave:
                self.songNameCard.setWidgetHidden(True)
                state = 'leave-play' if self.isPlaying else 'leave-notPlay'
                self.setDynamicProperty(state)
            elif e.type() == QEvent.MouseButtonPress:
                self.setProperty('state', 'pressed')
                self.songNameCard.buttonGroup.setProperty('state', 'pressed')
                self.setStyle(QApplication.style())
        return super().eventFilter(obj, e)

    def mousePressEvent(self, e):
        """ 鼠标按下时移动小部件 """
        super().mousePressEvent(e)
        # 移动小部件
        if self.aniGroup.state() == QAbstractAnimation.Stopped:
            for deltaX, widget in zip(self.__deltaX_list, self.__aniWidget_list):
                widget.move(widget.x() + deltaX, widget.y())
        else:
            self.aniGroup.stop()
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
        # 左键点击时才更新样式
        if e.button() == Qt.LeftButton:
            if not self.isPlaying:
                # 发送点击信号
                self.clicked.emit(self.itemIndex)
                self.aniGroup.finished.connect(self.aniFinishedSlot)

    def aniFinishedSlot(self):
        """ 动画完成时更新样式 """
        self.setDynamicProperty('enter-play')
        self.songNameCard.checkBox.hide()
        # 动画完成后需要断开连接，为下一次样式更新做准备
        self.aniGroup.disconnect()

    def __adjustWidgetWidth(self):
        """ 调整小部件宽度 """
        # if self.songNameCard.songNameWidth + 41 > self.__maxSongNameCardWidth:
        self.songNameCard.resize(self.__maxSongNameCardWidth, 60)
        if self.songerWidth > self.__maxSongerLabelWidth:
            self.songerLabel.resize(self.__maxSongerLabelWidth, 20)
        if self.albumWidth > self.__maxAlbumLabelWidth:
            self.albumLabel.resize(self.__maxAlbumLabelWidth, 20)

    def __createAnimations(self):
        """ 创建动画 """
        self.aniGroup = QParallelAnimationGroup(self)
        self.__deltaX_list = [13, 5, -3, -11, -13]
        self.__aniWidget_list = [self.songNameCard, self.songerLabel,
                                 self.albumLabel, self.yearLabel, self.durationLabel]
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

    def setPlay(self, isPlay: bool):
        """ 设置歌曲卡的播放状态 """
        self.isPlaying = isPlay
        self.songNameCard.setPlay(isPlay)
        if isPlay:
            self.setDynamicProperty('enter-play')
        else:
            self.setDynamicProperty('leave-notPlay')

    def updateSongCard(self, songInfo):
        """ 更新歌曲卡信息 """
        self.songInfo = songInfo
        self.songNameCard.setSongName(songInfo['songName'])
        self.songerLabel.setText(songInfo['songer'])
        self.albumLabel.setText(songInfo['album'][0])
        self.yearLabel.setText(songInfo['year'])
        self.durationLabel.setText(songInfo['duration'])
        # 调整宽度
        self.__getLabelWidth()
        songerWidth = self.songerWidth if self.songerWidth <= self.__maxSongerLabelWidth else self.__maxSongNameCardWidth
        albumWidth = self.albumWidth if self.albumWidth <= self.__maxAlbumLabelWidth else self.__maxAlbumLabelWidth
        self.songerLabel.resize(songerWidth, 20)
        self.albumLabel.resize(albumWidth, 20)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    songInfo = {'songName': '歩いても歩いても、夜空は僕を追いかけてくる (步履不停，夜空追逐着我)',
                'songer': '鎖那',
                'album': ['(un)sentimental spica'],
                'year': '2015年',
                'duration': '4:33'}
    demo = SongCard(songInfo)
    demo.show()
    sys.exit(app.exec_())
