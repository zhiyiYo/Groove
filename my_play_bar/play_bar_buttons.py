import sys

from PyQt5.QtCore import QEvent, QSize, Qt
from PyQt5.QtGui import QBrush, QColor, QEnterEvent, QIcon, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QApplication, QToolButton, QWidget, QSlider


class PlayButton(QToolButton):
    """ 控制播放和暂停的按钮 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置标志位
        self.isPlaying = False
        self.isEnter = False
        self.isPressed = True
        # 设置图标
        self.setFixedSize(65, 65)
        self.setStyleSheet(
            "QToolButton{border:none;margin:0;background:transparent}")
        self.installEventFilter(self)

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
        painter.setRenderHint(QPainter.Antialiasing, True)
        # 设置描边画笔
        #pen = QPen(QColor(153, 157, 169, 150))
        pen = QPen(QColor(153, 157, 169, 120))
        pen.setWidth(2)
        # 设置画笔
        painter.setPen(pen)
        painter.drawEllipse(1, 1, 62, 62)
        # 绘制背景
        if not self.isPressed and self.isEnter:
            painter.setPen(QPen(QColor(101, 106, 116, 180)))
            bgBrush = QBrush(QColor(73, 76, 84, 80))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 62, 62)
        # 设置背景图
        painter.setPen(Qt.NoPen)
        if not self.isPlaying:
            self.image = QPixmap(r'resource\images\playBar\播放_63_63.png')
        else:
            self.image = QPixmap(r'resource\images\playBar\暂停_63_63.png')
        brush = QBrush(self.image)
        painter.setBrush(brush)
        # 绘制背景图
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
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)
        if self.isSelected:
            bgBrush = QBrush(QColor(73, 76, 84, 180))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
        else:
            if self.isPressed:
                painter.setPen(QPen(QColor(101, 106, 116, 80)))
                bgBrush = QBrush(QColor(73, 76, 84, 110))
                painter.setBrush(bgBrush)
                painter.drawEllipse(1, 1, 44, 44)
            elif self.isEnter:
                # 设置画笔
                painter.setPen(QPen(QColor(101, 106, 116, 180)))
                bgBrush = QBrush(QColor(73, 76, 84, 80))
                painter.setBrush(bgBrush)
                painter.drawEllipse(1, 1, 44, 44)
        # 绘制背景图
        painter.setPen(Qt.NoPen)
        self.image = QPixmap(r'resource\images\playBar\随机播放_45_45.png')
        brush = QBrush(self.image)
        painter.setBrush(brush)
        painter.drawEllipse(1, 1, 45, 45)

class BasicButton(QToolButton):
    """ 基本圆形按钮 """

    def __init__(self, icon_path, parent=None):
        super().__init__(parent)
        # 设置标志位
        self.isEnter = False
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

    def paintEvent(self, e):
        """ 绘制背景 """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        # 设置画笔
        painter.setPen(Qt.NoPen)
        if self.isEnter:
            painter.setPen(QPen(QColor(101, 106, 116, 180)))
            bgBrush = QBrush(QColor(73, 76, 84, 80))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
        painter.setPen(Qt.NoPen)
        self.image = QPixmap(self.icon_path)
        brush = QBrush(self.image)
        painter.setBrush(brush)
        # 绘制背景图
        painter.drawEllipse(1, 1, 45, 45)


class LastSongButton(BasicButton):
    """ 播放上一首按钮 """

    def __init__(self, parent=None):
        self.icon_path = r'resource\images\playBar\上一首_45_45.png'
        super().__init__(self.icon_path,parent)


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
        # 设置点击次数以及对应的图标
        self.clickedTime = 0
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
            brush = QBrush(QColor(73, 76, 84, 180))
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
        # 当前音量等级及其各个图标地址
        self.currentVolumeLevel = 0
        self.__iconPath_list = [r'resource\images\playBar\音量按钮_无_45_45.png',
                                r'resource\images\playBar\音量按钮_低_45_45.png',
                                r'resource\images\playBar\音量按钮_中_45_45.png',
                                r'resource\images\playBar\音量按钮_高_45_45.png']
        self.setFixedSize(47, 47)
        self.installEventFilter(self)

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
        painter.setRenderHint(QPainter.Antialiasing, True)
        # 设置画笔
        painter.setPen(Qt.NoPen)
        if self.isSelected:
            bgBrush = QBrush(QColor(73, 76, 84, 180))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
        elif self.isEnter:
            # 设置画笔
            painter.setPen(QPen(QColor(101, 106, 116, 180)))
            bgBrush = QBrush(QColor(73, 76, 84, 80))
            painter.setBrush(bgBrush)
            painter.drawEllipse(1, 1, 44, 44)
        # 绘制背景图
        painter.setPen(Qt.NoPen)
        self.image = QPixmap(self.__iconPath_list[self.currentVolumeLevel])
        brush = QBrush(self.image)
        painter.setBrush(brush)
        painter.drawEllipse(1, 1, 45, 45)


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


class Demo(QWidget):
    """ 测试 """

    def __init__(self):
        super().__init__()
        self.resize(400, 200)
        self.setObjectName('demo')
        self.setAttribute(Qt.WA_StyledBackground)
        self.playButton = MoreActionsButton(self)
        self.playButton.move(170, 20)
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.move(50, 100)
        self.slider.setObjectName('slider')
        self.setQss()

    def setQss(self):
        with open(r'resource\css\playBar.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
