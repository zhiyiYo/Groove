# coding:utf-8
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from .media_playlist import MediaPlaylist


class MediaPlayer(QMediaPlayer):
    """ Media player """

    def __init__(self, playlist: MediaPlaylist, parent=None) -> None:
        super().__init__(parent=parent)
        self.mediaPlaylist = playlist
        self.currentIndex = None
        self.__position = 0
        self.__isPlayingBefore = False
        self.setNotifyInterval(1000)
        self.setPlaylist(playlist)

    def isPlaying(self):
        """ whether the player is playing """
        return self.state() == self.PlayingState

    @property
    def isPlayingBeforeRelease(self):
        return self.__isPlayingBefore

    def releaseAudioHandle(self):
        """ release the handle of audio file """
        self.currentIndex = self.mediaPlaylist.currentIndex()
        self.__position = self.position()
        self.__isPlayingBefore = self.isPlaying()

        # block the signal to prevent switching songs
        self.mediaPlaylist.blockSignals(True)
        self.blockSignals(True)
        self.setMedia(QMediaContent())

    def recoverAudioHandle(self):
        """ recover the handle of audio file """
        self.setPlaylist(self.mediaPlaylist)
        self.mediaPlaylist.setCurrentIndex(self.currentIndex)
        self.setPosition(self.__position)

        self.blockSignals(False)
        self.mediaPlaylist.blockSignals(False)