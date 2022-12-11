# coding:utf-8
import os
from common.database.entity import SongInfo
from common.signal_bus import signalBus
from components.widgets.label import ClickableLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QLabel

from .basic_song_card import BasicSongCard
from .song_card_type import SongCardType


class DurationSongCard(BasicSongCard):
    """ Song card with a duration label """

    def __init__(self, songInfo: SongInfo, songCardType, parent=None):
        super().__init__(songInfo, songCardType, parent)
        self.durationLabel = QLabel(self.duration, self)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setWidgetState("notSelected-leave")
        self.setCheckBoxBtLabelState("notSelected-notPlay")

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.durationLabel.move(self.width() - 45, 20)
        self._getAniTargetX()

    def updateSongCard(self, songInfo: SongInfo):
        self.setSongInfo(songInfo)
        self.durationLabel.setText(self.duration)


class SongTabSongCard(DurationSongCard):
    """ Song tab interface song card """

    def __init__(self, songInfo: SongInfo, parent=None):
        super().__init__(songInfo, SongCardType.SONG_TAB_SONG_CARD, parent)
        self.singerLabel = ClickableLabel(self.singer, self, False)
        self.albumLabel = ClickableLabel(self.album, self, False)
        self.yearLabel = QLabel(self.year, self)
        self.genreLabel = QLabel(self.genre, self)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.yearLabel.setFixedWidth(60)
        self.addLabels(
            [
                self.singerLabel,
                self.albumLabel,
                self.yearLabel,
                self.genreLabel,
                self.durationLabel,
            ],
            [30, 15, 27, 19, 70],
        )

        # The width of year is fixed to 60px, duration distance window right border 45px
        self.setScalableWidgets(
            [self.songNameCard, self.singerLabel, self.albumLabel, self.genreLabel],
            [326, 191, 191, 178],
            105,
        )
        self.setDynamicStyleLabels(self.labels)

        # set song card clicked animation
        self.setAnimation(self.widgets, [13, 6, -3, -6, -8, -13])

        self.setClickableLabels([self.singerLabel, self.albumLabel])
        self.setClickableLabelCursor(Qt.PointingHandCursor)

        # connect signal to slot
        self.addToButton.clicked.connect(self._showAddToMenu)
        self.checkBox.stateChanged.connect(self._onCheckedStateChanged)
        self.singerLabel.clicked.connect(
            lambda: signalBus.switchToSingerInterfaceSig.emit(self.singer))
        self.albumLabel.clicked.connect(
            lambda: signalBus.switchToAlbumInterfaceSig.emit(self.singer, self.album))

    def updateSongCard(self, songInfo: SongInfo):
        if self.songInfo == songInfo:
            return

        super().updateSongCard(songInfo)
        self.songNameCard.updateSongNameCard(self.songName)
        self.singerLabel.setText(self.singer)
        self.albumLabel.setText(self.album)
        self.yearLabel.setText(str(self.year))
        self.genreLabel.setText(self.genre)
        self._adjustWidgetWidth()


class AlbumInterfaceSongCard(DurationSongCard):
    """ Album interface song card """

    def __init__(self, songInfo: SongInfo, parent=None):
        super().__init__(songInfo, SongCardType.ALBUM_INTERFACE_SONG_CARD, parent)
        self.singerLabel = ClickableLabel(self.singer, self, False)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.addLabels([self.singerLabel, self.durationLabel], [16, 70])

        # set scaleable widgets
        self.setScalableWidgets(
            [self.songNameCard, self.singerLabel], [554, 401], 45)
        self.setDynamicStyleLabels(self.labels)

        # set song card clicked animation
        self.setAnimation(self.widgets, [13, -3, -13])

        # set clickable labels
        self.setClickableLabels([self.singerLabel])
        self.setClickableLabelCursor(Qt.PointingHandCursor)

        # connect signal to slot
        self.singerLabel.clicked.connect(
            lambda: signalBus.switchToSingerInterfaceSig.emit(self.singer))
        self.addToButton.clicked.connect(self._showAddToMenu)
        self.checkBox.stateChanged.connect(self._onCheckedStateChanged)

    def updateSongCard(self, songInfo: SongInfo):
        if self.songInfo == songInfo:
            return

        super().updateSongCard(songInfo)
        self.songNameCard.updateSongNameCard(self.songName, self.track)
        self.singerLabel.setText(self.singer)
        self._adjustWidgetWidth()


