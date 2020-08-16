import sys

from PyQt5.QtCore import Qt, QEvent, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap,QFont,QFontMetrics
from PyQt5.QtWidgets import QApplication, QWidget, QLabel

from my_functions.get_album_cover_path import getAlbumCoverPath
from my_widget.my_label import ClickableLabel


class SongInfoCard(QWidget):
    """ 歌曲信息卡 """
    showPlayBarSignal = pyqtSignal()
    hidePlayBarSignal = pyqtSignal()
    switchToAlbumInterfaceSig = pyqtSignal(str,str)

    def __init__(self, parent=None, songInfo: dict = None):
        super().__init__(parent)
        self.setSongInfo(songInfo)
        self.timer = QTimer(self)
        self.albumCoverLabel = QLabel(self)
        self.songNameLabel = ClickableLabel(parent=self)
        self.songerAlbumLabel = ClickableLabel(parent=self)
        # 初始化标志位
        self.isPlayBarVisible = False
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1307,136)
        self.setFixedHeight(136)
        self.setMinimumWidth(400)
        self.albumCoverLabel.move(30, 0)
        self.albumCoverLabel.setFixedSize(136, 136)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.updateCard(self.songInfo)
        # 初始化定时器
        self.timer.setInterval(3000)
        self.timer.timeout.connect(self.timerSlot)
        # 分配ID
        self.songNameLabel.setObjectName('songNameLabel')
        self.songerAlbumLabel.setObjectName('songerAlbumLabel')
        # 设置属性
        self.songNameLabel.setProperty('state', 'normal')
        self.songerAlbumLabel.setProperty('state', 'normal')
        #self.__initLayout()
        self.__setQss()
        # 安装事件过滤器
        self.songNameLabel.installEventFilter(self)
        self.songerAlbumLabel.installEventFilter(self)
        # 信号连接到槽
        slot = lambda: self.switchToAlbumInterfaceSig.emit(self.album[0],self.songerName)
        self.songNameLabel.clicked.connect(slot)
        self.songerAlbumLabel.clicked.connect(slot)

    def __initLayout(self):
        """ 初始化布局 """
        self.songNameLabel.move(186, 30)
        self.songerAlbumLabel.move(186, 82)

    def setSongInfo(self, songInfo: dict):
        """ 设置歌曲信息 """
        self.songInfo = songInfo
        if not self.songInfo:
            self.songInfo = {}
        self.album = self.songInfo.get('album', ['未知专辑'])
        self.songName = self.songInfo.get('songName', '未知歌名')
        self.songerName = self.songInfo.get('songer', '未知歌手')
        self.albumCoverPath = getAlbumCoverPath(self.album[-1])

    def updateCard(self, songInfo: dict):
        """ 更新歌曲信息卡 """
        self.setSongInfo(songInfo)
        self.songNameLabel.setText(self.songName)
        self.songerAlbumLabel.setText(self.songerName + ' • ' + self.album[0])
        self.albumCoverLabel.setPixmap(QPixmap(self.albumCoverPath).scaled(
            136, 136, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        # 调整文本
        self.adjustText()

    def __setQss(self):
        """ 设置层叠样式 """
        with open(r'resource\css\playInterfaceSongInfoCard.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def eventFilter(self, obj, e: QEvent):
        """ 重写事件过滤器 """
        if obj in [self.songNameLabel, self.songerAlbumLabel]:
            if e.type() == QEvent.MouseButtonPress:
                self.songNameLabel.setProperty('state', 'pressed')
                self.songerAlbumLabel.setProperty('state', 'pressed')
                self.setStyle(QApplication.style())
            elif e.type() == QEvent.Enter:
                self.songNameLabel.setProperty('state', 'hover')
                self.songerAlbumLabel.setProperty('state', 'hover')
                self.setStyle(QApplication.style())
            elif e.type() in [QEvent.MouseButtonRelease,QEvent.Leave]:
                self.songNameLabel.setProperty('state', 'normal')
                self.songerAlbumLabel.setProperty('state', 'normal')
                self.setStyle(QApplication.style())
        return super().eventFilter(obj, e)

    def enterEvent(self, e):
        """ 鼠标进入时打开计时器并显示播放栏 """
        if not self.isPlayBarVisible:
            if not self.timer.isActive():
                # 显示播放栏
                self.timer.start()
                self.showPlayBarSignal.emit()
            else:
                # 重置定时器
                self.timer.stop()
                self.timer.start()

    def timerSlot(self):
        """ 定时器溢出时隐藏播放栏 """
        self.timer.stop()
        self.hidePlayBarSignal.emit()

    def adjustText(self):
        """ 根据文本长度决定是否插入换行符 """
        maxWidth = self.width() - 232
        # 设置专辑名歌手名标签的长度
        fontMetrics = QFontMetrics(QFont('Microsoft YaHei', 13))
        songerAlbumWidth = sum([fontMetrics.width(i) for i in self.songerAlbumLabel.text()])
        self.songerAlbumLabel.setFixedWidth(min(maxWidth, songerAlbumWidth))
        # 调整专辑名标签
        fontMetrics = QFontMetrics(QFont('Microsoft YaHei', 21, 75))
        newSongName_list = list(self.songName) #type:list
        totalWidth = 0
        isWrap = False
        for i in range(len(self.songName)):
            totalWidth += fontMetrics.width(self.songName[i])
            if totalWidth > maxWidth:
                newSongName_list.insert(i, '\n')
                isWrap = True
                break
        if isWrap:
            self.songNameLabel.setText(''.join(newSongName_list))
            self.songNameLabel.move(186, 6)
            self.songerAlbumLabel.move(186, 101)
            self.songNameLabel.setFixedSize(maxWidth,83)
        else:
            self.songNameLabel.move(186, 26)
            self.songerAlbumLabel.move(186, 82)
            self.songNameLabel.setFixedSize(totalWidth, 46)
            self.songNameLabel.setText(self.songName)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    songInfo = {'songName': 'be Your XXX',
                'songer': '鎖那',
                'album': ['(un)sentimental spica']}
    demo = SongInfoCard(songInfo=songInfo)
    demo.show()
    sys.exit(app.exec_())
