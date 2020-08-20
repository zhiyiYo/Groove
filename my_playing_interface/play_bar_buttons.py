import sys

from PyQt5.QtCore import Qt, QEvent, QTimer,pyqtSignal
from PyQt5.QtGui import QPainter, QPixmap, QBrush, QColor, QPen
from PyQt5.QtWidgets import QApplication, QToolButton, QWidget
from PyQt5.QtMultimedia import QMediaPlaylist


class BasicCircleButton(QToolButton):
    """ 圆形按钮 """

    def __init__(self, iconPath, parent=None, iconSize: tuple = (47, 47), buttonSize: tuple = (47, 47)):
        super().__init__(parent)
        self.iconWidth, self.iconHeight = iconSize
        self.buttonSize_tuple = buttonSize
        self.iconPath = iconPath
        self.iconPixmap = QPixmap(iconPath)
        # 标志位
        self.isEnter = False
        self.isPressed = False
        # 控制绘图位置
        self._pixPos_list = [(1, 0), (2, 2)]
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(self.buttonSize_tuple[0], self.buttonSize_tuple[1])
        self.setStyleSheet(
            "QToolButton{border:none;margin:0;background:transparent}")
        # 安装事件过滤器
        self.installEventFilter(self)

    def eventFilter(self, obj, e: QEvent):
        """ 根据鼠标动作更新标志位和图标 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.isEnter = True
                self.update()
                return False
            elif e.type() == QEvent.Leave:
                self.isEnter = False
                self.update()
                return False
            elif e.type() in [QEvent.MouseButtonPress, QEvent.MouseButtonDblClick, QEvent.MouseButtonRelease]:
                self.isPressed = not self.isPressed
                self.update()
                return False
        return super().eventFilter(obj, e)
        
    def paintEvent(self, e):
        """ 绘制图标 """
        iconPixmap = self.iconPixmap
        px, py = self._pixPos_list[0]
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        # 鼠标按下时绘制圆形背景，pressed的优先级比hover的优先级高
        if self.isPressed:
            #brush = QBrush(QColor(162, 162, 162, 120))
            brush = QBrush(QColor(255, 255, 255, 70))
            painter.setBrush(brush)
            painter.drawEllipse(0, 0, self.iconWidth, self.iconHeight)
            iconPixmap = self.iconPixmap.scaled(
                self.iconPixmap.width() - 4, self.iconPixmap.height() - 4, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            px, py = self._pixPos_list[1]
        # 鼠标进入时更换图标透明度
        elif self.isEnter:
            painter.setOpacity(0.5)
        # 绘制图标
        painter.drawPixmap(px, py, iconPixmap.width(),
                           iconPixmap.height(), iconPixmap)


class SelectableButton(BasicCircleButton):
    """ 可选中的按钮 """

    def __init__(self, iconPath_list: list, parent=None, iconSize=(47, 47), buttonSize=(47, 47)):
        super().__init__(iconPath_list[0], parent, iconSize, buttonSize)
        self.iconPath_list = iconPath_list
        # 设置选中标志位
        self.isSelected = False
        # 设置可选中的次数
        self.selectableTime = len(self.iconPath_list)
        self.clickedTime = 0

    def mouseReleaseEvent(self, e):
        """ 鼠标松开时更新点击次数和图标 """
        if not self.clickedTime:
            self.isSelected = True
        self.clickedTime += 1
        if self.clickedTime == self.selectableTime + 1:
            self.isSelected = False
            self.clickedTime = 0
            # 更新图标
            self.iconPixmap = QPixmap(self.iconPath_list[0])
        else:
            self.iconPixmap = QPixmap(self.iconPath_list[self.clickedTime-1])
        self.update()
        super().mouseReleaseEvent(e)

    def paintEvent(self, e):
        """ 绘制背景 """
        iconPixmap = self.iconPixmap
        px, py = self._pixPos_list[0]
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        if self.isPressed:
            if not self.isSelected:
                brush = QBrush(QColor(162, 162, 162, 120))
                pen = Qt.NoPen
            else:
                brush = QBrush(QColor(110, 110, 110, 100))
                pen = QPen(QColor(255, 255, 255, 160))
                pen.setWidthF(1.5)
            # 绘制圆环和背景色
            self.__drawCircle(painter, pen, brush)
            # 更新图标大小和位置
            iconPixmap = self.iconPixmap.scaled(
                self.iconPixmap.width() - 4, self.iconPixmap.height() - 4, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            px, py = self._pixPos_list[1]
        else:
            if self.isSelected:
                pen = QPen(QColor(255, 255, 255, 100))
                pen.setWidthF(1.4)
                self.__drawCircle(painter, pen, QBrush(QColor(0, 0, 0, 60)))
            # 鼠标进入时更换图标透明度
            elif self.isEnter:
                painter.setOpacity(0.5)
        # 绘制图标
        painter.drawPixmap(px, py, iconPixmap.width(),
                           iconPixmap.height(), iconPixmap)

    def __drawCircle(self, painter, pen, brush):
        """ 画圆 """
        painter.setPen(Qt.NoPen)
        painter.setBrush(brush)
        painter.drawEllipse(1, 1, self.iconWidth-2, self.iconHeight-2)
        painter.setPen(pen)
        painter.drawEllipse(1, 1, self.iconWidth - 2, self.iconHeight - 2)
        

class RandomPlayButton(SelectableButton):
    """ 随机播放按钮 """

    def __init__(self, iconPath_list: list, parent=None, iconSize=(47, 47), buttonSize=(47, 47)):
        super().__init__(iconPath_list, parent, iconSize, buttonSize)
        
    def setRandomPlay(self, isRandomPlay: bool):
        """ 设置随机播放状态 """
        self.isSelected = isRandomPlay
        self.clickedTime = int(isRandomPlay)
        self.update()


class LoopModeButton(SelectableButton):
    """ 循环模式按钮 """
    loopModeChanged = pyqtSignal(int)

    def __init__(self, iconPath_list: list, parent=None, iconSize=(47, 47), buttonSize=(47, 47)):
        super().__init__(iconPath_list, parent, iconSize, buttonSize)
        self.loopMode = QMediaPlaylist.Sequential
        self.__loopMode_list = [QMediaPlaylist.Sequential,
                                QMediaPlaylist.Loop, QMediaPlaylist.CurrentItemInLoop]

    def mouseReleaseEvent(self,e):
        """ 更新循环模式 """
        super().mouseReleaseEvent(e)
        self.loopMode = self.__loopMode_list[self.clickedTime]
        self.loopModeChanged.emit(self.loopMode)
        
    def setLoopMode(self, loopMode):
        """ 设置循环模式 """
        self.loopMode = loopMode
        if self.loopMode in [QMediaPlaylist.Loop, QMediaPlaylist.CurrentItemInLoop]:
            self.isSelected = True
        else:
            self.isSelected = False
        self.clickedTime = self.__loopMode_list.index(loopMode)
        if self.clickedTime == 2:
            self.iconPixmap = QPixmap(self.iconPath_list[1])
        else:
            self.iconPixmap = QPixmap(self.iconPath_list[0])
        self.update()


class PullUpArrow(BasicCircleButton):
    """ 上拉正在播放列表箭头 """

    def __init__(self, iconPath, parent=None, iconSize=(27, 27), buttonSize=(27, 27)):
        super().__init__(iconPath, parent, iconSize, buttonSize)
        # 箭头旋转方向，顺时针旋转为1，逆时针旋转为-1
        self.rotateDirection = 1
        self.deltaAngleStep = 9
        self.totalRotateAngle = 0
        # 实例化定时器
        self.timer = QTimer(self)
        self.timer.setInterval(24)
        self.timer.timeout.connect(self.timerSlot)

    def setArrowDirection(self, direction: str = 'up'):
        """ 设置箭头方向，up朝上，down朝下 """
        self.rotateDirection = 1 if direction.upper() == 'UP' else - 1
        self.totalRotateAngle = 0 if direction.upper() == 'UP' else 180
        self.update()

    def timerSlot(self):
        """ 定时器溢出时旋转箭头 """
        self.totalRotateAngle = self.rotateDirection * \
            self.deltaAngleStep + self.totalRotateAngle
        self.update()
        if self.totalRotateAngle in [180, 0]:
            self.timer.stop()
            self.rotateDirection = -self.rotateDirection

    def mouseReleaseEvent(self, e):
        """ 鼠标松开时打开计时器 """
        self.timer.start()
        super().mouseReleaseEvent(e)

    def paintEvent(self, e):
        """ 绘制图标 """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        # 鼠标按下时绘制圆形背景，pressed的优先级比hover的优先级高
        if self.isPressed and self.rotateDirection == 1:
            brush = QBrush(QColor(0, 0, 0, 50))
            painter.setBrush(brush)
            painter.drawEllipse(0, 0, self.iconWidth, self.iconHeight)
        # 鼠标进入时更换图标透明度
        elif self.isEnter:
            painter.setOpacity(0.5)
        # 绘制图标
        painter.translate(13, 13)
        painter.rotate(self.totalRotateAngle)  # 坐标系旋转
        painter.drawPixmap(-int(self.iconWidth / 2),
                           - int(self.iconHeight / 2), self.iconPixmap)


class TwoStateButton(BasicCircleButton):
    """ 两种状态的按钮 """

    def __init__(self, iconPath_list, parent=None, isState_1=True):
        self.iconPath_list = iconPath_list
        super().__init__(self.iconPath_list[isState_1], parent)
        # 设置状态1标志位，状态1的图标为图标列表的第二个
        self._isState_1 = isState_1
        # 创建pixmap列表
        self.pixmap_list = [QPixmap(iconPath)
                            for iconPath in self.iconPath_list]
        self._pixPos_list = [(0, 0), (2, 2)]

    def mouseReleaseEvent(self, e):
        """ 鼠标松开时更换图标 """
        self.setState(not self._isState_1)
        super().mouseReleaseEvent(e)

    def setState(self, isState_1: bool):
        """ 设置按钮状态 """
        self._isState_1 = isState_1
        self.iconPixmap = self.pixmap_list[self._isState_1]
        self.update()


class PlayButton(TwoStateButton):
    """ 播放按钮 """

    def __init__(self, parent=None):
        self.iconPath_list = [
            r'resource\images\playing_interface\play_47_47.png',
            r'resource\images\playing_interface\pause_47_47.png']
        super().__init__(self.iconPath_list, parent)
        # 设置暂停标志位
        self.__isPaused = True

    def setPlay(self, isPlay: bool):
        """ 设置按钮状态 """
        self.__isPaused = not isPlay
        self.setState(self.__isPaused)
        self.update()

class FillScreenButton(TwoStateButton):
    """ 转到全屏按钮 """

    def __init__(self, parent=None):
        self.iconPath_list = [
            r'resource\images\playing_interface\转到全屏_47_47.png',
            r'resource\images\playing_interface\退出全屏_47_47.png']
        super().__init__(self.iconPath_list, parent, False)
        # 设置暂停标志位
        self.__isFillScreen = False

    def setFillScreen(self, isFillScreen: bool):
        """ 设置按钮状态 """
        self.__isFillScreen = isFillScreen
        self.setState(self.__isFillScreen)


class VolumeButton(BasicCircleButton):
    """ 音量按钮 """

    def __init__(self, parent=None):
        # 按钮图标地址列表
        self.__iconPath_list = [
            r'resource\images\playing_interface\volume_white_level_0_47_47.png',
            r'resource\images\playing_interface\volume_white_level_1_47_47.png',
            r'resource\images\playing_interface\volume_white_level_2_47_47.png',
            r'resource\images\playing_interface\volume_white_level_3_47_47.png',
            r'resource\images\playing_interface\volume_white_level_mute_47_47.png']
        self.pixmap_list = [QPixmap(i) for i in self.__iconPath_list]
        super().__init__(self.__iconPath_list[0], parent)
        # 初始化标志位
        self.isMute = False
        self.__volumeLevel = 0

    def setMute(self, isMute):
        """ 设置静音 """
        self.isMute = isMute
        if isMute:
            self.iconPixmap = self.pixmap_list[-1]
        else:
            self.iconPixmap = self.pixmap_list[self.__volumeLevel]
        self.update()

    def setVolumeLevel(self, volume):
        """ 根据音量来设置 """
        if volume == 0:
            self.updateIcon(0)
        elif 0 < volume <= 32 and self.__volumeLevel != 1:
            self.updateIcon(1)
        elif 32 < volume <= 65 and self.__volumeLevel != 2:
            self.updateIcon(2)
        elif volume > 65 and self.__volumeLevel != 3:
            self.updateIcon(3)

    def updateIcon(self, iconIndex):
        """ 更新图标 """
        self.__volumeLevel = iconIndex
        # 静音时不更新图标
        if not self.isMute:
            self.iconPixmap = self.pixmap_list[iconIndex]
            self.update()


class Demo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(100, 100)
        self.lastSongButton = FillScreenButton(self)
        self.setStyleSheet('QWidget{background:rgb(88,150,140)}')
        self.lastSongButton.move(27, 27)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
