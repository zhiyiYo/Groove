# coding:utf-8
import base64
import os
from pathlib import Path
from typing import List, Union

from common.database.entity import SongInfo
from common.image_utils import getPicMimeType
from common.logger import Logger
from mutagen import File
from mutagen.aac import AAC
from mutagen.aiff import AIFF
from mutagen.apev2 import APEBinaryValue, APETextValue, APEv2
from mutagen.asf import ASF, ASFByteArrayAttribute, ASFUnicodeAttribute
from mutagen.flac import FLAC, Picture
from mutagen.id3 import (APIC, ID3, TALB, TCON, TDRC, TIT2, TPE1, TPE2, TPOS,
                         TRCK)
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

from .frame_map import (APEV2_FRAME_MAP, ASF_FRAME_MAP, MP4_FRAME_MAP,
                        VORBIS_FRAME_MAP)

logger = Logger('meta_data_writer')


def save(func):
    """ Auto save tag decorator """

    def wrapper(writer, *args, **kwargs):
        try:
            func(writer, *args, **kwargs)
            writer.audio.save(writer.file)
            return True
        except Exception as e:
            logger.error(e)
            return False

    return wrapper


class MetaDataWriterBase:
    """ Song meta data writer base class """

    formats = []
    options = []
    _Tag = None
    frameMap = {}
    excludeFrames = ['trackTotal', "discTotal"]

    def __init__(self, file: Union[str, Path]):
        """
        Parameters
        ----------
        file: str or Path
            audio file path
        """
        self.file = file
        if not self._Tag:
            self.audio = File(file, options=self.options)
        else:
            try:
                self.audio = self._Tag(file)
            except:
                self.audio = self._Tag()

    @classmethod
    def canWrite(cls, file: Union[str, Path]):
        """ determine whether information can be written to the file """
        return str(file).lower().endswith(tuple(cls.formats))

    @save
    def writeSongInfo(self, songInfo: SongInfo):
        """ write song information

        Parameters
        ----------
        songInfo: SongInfo
            song information

        Returns
        -------
        success: bool
            whether write song information successfully
        """
        for k, value in self.frameMap.items():
            if not isinstance(value, list):
                value = [value]

            for v in value:
                if k not in self.excludeFrames and songInfo[k] is not None:
                    self.audio[v] = self._v(songInfo, k)

    def writeAlbumCover(self, picData: bytes, mimeType: str):
        """ write album cover

        Parameters
        ----------
        picData:
            binary data of album cover image

        mimeType: str
            image mime type, e.g. `image/jpeg`, `image/png`

        Returns
        -------
        success: bool
            whether write album cover successfully
        """
        raise NotImplementedError

    def _v(self, songInfo: SongInfo, key: str):
        """ get the value of frame """
        return str(songInfo[key])


class MetaDataWriter:
    """ Meta data writer """

    _writers = []  # type:List[MetaDataWriterBase]

    @classmethod
    def register(cls, writer):
        """ register meta data writer

        Parameters
        ----------
        writer:
            Meta data writer class
        """
        if writer not in cls._writers:
            cls._writers.append(writer)

        return writer

    def writeSongInfo(self, songInfo: SongInfo) -> bool:
        """ write song information

        Parameters
        ----------
        songInfo: SongInfo
            song information

        Returns
        -------
        success: bool
            whether write song information successfully
        """
        # select available writer to write song information
        file = songInfo.file
        for Writer in self._writers:
            if Writer.canWrite(file):
                return Writer(file).writeSongInfo(songInfo)

        logger.error(f'The format of `{songInfo.file}` is not supported')
        return False

    def writeAlbumCover(self, file: Union[str, Path], coverPath: str, picData: bytes = None) -> bool:
        """ write album cover

        Parameters
        ----------
        songPath : str or Path
            audio file path

        coverPath : str
            album cover path

        picData : bytes
            binary data of album cover image

        Returns
        -------
        success: bool
            whether write album cover successfully
        """
        if not os.path.exists(coverPath) and not picData:
            logger.error(
                f'Unable to read the data of `{coverPath}`, please check whether the cover path is correct.')
            return False

        # read binary data of album cover
        if not picData:
            with open(coverPath, 'rb') as f:
                picData = f.read()

        # select available writer to write album cover
        mimeType = getPicMimeType(picData)
        for Writer in self._writers:
            if Writer.canWrite(file):
                return Writer(file).writeAlbumCover(picData, mimeType)

        logger.info(f'The format of {file} is not supported')
        return False


