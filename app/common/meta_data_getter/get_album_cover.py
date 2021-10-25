# coding:utf-8
import os
from shutil import rmtree

from mutagen import File
from mutagen.m4a import M4A
from mutagen.mp4 import MP4
from mutagen.mp3 import MP3
from mutagen.flac import FLAC

from common.image_process_utils import getPicSuffix


class AlbumCoverGetter:
    """ 获取专辑封面的类 """

    coverFolder = "Album_Cover"

    def __init__(self, songInfo_list: list):
        """
        Parameters
        ----------
        songInfo_list: list
            歌曲文件夹路径列表
        """
        self.songInfo_list = songInfo_list
        self.getAlbumCover(songInfo_list)

    def updateAlbumCover(self, songInfo_list: list):
        """ 重新扫描指定的文件下的音频文件的专辑封面 """
        self.songInfo_list = songInfo_list
        self.getAlbumCover(songInfo_list)

    @classmethod
    def getAlbumCover(cls, songInfo_list: list):
        """ 获取多张专辑封面 """
        os.makedirs(cls.coverFolder, exist_ok=True)
        for songInfo in songInfo_list:
            cls.getOneAlbumCover(songInfo)

    @classmethod
    def getOneAlbumCover(cls, songInfo: dict):
        """ 获取一张专辑封面 """
        isPicExist, subAlbumFolder = cls.__isPicExist(songInfo)
        if isPicExist:
            return

        id_card = File(songInfo["songPath"])

        if isinstance(id_card, MP3):
            cls.__getMp3AlbumCover(id_card, songInfo, subAlbumFolder)
        elif isinstance(id_card, FLAC):
            cls.__getFlacAlbumCover(id_card, songInfo, subAlbumFolder)
        elif isinstance(id_card, M4A) or isinstance(id_card, MP4):
            cls.__getM4aAlbumCover(id_card, songInfo, subAlbumFolder)

    @classmethod
    def __getMp3AlbumCover(cls, id_card: MP3, songInfo: dict, subAlbumFolder: str):
        """ 获取mp3文件的封面并写入文件夹 """
        for key in id_card.tags.keys():
            if key.startswith("APIC"):
                # 如果不存在专辑对应的目录,就新建一个并写入专辑封面
                os.mkdir(subAlbumFolder)
                # 提取封面数据
                pic_data = id_card[key].data
                cls.__savePic(subAlbumFolder, songInfo, pic_data)
                break
        else:
            # 没有提取到封面时也创建一个空文件夹
            os.mkdir(subAlbumFolder)

    @classmethod
    def __getFlacAlbumCover(cls, id_card: FLAC, songInfo: dict, subAlbumFolder: str):
        """ 获取flac文件的封面并写入文件夹 """
        if id_card.pictures:
            # 如果不存在专辑对应的目录,就新建一个并写入专辑封面
            os.mkdir(subAlbumFolder)
            # 提取封面数据
            pic_data = id_card.pictures[0].data
            cls.__savePic(subAlbumFolder, songInfo, pic_data)

    @classmethod
    def __getM4aAlbumCover(cls, id_card: M4A, songInfo: dict, subAlbumFolder: str):
        """ 获取m4a文件的封面 """
        if id_card.get("covr"):
            # 如果不存在专辑对应的目录,就新建一个并写入专辑封面
            os.mkdir(subAlbumFolder)
            # 提取封面数据
            pic_data = bytes(id_card["covr"][0])
            cls.__savePic(subAlbumFolder, songInfo, pic_data)

    @classmethod
    def __isPicExist(cls, songInfo: dict):
        """ 检测封面是否存在 """
        subAlbumFolder = os.path.join(
            cls.coverFolder, songInfo['coverName'])

        # 默认封面存在
        isPicExist = True
        if os.path.exists(subAlbumFolder):
            fileName_list = os.listdir(subAlbumFolder)
            if not fileName_list:
                # 如果目录为空说明封面不存在,直接删除旧文件夹
                isPicExist = False
                rmtree(subAlbumFolder)
            else:
                # 如果第一个文件不是图片也需要删除文件夹并重新提取封面
                suffix = os.path.splitext(fileName_list[0])[1][1:]
                if suffix.lower() not in ["png", "jpg", "jpeg", "jiff"]:
                    rmtree(subAlbumFolder)
                    isPicExist = False
        else:
            isPicExist = False

        return isPicExist, subAlbumFolder

    @staticmethod
    def __savePic(subAlbumFolder: str, songInfo: dict, pic_data):
        """ 储存提取到的专辑封面 """
        # 获取后缀名
        suffix = getPicSuffix(pic_data)
        # 封面路径
        pic_path = os.path.join(subAlbumFolder,
                                songInfo['coverName']+suffix)
        # 写入封面
        with open(pic_path, "wb") as f:
            f.write(pic_data)
