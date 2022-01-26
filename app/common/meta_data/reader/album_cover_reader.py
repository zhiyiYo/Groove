# coding:utf-8
from pathlib import Path
from shutil import rmtree
from typing import List

from common.database.entity import SongInfo
from common.image_process_utils import getPicSuffix
from common.os_utils import adjustName
from mutagen import File, FileType
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4


class AlbumCoverReaderBase:
    """ 专辑封面获取器抽象类 """

    @staticmethod
    def getAlbumCover(audio: FileType) -> bytes:
        """ 读取专辑封面

        Parameters
        ----------
        audio: FileType
            音频标签文件

        Returns
        -------
        picData: bytes
            封面二进制数据，不存在封面时返回 `None`
        """
        raise NotImplementedError("该方法必须被子类实现")


class MP3AlbumCoverReader(AlbumCoverReaderBase):
    """ MP3 专辑封面获取器 """

    @staticmethod
    def getAlbumCover(audio: MP3) -> bytes:
        for k in audio.tags.keys():
            if k.startswith("APIC"):
                return audio[k].data


class FLACAlbumCoverReader(AlbumCoverReaderBase):
    """ FLAC 专辑封面获取器 """

    @staticmethod
    def getAlbumCover(audio: FLAC) -> bytes:
        if not audio.pictures:
            return None

        return audio.pictures[0].data


class MP4AlbumCoverReader(AlbumCoverReaderBase):
    """ MP4/M4A 专辑封面获取器 """

    @staticmethod
    def getAlbumCover(audio: MP4) -> bytes:
        if not audio.get("covr"):
            return None

        return bytes(audio["covr"][0])


class AlbumCoverReader:
    """ 读取并保存专辑封面类 """

    coverFolder = Path("cache/Album_Cover")

    @classmethod
    def updateAlbumCovers(cls, songInfos: List[SongInfo]):
        """ 重新扫描指定的文件下的音频文件的专辑封面 """
        cls.getAlbumCovers(songInfos)

    @classmethod
    def getAlbumCovers(cls, songInfos: List[SongInfo]):
        """ 获取多张专辑封面 """
        cls.coverFolder.mkdir(exist_ok=True, parents=True)
        for songInfo in songInfos:
            cls.getOneAlbumCover(songInfo)

    @classmethod
    def getOneAlbumCover(cls, songInfo: SongInfo):
        """ 获取一张专辑封面 """
        cls.coverFolder.mkdir(exist_ok=True, parents=True)

        isExists = cls.__isCoverExists(songInfo.singer, songInfo.album)
        if isExists:
            return

        audio = File(songInfo.file, options=[MP3, FLAC, MP4])
        AudioType = type(audio)
        readerMap = {
            MP3: MP3AlbumCoverReader,
            FLAC: FLACAlbumCoverReader,
            MP4: MP4AlbumCoverReader
        }

        if AudioType not in readerMap:
            return

        picData = readerMap[AudioType].getAlbumCover(audio)
        if picData:
            cls.__save(songInfo.singer, songInfo.album, picData)

    @classmethod
    def __isCoverExists(cls, singer: str, album: str) -> bool:
        """ 检测封面是否存在

        Parameters
        ----------
        singer: str
            歌手

        album: str
            专辑

        Returns
        -------
        isExists: bool
            封面是否存在
        """
        coverName = adjustName(singer + '_' + album)
        folder = cls.coverFolder / coverName

        isExists = False
        if folder.exists():
            files = list(folder.glob('*'))

            if files:
                suffix = files[0].suffix.lower()
                if suffix in [".png", ".jpg", ".jpeg", ".jiff", ".gif"]:
                    isExists = True
                else:
                    rmtree(folder)

        return isExists

    @classmethod
    def __save(cls, singer: str, album: str, picData: bytes):
        """ 储存提取到的专辑封面

        Parameters
        ----------
        singer: str
            歌手

        album: str
            专辑

        picData: bytes
            封面二进制数据
        """
        coverName = adjustName(singer + '_' + album)
        folder = cls.coverFolder / coverName
        folder.mkdir(exist_ok=True, parents=True)

        suffix = getPicSuffix(picData)
        with open(folder/(coverName + suffix), "wb") as f:
            f.write(picData)
