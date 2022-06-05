# coding:utf-8
import base64
import imghdr
import os
from pathlib import Path
from typing import Union

from common.database.entity import SongInfo
from common.logger import Logger
from mutagen import File, MutagenError
from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, TALB, TCON, TDRC, TIT2, TPE1, TPE2, TPOS, TRCK
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis


class MetaDataWriterBase:
    """ Song meta data writer base class """

    def __init__(self, songPath: Union[str, Path]):
        """
        Parameters
        ----------
        songPath: str or Path
            audio file path
        """
        self.audio = None

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


logger = Logger('meta_data_writer')


def saveExceptionHandler(func):

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MutagenError as e:
            logger.error(e)
            return False

    return wrapper


class MP3Writer(MetaDataWriterBase):
    """ MP3 meta data writer class """

    def __init__(self, songPath: Union[str, Path]):
        self.audio = MP3(songPath)

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

        self.audio.save()
        return True

    @saveExceptionHandler
    def writeAlbumCover(self, picData: bytes, mimeType: str):
        keyName = 'APIC:'
        keyNames = []

        # get cover keys which may already exist
        for key in self.audio.tags.keys():
            if key.startswith('APIC'):
                keyName = key
                keyNames.append(key)

        # pop old cover keys to write new data
        for key in keyNames:
            self.audio.pop(key)

        self.audio[keyName] = APIC(
            encoding=0, mime=mimeType, type=3, desc='', data=picData)

        self.audio.save()
        return True


class FLACWriter(MetaDataWriterBase):
    """ FLAC meta data writer class """

    def __init__(self, songPath: Union[str, Path]):
        self.audio = FLAC(songPath)

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

        self.audio.save()
        return True

    @saveExceptionHandler
    def writeAlbumCover(self, picData: bytes, mimeType: str):
        picture = Picture()
        picture.mime = mimeType
        picture.data = picData
        picture.type = 0
        self.audio.clear_pictures()
        self.audio.add_picture(picture)
        self.audio.save()
        return True


class OGGWriter(MetaDataWriterBase):
    """ OGG meta data writer class """

    def __init__(self, songPath: Union[str, Path]):
        self.audio = OggVorbis(songPath)

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

        self.audio.save()
        return True

    @saveExceptionHandler
    def writeAlbumCover(self, picData: bytes, mimeType: str):
        picture = Picture()
        picture.mime = mimeType
        picture.data = picData
        picture.type = 3

        picData = picture.write()
        picData = base64.b64encode(picData).decode("ascii")

        self.audio["metadata_block_picture"] = [picData]
        self.audio.save()
        return True


class MP4Writer(MetaDataWriterBase):
    """ MP4/M4A meta data writer class """

    def __init__(self, songPath: Union[str, Path]):
        self.audio = MP4(songPath)

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

        self.audio.save()
        return True

    @saveExceptionHandler
    def writeAlbumCover(self, picData: bytes, mimeType: str):
        self.audio['covr'] = [picData]
        self.audio.save()
        return True


def writeSongInfo(songInfo: SongInfo) -> bool:
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
    fileType = type(File(songInfo.file, options=[MP3, FLAC, MP4, OggVorbis]))
    writerMap = {
        MP3: MP3Writer,
        FLAC: FLACWriter,
        MP4: MP4Writer,
        OggVorbis: OGGWriter
    }
    if fileType not in writerMap:
        logger.info(f'The format of {songInfo.file} is not supported')
        return False

    writer = writerMap[fileType](songInfo.file)  # type:MetaDataWriterBase
    return writer.writeSongInfo(songInfo)


def writeAlbumCover(songPath: Union[str, Path], coverPath: str, picData: bytes = None) -> bool:
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
        return False

    # read binary data of album cover
    if not picData:
        with open(coverPath, 'rb') as f:
            picData = f.read()

    # determine the mime type of binary data
    try:
        mimeType = "image/" + imghdr.what(None, picData)
    except:
        mimeType = "image/jpeg"

    fileType = type(File(songPath, options=[MP3, FLAC, MP4, OggVorbis]))
    writerMap = {
        MP3: MP3Writer,
        FLAC: FLACWriter,
        MP4: MP4Writer,
        OggVorbis: OGGWriter
    }
    if fileType not in writerMap:
        logger.info(f'The format of {songPath} is not supported')
        return False

    writer = writerMap[fileType](songPath)  # type:MetaDataWriterBase
    return writer.writeAlbumCover(picData, mimeType)
