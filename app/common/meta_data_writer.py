# coding:utf-8
import imghdr
import os

from mutagen import File, MutagenError
from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, TALB, TCON, TDRC, TIT2, TPE1, TPE2, TRCK
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from tinytag import TinyTag


def writeSongInfo(songInfo: dict) -> bool:
    """ 从字典中读取信息并写入歌曲的标签卡信息

    Parameters
    ----------
    songInfo: dict
        歌曲信息

    Returns
    -------
    isWriteOk: bool
        是否成功写入
    """
    id_card = File(songInfo['songPath'])

    if isinstance(id_card, MP3):
        id_card['TRCK'] = TRCK(encoding=3, text=songInfo['tracknumber'])
        id_card['TIT2'] = TIT2(encoding=3, text=songInfo['songName'])
        id_card['TDRC'] = TDRC(encoding=3, text=songInfo['year'][:4])
        id_card['TPE1'] = TPE1(encoding=3, text=songInfo['singer'])
        id_card['TPE2'] = TPE2(encoding=3, text=songInfo['singer'])
        id_card['TALB'] = TALB(encoding=3, text=songInfo['album'])
        id_card['TCON'] = TCON(encoding=3, text=songInfo['genre'])

    elif isinstance(id_card, FLAC):
        id_card['tracknumber'] = songInfo['tracknumber']
        id_card['title'] = songInfo['songName']
        id_card['year'] = songInfo['year'][:4]
        id_card['artist'] = songInfo['singer']
        id_card['album'] = songInfo['album']
        id_card['genre'] = songInfo['genre']

    elif isinstance(id_card, MP4):
        # m4a写入曲目时还需要指定总曲目数
        tag = TinyTag.get(id_card.filename)
        trackNum = int(songInfo['tracknumber'])
        trackTotal = 1 if not tag.track_total else int(tag.track_total)
        trackTotal = max(trackNum, trackTotal)
        id_card['trkn'] = [(trackNum, trackTotal)]
        id_card['©nam'] = songInfo['songName']
        id_card['©day'] = songInfo['year'][:4]
        id_card['©ART'] = songInfo['singer']
        id_card['aART'] = songInfo['singer']
        id_card['©alb'] = songInfo['album']
        id_card['©gen'] = songInfo['genre']

    try:
        id_card.save()
        return True
    except MutagenError:
        return False


def writeAlbumCover(songPath: str, coverPath: str, picData=None) -> bool:
    """ 给音频文件写入封面

    Parameters
    ----------
    songPath : str
        音频文件路径

    coverPath : str
        封面图片路径

    picData : str
        封面图片二进制数据

    Returns
    -------
    isWriteOk: bool
        是否成功写入
    """
    if not os.path.exists(coverPath) and not picData:
        return

    # 读取封面数据
    if not picData:
        with open(coverPath, 'rb') as f:
            picData = f.read()

    id_card = File(songPath)

    # 获取图片数据后缀名
    try:
        picSuffix = imghdr.what(None, picData)
    except:
        picSuffix = 'jpeg'
    mimeType = 'image/' + picSuffix

    # 开始写入封面
    if isinstance(id_card, MP3):
        keyName = 'APIC:'
        keyName_list = []
        # 获取可能已经存在的封面键名
        for key in id_card.tags.keys():
            if key.startswith('APIC'):
                keyName = key
                keyName_list.append(key)
        # 弹出所有旧标签才能写入新数据
        for key in keyName_list:
            id_card.pop(key)
        id_card[keyName] = APIC(encoding=0,
                                mime=mimeType,
                                type=3,
                                desc='',
                                data=picData)

    elif isinstance(id_card, FLAC):
        # 创建Picture实例
        picture = Picture()
        # 设置属性值
        picture.mime = mimeType
        picture.data = picData
        picture.type = 0
        # 清除原来的图片数据
        id_card.clear_pictures()
        # 添加图片
        id_card.add_picture(picture)

    elif isinstance(id_card, MP4):
        try:
            id_card['covr'][0] = picData
        except:
            id_card['covr'] = [picData]  # 没有键时需要创建一个

    try:
        id_card.save()
        return True
    except:
        return False