class PlaylistInterfaceSongCard(DurationSongCard):
    """ Playlist interface song card """

    removeSongSignal = pyqtSignal(int)

    def __init__(self, songInfo: SongInfo, parent=None):
        super().__init__(songInfo, SongCardType.PLAYLIST_INTERFACE_SONG_CARD, parent)
        self.singerLabel = ClickableLabel(self.singer, self, False)
        self.albumLabel = ClickableLabel(self.album, self, False)
        self.yearLabel = QLabel(self.year, self)
        self.genreLabel = QLabel(self.genre, self)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.yearLabel.setFixedWidth(60)
        self.addLabels(
            [
                self.singerLabel,
                self.albumLabel,
                self.yearLabel,
                self.genreLabel,
                self.durationLabel,
            ],
            [30, 15, 27, 19, 70],
        )

        # The width of year is fixed to 60px, duration distance window right border 45px
        self.setScalableWidgets(
            [self.songNameCard, self.singerLabel, self.albumLabel, self.genreLabel],
            [326, 191, 191, 178],
            105,
        )
        self.setDynamicStyleLabels(self.labels)

        # set song card clicked animation
        self.setAnimation(self.widgets, [13, 6, -3, -6, -8, -13])

        self.setClickableLabels([self.singerLabel, self.albumLabel])
        self.setClickableLabelCursor(Qt.PointingHandCursor)

        # connect signal to slot
        self.singerLabel.clicked.connect(
            lambda: signalBus.switchToSingerInterfaceSig.emit(self.singer))
        self.albumLabel.clicked.connect(
            lambda: signalBus.switchToAlbumInterfaceSig.emit(self.singer, self.album))
        self.addToButton.clicked.connect(
            lambda: self.removeSongSignal.emit(self.itemIndex))
        self.checkBox.stateChanged.connect(self._onCheckedStateChanged)

    def updateSongCard(self, songInfo: SongInfo):
        if self.songInfo == songInfo:
            return

        super().updateSongCard(songInfo)
        self.songNameCard.updateSongNameCard(self.songName)
        self.singerLabel.setText(self.singer)
        self.albumLabel.setText(self.album)
        self.yearLabel.setText(self.year)
        self.genreLabel.setText(self.genre)
        self._adjustWidgetWidth()

    def _validateSongPath(self):
        if self.songPath.startswith("http"):
            self.isSongExist = True
        else:
            self.isSongExist = os.path.exists(self.songPath)


class NoCheckBoxSongCard(DurationSongCard):
    """ Song card without check box """

    def __init__(self, songInfo: SongInfo, parent=None):
        super().__init__(songInfo, SongCardType.NO_CHECKBOX_SONG_CARD, parent=parent)
        self.singerLabel = ClickableLabel(self.singer, self, False)
        self.albumLabel = ClickableLabel(self.album, self, False)
        self.yearLabel = QLabel(self.year, self)
        self.genreLabel = QLabel(self.genre, self)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.yearLabel.setFixedWidth(60)
        self.addLabels(
            [
                self.singerLabel,
                self.albumLabel,
                self.yearLabel,
                self.genreLabel,
                self.durationLabel,
            ],
            [30, 15, 27, 19, 70],
        )

        # The width of year is fixed to 60px, duration distance window right border 45px
        self.setScalableWidgets(
            [self.songNameCard, self.singerLabel,
                self.albumLabel, self.genreLabel],
            [326, 191, 191, 178],
            105,
        )
        self.setDynamicStyleLabels(self.labels)

        # set song card clicked animation
        self.setAnimation(self.widgets, [13, 6, -3, -6, -8, -13])

        self.setClickableLabels([self.singerLabel, self.albumLabel])
        self.setClickableLabelCursor(Qt.PointingHandCursor)

        # connect signal to slot
        self.singerLabel.clicked.connect(
            lambda: signalBus.switchToSingerInterfaceSig.emit(self.singer))
        self.albumLabel.clicked.connect(
            lambda: signalBus.switchToAlbumInterfaceSig.emit(self.singer, self.album))
        self.addToButton.clicked.connect(self._showAddToMenu)

    def updateSongCard(self, songInfo: SongInfo):
        if self.songInfo == songInfo:
            return

        super().updateSongCard(songInfo)
        self.songNameCard.updateSongNameCard(self.songName)
        self.singerLabel.setText(self.singer)
        self.albumLabel.setText(self.album)
        self.yearLabel.setText(self.year)
        self.genreLabel.setText(self.genre)
        self._adjustWidgetWidth()


