# coding:utf-8
import os
from shutil import rmtree

from mutagen import File
from mutagen.m4a import M4A
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
        suffix = songInfo["suffix"]
        if suffix == ".mp3":
            cls.getMp3AlbumCover(songInfo)
        elif suffix == ".flac":
            cls.getFlacAlbumCover(songInfo)
        elif suffix == ".m4a":
            cls.getM4aAlbumCover(songInfo)

    @classmethod
    def getMp3AlbumCover(cls, songInfo: dict):
        """ 获取mp3文件的封面并写入文件夹 """
        # 封面目录
        isPicExist, sub_album_cover_folder = cls.__isPicExist(songInfo)
        if isPicExist:
            return

        # 如果文件夹中不存在图片就扫描歌曲元数据来提取
        id_card = File(songInfo["songPath"])

        # 如果文件后缀名与实际类型不匹配就调用另一个函数
        if isinstance(id_card, FLAC):
            cls.getFlacAlbumCover(songInfo)
            return
        elif isinstance(id_card, M4A):
            cls.getM4aAlbumCover(songInfo)
            return

        for key in id_card.tags.keys():
            if key.startswith("APIC"):
                # 如果不存在专辑对应的目录,就新建一个并写入专辑封面
                os.mkdir(sub_album_cover_folder)
                # 提取封面数据
                pic_data = id_card[key].data
                cls.__savePic(sub_album_cover_folder, songInfo, pic_data)
                break
        else:
            # 没有提取到封面时也创建一个空文件夹
            os.mkdir(sub_album_cover_folder)

    @classmethod
    def getFlacAlbumCover(cls, songInfo: dict):
        """ 获取flac文件的封面并写入文件夹 """
        isPicExist, sub_album_cover_folder = cls.__isPicExist(songInfo)
        if isPicExist:
            return

        id_card = File(songInfo["songPath"])

        # 如果文件后缀名与实际类型不匹配就调用另一个函数
        if isinstance(id_card, M4A):
            cls.getM4aAlbumCover(songInfo)
            return
        elif isinstance(id_card, MP3):
            cls.getMp3AlbumCover(songInfo)
            return

        # 确认是否存在封面数据
        if id_card.pictures:
            # 如果不存在专辑对应的目录,就新建一个并写入专辑封面
            os.mkdir(sub_album_cover_folder)
            # 提取封面数据
            pic_data = id_card.pictures[0].data
            cls.__savePic(sub_album_cover_folder, songInfo, pic_data)

    @classmethod
    def getM4aAlbumCover(cls, songInfo: dict):
        """ 获取m4a文件的封面 """
        isPicExist, sub_album_cover_folder = cls.__isPicExist(songInfo)
        if isPicExist:
            return

        id_card = File(songInfo["songPath"])

        # 如果文件后缀名与实际类型不匹配就直接返回
        if isinstance(id_card, FLAC):
            cls.getFlacAlbumCover(songInfo)
            return
        elif isinstance(id_card, MP3):
            cls.getMp3AlbumCover(songInfo)
            return

        if id_card.get("covr"):
            # 如果不存在专辑对应的目录,就新建一个并写入专辑封面
            os.mkdir(sub_album_cover_folder)
            # 提取封面数据
            pic_data = bytes(id_card["covr"][0])
            cls.__savePic(sub_album_cover_folder, songInfo, pic_data)

    @classmethod
    def __isPicExist(cls, songInfo: dict):
        """ 检测封面是否存在 """
        sub_album_cover_folder = os.path.join(
            cls.coverFolder, songInfo['coverName'])
        # 默认封面存在
        isPicExist = True
        if os.path.exists(sub_album_cover_folder):
            fileName_list = os.listdir(sub_album_cover_folder)
            if not fileName_list:
                # 如果目录为空说明封面不存在,直接删除旧文件夹
                isPicExist = False
                rmtree(sub_album_cover_folder)
            else:
                # 如果第一个文件不是图片也需要删除文件夹并重新提取封面
                suffix = os.path.splitext(fileName_list[0])[1][1:]
                if suffix.lower() not in ["png", "jpg", "jpeg", "jiff"]:
                    rmtree(sub_album_cover_folder)
                    isPicExist = False
        else:
            isPicExist = False
        return isPicExist, sub_album_cover_folder

    @staticmethod
    def __savePic(sub_album_cover_folder: str, songInfo: dict, pic_data):
        """ 储存提取到的专辑封面 """
        # 获取后缀名
        suffix = getPicSuffix(pic_data)
        # 封面路径
        pic_path = os.path.join(sub_album_cover_folder,
                                songInfo['coverName']+suffix)
        # 写入封面
        with open(pic_path, "wb") as f:
            f.write(pic_data)
