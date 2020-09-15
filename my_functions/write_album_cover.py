# coding:utf-8

import imghdr

from mutagen import File
from mutagen.id3 import APIC
from mutagen.flac import Picture


def writeAlbumCover(songPath: str, coverPath: str, picData=None):
    """ 给音频文件写入封面
    Parameters
    ----------
    songPath: 音频文件路径\n
    coverPath: 封面图片路径\n
    picData: 封面图片二进制数据
    """
    id_card = File(songPath)
    # 读取封面数据
    if not picData:
        with open(coverPath, 'rb') as f:
            picData = f.read()
    # 获取音频数据和图片数据后缀名
    audioSuffix = id_card.mime[0].split('/')[-1]
    try:
        picSuffix = imghdr.what(None, picData)
    except:
        picSuffix = 'jpeg'
    mimeType = 'image/' + picSuffix
    # 开始写入封面
    if audioSuffix == 'mp3':
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
    elif audioSuffix == 'flac':
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
    elif audioSuffix == 'mp4':
        try:
            id_card['covr'][0] = picData
        except:
            id_card['covr'] = [picData]  # 没有键时需要创建一个
    id_card.save()
