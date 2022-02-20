# coding:utf-8
from common.database.entity import AlbumInfo, SongInfo
from common.meta_data.writer import writeSongInfo, writeAlbumCover
from common.meta_data.reader import SongInfoReader
from PyQt5.QtCore import QThread, pyqtSignal


class SaveAlbumInfoThread(QThread):
    """ Save album information thread """

    saveFinishedSignal = pyqtSignal(AlbumInfo, AlbumInfo, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.oldAlbumInfo = AlbumInfo()
        self.newAlbumInfo = AlbumInfo()
        self.coverPath = ''

    def setAlbumInfo(self, oldAlbumInfo: AlbumInfo, newAlbumInfo: AlbumInfo, coverPath: str):
        """ set the album information to be saved """
        self.oldAlbumInfo = oldAlbumInfo
        self.newAlbumInfo = newAlbumInfo
        self.coverPath = coverPath

    def run(self):
        """ start to save information """
        for i, songInfo in enumerate(self.newAlbumInfo.songInfos):
            # modify album cover
            writeAlbumCover(songInfo.file, self.coverPath)

            # rollback when writing song information fails
            if not writeSongInfo(songInfo):
                self.newAlbumInfo.songInfos[i] = self.oldAlbumInfo.songInfos[i]

            # update the modified time of audio file
            songInfo.modifiedTime = SongInfoReader.getModifiedTime(
                songInfo.file)

        self.saveFinishedSignal.emit(
            self.oldAlbumInfo, self.newAlbumInfo, self.coverPath)
