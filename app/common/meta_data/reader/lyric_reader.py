# coding:utf-8
from pathlib import Path
from typing import List, Union

from common.lyric import Lyric
from common.exception_handler import exceptionHandler
from mutagen import File
from mutagen.aiff import AIFF
from mutagen.apev2 import APEv2
from mutagen.asf import ASF, ASFUnicodeAttribute
from mutagen.flac import FLAC
from mutagen.id3 import ID3, USLT
from mutagen.mp4 import MP4
from mutagen.oggflac import OggFLAC
from mutagen.oggopus import OggOpus
from mutagen.oggspeex import OggSpeex
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE


class LyricReader:
    """ Lyric reader """

    _readers = []  # type:List[LyricReaderBase]

    @classmethod
    def register(cls, reader):
        """ register lyric reader

        Parameters
        ----------
        reader:
            lyric reader class
        """
        if reader not in cls._readers:
            cls._readers.append(reader)

        return reader

    @classmethod
    @exceptionHandler("meta_data_reader", Lyric.new())
    def read(cls, file: Union[Path, str]) -> Lyric:
        """ read lyrics from audio file

        Parameters
        ----------
        file: str or Path
            audio file path

        Returns
        -------
        lyric: Lyric
            song lyrics
        """
        if str(file).startswith('http'):
            return Lyric.new()

        for reader in cls._readers:
            if reader.canRead(file):
                return reader.read(file)

        return Lyric.new()


class LyricReaderBase:
    """ Lyrics reader base class """

    formats = []

    @classmethod
    def canRead(cls, file: Union[Path, str]) -> bool:
        """ determine whether lyric data of the file can be read """
        return str(file).lower().endswith(tuple(cls.formats))

    @classmethod
    def read(cls, file: Union[Path, str]) -> Lyric:
        """ read lyrics from audio file

        Parameters
        ----------
        file: str or Path
            audio file path

        Returns
        -------
        lyric: Lyric
            song lyrics
        """
        raise NotImplementedError


@LyricReader.register
class ID3LyricReader(LyricReaderBase):
    """ MP3 lyric reader """

    formats = [".mp3", ".aac", ".tta"]

    @classmethod
    def read(cls, file: Union[Path, str]) -> Lyric:
        try:
            return cls._readFromTag(ID3(file))
        except:
            return Lyric.new()

    @classmethod
    def _readFromTag(cls, tag: ID3):
        """ read cover from tag """
        for k, v in tag.items():
            if k.upper().startswith("USLT"):
                return Lyric.parse(str(v))

        return Lyric.new()


@LyricReader.register
class SuperID3LyricReader(ID3LyricReader):
    """ Super ID3 album cover data reader """

    formats = [".aiff", ".wav"]
    options = [AIFF, WAVE]

    @classmethod
    def read(cls, file: Union[Path, str]):
        return cls._readFromTag(File(file, options=cls.options))


@LyricReader.register
class FLACLyricReader(LyricReaderBase):
    """ FLAC lyric reader """

    formats = [".flac", ".ogg", ".opus"]

    @classmethod
    def read(cls, file: Union[Path, str]):
        audio = File(file, options=[FLAC, OggVorbis,
                     OggFLAC, OggSpeex, OggOpus])
        if not audio.get("lyrics"):
            return Lyric.new()

        return Lyric.parse(audio["lyrics"][0])


@LyricReader.register
class MP4LyricReader(LyricReaderBase):
    """ MP4 lyric reader """

    formats = [".m4a", ".mp4"]

    @classmethod
    def read(cls, file: Union[Path, str]):
        audio = MP4(file)
        lyric = audio.get("©lyr") or audio.get("----:com.apple.iTunes:Lyrics")
        if not lyric:
            return Lyric.new()

        lyric = lyric[0]
        lyric = lyric if isinstance(lyric, str) else lyric.decode("utf-8")
        return Lyric.parse(lyric)


@LyricReader.register
class APECoverDataReader(LyricReaderBase):
    """ APEv2 lyric reader """

    formats = [".ac3", ".ape", ".wv", ".mpc"]

    @classmethod
    def read(cls, file: Union[Path, str]) -> bytes:
        tag = APEv2(file)
        if not tag.get("Lyrics"):
            return Lyric.new()

        return Lyric.parse(str(tag["Lyrics"]))


@LyricReader.register
class ASFLyricReader(LyricReaderBase):
    """ ASF lyric reader """

    formats = [".asf", ".wma"]

    @classmethod
    def read(cls, file: Union[Path, str]) -> Lyric:
        audio = ASF(file)
        lyric = audio.get("WM/Lyrics", [None])[0]  # type:ASFUnicodeAttribute
        if not lyric:
            return Lyric.new()

        return Lyric.parse(str(lyric.value))
