# coding:utf-8
from common.database.entity import SongInfo
from common.os_utils import getCoverPath
from common.signal_bus import signalBus
from components.widgets.label import ClickableLabel
from PyQt5.QtCore import QEvent, QFile, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QWidget


class SongInfoCard(QWidget):
    """ 歌曲信息卡 """

    showPlayBarSignal = pyqtSignal()
    hidePlayBarSignal = pyqtSignal()

    def __init__(self, songInfo=SongInfo(), parent=None):
        super().__init__(parent)
        self.setSongInfo(songInfo)
        self.timer = QTimer(self)
        self.albumCoverLabel = QLabel(self)
        self.songNameLabel = ClickableLabel(parent=self)
        self.singerAlbumLabel = ClickableLabel(parent=self)
        self.isPlayBarVisible = False
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1307, 136)
        self.setFixedHeight(136)
        self.setMinimumWidth(400)
        self.albumCoverLabel.move(30, 0)
        self.albumCoverLabel.setFixedSize(136, 136)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.updateCard(self.songInfo)

        # 初始化定时器
        self.timer.setInterval(3000)
        self.timer.timeout.connect(self.timerSlot)
        self.__setQss()

        # 安装事件过滤器
        self.songNameLabel.installEventFilter(self)
        self.singerAlbumLabel.installEventFilter(self)

        # 信号连接到槽
        self.songNameLabel.clicked.connect(
            lambda: signalBus.switchToAlbumInterfaceSig.emit(self.singer, self.album))
        self.singerAlbumLabel.clicked.connect(
            lambda: signalBus.switchToAlbumInterfaceSig.emit(self.singer, self.album))

    def setSongInfo(self, songInfo: SongInfo):
        """ 设置歌曲信息 """
        self.songInfo = songInfo
        self.songName = songInfo.title or ''
        self.singer = songInfo.singer or ''
        self.album = songInfo.album or ''
        self.coverPath = getCoverPath(self.singer, self.album, 'album_big')

    def updateCard(self, songInfo: SongInfo):
        """ 更新歌曲信息卡 """
        self.setSongInfo(songInfo)
        self.songNameLabel.setText(self.songName)
        self.singerAlbumLabel.setText(self.singer + " • " + self.album)
        self.albumCoverLabel.setPixmap(QPixmap(self.coverPath).scaled(
            136, 136, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.adjustText()

    def resizeEvent(self, e):
        self.adjustText()

    def __setQss(self):
        """ 设置层叠样式 """
        self.songNameLabel.setObjectName("songNameLabel")
        self.singerAlbumLabel.setObjectName("singerAlbumLabel")
        self.songNameLabel.setProperty("state", "normal")
        self.singerAlbumLabel.setProperty("state", "normal")

        f = QFile(":/qss/playing_interface_song_info_card.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

    def eventFilter(self, obj, e: QEvent):
        """ 重写事件过滤器 """
        if obj in [self.songNameLabel, self.singerAlbumLabel]:
            if e.type() == QEvent.MouseButtonPress:
                self.songNameLabel.setProperty("state", "pressed")
                self.singerAlbumLabel.setProperty("state", "pressed")
                self.setStyle(QApplication.style())
            elif e.type() == QEvent.Enter:
                self.songNameLabel.setProperty("state", "hover")
                self.singerAlbumLabel.setProperty("state", "hover")
                self.setStyle(QApplication.style())
            elif e.type() in [QEvent.MouseButtonRelease, QEvent.Leave]:
                self.songNameLabel.setProperty("state", "normal")
                self.singerAlbumLabel.setProperty("state", "normal")
                self.setStyle(QApplication.style())

        return super().eventFilter(obj, e)

    def enterEvent(self, e):
        """ 鼠标进入时打开计时器并显示播放栏 """
        if self.isPlayBarVisible:
            return

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
        fontMetrics = self.singerAlbumLabel.fontMetrics()
        w = fontMetrics.width(self.singerAlbumLabel.text())
        self.singerAlbumLabel.setFixedWidth(min(maxWidth, w))

        # 调整专辑名标签
        fontMetrics = self.songNameLabel.fontMetrics()
        newSongName_list = list(self.songName)  # type:list
        totalWidth = 0
        isWrap = False
        for i in range(len(self.songName)):
            totalWidth += fontMetrics.width(self.songName[i])
            if totalWidth > maxWidth:
                newSongName_list.insert(i, "\n")
                isWrap = True
                break

        if isWrap:
            self.songNameLabel.setText("".join(newSongName_list))
            self.songNameLabel.move(186, 6)
            self.singerAlbumLabel.move(186, 101)
            self.songNameLabel.setFixedSize(maxWidth, 83)
        else:
            self.songNameLabel.move(186, 26)
            self.singerAlbumLabel.move(186, 82)
            self.songNameLabel.setFixedSize(totalWidth, 46)
            self.songNameLabel.setText(self.songName)
