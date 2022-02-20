# coding:utf-8
from pathlib import Path
from shutil import rmtree
from typing import List

from common.database.entity import SongInfo
from common.image_process_utils import getPicSuffix
from common.os_utils import getCoverName
from mutagen import File, FileType
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4


class AlbumCoverReaderBase:
    """ Album cover reader base class """

    @staticmethod
    def getAlbumCover(audio: FileType) -> bytes:
        """ extract binary data of album cover from audio file

        Parameters
        ----------
        audio: FileType
            audio tag instance

        Returns
        -------
        picData: bytes
            binary data of album cover, `None` if no cover is found
        """
        raise NotImplementedError


class MP3AlbumCoverReader(AlbumCoverReaderBase):
    """ MP3 album cover reader """

    @staticmethod
    def getAlbumCover(audio: MP3) -> bytes:
        for k in audio.tags.keys():
            if k.startswith("APIC"):
                return audio[k].data


class FLACAlbumCoverReader(AlbumCoverReaderBase):
    """ FLAC album cover reader """

    @staticmethod
    def getAlbumCover(audio: FLAC) -> bytes:
        if not audio.pictures:
            return None

        return audio.pictures[0].data


class MP4AlbumCoverReader(AlbumCoverReaderBase):
    """ MP4/M4A album cover reader """

    @staticmethod
    def getAlbumCover(audio: MP4) -> bytes:
        if not audio.get("covr"):
            return None

        return bytes(audio["covr"][0])


class AlbumCoverReader:
    """ Read and save album cover class """

    coverFolder = Path("cache/Album_Cover")

    @classmethod
    def getAlbumCovers(cls, songInfos: List[SongInfo]):
        """ Read and save album covers from audio files """
        cls.coverFolder.mkdir(exist_ok=True, parents=True)
        for songInfo in songInfos:
            cls.getAlbumCover(songInfo)

    @classmethod
    def getAlbumCover(cls, songInfo: SongInfo):
        """ Read and save an album cover from audio file """
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
        """ Check whether the cover exists

        Parameters
        ----------
        singer: str
            singer name

        album: str
            album name

        Returns
        -------
        isExists: bool
            whether the cover exists
        """
        folder = cls.coverFolder / getCoverName(singer, album)

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
        """ save album cover

        Parameters
        ----------
        singer: str
            singer name

        album: str
            album name

        picData: bytes
            binary data of album cover
        """
        folder = cls.coverFolder / getCoverName(singer, album)
        folder.mkdir(exist_ok=True, parents=True)

        suffix = getPicSuffix(picData)
        with open(folder/("cover" + suffix), "wb") as f:
            f.write(picData)
