# coding:utf-8
import base64
from pathlib import Path
from shutil import rmtree
from typing import List, Union

from common.exception_handler import exceptionHandler
from common.cache import albumCoverFolder
from common.database.entity import SongInfo
from common.picture import Cover
from mutagen import File, FileType
from mutagen.aac import AAC
from mutagen.aiff import AIFF
from mutagen.apev2 import APEv2
from mutagen.asf import ASF, ASFByteArrayAttribute
from mutagen.flac import FLAC, Picture
from mutagen.flac import error as FLACError
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.oggflac import OggFLAC
from mutagen.oggopus import OggOpus
from mutagen.oggspeex import OggSpeex
from mutagen.oggvorbis import OggVorbis
from mutagen.trueaudio import TrueAudio
from mutagen.wave import WAVE


class AlbumCoverReader:
    """ Read and save album cover class """

    coverFolder = albumCoverFolder
    _readers = []

    @classmethod
    def register(cls, reader):
        """ register album cover reader

        Parameters
        ----------
        reader:
            album cover reader class
        """
        if reader not in cls._readers:
            cls._readers.append(reader)

        return reader

    @classmethod
    def getAlbumCovers(cls, songInfos: List[SongInfo]):
        """ Read and save album covers from audio files """
        cls.coverFolder.mkdir(exist_ok=True, parents=True)
        for songInfo in songInfos:
            cls.getAlbumCover(songInfo)

    @classmethod
    @exceptionHandler("meta_data_reader", False)
    def getAlbumCover(cls, songInfo: SongInfo) -> bool:
        """ Read and save an album cover from audio file """
        cls.coverFolder.mkdir(exist_ok=True, parents=True)

        cover = Cover(songInfo.singer, songInfo.album)
        if cover.isExists():
            return True

        # remove the dirty folder
        if cover.folder.exists():
            rmtree(cover.folder)

        file = songInfo.file
        if file.startswith('http'):
            return False

        for Reader in cls._readers:
            if not Reader.canRead(file):
                continue

            picData = Reader.read(file)
            if picData:
                cover.save(picData)
                return True

        return False


class CoverDataReaderBase:
    """ Album cover data reader base class """

    formats = []
    options = []

    @classmethod
    def canRead(cls, file: Union[Path, str]) -> bool:
        """ determine whether cover data of the file can be read """
        return str(file).lower().endswith(tuple(cls.formats))

    @classmethod
    def read(cls, audio: FileType) -> bytes:
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


@AlbumCoverReader.register
class ID3CoverDataReader(CoverDataReaderBase):
    """ MP3 album cover data reader """

    formats = [".mp3", ".aac", ".tta"]
    options = [MP3, AAC, TrueAudio]

    @classmethod
    def read(cls, file: Union[Path, str]) -> bytes:
        try:
            return cls._readFromTag(ID3(file))
        except:
            return None

    @classmethod
    def _readFromTag(cls, tag):
        """ read cover from tag """
        for k in tag.keys():
            if k.startswith("APIC"):
                return tag[k].data


@AlbumCoverReader.register
class FLACCoverDataReader(CoverDataReaderBase):
    """ FLAC album cover data reader """

    formats = [".flac"]
    options = [FLAC]

    @classmethod
    def read(cls, file: Union[Path, str]) -> bytes:
        audio = FLAC(file)
        if not audio.pictures:
            return None

        return audio.pictures[0].data


@AlbumCoverReader.register
class MP4CoverDataReader(CoverDataReaderBase):
    """ MP4/M4A album cover data reader """

    formats = [".m4a", ".mp4"]
    options = [MP4]

    @classmethod
    def read(cls, file: Union[Path, str]) -> bytes:
        audio = MP4(file)
        if not audio.get("covr"):
            return None

        return bytes(audio["covr"][0])


@AlbumCoverReader.register
class OGGCoverDataReader(CoverDataReaderBase):
    """ OGG album cover data reader """

    formats = [".ogg", ".opus"]
    options = [OggVorbis, OggFLAC, OggSpeex, OggOpus]

    @classmethod
    def read(cls, file: Union[Path, str]) -> bytes:
        audio = File(file, options=cls.options)
        for base64Data in audio.get("metadata_block_picture", []):
            try:
                return Picture(base64.b64decode(base64Data)).data
            except (TypeError, ValueError, FLACError):
                continue


@AlbumCoverReader.register
class SuperID3CoverDataReader(ID3CoverDataReader):
    """ Super ID3 album cover data reader """

    formats = [".aiff", ".wav"]
    options = [AIFF, WAVE]

    @classmethod
    def read(cls, file: Union[Path, str]) -> bytes:
        return cls._readFromTag(File(file, options=cls.options))


@AlbumCoverReader.register
class APECoverDataReader(CoverDataReaderBase):
    """ APEv2 album cover data reader """

    formats = [".ac3", ".ape", ".wv", ".mpc"]
    options = [APEv2]

    @classmethod
    def read(cls, file: Union[Path, str]) -> bytes:
        try:
            return cls._readFromTag(APEv2(file))
        except:
            return None

    @classmethod
    def _readFromTag(cls, tag):
        """ read cover from tag """
        picture = tag.get("Cover Art (Front)", None)
        if picture is None:
            return None

        return picture.value


@AlbumCoverReader.register
class ASFCoverDataReader(CoverDataReaderBase):
    """ ASF album cover data reader """

    formats = [".asf", ".wma"]
    options = [ASF]

    @classmethod
    def read(cls, file: Union[Path, str]) -> bytes:
        audio = ASF(file)
        picture = audio.get('WM/Picture')  # type:List[ASFByteArrayAttribute]
        if not picture:
            return None

        return picture[0].value
