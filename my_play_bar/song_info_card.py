import sys

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QFontMetrics, QPainter, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QWidget


class SongInfoCard(QWidget):
    """ 播放栏左侧歌曲信息卡 """

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(parent)
        # 保存信息
        self.setSongInfo(songInfo)
        # 实例化小部件
        self.albumPic = QLabel(self)
        self.scrollTextWindow = ScrollTextWindow(songInfo, self)
        # 初始化界面
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        self.setFixedHeight(115)
        self.setFixedWidth(115 + 15 + self.scrollTextWindow.width() + 25)
        self.setAttribute(Qt.WA_StyledBackground|Qt.WA_TranslucentBackground)
        self.scrollTextWindow.move(130, 0)
        self.albumPic.setPixmap(QPixmap(self.songInfo['album'][-1]).scaled(
                                115, 115, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def setSongInfo(self, songInfo: dict):
        """ 设置歌曲信息 """
        self.songInfo = songInfo
        self.songName = self.songInfo['songName']
        self.songerName = self.songInfo['songer']

    def updateSongInfoCard(self, songInfo: dict):
        """ 更新歌曲信息卡 """
        self.setSongInfo(songInfo)
        self.scrollTextWindow.initUI(songInfo)
        self.setFixedWidth(115 + 15 + self.scrollTextWindow.width() + 25)
        self.albumPic.setPixmap(QPixmap(self.songInfo['album'][-1]).scaled(
                                115, 115, Qt.KeepAspectRatio, Qt.SmoothTransformation))

class ScrollTextWindow(QWidget):
    """ 滚动字幕 """

    def __init__(self, songInfo:dict, parent=None):
        super().__init__(parent)
        # 实例化定时器
        self.timer = QTimer(self)
        # 初始化界面
        self.initUI(songInfo)

    def setSongInfo(self, songInfo: dict):
        """ 更新歌曲信息 """
        self.songInfo = songInfo
        self.songName = self.songInfo['songName']
        self.songerName = self.songInfo['songer']

    def initUI(self, songInfo: dict):
        """ 重置所有属性 """
        # 设置刷新时间和移动距离
        self.timeStep = 20
        self.moveStep = 1
        self.songCurrentIndex = 0
        self.songerCurrentIndex = 0
        # 设置字符串溢出标志位
        self.isSongNameAllOut = False
        self.isSongerNameAllOut = False
        # 设置两段字符串之间留白的宽度
        self.spacing = 25
        # 初始化界面
        self.setSongInfo(songInfo)
        self.initWidget()

    def initWidget(self):
        """ 初始化界面 """
        self.setFixedHeight(115)
        self.setAttribute(Qt.WA_StyledBackground)
        # 调整窗口宽度
        self.adjustWindowWidth()
        # 初始化定时器
        self.timer.setInterval(self.timeStep)
        self.timer.timeout.connect(self.updateIndex)
        # 只要有一个字符串宽度大于窗口宽度就开启滚动：
        if self.timer.isActive():
            self.timer.stop()
        if self.isSongerNameTooLong or self.isSongNameTooLong:
            self.timer.start()

    def getTextWidth(self):
        """ 计算文本的总宽度 """
        songFontMetrics = QFontMetrics(QFont('Microsoft YaHei', 14, 400))
        self.songNameWidth = sum([songFontMetrics.width(i)
                                  for i in self.songName])
        songerFontMetrics = QFontMetrics(QFont('Microsoft YaHei', 12, 500))
        self.songerNameWidth = sum(
            [songerFontMetrics.width(i) for i in self.songerName])

    def adjustWindowWidth(self):
        """ 根据字符串长度调整窗口宽度 """
        self.getTextWidth()
        maxWidth = max(self.songNameWidth, self.songerNameWidth)
        # 判断是否有字符串宽度超过窗口的最大宽度
        self.isSongNameTooLong = self.songNameWidth > 250
        self.isSongerNameTooLong = self.songerNameWidth > 250
        # 设置窗口的宽度
        self.setFixedWidth(min(maxWidth, 250))

    def updateIndex(self):
        """ 更新下标 """
        self.update()
        self.songCurrentIndex += 1
        self.songerCurrentIndex += 1
        # 设置下标重置条件
        resetSongIndexCond = self.songCurrentIndex * \
            self.moveStep >= self.songNameWidth + self.spacing * self.isSongNameAllOut
        resetSongerIndexCond = self.songerCurrentIndex * \
            self.moveStep >= self.songerNameWidth + self.spacing * self.isSongerNameAllOut
        # 只要条件满足就要重置下标并将字符串溢出置位，保证在字符串溢出后不会因为留出的空白而发生跳变
        if resetSongIndexCond:
            self.songCurrentIndex = 0
            self.isSongNameAllOut = True
        if resetSongerIndexCond:
            self.songerCurrentIndex = 0
            self.isSongerNameAllOut = True

    def paintEvent(self, e):
        """ 绘制文本 """
        # super().paintEvent(e)
        painter = QPainter(self)
        painter.setPen(Qt.white)
        # 绘制歌名
        painter.setFont(QFont('Microsoft YaHei', 14))
        if self.isSongNameTooLong:
            # 实际上绘制了两段完整的字符串
            # 从负的横坐标开始绘制第一段字符串
            painter.drawText(self.spacing * self.isSongNameAllOut - self.moveStep *
                             self.songCurrentIndex, 54, self.songName)
            # 绘制第二段字符串
            painter.drawText(self.songNameWidth - self.moveStep * self.songCurrentIndex +
                             self.spacing * (1 + self.isSongNameAllOut), 54, self.songName)
        else:
            painter.drawText(0, 54, self.songName)

        # 绘制歌手名  
        painter.setFont(QFont('Microsoft YaHei', 12, 500))
        if self.isSongerNameTooLong:
            painter.drawText(self.spacing * self.isSongerNameAllOut - self.moveStep *
                             self.songerCurrentIndex, 82, self.songerName)
            painter.drawText(self.songerNameWidth - self.moveStep * self.songerCurrentIndex +
                             self.spacing * (1 + self.isSongerNameAllOut), 82, self.songerName)
        else:
            painter.drawText(0, 82, self.songerName)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    songInfo = {
        'songName': 'ハッピーでバッドな眠りは浅い', 'songer': '鎖那',
        'album': [r'resource\Album Cover\ハッピーでバッドな眠りは浅い\ハッピーでバッドな眠りは浅い.png']}
    demo = SongInfoCard(songInfo)
    demo.setStyleSheet('background:rgb(129,133,137)')
    demo.show()
    sys.exit(app.exec_())
