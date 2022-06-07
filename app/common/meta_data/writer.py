# coding:utf-8
import base64
import os
from pathlib import Path
from typing import Union

from common.database.entity import SongInfo
from common.image_process_utils import getPicMimeType
from common.logger import Logger
from mutagen import File
from mutagen.aac import AAC
from mutagen.apev2 import APEv2
from mutagen.aiff import AIFF
from mutagen.apev2 import APEBinaryValue, APETextValue
from mutagen.flac import FLAC, Picture
from mutagen.id3 import (APIC, ID3, TALB, TCON, TDRC, TIT2, TPE1, TPE2, TPOS,
                         TRCK)
from mutagen.monkeysaudio import MonkeysAudio
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.oggflac import OggFLAC
from mutagen.oggopus import OggOpus
from mutagen.oggspeex import OggSpeex
from mutagen.oggvorbis import OggVorbis


class MetaDataWriterBase:
    """ Song meta data writer base class """

    formats = []
    options = []

    def __init__(self, file: Union[str, Path]):
        """
        Parameters
        ----------
        file: str or Path
            audio file path
        """
        self.audio = File(file, options=self.options)

    @classmethod
    def canWrite(cls, file: Union[str, Path]):
        """ determine whether information can be written to the file """
        return str(file).lower().endswith(tuple(cls.formats))

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
        raise NotImplementedError

    def writeAlbumCover(self, file: Union[Path, str], picData: bytes, mimeType: str):
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


logger = Logger('meta_data_writer')


def saveExceptionHandler(func):

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(e)
            return False

    return wrapper


class ID3Writer(MetaDataWriterBase):
    """ ID3 meta data writer class """

    formats = [".mp3", ".aiff"]
    options = [MP3, AIFF]

    @saveExceptionHandler
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

        self.audio.save(songInfo.file)
        return True

    @saveExceptionHandler
    def writeAlbumCover(self, file: Union[Path, str], picData: bytes, mimeType: str):
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

        self.audio.save(file)
        return True


class PureID3Writer(ID3Writer):
    """ Pure ID3 meta data writer """

    formats = [".aac"]
    options = [AAC]

    def __init__(self, file: Union[str, Path]):
        self.audio = ID3()
        try:
            self.audio.load(file)
        except:
            pass


class FLACWriter(MetaDataWriterBase):
    """ FLAC meta data writer class """

    formats = [".flac"]
    options = [FLAC]

    @saveExceptionHandler
    def writeSongInfo(self, songInfo: SongInfo):
        self.audio['title'] = songInfo.title
        self.audio['artist'] = songInfo.singer
        self.audio['album'] = songInfo.album
        self.audio['genre'] = songInfo.genre
        if songInfo.disc:
            self.audio['discnumber'] = str(songInfo.disc)
            self.audio['tracknumber'] = str(songInfo.track)
        if songInfo.year:
            self.audio['year'] = str(songInfo.year)

        self.audio.save(songInfo.file)
        return True

    @saveExceptionHandler
    def writeAlbumCover(self, file: Union[Path, str], picData: bytes, mimeType: str):
        picture = Picture()
        picture.mime = mimeType
        picture.data = picData
        picture.type = 0
        self.audio.clear_pictures()
        self.audio.add_picture(picture)
        self.audio.save(file)
        return True


class OGGWriter(MetaDataWriterBase):
    """ Ogg/Opus meta data writer class """

    formats = [".ogg", ".opus"]
    options = [OggVorbis, OggFLAC, OggSpeex, OggOpus]

    @saveExceptionHandler
    def writeSongInfo(self, songInfo: SongInfo):
        self.audio['title'] = [songInfo.title]
        self.audio['artist'] = [songInfo.singer]
        self.audio['album'] = [songInfo.album]
        self.audio['genre'] = [songInfo.genre]
        if songInfo.disc:
            self.audio['discnumber'] = [str(songInfo.disc)]
            self.audio['tracknumber'] = [str(songInfo.track)]
        if songInfo.year:
            self.audio['year'] = [str(songInfo.year)]
            self.audio['date'] = [str(songInfo.year)]

        self.audio.save(songInfo.file)
        return True

    @saveExceptionHandler
    def writeAlbumCover(self, file: Union[Path, str], picData: bytes, mimeType: str):
        picture = Picture()
        picture.mime = mimeType
        picture.data = picData
        picture.type = 3

        picData = picture.write()
        picData = base64.b64encode(picData).decode("ascii")

        self.audio["metadata_block_picture"] = [picData]
        self.audio.save(file)
        return True


class MP4Writer(MetaDataWriterBase):
    """ MP4/M4A meta data writer class """

    formats = [".m4a", ".mp4"]
    options = [MP4]

    @saveExceptionHandler
    def writeSongInfo(self, songInfo: SongInfo):
        # write track number
        trackTotal = max(songInfo.track, songInfo.trackTotal)
        self.audio['trkn'] = [(songInfo.track, trackTotal)]

        # writer disc
        if songInfo.disc:
            discTotal = max(songInfo.disc, songInfo.discTotal)
            self.audio['disk'] = [(songInfo.disc, discTotal)]

        self.audio['©nam'] = songInfo.title
        self.audio['©ART'] = songInfo.singer
        self.audio['aART'] = songInfo.singer
        self.audio['©alb'] = songInfo.album
        self.audio['©gen'] = songInfo.genre

        if songInfo.year:
            self.audio['©day'] = str(songInfo.year)

        self.audio.save(songInfo.file)
        return True

    @saveExceptionHandler
    def writeAlbumCover(self, file: Union[Path, str], picData: bytes, mimeType: str):
        self.audio['covr'] = [picData]
        self.audio.save(file)
        return True


class APEWriter(MetaDataWriterBase):
    """ APE meta data writer """

    formats = [".ape"]
    options = [MonkeysAudio]

    @saveExceptionHandler
    def writeSongInfo(self, songInfo: SongInfo):
        self.audio['Title'] = APETextValue(songInfo.title)
        self.audio['Artist'] = APETextValue(songInfo.singer)
        self.audio['Album'] = APETextValue(songInfo.album)
        self.audio['Genre'] = APETextValue(songInfo.genre)
        self.audio['Track'] = APETextValue(str(songInfo.track))
        if songInfo.disc:
            self.audio['Disc'] = APETextValue(str(songInfo.disc))
        if songInfo.year:
            self.audio['Year'] = APETextValue(str(songInfo.year))

        self.audio.save(songInfo.file)
        return True

    @saveExceptionHandler
    def writeAlbumCover(self, file: Union[Path, str], picData: bytes, mimeType: str):
        self.audio['Cover Art (Front)'] = APEBinaryValue(picData)
        self.audio.save(file)
        return True


class PureAPEWriter(APEWriter):
    """ Pure APEv2 meta data writer """

    formats = [".ac3"]
    options = [APEv2]

    def __init__(self, file: Union[str, Path]):
        self.audio = APEv2()
        try:
            self.audio.load(file)
        except:
            pass


class MetaDataWriter:
    """ Meta data writer """

    writers = [
        ID3Writer, FLACWriter, MP4Writer,
        OGGWriter, PureID3Writer, APEWriter,
        PureAPEWriter
    ]

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
        for Writer in self.writers:
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
        for Writer in self.writers:
            if Writer.canWrite(file):
                return Writer(file).writeAlbumCover(file, picData, mimeType)

        logger.info(f'The format of {file} is not supported')
        return False
