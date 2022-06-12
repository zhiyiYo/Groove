# coding:utf-8
from pathlib import Path
from typing import Union

from common.database.entity import SongInfo
from common.logger import Logger
from mutagen import File
from mutagen.aac import AAC
from mutagen.ac3 import AC3
from mutagen.aiff import AIFF
from mutagen.apev2 import APEv2
from mutagen.asf import ASF, ASFUnicodeAttribute
from mutagen.flac import FLAC
from mutagen.id3 import ID3
from mutagen.monkeysaudio import MonkeysAudio
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.musepack import Musepack
from mutagen.oggflac import OggFLAC
from mutagen.oggopus import OggOpus
from mutagen.oggspeex import OggSpeex
from mutagen.oggvorbis import OggVorbis
from mutagen.trueaudio import TrueAudio
from mutagen.wave import WAVE
from mutagen.wavpack import WavPack
from PyQt5.QtCore import QObject
from tinytag import TinyTag

from ..frame_map import (APEV2_FRAME_MAP, ASF_FRAME_MAP, ID3_FRAME_MAP,
                         VORBIS_FRAME_MAP)

logger = Logger("meta_data_reader")


def exceptionHandler(func):
    """ decorator for exception handling

    Parameters
    ----------
    *default:
        the default value returned when an exception occurs
    """

    def wrapper(reader, *args, **kwargs):
        try:
            return func(reader, *args, **kwargs)
        except Exception as e:
            logger.error(e)
            return SongInfoReaderBase().read(*args, **kwargs)

    return wrapper


class SongInfoReaderBase(QObject):
    """ Song information reader base class """

    formats = []
    options = []

    def __init__(self):
        super().__init__()
        # default values of song information
        self.singer = self.tr('Unknown artist')
        self.album = self.tr("Unknown album")
        self.genre = self.tr("Unknown genre")
        self.year = None
        self.track = 0
        self.trackTotal = 1
        self.disc = 1
        self.discTotal = 1

    @classmethod
    def canRead(cls, file: Union[str, Path]) -> bool:
        """ determine whether song information of the file can be read """
        if not isinstance(file, Path):
            file = Path(file)

        return file.suffix.lower() in cls.formats

    def read(self, file: Union[str, Path]) -> SongInfo:
        """ read song information from audio file

        Parameters
        ----------
        file: str or Path
            audio file path

        Returns
        -------
        songInfo: SongInfo
            song information
        """
        if not isinstance(file, Path):
            file = Path(file)

        return SongInfo(
            file=str(file).replace('\\', '/'),
            title=file.stem,
            singer=self.singer,
            album=self.album,
            genre=self.genre,
            duration=0,
            track=self.track,
            trackTotal=self.trackTotal,
            disc=self.disc,
            discTotal=self.discTotal,
            createTime=int(file.stat().st_ctime),
            modifiedTime=int(file.stat().st_mtime)
        )

    def _parseTrack(self, track):
        """ parse track number """
        track = str(track)
        if not track:
            return self.track

        # handle a/b
        track = track.split('/')[0]

        # handle An
        if track[0].upper() == 'A':
            track = track[1:]

        return int(track)

    @staticmethod
    def getModifiedTime(file: str):
        """ get modified time of audio file """
        path = Path(file)
        return int(path.stat().st_mtime)


class SongInfoReader(SongInfoReaderBase):
    """ Song information reader """

    readers = []

    @classmethod
    def register(cls, reader):
        """ register song information reader

        Parameters
        ----------
        reader:
            song information reader class
        """
        if reader not in cls.readers:
            # shouldn't instantiate directly, or tr() will not work
            cls.readers.append(reader)

        return reader

    def read(self, file: Union[str, Path]) -> SongInfo:
        if not isinstance(file, Path):
            file = Path(file)

        for reader in self.readers:
            if reader.canRead(file):
                return reader().read(file)

        logger.warning(f"No song information reader available for `{file}`")
        return super().read(file)


@SongInfoReader.register
class GeneralSongInfoReader(SongInfoReaderBase):
    """ General song information reader """

    formats = [".mp3", ".flac", ".m4a", ".mp4", ".aiff"]
    options = [MP3, FLAC, MP4, AIFF]

    @exceptionHandler
    def read(self, file: Union[str, Path]):
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
        track = self._parseTrack(tag.track or self.track)
        trackTotal = int(tag.track_total or self.trackTotal)
        disc = int(tag.disc or self.disc)
        discTotal = int(tag.disc_total or self.discTotal)
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
        """ get release year of song """
        if tag.year and tag.year[0] != '0':
            return int(tag.year[:4])

        audio = File(file, self.options)

        if isinstance(audio, (MP3, AIFF)):
            year = [str(audio.get("TDRC", 0))]
        elif isinstance(audio, MP4):
            year = audio.get('©day', ['0'])
        elif isinstance(audio, FLAC):
            year = audio.get('year', ['0'])
        else:
            year = ['0']

        if year and year[0] != '0':
            return int(year[0][:4])

        return self.year