@MetaDataWriter.register
class ID3Writer(MetaDataWriterBase):
    """ ID3 meta data writer class """

    formats = [".mp3", ".tta", ".aac"]
    options = [MP3, TrueAudio, AAC]
    _Tag = ID3

    @save
    def writeSongInfo(self, songInfo: SongInfo):
        self.audio['TIT2'] = TIT2(encoding=3, text=songInfo.title)
        self.audio['TPE1'] = TPE1(encoding=3, text=songInfo.singer)
        self.audio['TPE2'] = TPE2(encoding=3, text=songInfo.singer)
        self.audio['TALB'] = TALB(encoding=3, text=songInfo.album)
        self.audio['TCON'] = TCON(encoding=3, text=songInfo.genre)
        self.audio['TRCK'] = TRCK(encoding=3, text=str(songInfo.track))
        if songInfo.disc:
            self.audio['TPOS'] = TPOS(encoding=3, text=str(songInfo.disc))
        if songInfo.year:
            self.audio['TDRC'] = TDRC(encoding=3, text=str(songInfo.year))

    @save
    def writeAlbumCover(self, picData: bytes, mimeType: str):
        keyName = 'APIC:'
        keyNames = []

        # get cover keys which may already exist
        for key in self.audio.keys():
            if key.startswith('APIC'):
                keyName = key
                keyNames.append(key)

        # pop old cover keys to write new data
        for key in keyNames:
            self.audio.pop(key)

        self.audio[keyName] = APIC(
            encoding=0, mime=mimeType, type=3, desc='', data=picData)


@MetaDataWriter.register
class AIFFWriter(ID3Writer):
    """ AIFF meta data writer """

    formats = [".aiff"]
    options = [AIFF]
    _Tag = None


@MetaDataWriter.register
class WAVWriter(ID3Writer):
    """ Waveform meta data writer """

    formats = [".wav"]
    options = [WAVE]
    _Tag = None


@MetaDataWriter.register
class FLACWriter(MetaDataWriterBase):
    """ FLAC meta data writer class """

    formats = [".flac"]
    options = [FLAC]
    frameMap = VORBIS_FRAME_MAP
    excludeFrames = []

    @save
    def writeAlbumCover(self, picData: bytes, mimeType: str):
        picture = Picture()
        picture.mime = mimeType
        picture.data = picData
        picture.type = 0
        self.audio.clear_pictures()
        self.audio.add_picture(picture)


@MetaDataWriter.register
class OGGWriter(MetaDataWriterBase):
    """ Ogg/Opus meta data writer class """

    formats = [".ogg", ".opus"]
    options = [OggVorbis, OggFLAC, OggSpeex, OggOpus]
    frameMap = VORBIS_FRAME_MAP
    excludeFrames = []

    def _v(self, songInfo, key):
        return [str(songInfo[key])]

    @save
    def writeAlbumCover(self, picData: bytes, mimeType: str):
        picture = Picture()
        picture.mime = mimeType
        picture.data = picData
        picture.type = 3

        picData = picture.write()
        picData = base64.b64encode(picData).decode("ascii")

        self.audio["metadata_block_picture"] = [picData]


@MetaDataWriter.register
class MP4Writer(MetaDataWriterBase):
    """ MP4/M4A meta data writer class """

    formats = [".m4a", ".mp4"]
    options = [MP4]
    frameMap = MP4_FRAME_MAP

    def _v(self, songInfo, key):
        if key not in ['track', 'disc']:
            return str(songInfo[key])

        if key == "track":
            total = max(songInfo.track, songInfo.trackTotal)
        else:
            total = max(songInfo.disc, songInfo.discTotal)

        return [(songInfo[key], total)]

    @save
    def writeAlbumCover(self, picData: bytes, mimeType: str):
        self.audio['covr'] = [picData]


@MetaDataWriter.register
class APEWriter(MetaDataWriterBase):
    """ APEv2 meta data writer """

    formats = [".ape", ".ac3", ".wv", ".mpc"]
    options = [MonkeysAudio, AAC, WavPack, Musepack]
    _Tag = APEv2
    frameMap = APEV2_FRAME_MAP

    def _v(self, songInfo, key):
        return APETextValue(str(songInfo[key]))

    @save
    def writeAlbumCover(self, picData: bytes, mimeType: str):
        self.audio['Cover Art (Front)'] = APEBinaryValue(picData)


@MetaDataWriter.register
class ASFWriter(MetaDataWriterBase):
    """ ASF meta data writer """

    formats = [".asf", ".wma"]
    options = [ASF]
    frameMap = ASF_FRAME_MAP

    def _v(self, songInfo, key):
        return ASFUnicodeAttribute(str(songInfo[key]))

    @save
    def writeAlbumCover(self, picData: bytes, mimeType: str):
        self.audio['WM/Picture'] = ASFByteArrayAttribute(data=picData)
