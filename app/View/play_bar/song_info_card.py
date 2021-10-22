# coding:utf-8
import re

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QFontMetrics, QPainter, QPixmap
from PyQt5.QtWidgets import QLabel, QWidget

from common.os_utils import getCoverPath

from components.perspective_widget import PerspectiveWidget


class SongInfoCard(PerspectiveWidget):
    """ 播放栏左侧歌曲信息卡 """

    clicked = pyqtSignal()
    albumChanged = pyqtSignal(str)
    MAXWIDTH = 405

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(parent, True)
        # 保存信息
        self.__setSongInfo(songInfo)
        self.coverPath = ""
        # 实例化小部件
        self.albumPic = QLabel(self)
        self.windowMask = WindowMask(self, (0, 0, 0, 25))
        self.scrollTextWindow = ScrollTextWindow(songInfo, self)
        # 初始化界面
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        self.resize(115 + 15 + self.scrollTextWindow.width() + 25, 115)
        self.setAttribute(Qt.WA_StyledBackground | Qt.WA_TranslucentBackground)
        self.scrollTextWindow.move(130, 0)
        self.albumPic.resize(115, 115)
        # 获取封面路径
        self.setAlbumCover()
        # 如果传入的歌曲信息为空，就隐藏
        if not self.songInfo:
            self.hide()

    def __setSongInfo(self, songInfo: dict):
        """ 设置歌曲信息 """
        self.songInfo = songInfo
        self.songName = self.songInfo.get("songName", "")
        self.singerName = self.songInfo.get("singer", "")

    def updateSongInfoCard(self, songInfo: dict):
        """ 更新歌曲信息卡 """
        if songInfo:
            self.show()
            self.__setSongInfo(songInfo)
            self.scrollTextWindow.initUI(songInfo)
            self.setFixedWidth(115 + 15 + self.scrollTextWindow.width() + 25)
            self.setAlbumCover()
        else:
            self.hide()

    def enterEvent(self, e):
        """ 鼠标进入时显示遮罩 """
        if (
            self.scrollTextWindow.isSongNameTooLong
            and not self.scrollTextWindow.songNameTimer.isActive()
        ):
            self.scrollTextWindow.songNameTimer.start()
        if (
            self.scrollTextWindow.isSongerNameTooLong
            and not self.scrollTextWindow.singerNameTimer.isActive()
        ):
            self.scrollTextWindow.singerNameTimer.start()
        self.windowMask.show()

    def leaveEvent(self, e):
        self.windowMask.hide()

    def setAlbumCover(self):
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

    def mouseReleaseEvent(self, e):
        """ 鼠标松开发送信号 """
        super().mouseReleaseEvent(e)
        self.clicked.emit()


