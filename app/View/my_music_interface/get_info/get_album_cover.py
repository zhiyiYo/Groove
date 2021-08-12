# coding:utf-8

import imghdr
import os
from shutil import copyfile, rmtree

from mutagen import File

from .get_song_info import SongInfoGetter


class GetAlbumCover:
    """ 定义一个遍历音频文件和封面文件夹获取专辑封面的类 """

    def __init__(self, target_path_list: list):
        """
        Parameters
        ----------
        target_path_list: list
            目标文件夹路径列表
        """
        self.album_cover_folder = r"app\resource\Album_Cover"
        self.target_path_list = target_path_list
        self.songInfo = SongInfoGetter(target_path_list)
        # 获取封面
        self.getAlbum()

    def getAlbum(self):
        """ 获取封面 """
        # 检查当前目录下是否存在用于储存所有封面的目录,没有就创建
        os.makedirs(self.album_cover_folder, exist_ok=True)
        # 开始获取封面
        for songInfo in self.songInfo.songInfo_list:
            suffix = songInfo["suffix"]
            # 根据后缀名选择获取封面的方式
            if suffix == ".mp3":
                self.__getID3AlbumCover(songInfo)
            elif suffix == ".flac":
                self.__getFlacAlbumCover(songInfo)
            elif suffix == ".m4a":
                self.__getM4aAlbumCover(songInfo)

    def updateAlbumCover(self, target_path_list: list):
        """ 重新扫描指定的文件下的音频文件的专辑封面 """
        self.target_path_list = target_path_list
        self.songInfo.getInfo(target_path_list)
        self.getAlbum()

    def __getID3AlbumCover(self, songInfo: dict):
        """ 获取mp3文件的封面并写入文件夹 """
        # 封面目录
        isPicExist, sub_album_cover_folder = self.__isPicExist(songInfo)
        if isPicExist:
            return
        # 如果文件夹中不存在图片就扫描歌曲元数据来提取
        id_card = File(songInfo["songPath"])
        # 如果文件后缀名与实际类型不匹配就调用另一个函数
        if id_card.mime[0].split("/")[-1] == "flac":
            self.__getFlacAlbumCover(songInfo)
            return

        for key in id_card.tags.keys():
            if key.startswith("APIC"):
                # 如果不存在专辑对应的目录,就新建一个并写入专辑封面
                os.mkdir(sub_album_cover_folder)
                # 提取封面数据
                pic_data = id_card[key].data
                self.__savePic(sub_album_cover_folder, songInfo, pic_data)
                break
        else:
            # 没有提取到封面时也创建一个空文件夹
            os.mkdir(sub_album_cover_folder)

    def __getFlacAlbumCover(self, songInfo: dict):
        """ 获取flac文件的封面并写入文件夹 """
        isPicExist, sub_album_cover_folder = self.__isPicExist(songInfo)
        if isPicExist:
            return
        id_card = File(songInfo["songPath"])
        # 如果文件后缀名与实际类型不匹配就调用另一个函数
        if id_card.mime[0].split("/")[-1] == "mp4":
            self.__getM4aAlbumCover(songInfo)
            return
        # 确认是否存在封面数据
        if id_card.pictures:
            # 如果不存在专辑对应的目录,就新建一个并写入专辑封面
            os.mkdir(sub_album_cover_folder)
            # 提取封面数据
            pic_data = id_card.pictures[0].data
            self.__savePic(sub_album_cover_folder, songInfo, pic_data)

    def __getM4aAlbumCover(self, songInfo: dict):
        """ 获取m4a文件的封面 """
        isPicExist, sub_album_cover_folder = self.__isPicExist(songInfo)
        if isPicExist:
            return
        id_card = File(songInfo["songPath"])
        # 如果文件后缀名与实际类型不匹配就直接返回
        if id_card.mime[0].split("/")[-1] != "mp4":
            return
        if id_card.get("covr"):
            # 如果不存在专辑对应的目录,就新建一个并写入专辑封面
            os.mkdir(sub_album_cover_folder)
            # 提取封面数据
            pic_data = bytes(id_card["covr"][0])
            self.__savePic(sub_album_cover_folder, songInfo, pic_data)

    def __isPicExist(self, songInfo: dict):
        """ 检测封面是否存在 """
        sub_album_cover_folder = os.path.join(
            self.album_cover_folder, songInfo["modifiedAlbum"]
        )
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

    def __getPicSuffix(self, pic_data):
        """ 获取二进制数据的后缀名 """
        try:
            suffix = "." + imghdr.what(None, pic_data)
            if suffix == ".jpeg":
                suffix = ".jpg"
        except:
            suffix = ".jpg"
        return suffix

    def __savePic(self, sub_album_cover_folder: str, songInfo: dict, pic_data):
        """ 储存提取到的专辑封面 """
        # 获取后缀名
        suffix = self.__getPicSuffix(pic_data)
        # 封面路径
        pic_path = os.path.join(
            sub_album_cover_folder, songInfo["modifiedAlbum"] + suffix
        )
        # 写入封面
        with open(pic_path, "wb") as f:
            f.write(pic_data)
