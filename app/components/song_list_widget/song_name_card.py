# coding:utf-8
from PyQt5.QtCore import QEvent, QSize, Qt
from PyQt5.QtGui import QFont, QFontMetrics, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import (QApplication, QCheckBox, QLabel, QToolButton,
                             QWidget)

from .song_card_type import SongCardType


class ToolButton(QToolButton):
    """ Tool button of song name card """

    def __init__(self, iconPaths: dict, parent=None):
        super().__init__(parent)
        self.iconPaths = iconPaths
        self.setFixedSize(60, 60)
        self.setIconSize(QSize(60, 60))
        self.setState("notSelected-notPlay")
        self.setStyleSheet("QToolButton{border:none;margin:0}")

    def setState(self, state: str):
        """ set button state

        Parameters
        ----------
        state: str
            button state, including:
            * notSelected-notPlay
            * notSelected-play
            * selected
        """
        self.state = state
        self.update()
        self.setProperty("state", state)

    def setIconPaths(self, iconPaths: dict):
        """ set icon paths of button """
        self.iconPaths = iconPaths
        self.update()

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setRenderHints(QPainter.Antialiasing |
                              QPainter.SmoothPixmapTransform)
        pixmap = QPixmap(self.iconPaths[self.state])
        painter.drawPixmap(self.rect(), pixmap)