class ScrollTextWindow(QWidget):
    """ 滚动字幕 """

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(parent)
        # 设置默认最大宽度
        self.maxWidth = 250
        self.hasInitWidget = False
        # 设置刷新时间和移动距离
        self.timeStep = 19
        self.moveStep = 1
        # 设置两段字符串之间留白的宽度
        self.spacing = 25
        # 实例化定时器
        self.songPauseTimer = QTimer(self)
        self.songNameTimer = QTimer(self)
        self.singerNameTimer = QTimer(self)
        self.singerPauseTimer = QTimer(self)
        # 初始化界面
        self.initUI(songInfo)

    def __setSongInfo(self, songInfo: dict):
        """ 更新歌曲信息 """
        self.songInfo = songInfo
        self.songName = self.songInfo.get("songName", "")
        self.singerName = self.songInfo.get("singer", "")

    def initFlagsWidth(self):
        """ 初始化各标志位并调整窗口宽度 """
        self.__initFlags()
        # 调整宽度
        self.adjustWindowWidth()
        if self.isSongNameTooLong:
            self.songNameTimer.start()
        if self.isSongerNameTooLong:
            self.singerNameTimer.start()

    def __initFlags(self):
        """ 初始化标志位 """
        # 初始化下标
        self.songCurrentIndex = 0
        self.singerCurrentIndex = 0
        # 设置字符串溢出标志位
        self.isSongNameAllOut = False
        self.isSongerNameAllOut = False

    def initUI(self, songInfo: dict):
        """ 重置所有属性 """
        self.__initFlags()
        # 初始化界面
        self.__setSongInfo(songInfo)
        self.initWidget()
        self.update()

    def initWidget(self):
        """ 初始化界面 """
        self.adjustWindowWidth()
        if not self.hasInitWidget:
            self.setFixedHeight(115)
            self.setAttribute(Qt.WA_StyledBackground)
            # 初始化定时器
            self.songPauseTimer.setInterval(400)
            self.singerPauseTimer.setInterval(400)
            self.songNameTimer.setInterval(self.timeStep)
            self.singerNameTimer.setInterval(self.timeStep)
            self.songNameTimer.timeout.connect(self.updateSongIndex)
            self.singerNameTimer.timeout.connect(self.updateSongerIndex)
            self.songPauseTimer.timeout.connect(self.restartTextTimer)
            self.singerPauseTimer.timeout.connect(self.restartTextTimer)
            # 根据字符串宽度是否大于窗口宽度开启滚动：
            self.songNameTimer.stop()
            self.singerNameTimer.stop()
        if self.isSongNameTooLong:
            self.songNameTimer.start()
        if self.isSongerNameTooLong:
            self.singerNameTimer.start()
        self.hasInitWidget = True

    def getTextWidth(self):
        """ 计算文本的总宽度 """
        songFontMetrics = QFontMetrics(QFont("Microsoft YaHei", 14))
        self.songNameWidth = sum([songFontMetrics.width(i)
                                 for i in self.songName])
        # 检测歌手名是否全是英文
        self.isMatch = re.match(r"^[a-zA-Z]+$", self.singerName)
        if not self.isMatch:
            singerFontMetrics = QFontMetrics(QFont("Microsoft YaHei", 12, 75))
        else:
            singerFontMetrics = QFontMetrics(QFont("Microsoft YaHei", 11, 75))
        # 总是会少一个字符的长度
        self.singerNameWidth = sum(
            [singerFontMetrics.width(i) for i in self.singerName]
        )

    def adjustWindowWidth(self):
        """ 根据字符串长度调整窗口宽度 """
        self.getTextWidth()
        maxWidth = max(self.songNameWidth, self.singerNameWidth)
        # 判断是否有字符串宽度超过窗口的最大宽度
        self.isSongNameTooLong = self.songNameWidth > self.maxWidth
        self.isSongerNameTooLong = self.singerNameWidth > self.maxWidth
        # 设置窗口的宽度
        self.setFixedWidth(min(maxWidth, self.maxWidth))

    def updateSongIndex(self):
        """ 更新歌名下标 """
        self.update()
        self.songCurrentIndex += 1
        # 设置下标重置条件
        resetSongIndexCond = (
            self.songCurrentIndex * self.moveStep
            >= self.songNameWidth + self.spacing * self.isSongNameAllOut
        )
        # 只要条件满足就要重置下标并将字符串溢出置位，保证在字符串溢出后不会因为留出的空白而发生跳变
        if resetSongIndexCond:
            self.songCurrentIndex = 0
            self.isSongNameAllOut = True

    def updateSongerIndex(self):
        """ 更新歌手名下标 """
        self.update()
        self.singerCurrentIndex += 1
        resetSongerIndexCond = (
            self.singerCurrentIndex * self.moveStep
            >= self.singerNameWidth + self.spacing * self.isSongerNameAllOut
        )
        if resetSongerIndexCond:
            self.singerCurrentIndex = 0
            self.isSongerNameAllOut = True

    def paintEvent(self, e):
        """ 绘制文本 """
        painter = QPainter(self)
        painter.setPen(Qt.white)
        # 绘制歌名
        painter.setFont(QFont("Microsoft YaHei", 14))
        if self.isSongNameTooLong:
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
        if not self.isMatch:
            painter.setFont(QFont("Microsoft YaHei", 12, 75))
        else:
            painter.setFont(QFont("Microsoft YaHei", 11, 75))
        if self.isSongerNameTooLong:
            x3 = (
                self.spacing * self.isSongerNameAllOut
                - self.moveStep * self.singerCurrentIndex
            )
            x4 = (
                self.singerNameWidth
                - self.moveStep * self.singerCurrentIndex
                + self.spacing * (1 + self.isSongerNameAllOut)
            )
            painter.drawText(x3, 82, self.singerName)
            painter.drawText(x4, 82, self.singerName)
            if self.isSongerNameAllOut and not (x3 and x4):
                if not self.isNotLeave():
                    self.singerNameTimer.stop()
                else:
                    self.singerNameTimer.stop()
                    self.singerPauseTimer.start()
        else:
            painter.drawText(0, 82, self.singerName)

    def enterEvent(self, e):
        """ 鼠标进入时打开滚动效果 """
        if self.isSongNameTooLong and not self.songNameTimer.isActive():
            self.songNameTimer.start()
        if self.isSongerNameTooLong and not self.singerNameTimer.isActive():
            self.singerNameTimer.start()

    def restartTextTimer(self):
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
        # 判断事件发生的位置发生在自己所占的rect内
        condX = (globalX <= self.cursor().pos().x()
                 <= globalX + self.width())
        condY = (globalY <= self.cursor().pos().y()
                 <= globalY + self.height())
        return (condX and condY)


class WindowMask(QWidget):
    """ 歌曲卡的半透明遮罩 """

    def __init__(self, parent, maskColor: tuple = (255, 255, 255, 172)):
        super().__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground)
        # 设置背景色
        self.setStyleSheet(
            f'background:rgba({maskColor[0]},{maskColor[1]},{maskColor[2]},{maskColor[-1]});')
        self.hide()

    def show(self):
        """ 获取父窗口的位置后显示 """
        parent_rect = self.parent().geometry()
        self.setGeometry(0, 0, parent_rect.width(), parent_rect.height())
        self.raise_()
        super().show()