class MutagenSongInfoReader(SongInfoReaderBase):
    """ Mutagen song information reader """

    _Tag = None
    frameMap = {
        "title": "title",
        "singer": "artist",
        "album": "album",
        "year": "year",
        "genre": "genre",
        "track": "tracknumber",
        "trackTotal": "tracktotal",
        "disc": "discnumber",
        "discTotal": "discTotal"
    }

    @exceptionHandler
    def read(self, file: Union[str, Path]) -> SongInfo:
        if not isinstance(file, Path):
            file = Path(file)

        audio = File(file, self.options)
        if self._Tag is not None:
            try:
                tag = self._Tag(file)
            except:
                tag = self._Tag()
        else:
            tag = audio

        file_ = str(file).replace('\\', '/')
        title = self._v(tag, self.frameMap['title'], file.stem)
        singer = self._v(tag, self.frameMap['singer'], self.singer)
        album = self._v(tag, self.frameMap['album'], self.album)
        genre = self._v(tag, self.frameMap['genre'], self.genre)
        track = self._v(tag, self.frameMap['track'], self.track)
        track = self._parseTrack(track)
        trackTotal = self._v(tag, self.frameMap['trackTotal'], self.trackTotal)
        trackTotal = self._parseTrack(trackTotal)
        disc = int(self._v(tag, self.frameMap['disc'], self.trackTotal))
        discTotal = int(
            self._v(tag, self.frameMap['discTotal'], self.trackTotal))
        duration = int(audio.info.length)
        createTime = int(file.stat().st_ctime)
        modifiedTime = int(file.stat().st_mtime)

        year = None
        if isinstance(self.frameMap['year'], list):
            for k in self.frameMap['year']:
                year = year or self._v(tag, k)
        else:
            year = self._v(tag, self.frameMap['year'])

        year = int(year) if year and str(year).isdigit() else self.year

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

    def _v(self, tag, key: str, default=None):
        """ get the value of frame """
        v = tag.get(key)
        return str(v) if v else str(default)


@SongInfoReader.register
class OGGSongInfoReader(MutagenSongInfoReader):
    """ Ogg song information reader """

    formats = [".ogg"]
    options = [OggVorbis, OggFLAC, OggSpeex]
    frameMap = VORBIS_FRAME_MAP

    def _v(self, tag, key, default=None):
        v = tag.get(key, [None])[0]
        return v or default


@SongInfoReader.register
class OPUSSongInfoReader(OGGSongInfoReader):
    """ Opus song information reader """

    formats = [".opus"]
    options = [OggOpus]


@SongInfoReader.register
class ID3SongInfoReader(MutagenSongInfoReader):
    """ ID3 song information reader """

    formats = [".aac"]
    options = [AAC]
    _Tag = ID3
    frameMap = ID3_FRAME_MAP


@SongInfoReader.register
class TrueAudioSongInfoReader(ID3SongInfoReader):
    """ True audio song information reader """

    formats = [".tta"]
    options = [TrueAudio]
    _Tag = None


@SongInfoReader.register
class WAVSongInfoReader(ID3SongInfoReader):
    """ Waveform song information reader """

    formats = [".wav"]
    options = [WAVE]
    _Tag = None


@SongInfoReader.register
class APESongInfoReader(MutagenSongInfoReader):
    """ APEv2 song information reader """

    formats = [".ac3"]
    options = [AC3]
    _Tag = APEv2
    frameMap = APEV2_FRAME_MAP


@SongInfoReader.register
class MonkeysAudioSongInfoReader(APESongInfoReader):
    """ Monkey's Audio song information reader """

    formats = [".ape"]
    options = [MonkeysAudio]
    _Tag = None


@SongInfoReader.register
class MusepackAudioSongInfoReader(APESongInfoReader):
    """ Musepack Audio song information reader """

    formats = [".mpc"]
    options = [Musepack]
    _Tag = None


@SongInfoReader.register
class WavPackSongInfoReader(APESongInfoReader):
    """ WavPack song information reader """

    formats = [".wv"]
    options = [WavPack]
    _Tag = None


@SongInfoReader.register
class ASFSongInfoReader(MutagenSongInfoReader):
    """ ASF song information reader """

    formats = [".asf", ".wma"]
    options = [ASF]
    frameMap = ASF_FRAME_MAP

    def _v(self, tag, key, default=None):
        v = tag.get(key, [None])[0]  # type:ASFUnicodeAttribute

        if v and not v.value or v is None:
            return str(default)

        return str(v)
