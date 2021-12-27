# coding:utf-8
import re

from common.os_utils import getCoverPath
from components.widgets.perspective_widget import PerspectiveWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QFontMetrics, QPainter, QPixmap
from PyQt5.QtWidgets import QLabel, QWidget


class SongInfoCard(PerspectiveWidget):
    """ 播放栏左侧歌曲信息卡 """

    clicked = pyqtSignal()
    albumChanged = pyqtSignal(str)
    MAXWIDTH = 405

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(parent, True)
        self.__setSongInfo(songInfo)
        self.coverPath = ""

        # 创建小部件
        self.albumPic = QLabel(self)
        self.windowMask = WindowMask(self, (0, 0, 0, 25))
        self.textWindow = ScrollTextWindow(songInfo, self)

        # 初始化界面
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(115 + 15 + self.textWindow.width() + 25, 115)
        self.setAttribute(Qt.WA_StyledBackground | Qt.WA_TranslucentBackground)
        self.textWindow.move(130, 0)
        self.albumPic.resize(115, 115)

        self.__setAlbumCover()

        if not self.songInfo:
            self.hide()

    def __setSongInfo(self, songInfo: dict):
        """ 设置歌曲信息 """
        self.songInfo = songInfo
        self.songName = self.songInfo.get("songName", "")
        self.singer = self.songInfo.get("singer", "")

    def updateWindow(self, songInfo: dict):
        """ 更新歌曲信息卡 """
        self.setVisible(bool(songInfo))
        if not songInfo:
            return

        self.show()
        self.__setSongInfo(songInfo)
        self.textWindow.updateWindow(songInfo)
        self.setFixedWidth(115 + 15 + self.textWindow.width() + 25)
        self.__setAlbumCover()

    def enterEvent(self, e):
        """ 鼠标进入时显示遮罩并打开定时器 """
        super().enterEvent(e)
        self.windowMask.show()

    def leaveEvent(self, e):
        self.windowMask.hide()

    def mouseReleaseEvent(self, e):
        """ 鼠标松开发送信号 """
        super().mouseReleaseEvent(e)
        self.clicked.emit()

    def adjustSize(self):
        self.textWindow.adjustSize()
        self.setFixedWidth(115 + 15 + self.textWindow.width() + 25)

    def __setAlbumCover(self):
        """ 设置封面 """
        # 如果专辑信息为空就直接隐藏
        if not self.songInfo.get("album"):
            self.hide()
            return

        name = self.songInfo.get('coverName', '未知歌手_未知专辑')
        newCoverPath = getCoverPath(name, "album_big")

        # 封面路径变化时发送信号并更新封面
        if newCoverPath != self.coverPath:
            self.albumChanged.emit(newCoverPath)
            self.coverPath = newCoverPath
            self.albumPic.setPixmap(QPixmap(newCoverPath).scaled(
                115, 115, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))


