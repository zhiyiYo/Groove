# coding:utf-8
from common.database.entity import SongInfo
from common.os_utils import getCoverPath
from common.signal_bus import signalBus
from components.widgets.label import ClickableLabel, AlbumCover
from PyQt5.QtCore import QEvent, QFile, Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget


class SongInfoCard(QWidget):
    """ Song information card """

    showPlayBarSignal = pyqtSignal()
    hidePlayBarSignal = pyqtSignal()

    def __init__(self, songInfo=SongInfo(), parent=None):
        super().__init__(parent)
        self.setSongInfo(songInfo)
        self.timer = QTimer(self)
        self.albumCoverLabel = AlbumCover(self.coverPath, (136, 136), self)
        self.songNameLabel = ClickableLabel(parent=self)
        self.singerAlbumLabel = ClickableLabel(parent=self)
        self.isPlayBarVisible = False
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.resize(1307, 136)
        self.setFixedHeight(136)
        self.setMinimumWidth(400)
        self.albumCoverLabel.move(30, 0)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.updateCard(self.songInfo)

        # initialize timer
        self.timer.setInterval(3000)
        self.timer.timeout.connect(self.timerSlot)
        self.__setQss()

        self.songNameLabel.installEventFilter(self)
        self.singerAlbumLabel.installEventFilter(self)

        # connect signal to slot
        self.songNameLabel.clicked.connect(
            lambda: signalBus.switchToAlbumInterfaceSig.emit(self.singer, self.album))
        self.singerAlbumLabel.clicked.connect(
            lambda: signalBus.switchToAlbumInterfaceSig.emit(self.singer, self.album))

    def setSongInfo(self, songInfo: SongInfo):
        """ set song information """
        self.songInfo = songInfo
        self.songName = songInfo.title or ''
        self.singer = songInfo.singer or ''
        self.album = songInfo.album or ''
        self.coverPath = getCoverPath(self.singer, self.album, 'album_big')

    def updateCard(self, songInfo: SongInfo):
        """ update song information card """
        self.setSongInfo(songInfo)
        self.songNameLabel.setText(self.songName)
        self.singerAlbumLabel.setText(self.singer + " • " + self.album)
        self.albumCoverLabel.setCover(self.coverPath)
        self.adjustText()

    def resizeEvent(self, e):
        self.adjustText()

    def __setQss(self):
        """ set style sheet """
        self.songNameLabel.setObjectName("songNameLabel")
        self.singerAlbumLabel.setObjectName("singerAlbumLabel")
        self.songNameLabel.setProperty("state", "normal")
        self.singerAlbumLabel.setProperty("state", "normal")

        f = QFile(":/qss/playing_interface_song_info_card.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

    def eventFilter(self, obj, e: QEvent):
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
        if self.isPlayBarVisible:
            return

        if not self.timer.isActive():
            self.timer.start()
            self.showPlayBarSignal.emit()
        else:
            self.timer.stop()
            self.timer.start()

    def timerSlot(self):
        """ timer time out slot """
        self.timer.stop()
        self.hidePlayBarSignal.emit()

    def adjustText(self):
        """ adjust the text of labels """
        maxWidth = self.width() - 232

        # set width of album name
        fontMetrics = self.singerAlbumLabel.fontMetrics()
        w = fontMetrics.width(self.singerAlbumLabel.text())
        self.singerAlbumLabel.setFixedWidth(min(maxWidth, w))

        # adjust album name
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
