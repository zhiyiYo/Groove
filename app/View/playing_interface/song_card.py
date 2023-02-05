# coding:utf-8
from common.config import Theme
from common.icon import Icon
from common.database.entity import SongInfo
from common.signal_bus import signalBus
from common.style_sheet import setStyleSheet
from components.widgets.menu import AddToMenu
from components.widgets.label import ClickableLabel, PixmapLabel
from PyQt5.QtCore import (QAbstractAnimation, QEasingCurve, QEvent,
                          QParallelAnimationGroup, QPoint, QPropertyAnimation,
                          QSize, Qt, pyqtSignal)
from PyQt5.QtGui import QFont, QFontMetrics, QMouseEvent, QPixmap
from PyQt5.QtWidgets import (QApplication, QCheckBox, QLabel, QToolButton,
                             QWidget)


class SongCard(QWidget):
    """ Song card """

    clicked = pyqtSignal(int)                      # 歌曲卡点击
    aniStartSig = pyqtSignal()                     # 反弹动画开始
    checkedStateChanged = pyqtSignal(int, bool)    # 歌曲卡选中状态改变

    def __init__(self, songInfo: SongInfo, parent=None):
        super().__init__(parent=parent)
        self.__getInfo(songInfo)
        self.__resizeTime = 0
        self.isPlaying = False
        self.isChecked = False
        self.isInSelectionMode = False

        # the maximum width occupied by each widget
        self.__maxSongNameCardWidth = 420
        self.__maxSingerWidth = 284
        self.__maxAlbumWidth = 284

        # the index of the corresponding item
        self.itemIndex = None

        # create widgets
        self.songNameCard = SongNameCard(self.songName, self)
        self.singerLabel = ClickableLabel(self.singer, self, False)
        self.albumLabel = ClickableLabel(self.album, self, False)
        self.yearLabel = QLabel(self.year, self)
        self.durationLabel = QLabel(self.duration, self)
        self.songNameLabel = self.songNameCard.songNameLabel
        self.buttonGroup = self.songNameCard.buttonGroup
        self.playButton = self.songNameCard.playButton
        self.addToButton = self.songNameCard.addToButton
        self.checkBox = self.songNameCard.checkBox
        self.labels = [
            self.songNameLabel, self.singerLabel,
            self.albumLabel, self.yearLabel, self.durationLabel
        ]
        self.__createAnimations()
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.__getLabelWidth()
        self.resize(1234, 60)
        self.resize(1234, 60)
        self.setFixedHeight(60)
        self.albumLabel.setCursor(Qt.PointingHandCursor)
        self.singerLabel.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_StyledBackground)

        # set properties and ID
        self.setObjectName("songCard")
        self.songNameLabel.setObjectName('songNameLabel')
        self.albumLabel.setObjectName("clickableLabel")
        self.singerLabel.setObjectName("clickableLabel")
        self.setState(False, False, False, False)

        self.installEventFilter(self)
        self.__connectSignalToSlot()

    def setState(self, isPlay: bool, isEnter: bool, isChecked: bool, isPressed: bool):
        """ set the state of song card

        Parameters
        ----------
        isPlay: bool
            whether the song card is in playing state

        isEnter: bool
            whether the mouse enters the song card

        isChecked: bool
            whether the song card is checked, used in selection mode

        isPressed: bool
            whether the song card is pressed
        """
        playState = 'play' if isPlay else 'notPlay'
        enterState = 'enter' if isEnter else 'leave'
        checkedState = 'checked' if isChecked else 'notChecked'
        bgState = f'{checkedState}-{enterState}' if not isPressed else f'{checkedState}-pressed'
        labelState = f'notChecked-{playState}-{enterState}' if not isChecked else 'checked'
        checkBoxState = f'notChecked-{playState}' if not isChecked else 'checked'
        self.setProperty('state', bgState)
        self.buttonGroup.setProperty('state', bgState)
        self.checkBox.setProperty('state', checkBoxState)
        self.songNameCard.playingLabel.setProperty('state', checkedState)

        for label in self.labels:
            label.setProperty('state', labelState)

        self.setStyle(QApplication.style())

    def __getInfo(self, songInfo: SongInfo):
        """ set song information """
        self.songInfo = songInfo
        self.songName = songInfo.title
        self.singer = songInfo.singer
        self.album = songInfo.album
        self.year = str(songInfo.year or '')
        self.duration = f"{int(songInfo.duration//60)}:{int(songInfo.duration%60):02}"

    def __createAnimations(self):
        """ create animations """
        self.aniGroup = QParallelAnimationGroup(self)
        self.__deltaXs = [13, 5, -3, -11, -13]
        self.__aniWidgets = [
            self.songNameCard, self.singerLabel, self.albumLabel,
            self.yearLabel, self.durationLabel,
        ]
        self.__anis = [
            QPropertyAnimation(w, b"pos") for w in self.__aniWidgets]

        for ani in self.__anis:
            ani.setDuration(400)
            ani.setEasingCurve(QEasingCurve.OutQuad)
            self.aniGroup.addAnimation(ani)

        self.__getAniTargetXs()

    def __getAniTargetXs(self):
        """ get the initial x-axis value of animations """
        self.__aniTargetXs = []
        for deltaX, widget in zip(self.__deltaXs, self.__aniWidgets):
            self.__aniTargetXs.append(deltaX + widget.x())

    def eventFilter(self, obj, e: QEvent):
        if obj is self:
            if e.type() == QEvent.Enter:
                self.checkBox.show()
                self.buttonGroup.setVisible(not self.isInSelectionMode)
                self.setState(self.isPlaying, True, self.isChecked, False)
            elif e.type() == QEvent.Leave:
                self.checkBox.setVisible(self.isInSelectionMode)
                self.buttonGroup.hide()
                self.setState(self.isPlaying, False, self.isChecked, False)
            elif e.type() == QEvent.MouseButtonPress:
                self.setState(self.isPlaying, False, self.isChecked, True)
            elif e.type() == QEvent.MouseButtonRelease:
                self.setState(True, False, self.isChecked, False)

        return super().eventFilter(obj, e)

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        if self.aniGroup.state() == QAbstractAnimation.Stopped:
            for dx, w in zip(self.__deltaXs, self.__aniWidgets):
                w.move(w.x() + dx, w.y())
        else:
            self.aniGroup.stop()
            for x, w in zip(self.__aniTargetXs, self.__aniWidgets):
                w.move(x, w.y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        for ani, w, dx in zip(self.__anis, self.__aniWidgets, self.__deltaXs):
            ani.setStartValue(w.pos())
            ani.setEndValue(QPoint(w.x() - dx, w.y()))

        self.checkBox.setVisible(self.isInSelectionMode)

        if e.button() == Qt.LeftButton:
            if not self.isInSelectionMode:
                self.aniGroup.finished.connect(self.__onAniFinished)
                # send signal to SonglistWidget requests to cancel the current song card playback status
                self.aniStartSig.emit()
                self.setPlay(True)
            else:
                self.setChecked(not self.isChecked)

        self.aniGroup.start()

    def __onAniFinished(self):
        """ animation finished slot """
        if not self.isInSelectionMode:
            self.clicked.emit(self.itemIndex)

        self.aniGroup.disconnect()

    def resizeEvent(self, e):
        self.__resizeTime += 1

        if self.__resizeTime == 1:
            self.originalWidth = self.width()
            width = self.width() - 246

            # get the maximun width occupied by each widget
            self.__maxSongNameCardWidth = int(42 / 99 * width)
            self.__maxSingerWidth = int(
                (width - self.__maxSongNameCardWidth) / 2)
            self.__maxAlbumWidth = self.__maxSingerWidth

            self.__adjustWidgetWidth()

        elif self.__resizeTime > 1:
            deltaWidth = self.width() - self.originalWidth
            self.originalWidth = self.width()

            # distribute width
            threeEqualWidth = int(deltaWidth / 3)
            self.__maxSongNameCardWidth += threeEqualWidth
            self.__maxSingerWidth += threeEqualWidth
            self.__maxAlbumWidth += deltaWidth - 2 * threeEqualWidth
            self.__adjustWidgetWidth()

        # move labels
        self.durationLabel.move(self.width() - 45, 20)
        self.yearLabel.move(self.width() - 190, 20)
        self.singerLabel.move(self.__maxSongNameCardWidth + 26, 20)
        self.albumLabel.move(self.singerLabel.x() +
                             self.__maxSingerWidth + 15, 20)

        self.__getAniTargetXs()

    def __adjustWidgetWidth(self):
        """ adjust the width of widgets """
        self.songNameCard.resize(self.__maxSongNameCardWidth, 60)
        self.singerLabel.setFixedWidth(
            min(self.singerWidth, self.__maxSingerWidth))
        self.albumLabel.setFixedWidth(
            min(self.albumWidth, self.__maxAlbumWidth))

    def __getLabelWidth(self):
        """ get the text width of labels """
        font = QFont("Microsoft YaHei")
        font.setPixelSize(15)
        fontMetrics = QFontMetrics(font)
        self.singerWidth = fontMetrics.width(self.singer)
        self.albumWidth = fontMetrics.width(self.album)

    def updateSongCard(self, songInfo: SongInfo):
        """ update song card """
        self.resize(self.size())
        self.__getInfo(songInfo)

        self.songNameCard.setSongName(self.songName)
        self.singerLabel.setText(self.singer)
        self.albumLabel.setText(self.album)
        self.yearLabel.setText(self.year)
        self.durationLabel.setText(self.duration)

        self.__getLabelWidth()
        self.__adjustWidgetWidth()

    def setPlay(self, isPlay: bool):
        """ set the play state """
        if self.isPlaying == isPlay:
            return

        self.isPlaying = isPlay
        self.songNameCard.setPlay(isPlay)
        self.setState(isPlay, False, self.isChecked, False)

    def setChecked(self, isChecked: bool):
        """ set the checked state """
        self.checkBox.setChecked(isChecked)

    def onCheckedStateChanged(self):
        """ checked state changed slot """
        self.isChecked = self.checkBox.isChecked()
        self.setState(self.isPlaying, False, self.isChecked, False)

        # enter selection mode
        self.checkBox.show()
        self.setSelectionModeOpen(True)
        self.checkedStateChanged.emit(self.itemIndex, self.isChecked)

    def setSelectionModeOpen(self, isOpen: bool):
        """ set whether to open selection mode """
        if self.isInSelectionMode == isOpen:
            return

        self.isInSelectionMode = isOpen
        self.checkBox.setVisible(isOpen)
        self.buttonGroup.setHidden(True)

    def __showAddToMenu(self):
        """ show add to menu """
        menu = AddToMenu(parent=self, theme=Theme.DARK)
        menu.setObjectName('darkMenu')
        setStyleSheet(menu, 'menu', Theme.DARK)
        menu.newPlaylistAct.triggered.connect(
            lambda: signalBus.addSongsToNewCustomPlaylistSig.emit([self.songInfo]))
        menu.addSongsToPlaylistSig.connect(
            lambda name: signalBus.addSongsToCustomPlaylistSig.emit(name, [self.songInfo]))
        menu.exec_(menu.getPopupPos(self.addToButton))

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.playButton.clicked.connect(
            lambda: self.clicked.emit(self.itemIndex))
        self.singerLabel.clicked.connect(
            lambda: signalBus.switchToSingerInterfaceSig.emit(self.singer))
        self.albumLabel.clicked.connect(
            lambda: signalBus.switchToAlbumInterfaceSig.emit(self.singer, self.album))
        self.checkBox.stateChanged.connect(self.onCheckedStateChanged)
        self.addToButton.clicked.connect(self.__showAddToMenu)


class ToolButton(QToolButton):
    """ Tool button """

    def __init__(self, iconPaths: dict, parent=None):
        super().__init__(parent)
        self.iconPaths = iconPaths
        self.isPlaying = False
        self.setFixedSize(60, 60)
        self.setIconSize(QSize(60, 60))
        self.setIcon(Icon(self.iconPaths[self.isPlaying]))
        self.setStyleSheet("QToolButton{border:none;margin:0}")

    def setPlay(self, isPlay: bool):
        """ set play state """
        self.isPlaying = isPlay
        self.setIcon(Icon(self.iconPaths[self.isPlaying]))


class ButtonGroup(QWidget):
    """ Button group """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.playButton = ToolButton(
            [
                ":/images/playing_interface/Play_60_60.png",
                ":/images/playing_interface/Play_green_60_60.png",
            ],
            self,
        )
        self.addToButton = ToolButton(
            [
                ":/images/playing_interface/Add.png",
                ":/images/playing_interface/Add_green.png",
            ],
            self,
        )
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedSize(140, 60)

        self.addToButton.move(80, 0)
        self.playButton.move(20, 0)

    def setPlay(self, isPlay: bool):
        """ set play state """
        self.playButton.setPlay(isPlay)
        self.addToButton.setPlay(isPlay)


class SongNameCard(QWidget):
    """ Song name card """

    def __init__(self, songName: str, parent=None):
        super().__init__(parent)
        self.songName = songName
        self.checkBox = QCheckBox(self)
        self.playingLabel = PixmapLabel(self)
        self.songNameLabel = QLabel(songName, self)
        self.buttonGroup = ButtonGroup(self)
        self.playButton = self.buttonGroup.playButton
        self.addToButton = self.buttonGroup.addToButton
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setFixedHeight(60)
        self.resize(390, 60)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.playingLabel.setPixmap(
            QPixmap(":/images/playing_interface/Playing_green.png"))
        self.playingLabel.setObjectName('playingLabel')

        self.checkBox.hide()
        self.buttonGroup.hide()
        self.playingLabel.hide()

        self.__getSongNameWidth()
        self.__initLayout()

    def __initLayout(self):
        """ initialize layout """
        self.checkBox.move(8, 17)
        self.playingLabel.move(43, 22)
        self.songNameLabel.move(41, 20)
        self.__moveButtonGroup()

    def __getSongNameWidth(self):
        """ get song name width """
        font = QFont("Microsoft YaHei")
        font.setPixelSize(15)
        fontMetrics = QFontMetrics(font)
        self.songNameWidth = fontMetrics.width(self.songName)

    def setPlay(self, isPlay: bool):
        """ set play state """
        self.buttonGroup.setPlay(isPlay)
        self.playingLabel.setHidden(not isPlay)
        self.songNameLabel.move(68 if isPlay else 41, self.songNameLabel.y())
        self.__moveButtonGroup()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.__moveButtonGroup()

    def __moveButtonGroup(self):
        """ move button group """
        if self.songNameWidth+self.songNameLabel.x() >= self.width()-140:
            x = self.width() - 140
        else:
            x = self.songNameWidth + self.songNameLabel.x()

        self.buttonGroup.move(x, 0)

    def setSongName(self, songName: str):
        """ set song name """
        self.songName = songName
        self.songNameLabel.setText(songName)
        self.__getSongNameWidth()
        self.__moveButtonGroup()
        self.songNameLabel.setFixedWidth(self.songNameWidth)