class NoCheckBoxOnlineSongCard(DurationSongCard):
    """ Online song card without check box """

    cardType =  SongCardType.NO_CHECKBOX_ONLINE_SONG_CARD

    def __init__(self, songInfo: SongInfo, parent=None):
        super().__init__(songInfo, self.cardType, parent=parent)
        self.singerLabel = QLabel(self.singer, self)
        self.albumLabel = QLabel(self.album, self)
        self.yearLabel = QLabel(self.year, self)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.addLabels(
            [self.singerLabel, self.albumLabel, self.yearLabel, self.durationLabel],
            [30, 15, 27, 70],
        )

        # The width of year is fixed to 60px, duration distance window right border 45px
        self.setScalableWidgets(
            [self.songNameCard, self.singerLabel, self.albumLabel],
            [326, 191, 191],
            105,
        )
        self.setDynamicStyleLabels(self.labels)

        # set song card clicked animation
        self.setAnimation(self.widgets, [13, 6, -3, -6, -13])

        # connect signal to slot
        self.addToButton.clicked.connect(self._showDownloadMenu)

    def updateSongCard(self, songInfo: SongInfo):
        if self.songInfo == songInfo:
            return

        super().updateSongCard(songInfo)
        self.songNameCard.updateSongNameCard(self.songName)
        self.singerLabel.setText(self.singer)
        self.albumLabel.setText(self.album)
        self.yearLabel.setText(self.year)
        self._adjustWidgetWidth()

    def _validateSongPath(self):
        self.isSongExist = True


class OnlineSongCard(NoCheckBoxOnlineSongCard):
    """ Online song card """

    cardType = SongCardType.ONLINE_SONG_CARD

    def __init__(self, songInfo: SongInfo, parent=None):
        super().__init__(songInfo, parent=parent)
        self.checkBox.stateChanged.connect(self._onCheckedStateChanged)


class SongCardFactory:
    """ Song card factory """

    @staticmethod
    def create(songCardType: SongCardType, songInfo: SongInfo, parent=None) -> BasicSongCard:
        """ create a song card

        Parameters
        ----------
        songCardType: SongCardType
            song card type

        songInfo: SongInfo
            song information

        parent:
            parent window
        """
        songCardMap = {
            SongCardType.SONG_TAB_SONG_CARD: SongTabSongCard,
            SongCardType.ALBUM_INTERFACE_SONG_CARD: AlbumInterfaceSongCard,
            SongCardType.PLAYLIST_INTERFACE_SONG_CARD: PlaylistInterfaceSongCard,
            SongCardType.NO_CHECKBOX_SONG_CARD: NoCheckBoxSongCard,
            SongCardType.NO_CHECKBOX_ONLINE_SONG_CARD: NoCheckBoxOnlineSongCard,
            SongCardType.ONLINE_SONG_CARD: OnlineSongCard,
        }

        if songCardType not in songCardMap:
            raise ValueError(f"Song card type `{songCardType}` is illegal")

        return songCardMap[songCardType](songInfo, parent)
