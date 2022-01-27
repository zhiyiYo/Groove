# coding:utf-8
import imghdr
import os
from pathlib import Path
from typing import Union

from common.database.entity import SongInfo
from mutagen import File, MutagenError
from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, TALB, TCON, TDRC, TIT2, TPE1, TPE2, TPOS, TRCK
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4


class MetaDataWriter:
    """ 元数据写入器基类 """

    def __init__(self, songPath: Union[str, Path]):
        """
        Parameters
        ----------
        songPath: str or Path
            音频文件路径
        """
        self.audio = None

    def writeSongInfo(self, songInfo: SongInfo):
        """ 写入歌曲信息

        Parameters
        ----------
        songInfo: SongInfo
            歌曲信息字典

        Returns
        -------
        success: bool
            写入是否成功
        """
        raise NotImplementedError

    def writeAlbumCover(self, picData: bytes, mimeType: str):
        """ 写入专辑封面

        Parameters
        ----------
        picData:
            封面二进制数据

        mimeData: str
            图片数据类型，比如 `image/jpeg`、`image/png`

        Returns
        -------
        success: bool
            写入是否成功
        """
        raise NotImplementedError


def saveExceptionHandler(func):

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MutagenError as e:
            print(e)
            return False

    return wrapper


class MP3Writer(MetaDataWriter):
    """ MP3 元数据写入器 """

    def __init__(self, songPath: Union[str, Path]):
        self.audio = MP3(songPath)

    @saveExceptionHandler
    def writeSongInfo(self, songInfo: SongInfo):
        self.audio['TIT2'] = TIT2(encoding=3, text=songInfo.title)
        self.audio['TPE1'] = TPE1(encoding=3, text=songInfo.singer)
        self.audio['TPE2'] = TPE2(encoding=3, text=songInfo.singer)
        self.audio['TALB'] = TALB(encoding=3, text=songInfo.album)
        self.audio['TCON'] = TCON(encoding=3, text=songInfo.genre)
        self.audio['TPOS'] = TPOS(encoding=3, text=str(songInfo.disc))
        self.audio['TRCK'] = TRCK(encoding=3, text=str(songInfo.track))
        if songInfo.year:
            self.audio['TDRC'] = TDRC(encoding=3, text=str(songInfo.year))

        self.audio.save()
        return True

    @saveExceptionHandler
    def writeAlbumCover(self, picData: bytes, mimeType: str):
        keyName = 'APIC:'
        keyNames = []

        # 获取可能已经存在的封面键名
        for key in self.audio.tags.keys():
            if key.startswith('APIC'):
                keyName = key
                keyNames.append(key)

        # 弹出所有旧标签才能写入新数据
        for key in keyNames:
            self.audio.pop(key)

        self.audio[keyName] = APIC(
            encoding=0, mime=mimeType, type=3, desc='', data=picData)

        self.audio.save()
        return True


class FLACWriter(MetaDataWriter):
    """ FLAC 元数据写入器 """

    def __init__(self, songPath: Union[str, Path]):
        self.audio = FLAC(songPath)

    @saveExceptionHandler
    def writeSongInfo(self, songInfo: SongInfo):
        self.audio['title'] = songInfo.title
        self.audio['artist'] = songInfo.singer
        self.audio['album'] = songInfo.album
        self.audio['genre'] = songInfo.genre
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


class MP4Writer(MetaDataWriter):
    """ MP4/M4A 元数据写入器 """

    def __init__(self, songPath: Union[str, Path]):
        self.audio = MP4(songPath)

    @saveExceptionHandler
    def writeSongInfo(self, songInfo: SongInfo):
        # 写入曲目
        trackTotal = max(songInfo.track, songInfo.trackTotal)
        self.audio['trkn'] = [(songInfo.track, trackTotal)]

        # 写入光盘
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
    """ 从字典中读取信息并写入歌曲的标签卡信息

    Parameters
    ----------
    songInfo: SongInfo
        歌曲信息

    Returns
    -------
    success: bool
        是否成功写入
    """
    fileType = type(File(songInfo.file, options=[MP3, FLAC, MP4]))
    writerMap = {
        MP3: MP3Writer,
        FLAC: FLACWriter,
        MP4: MP4Writer
    }
    if fileType not in writerMap:
        print(f'{songInfo.file} 文件格式不支持')
        return False

    writer = writerMap[fileType](songInfo.file)  # type:MetaDataWriter
    return writer.writeSongInfo(songInfo)


def writeAlbumCover(songPath: Union[str, Path], coverPath: str, picData: bytes = None) -> bool:
    """ 给音频文件写入封面

    Parameters
    ----------
    songPath : str or Path
        音频文件路径

    coverPath : str
        封面图片路径

    picData : bytes
        封面图片二进制数据

    Returns
    -------
    success: bool
        是否成功写入
    """
    if not os.path.exists(coverPath) and not picData:
        return False

    # 读取封面数据
    if not picData:
        with open(coverPath, 'rb') as f:
            picData = f.read()

    # 获取图片数据类型
    try:
        mimeType = "image/" + imghdr.what(None, picData)
    except:
        mimeType = "image/jpeg"

    fileType = type(File(songPath, options=[MP3, FLAC, MP4]))
    writerMap = {
        MP3: MP3Writer,
        FLAC: FLACWriter,
        MP4: MP4Writer
    }
    if fileType not in writerMap:
        print(f'{songPath} 文件格式不支持')
        return False

    writer = writerMap[fileType](songPath)  # type:MetaDataWriter
    return writer.writeAlbumCover(picData, mimeType)