class ScrollTextWindow(QWidget):
    """ 滚动字幕 """

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(parent)
        self.maxWidth = 250
        self.setMaximumWidth(250)
        self.pattern = re.compile(
            r"""^[a-zA-Z0-9\\/:<>\?\.\*;,&#@\$~`!-'"\^\+\(\)]+$""")

        # 刷新时间和移动距离
        self.timeStep = 19
        self.moveStep = 1

        # 两段字符串之间留白的宽度
        self.spacing = 25

        # 实定时器
        self.songPauseTimer = QTimer(self)
        self.songNameTimer = QTimer(self)
        self.singerNameTimer = QTimer(self)
        self.singerPauseTimer = QTimer(self)

        # 初始化界面
        self.__initWidget()
        self.updateWindow(songInfo)

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedHeight(115)
        self.setAttribute(Qt.WA_StyledBackground)

        # 初始化定时器
        self.songPauseTimer.setInterval(400)
        self.singerPauseTimer.setInterval(400)
        self.songNameTimer.setInterval(self.timeStep)
        self.singerNameTimer.setInterval(self.timeStep)
        self.songNameTimer.timeout.connect(self.__updateSongIndex)
        self.singerNameTimer.timeout.connect(self.__updateSingerIndex)
        self.songPauseTimer.timeout.connect(self.__restartTextTimer)
        self.singerPauseTimer.timeout.connect(self.__restartTextTimer)

    def __setSongInfo(self, songInfo: dict):
        """ 更新歌曲信息 """
        self.songInfo = songInfo
        self.songName = self.songInfo.get("songName", "")
        self.singer = self.songInfo.get("singer", "")

    def __resetFlags(self):
        """ 重置标志位 """
        self.songCurrentIndex = 0
        self.singerCurrentIndex = 0
        self.isSongNameAllOut = False
        self.isSingerAllOut = False

    def __adjustWidth(self, maxWidth=None):
        """ 根据字符串长度调整窗口宽度 """
        maxWidth = maxWidth or self.maxWidth
        fonts = ["Segoe UI", "Microsoft YaHei"]

        # 歌曲名字宽度
        font = fonts[self.pattern.match(self.songName) is None]
        self.songFont = QFont(font, 14)
        fontMetrics = QFontMetrics(self.songFont)
        self.songNameWidth = fontMetrics.width(self.songName)

        # 歌手宽度
        font = fonts[self.pattern.match(self.singer) is None]
        self.singerFont = QFont(font, 12, 75)
        self.singerFont.setPixelSize(19)
        fontMetrics = QFontMetrics(self.singerFont)
        self.singerWidth = fontMetrics.width(self.singer)

        # 是否有字符串超过窗口的最大宽度
        self.isSongTooLong = self.songNameWidth > maxWidth
        self.isSingerTooLong = self.singerWidth > maxWidth

        # 设置窗口的宽度
        w = max(self.songNameWidth, self.singerWidth)
        self.setFixedWidth(min(w, maxWidth))

    def updateWindow(self, songInfo: dict):
        """ 更新界面 """
        self.__resetFlags()
        self.__setSongInfo(songInfo)
        self.__adjustWidth()
        self.update()

    def __updateSongIndex(self):
        """ 更新歌名下标 """
        self.update()
        self.songCurrentIndex += 1

        if self.songCurrentIndex*self.moveStep >= self.songNameWidth + self.spacing*self.isSongNameAllOut:
            self.songCurrentIndex = 0
            self.isSongNameAllOut = True

    def __updateSingerIndex(self):
        """ 更新歌手名下标 """
        self.update()
        self.singerCurrentIndex += 1

        if self.singerCurrentIndex*self.moveStep >= self.singerWidth + self.spacing*self.isSingerAllOut:
            self.singerCurrentIndex = 0
            self.isSingerAllOut = True

    def setMaxWidth(self, width: int):
        """ 设置宽度最大值 """
        self.maxWidth = width
        self.__resetFlags()
        self.__adjustWidth()

    def initFlagsWidth(self):
        """ 初始化各标志位并调整窗口宽度 """

        if self.isSongTooLong:
            self.songNameTimer.start()
        if self.isSingerTooLong:
            self.singerNameTimer.start()

    def adjustSize(self):
        self.__adjustWidth(float('inf'))

    def paintEvent(self, e):
        """ 绘制文本 """
        painter = QPainter(self)
        painter.setPen(Qt.white)

        # 绘制歌名
        painter.setFont(self.songFont)
        if self.isSongTooLong:
            # 实际上绘制了两段完整的字符串
            # 从负的横坐标开始绘制第一段字符串
            x1 = (
                self.spacing * self.isSongNameAllOut
                - self.moveStep * self.songCurrentIndex
            )
            painter.drawText(x1, 54, self.songName)
            # 绘制第二段字符串
            x2 = (
                self.songNameWidth
                - self.moveStep * self.songCurrentIndex
                + self.spacing * (1 + self.isSongNameAllOut)
            )
            painter.drawText(x2, 54, self.songName)
            # 循环一次后就将滚动停止
            if self.isSongNameAllOut and not (x1 and x2):
                # 判断鼠标是否离开,离开的话就停止滚动
                if not self.isNotLeave():
                    self.songNameTimer.stop()
                else:
                    self.songNameTimer.stop()
                    self.songPauseTimer.start()
        else:
            painter.drawText(0, 54, self.songName)

        # 绘制歌手名
        painter.setFont(self.singerFont)
        if self.isSingerTooLong:
            x3 = (
                self.spacing * self.isSingerAllOut
                - self.moveStep * self.singerCurrentIndex
            )
            x4 = (
                self.singerWidth
                - self.moveStep * self.singerCurrentIndex
                + self.spacing * (1 + self.isSingerAllOut)
            )
            painter.drawText(x3, 82, self.singer)
            painter.drawText(x4, 82, self.singer)
            if self.isSingerAllOut and not (x3 and x4):
                if not self.isNotLeave():
                    self.singerNameTimer.stop()
                else:
                    self.singerNameTimer.stop()
                    self.singerPauseTimer.start()
        else:
            painter.drawText(0, 82, self.singer)

    def enterEvent(self, e):
        """ 鼠标进入时打开滚动效果 """
        if self.isSongTooLong and not self.songNameTimer.isActive():
            self.songNameTimer.start()
        if self.isSingerTooLong and not self.singerNameTimer.isActive():
            self.singerNameTimer.start()

    def __restartTextTimer(self):
        """ 重新打开指定的定时器 """
        self.sender().stop()
        if self.sender() == self.songPauseTimer:
            self.songNameTimer.start()
        else:
            self.singerNameTimer.start()

    def isNotLeave(self) -> bool:
        """ 判断leaveEvent是否发生在小部件所占据的区域 """
        if not self.isWindow():
            globalPos = self.parent().mapToGlobal(self.pos())
        else:
            globalPos = self.pos()

        globalX = globalPos.x()
        globalY = globalPos.y()

        x = globalX <= self.cursor().pos().x() <= globalX + self.width()
        y = globalY <= self.cursor().pos().y() <= globalY + self.height()
        return (x and y)


class WindowMask(QWidget):
    """ 歌曲卡的半透明遮罩 """

    def __init__(self, parent, maskColor: tuple = (255, 255, 255, 172)):
        super().__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground)
        # 设置背景色
        r, g, b, a = maskColor
        self.setStyleSheet(f'background:rgba({r},{g},{b},{a});')
        self.hide()

    def show(self):
        """ 获取父窗口的位置后显示 """
        parent_rect = self.parent().geometry()
        self.setGeometry(0, 0, parent_rect.width(), parent_rect.height())
        self.raise_()
        super().show()
