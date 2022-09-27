# coding:utf-8
import os
import sys

from common.database.entity import SongInfo
from common.signal_bus import signalBus
from components.widgets.menu import AddToMenu
from PyQt5.QtCore import (QAbstractAnimation, QEasingCurve, QEvent,
                          QParallelAnimationGroup, QPoint, QPropertyAnimation,
                          Qt, pyqtSignal)
from PyQt5.QtGui import QContextMenuEvent, QFont, QFontMetrics, QMouseEvent
from PyQt5.QtWidgets import QApplication, QWidget

from .song_card_type import SongCardType
from .song_name_card import SongNameCardFactory


class BasicSongCard(QWidget):
    """ Song card base class """

    clicked = pyqtSignal(int)
    doubleClicked = pyqtSignal(int)
    playButtonClicked = pyqtSignal(int)
    checkedStateChanged = pyqtSignal(int, bool)

    def __init__(self, songInfo: SongInfo, songCardType, parent=None):
        """
        Parameters
        ----------
        songInfo: SongInfo
            song information

        songCardType: SongCardType
            song card type

        parent:
            parent window
        """
        super().__init__(parent)
        self.setFixedHeight(60)
        self.setSongInfo(songInfo)
        self.__resizeTime = 0
        self.__songCardType = songCardType

        self.isSongExist = True
        self.isPlaying = False
        self.isSelected = False
        self.isChecked = False
        self.isInSelectionMode = False
        self.isDoubleClicked = False
        self.isPressed = False

        # the index of item corresponding to songCard
        self.itemIndex = None

        # create song name card
        self.songNameCard = SongNameCardFactory.create(
            songCardType, self.songName, self.track, self)

        self.__referenceWidgets()

        # create widgets list
        self.__scaleableLabelTextWidths = []  # 可拉伸的标签的文本的宽度列表
        self.__scaleableWidgetMaxWidths = []  # 可拉伸部件的最大宽度列表
        self.__dynamicStyleLabels = []
        self.__scaleableWidgets = []
        self.__clickableLabels = []
        self.__labelSpacings = []
        self.__labels = []
        self.__widgets = []  # contains all widgets

        # create animation
        self.__aniGroup = QParallelAnimationGroup(self)
        self.__aniWidgets = []
        self.__deltaXs = []
        self.__anis = []

        self.installEventFilter(self)

        # connect signal to slot
        self.playButton.clicked.connect(
            lambda: self.playButtonClicked.emit(self.itemIndex))

    def setSongInfo(self, songInfo: SongInfo):
        """ set song information without updating song card """
        self.songInfo = songInfo
        self.songPath = songInfo.file
        self.songName = songInfo.title
        self.singer = songInfo.singer
        self.album = songInfo.album
        self.year = str(songInfo.year or '')
        self.genre = songInfo.genre or ''
        self.track = str(songInfo.track or 0)
        self.duration = f"{int(songInfo.duration//60)}:{int(songInfo.duration%60):02}"

    def setScalableWidgets(self, widgets: list, widths: list, fixedWidth=0):
        """ set widgets that can expand as the song card expands.

        Parameters
        ----------
        widgets: list
            widgets list, the first element must be a song name card,
            and the following elements must be label

        widths: list
            initial width of widgets

        fixedWidth: int
            width reserved for other non-stretchable widgets
        """
        if self.__scaleableWidgetMaxWidths:
            return

        self.__checkIsLengthEqual(widgets, widths)

        if not self.__labels:
            raise Exception(
                "You must first call `addLabels()` to add labels to song card")

        self.__scaleableWidgets = widgets
        self.__scaleableWidgetMaxWidths = widths

        # calculate initial width of song card
        w = sum(widths) + sum(self.__labelSpacings) + fixedWidth
        self.resize(w, 60)

    def addLabels(self, labels: list, spacings: list):
        """ add labels to song card

        Paramerter
        ----------
        labels: list
            label list

        spacings: list
            the leading white space of each label
        """
        if self.__labels:
            return

        self.__checkIsLengthEqual(labels, spacings)
        self.__labels = labels
        self.__labelSpacings = spacings
        self.__widgets = [self.songNameCard] + self.__labels

    def setDynamicStyleLabels(self, labels: list):
        """ set labels that need to update styles dynamically """
        self.__dynamicStyleLabels = labels

    def setClickableLabels(self, labels: list):
        """ set labels which are clickable """
        self.__clickableLabels = labels
        for label in self.__clickableLabels:
            label.setObjectName("clickableLabel")

    def setSelected(self, isSelected: bool):
        """ set selected state """
        if self.isSelected == isSelected:
            return

        self.isSelected = isSelected
        if isSelected:
            self.setWidgetState("selected-leave")
            self.setCheckBoxBtLabelState("selected")
        else:
            self.songNameCard.setWidgetHidden(True)
            self.setWidgetState("notSelected-leave")
            state = "notSelected-play" if self.isPlaying else "notSelected-notPlay"
            self.setCheckBoxBtLabelState(state)

        self.setStyle(QApplication.style())

    def setPlay(self, isPlay: bool):
        """ set play state """
        self.isPlaying = isPlay
        self.isSelected = isPlay

        # judge whether the song file exists
        self._validateSongPath()

        if isPlay:
            self.isSelected = True
            self.setCheckBoxBtLabelState("selected")
            self.setWidgetState("selected-leave")
        else:
            self.setCheckBoxBtLabelState("notSelected-notPlay")
            self.setWidgetState("notSelected-leave")

        self.songNameCard.setPlay(isPlay, self.isSongExist)
        self.setStyle(QApplication.style())

    def setCheckBoxBtLabelState(self, state: str):
        """ set the state of check box, buttons and labels

        Parameters
        ----------
        state: str
            state of check box, buttons and labels, including:
            * `notSelected-notPlay`
            * `notSelected-play`
            * `selected`
        """
        self.songNameCard.setCheckBoxBtLabelState(state, self.isSongExist)
        for label in self.__dynamicStyleLabels:
            label.setProperty("state", state)

    def setWidgetState(self, state: str):
        """ set the state of song card

        Parameters
        ----------
        state: str
            song card state, including:
            * `notSelected-leave`
            * `notSelected-enter`
            * `notSelected-pressed`
            * `selected-leave`
            * `selected-enter`
            * `selected-pressed`
        """
        self.songNameCard.setButtonGroupState(state)
        self.setProperty("state", state)

    def setAnimation(self, widgets: list, deltaXs: list):
        """ set the animation of widgets

        Parameters
        ----------
        widgets: list
            widgets which need animation

        deltaXs: list
            position offsets for animation
        """
        self.__checkIsLengthEqual(widgets, deltaXs)
        self.__aniWidgets = widgets
        self.__deltaXs = deltaXs

        # clear animations
        self.__anis.clear()
        self.__aniGroup.clear()
        self.__anis = [QPropertyAnimation(w, b"pos")
                       for w in self.__aniWidgets]

        # initialize animation
        for ani in self.__anis:
            ani.setDuration(400)
            ani.setEasingCurve(QEasingCurve.OutQuad)
            self.__aniGroup.addAnimation(ani)

        self._getAniTargetX()

    def _validateSongPath(self):
        """ validate song path """
        self.isSongExist = os.path.exists(self.songPath)

    def _getAniTargetX(self):
        """ get initial value of animation """
        self.__aniTargetXs = []
        for deltaX, widget in zip(self.__deltaXs, self.__aniWidgets):
            self.__aniTargetXs.append(deltaX + widget.x())

    def eventFilter(self, obj, e: QEvent):
        if obj is not self:
            return super().eventFilter(obj, e)

        if e.type() == QEvent.Enter:
            self.songNameCard.checkBox.show()
            self.songNameCard.buttonGroup.setHidden(self.isInSelectionMode)
            state = "selected-enter" if self.isSelected else "notSelected-enter"
            self.setWidgetState(state)
            self.setStyle(QApplication.style())

        elif e.type() == QEvent.Leave:
            # When not in selection mode, hide the check box and button group
            # if the song card is not selected and the mouse leaves song card
            if not self.isSelected:
                self.songNameCard.buttonGroup.hide()
                self.songNameCard.checkBox.setHidden(
                    not self.isInSelectionMode)

            state = "selected-leave" if self.isSelected else "notSelected-leave"
            self.setWidgetState(state)
            self.setStyle(QApplication.style())

        elif e.type() == QEvent.MouseButtonPress:
            self.isPressed = True
            state = "selected-pressed" if self.isSelected else "notSelected-pressed"
            if e.button() == Qt.LeftButton:
                self.isSelected = True

            self.setWidgetState(state)
            self.setStyle(QApplication.style())

        elif e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
            self.setWidgetState("selected-leave")
            self.setCheckBoxBtLabelState("selected")
            self.setStyle(QApplication.style())

        elif e.type() == QEvent.MouseButtonDblClick:
            self.isDoubleClicked = True
            self.isPressed = True

        return super().eventFilter(obj, e)

    def mousePressEvent(self, e):
        super().mousePressEvent(e)

        # move widgets
        if self.__aniGroup.state() == QAbstractAnimation.Stopped:
            for dx, w in zip(self.__deltaXs, self.__aniWidgets):
                w.move(w.x() + dx, w.y())
        else:
            self.__aniGroup.stop()  # 强制停止还未结束的动画
            for x, w in zip(self.__aniTargetXs, self.__aniWidgets):
                w.move(x, w.y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        if not self.isPressed:
            return

        self.isPressed = False
        for ani, w, dx in zip(self.__anis, self.__aniWidgets, self.__deltaXs):
            ani.setStartValue(w.pos())
            ani.setEndValue(QPoint(w.x() - dx, w.y()))

        self.__aniGroup.start()

        if e.button() == Qt.LeftButton:
            self.clicked.emit(self.itemIndex)

        if self.isDoubleClicked and e.button() == Qt.LeftButton:
            self.isDoubleClicked = False
            if not self.isPlaying:
                self.__aniGroup.finished.connect(self.__onAniFinished)

    def contextMenuEvent(self, e: QContextMenuEvent):
        if sys.platform == "win32":
            return super().contextMenuEvent(e)

        event = QMouseEvent(
            QEvent.MouseButtonRelease,
            e.pos(),
            Qt.RightButton,
            Qt.RightButton,
            Qt.NoModifier
        )
        QApplication.sendEvent(self, event)
        return super().contextMenuEvent(e)

    def __onAniFinished(self):
        """ animation finished slot """
        self.doubleClicked.emit(self.itemIndex)
        self.__aniGroup.disconnect()

    def setClickableLabelCursor(self, cursor):
        """ set the cursor of clickable label """
        for label in self.__clickableLabels:
            label.setCursor(cursor)

    def __referenceWidgets(self):
        """ reference widgets """
        self.buttonGroup = self.songNameCard.buttonGroup
        self.playButton = self.songNameCard.playButton
        self.addToButton = self.songNameCard.addToButton
        self.checkBox = self.songNameCard.checkBox

    def _onCheckedStateChanged(self):
        """ checked state changed slot """
        self.isChecked = self.checkBox.isChecked()
        self.setSelected(self.isChecked)

        # open selection mode if check box is clicked
        self.checkBox.show()
        self.setSelectionModeOpen(True)

        self.checkedStateChanged.emit(self.itemIndex, self.isChecked)

    def setSelectionModeOpen(self, isOpen: bool):
        """ set whether to open selection mode """
        if self.isInSelectionMode == isOpen:
            return

        self.isInSelectionMode = isOpen
        self.checkBox.setHidden(not isOpen)
        self.buttonGroup.setHidden(True)

    def setChecked(self, isChecked: bool):
        """ set checked state """
        if self.isChecked == isChecked:
            return

        self.checkBox.setChecked(isChecked)

    def updateSongCard(self, songInfo: SongInfo):
        """ update song card """
        raise NotImplementedError

    def __checkIsLengthEqual(self, list_1: list, list_2: list):
        """ check if the length of list is equal """
        if len(list_1) != len(list_2):
            raise Exception("The length of the two list must be the same")

    def resizeEvent(self, e):
        self.__resizeTime += 1
        if self.__resizeTime > 1:
            # distribute width
            deltaWidth = self.width() - self.__originalWidth
            self.__originalWidth = self.width()
            equalWidth = int(deltaWidth / len(self.__scaleableWidgets))
            self.__scaleableWidgetMaxWidths = [
                i + equalWidth for i in self.__scaleableWidgetMaxWidths]
        else:
            self.__originalWidth = self.width()

        self._adjustWidgetWidth()

        # move labels
        x = self.songNameCard.width()
        for label, spacing in zip(self.__labels, self.__labelSpacings):
            if label in self.__scaleableWidgets:
                index = self.__scaleableWidgets.index(label)
                width = self.__scaleableWidgetMaxWidths[index]
            else:
                width = label.width()

            label.move(x + spacing, 20)
            x = width + label.x()

        self._getAniTargetX()

    def _adjustWidgetWidth(self):
        """ adjust widget width """
        self.__getScaleableLabelTextWidth()
        self.songNameCard.resize(self.__scaleableWidgetMaxWidths[0], 60)
        for i in range(1, len(self.__scaleableWidgets)):
            label = self.__scaleableWidgets[i]
            w = self.__scaleableLabelTextWidths[i - 1]
            mw = self.__scaleableWidgetMaxWidths[i]
            label.setFixedWidth(min(mw, w))

    def __getScaleableLabelTextWidth(self):
        """ get the text width of stretchable label """
        font = QFont("Microsoft YaHei")
        font.setPixelSize(15)
        fontMetrics = QFontMetrics(font)
        self.__scaleableLabelTextWidths = [
            fontMetrics.width(label.text()) for label in self.__scaleableWidgets[1:]]

    def _showAddToMenu(self):
        """ show add to menu """
        menu = AddToMenu(parent=self)
        pos = self.mapToGlobal(
            QPoint(self.addToButton.x()+self.buttonGroup.x(), 0))
        x = pos.x() + self.addToButton.width() + 5
        y = pos.y() + int(
            self.addToButton.height() / 2 - (13 + 38 * menu.actionCount()) / 2)

        menu.playingAct.triggered.connect(
            lambda: signalBus.addSongsToPlayingPlaylistSig.emit([self.songInfo]))
        menu.newPlaylistAct.triggered.connect(
            lambda: signalBus.addSongsToNewCustomPlaylistSig.emit([self.songInfo]))
        menu.addSongsToPlaylistSig.connect(
            lambda name: signalBus.addSongsToCustomPlaylistSig.emit(name, [self.songInfo]))
        menu.exec(QPoint(x, y))

    @property
    def widgets(self) -> list:
        return self.__widgets

    @property
    def labels(self) -> list:
        return self.__labels
