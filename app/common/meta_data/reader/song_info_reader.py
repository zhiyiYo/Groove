# coding:utf-8
from pathlib import Path
from typing import Union

from mutagen import File
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from PyQt5.QtCore import QObject
from tinytag import TinyTag

from common.database.entity import SongInfo


class SongInfoReader(QObject):
    """ 歌曲信息读取器 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 歌曲信息的默认值
        self.singer = self.tr('Unknown artist')
        self.album = self.tr("Unknown album")
        self.genre = self.tr("Unknown genre")
        self.year = None
        self.track = 1
        self.trackTotal = 1
        self.disc = 1
        self.discTotal = 1

    def read(self, file: Union[str, Path]):
        """ 读取歌曲信息

        Parameters
        ----------
        file: str or Path
            音频文件路径

        Returns
        -------
        songInfo: SongInfo
            歌曲信息
        """
        if not isinstance(file, Path):
            file = Path(file)

        tag = TinyTag.get(file)

        file_ = str(file).replace('\\', '/')
        title = tag.title or file.stem
        singer = tag.artist or self.singer
        album = tag.album or self.album
        year = self.__getYear(tag, file)
        genre = tag.genre or self.genre
        duration = int(tag.duration)
        track = self.__getTrack(tag)
        trackTotal = tag.track_total or self.trackTotal
        disc = int(tag.disc or self.disc)
        discTotal = tag.disc_total or self.discTotal
        createTime = int(file.stat().st_ctime)
        modifiedTime = int(file.stat().st_mtime)

        return SongInfo(
            file=file_,
            title=title,
            singer=singer,
            album=album,
            year=year,
            genre=genre,
            duration=duration,
            track=track,
            trackTotal=trackTotal,
            disc=disc,
            discTotal=discTotal,
            createTime=createTime,
            modifiedTime=modifiedTime
        )

    def __getYear(self, tag: TinyTag, file: Path):
        """ 获取年份 """
        if tag.year and tag.year[0] != '0':
            return int(tag.year[:4])

        audio = File(file, [MP3, FLAC, MP4])

        if isinstance(audio, MP3):
            year = [str(audio.get("TDRC", 0))]
        elif isinstance(audio, MP4):
            year = audio.get('©day', ['0'])
        elif isinstance(audio, FLAC):
            year = audio.get('year', ['0'])
        else:
            year = ['0']

        if year and year[0] != '0':
            return int(year[0])

        return self.year

    def __getTrack(self, tag: TinyTag):
        """ 获取曲目 """
        track = str(tag.track or self.track)

        # 处理 a/b
        track = track.split('/')[0]

        # 处理 An
        if track[0].upper() == 'A':
            track = track[1:]

        return int(track)

    @staticmethod
    def getModifiedTime(file: str):
        """ 获取歌曲信息修改时间 """
        path = Path(file)
        return int(path.stat().st_mtime)