class ButtonGroup(QWidget):
    """ Button group of song name card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.playButton = ToolButton(
            {
                "notSelected-notPlay": ":/images/song_tab_interface/Play_black.png",
                "notSelected-play": ":/images/song_tab_interface/Play_green.png",
                "selected": ":/images/song_tab_interface/Play_white.png",
            },
            self,
        )
        self.addToButton = ToolButton(
            {
                "notSelected-notPlay": ":/images/song_tab_interface/Add_black.png",
                "notSelected-play": ":/images/song_tab_interface/Add_green.png",
                "selected": ":/images/song_tab_interface/Add_white.png",
            },
            self,
        )
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedSize(140, 60)

        self.addToButton.move(80, 0)
        self.playButton.move(20, 0)

        # set property and ID
        self.setObjectName("buttonGroup")
        self.setProperty("state", "notSelected-leave")

        self.installEventFilter(self)

    def setButtonHidden(self, isHidden: bool):
        """ set whether to hide buttons """
        self.playButton.setHidden(isHidden)
        self.addToButton.setHidden(isHidden)

    def setButtonState(self, state: str):
        """ set button state

        Parameters
        ----------
        state: str
            button state, including:
            * notSelected-notPlay
            * notSelected-play
            * selected
        """
        self.playButton.setState(state)
        self.addToButton.setState(state)

    def setState(self, state: str):
        """ set button group state

        Parameters
        ----------
        state: str
            按钮组状态，有以下六种：
            * notSelected-leave
            * notSelected-enter
            * notSelected-pressed
            * selected-leave
            * selected-enter
            * selected-pressed
        """
        self.setProperty("state", state)

    def eventFilter(self, obj, e: QEvent):
        if obj == self:
            if e.type() == QEvent.Hide:
                # Cancel hover status of buttons when button group is hidden
                e = QEvent(QEvent.Leave)
                QApplication.sendEvent(self.playButton, e)
                QApplication.sendEvent(self.addToButton, e)

        return super().eventFilter(obj, e)


class SongNameCard(QWidget):
    """ Song name card """

    def __init__(self, songName: str, parent=None):
        super().__init__(parent)
        self.songName = songName
        self.isPlay = False
        self.checkBox = QCheckBox(self)  # type:QCheckBox
        self.playingLabel = QLabel(self)
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

        self.checkBox.setFocusPolicy(Qt.NoFocus)

        # hide widgets
        self.playingLabel.hide()
        self.setWidgetHidden(True)

        # set properties and ID
        self.setObjectName("songNameCard")
        self.songNameLabel.setObjectName("songNameLabel")

        self.__getSongNameWidth()
        self.__initLayout()

    def __initLayout(self):
        """ initialize layout """
        self.checkBox.move(15, 18)
        self.playingLabel.move(57, 22)
        self.songNameLabel.move(57, 18)
        self._moveButtonGroup()

    def __getSongNameWidth(self):
        """ get song name width """
        fontMetrics = QFontMetrics(QFont("Microsoft YaHei", 10))
        self.songNameWidth = fontMetrics.width(self.songName)

    def _moveButtonGroup(self):
        """ move button group """
        if self.songNameWidth + self.songNameLabel.x() >= self.width() - 140:
            x = self.width() - 140
        else:
            x = self.songNameWidth + self.songNameLabel.x()
        self.buttonGroup.move(x, 0)

    def updateSongNameCard(self, songName: str):
        """ update song name card """
        self.songName = songName
        self.songNameLabel.setText(songName)
        self.__getSongNameWidth()
        self._moveButtonGroup()
        self.songNameLabel.setFixedWidth(self.songNameWidth)

    def setWidgetHidden(self, isHidden: bool):
        """ set whether to hide widgets """
        self.buttonGroup.setHidden(isHidden)
        self.checkBox.setHidden(isHidden)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._moveButtonGroup()

    def setCheckBoxBtLabelState(self, state: str, isSongExit=True):
        """ set the state of check box, buttons and labels

        Parameters
        ----------
        state: str
            including `notSelected-notPlay`, `notSelected-play` and `selected`

        isSongExist: bool
            whether the song exists or not, the alarm icon will appear when it is `False`.
        """
        self.checkBox.setProperty("state", state)
        self.songNameLabel.setProperty("state", state)
        self.buttonGroup.setButtonState(state)

        # update icon
        if isSongExit:
            color = "white" if state == "selected" else "green"
            path = f":/images/song_tab_interface/Playing_{color}.png"
        else:
            color = "white" if state == "selected" else "red"
            path = f":/images/song_tab_interface/Info_{color}.png"

        self.playingLabel.setPixmap(QPixmap(path))

    def setButtonGroupState(self, state: str):
        """ set button group state """
        self.buttonGroup.setState(state)

    def setPlay(self, isPlay: bool, isSongExist: bool = True):
        """ set playing state """
        self.isPlay = isPlay
        self.playingLabel.setVisible(isPlay or (not isSongExist))
        self.setWidgetHidden(not isPlay)

        x = 83 if isPlay or (not isSongExist) else 57
        self.songNameLabel.move(x, self.songNameLabel.y())
        self._moveButtonGroup()


class TrackSongNameCard(SongNameCard):
    """ Song name card with track number """

    def __init__(self, songName: str, track: str, parent=None):
        super().__init__(songName, parent)
        self.trackLabel = QLabel(self)
        self.setTrack(track)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.__adjustTrackLabelPos()
        self.trackLabel.setFixedWidth(25)
        self.trackLabel.setObjectName("trackLabel")
        self.checkBox.installEventFilter(self)

    def setCheckBoxBtLabelState(self, state: str, isSongExist=True):
        super().setCheckBoxBtLabelState(state, isSongExist)
        self.trackLabel.setProperty("state", state)

    def updateSongNameCard(self, songName: str, track: str):
        super().updateSongNameCard(songName)
        self.setTrack(track)
        self.__adjustTrackLabelPos()

    def setTrack(self, track: str):
        """ set track number """
        self.track = track
        self.trackLabel.setText(f"{track}." if int(track) > 0 else '')

    def setWidgetsHidden(self, isHidden: bool):
        self.trackLabel.setHidden(not isHidden)
        super().setWidgetHidden(isHidden)

    def __adjustTrackLabelPos(self):
        """ adjust track label position """
        x = 19 if int(self.track) >= 10 else 28
        self.trackLabel.move(x, 18)

    def setPlay(self, isPlay: bool, isSongExist=True):
        """ set playing state """
        super().setPlay(isPlay, isSongExist)
        self.trackLabel.setHidden(isPlay)

    def eventFilter(self, obj, e: QEvent):
        if obj == self.checkBox:
            if e.type() == QEvent.Show:
                self.trackLabel.hide()
                return False
            elif e.type() == QEvent.Hide:
                self.trackLabel.show()
                return False

        return super().eventFilter(obj, e)


class PlaylistSongNameCard(SongNameCard):
    """ Playlist song name card """

    def __init__(self, songName, parent):
        super().__init__(songName, parent=parent)
        self.addToButton.setIconPaths({
            "notSelected-notPlay": ":/images/playlist_interface/Delete_black.png",
            "notSelected-play": ":/images/playlist_interface/Delete_green.png",
            "selected": ":/images/playlist_interface/Delete_white.png",
        })


class NoCheckBoxSongNameCard(SongNameCard):
    """ Song card without check box """

    def __init__(self, songName, parent):
        super().__init__(songName, parent=parent)
        self.songNameLabel.move(15, 18)
        self.playingLabel.move(15, 22)
        self.checkBox.setFixedWidth(0)
        self.checkBox.lower()

    def setPlay(self, isPlay: bool, isSongExist: bool = True):
        self.isPlay = isPlay
        self.playingLabel.setVisible(isPlay or (not isSongExist))
        self.setWidgetHidden(not isPlay)
        x = 41 if isPlay or (not isSongExist) else 15
        self.songNameLabel.move(x, self.songNameLabel.y())
        self._moveButtonGroup()


class OnlineSongNameCard(SongNameCard):
    """ Online song card """

    def __init__(self, songName, parent):
        super().__init__(songName, parent=parent)
        self.songNameLabel.move(15, 18)
        self.playingLabel.move(15, 22)
        self.checkBox.setFixedWidth(0)
        self.checkBox.lower()
        self.addToButton.setIconPaths({
            "notSelected-notPlay": ":/images/search_result_interface/Download_black.png",
            "notSelected-play": ":/images/search_result_interface/Download_green.png",
            "selected": ":/images/search_result_interface/Download_white.png",
        })

    def setPlay(self, isPlay: bool, isSongExist: bool = True):
        self.isPlay = isPlay
        self.playingLabel.setVisible(isPlay or (not isSongExist))
        self.setWidgetHidden(not isPlay)
        x = 41 if isPlay or (not isSongExist) else 15
        self.songNameLabel.move(x, self.songNameLabel.y())
        self._moveButtonGroup()


class SongNameCardFactory:
    """ Song name card factory """

    @staticmethod
    def create(songCardType: SongCardType, songName: str, track: int = None, parent=None) -> SongNameCard:
        """ create a song name card

        Parameters
        ----------
        songCardType: SongCardType
            song card type

        songName: str
            song name

        track: int
            track number, needs to be specified only if type is `SongCardType.ALBUM_INTERFACE_SONG_CARD`

        parent:
            parent window

        Returns
        -------
        songNameCard:
            song name card
        """
        songNameCard_dict = {
            SongCardType.SONG_TAB_SONG_CARD: SongNameCard,
            SongCardType.ALBUM_INTERFACE_SONG_CARD: TrackSongNameCard,
            SongCardType.PLAYLIST_INTERFACE_SONG_CARD: PlaylistSongNameCard,
            SongCardType.NO_CHECKBOX_SONG_CARD: NoCheckBoxSongNameCard,
            SongCardType.ONLINE_SONG_CARD: OnlineSongNameCard
        }

        if songCardType not in songNameCard_dict:
            raise ValueError(f"Song card type `{songCardType}` is illegal")

        SongNameCard_ = songNameCard_dict[songCardType]
        if songCardType != SongCardType.ALBUM_INTERFACE_SONG_CARD:
            return SongNameCard_(songName, parent)

        return SongNameCard_(songName, track, parent)
