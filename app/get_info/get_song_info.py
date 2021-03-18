# coding:utf-8
import json
import os
import re

from mutagen import File
from tinytag import TinyTag

from app.my_functions.adjust_album_name import adjustAlbumName
from PyQt5.QtCore import QFileInfo, Qt


class GetSongInfo:
    """ 创建一个获取和保存歌曲信息的类 """

    def __init__(self, targetFolderPath_list: list):
        # 获取音频文件夹列表
        self.targetFolderPath_list = targetFolderPath_list
        if not targetFolderPath_list:
            self.targetFolderPath_list = []
        self.songInfo_list = []
        self.getInfo(targetFolderPath_list)

    def scanTargetFolderSongInfo(self, targetFolderPath_list: list):
        """ 扫描指定文件夹的歌曲信息并更新歌曲信息 """
        self.targetFolderPath_list = targetFolderPath_list
        if not os.path.exists("app\\data"):
            os.mkdir("app\\data")
        with open("app\\data\\songInfo.json", "w", encoding="utf-8") as f:
            json.dump([{}], f)
        self.songInfo_list = []
        self.getInfo(targetFolderPath_list)

    def getInfo(self, targetFolderPath_list: list):
        """ 从指定的目录读取符合匹配规则的歌曲的标签卡信息 """
        filePath_list = []
        self.targetFolderPath_list = targetFolderPath_list
        for target_path in self.targetFolderPath_list:
            absPath_list = [
                os.path.join(target_path, filename)
                for filename in os.listdir(target_path)
            ]
            # 更新文件路径列表
            filePath_list += [
                filePath for filePath in absPath_list if os.path.isfile(filePath)
            ]

        # 获取符合匹配音频文件名和路径列表
        self.__splitSonglist(filePath_list)
        # 如果数据文件夹不存在就创建一个
        if not os.path.exists("app\\data"):
            os.mkdir("app\\data")
        # 从json文件读取旧信息
        try:
            with open("app\\data\\songInfo.json", "r", encoding="utf-8") as f:
                oldData = json.load(f)
        except:
            oldData = [{}]

        oldSongPath_list = [oldFileInfo.get("songPath") for oldFileInfo in oldData]

        # 判断旧文件路径列表是否与新文件名列表相等
        if set(self.songPath_list) == set(oldSongPath_list) and len(
            oldSongPath_list
        ) == len(self.songPath_list):
            # 如果文件路径完全相等就直接获取以前的文件信息并返回
            self.songInfo_list = oldData.copy()
            return
        newSongPath_set = set(self.songPath_list)
        oldSongPath_set = set(oldSongPath_list)
        # 计算文件路径差集
        diffSongPath_list = list(newSongPath_set - oldSongPath_set)
        # 计算文件路径的并集
        commonSongPath_set = newSongPath_set & oldSongPath_set

        # 根据文件路径并集获取部分文件信息字典
        if commonSongPath_set:
            self.songInfo_list = [
                oldSongInfo_dict
                for oldSongInfo_dict in oldData
                if oldSongInfo_dict["songPath"] in commonSongPath_set
            ]
        # 如果有差集的存在就需要更新json文件
        if not (newSongPath_set < oldSongPath_set and commonSongPath_set):
            # 获取后缀名，歌名，歌手名列表
            self.__splitSonglist(diffSongPath_list, flag=1)
            argZip = zip(
                self.song_list,
                self.songPath_list,
                self.songname_list,
                self.songer_list,
                self.suffix_list,
            )
            for index, (song, songPath, songname, songer, suffix) in enumerate(argZip):
                id_card = TinyTag.get(songPath)
                # 获取时间戳
                createTime = QFileInfo(songPath).birthTime().toString(Qt.ISODate)
                album_list, tcon, year, duration, tracknumber = self.__getAlbumTconYear(
                    suffix, id_card, songPath
                )
                # 将歌曲信息字典插入列表
                self.songInfo_list.append(
                    {
                        "song": song,
                        "songPath": songPath,
                        "songer": songer,
                        "songName": songname,
                        "album": album_list[0],  # album为原专辑名
                        "modifiedAlbum": album_list[-1],  # modifiedAlbum为修改后的专辑名
                        "tcon": tcon,
                        "year": year,
                        "tracknumber": tracknumber,
                        "duration": duration,
                        "suffix": suffix,
                        "createTime": createTime,
                    }
                )
        self.sortByCreateTime()
        # 更新json文件
        with open("app\\data\\songInfo.json", "w", encoding="utf-8") as f:
            json.dump(self.songInfo_list, f)

    def __splitSonglist(self, filePath_list, flag=0):
        """分离歌手名，歌名和后缀名,flag用于表示是否将匹配到的音频文件拆开,
        flag = 1为拆开,flag=0为不拆开，update_songList用于更新歌曲文件列表"""
        self.songPath_list = filePath_list.copy()
        # 获取文件名列表
        fileName_list = [filePath.split("\\")[-1] for filePath in filePath_list]
        self.song_list = fileName_list.copy()
        # 创建列表
        self.songer_list, self.songname_list, self.suffix_list = [], [], []
        # 过滤文件
        rex = r"(.+) - (.+)(\..+)"
        for file_name, file_path in zip(fileName_list, filePath_list):
            if file_name.endswith(("mp3", "flac", "m4a")):
                Match = re.match(rex, file_name)
                if Match and flag == 1:
                    self.songer_list.append(Match.group(1))
                    self.songname_list.append(Match.group(2))
                    self.suffix_list.append(Match.group(3))
            else:
                self.song_list.remove(file_name)
                self.songPath_list.remove(file_path)

    def __getAlbumTconYear(self, suffix: str, id_card: TinyTag, songPath: str):
        """ 根据文件的后缀名来获取专辑信息及时长 """
        # 有可能出现专辑为'   '的情况
        album = id_card.album if id_card.album and id_card.album.strip() else "未知专辑"
        tracknumber = str(id_card.track) if id_card.track else "0"
        tcon = id_card.genre if id_card.genre else "未知流派"
        duration = f"{int(id_card.duration//60)}:{int(id_card.duration%60):02}"
        # 调整曲目序号
        tracknumber = self.__adjustTrackNumber(tracknumber)
        if id_card.year and id_card.year[0] != "0":
            year = id_card.year[:4] + "年"
        else:
            id_card = File(songPath)
            key_dict = {".m4a": "©day", ".mp3": "TDRC", ".flac": "year"}
            year = (
                str(id_card.get(key_dict[suffix])[0])[:4] + "年"
                if id_card.get(key_dict[suffix])
                else "未知年份"
            )
        # album作为列表返回，最后元素是改过的专辑名，第一个是原名
        album_list = adjustAlbumName(album)
        return album_list, tcon, year, duration, tracknumber

    def sortByCreateTime(self):
        """ 依据文件修改日期排序文件信息列表 """
        self.songInfo_list.sort(
            key=lambda songInfo: songInfo["createTime"], reverse=True
        )

    def sortByDictOrder(self):
        """ 以字典序排序文件信息列表 """
        self.songInfo_list.sort(key=lambda songInfo: songInfo["songName"])

    def sortBySonger(self):
        """ 以歌手名排序文件信息列表 """
        self.songInfo_list.sort(key=lambda songInfo: songInfo["songer"])

    def __adjustTrackNumber(self, trackNum: str):
        """ 调整曲目编号 """
        if trackNum != "0":
            trackNum = trackNum.lstrip("0")
        # 处理a/b
        trackNum = trackNum.split("/")[0]
        # 处理An
        if trackNum[0].upper() == "A":
            trackNum = trackNum[1:]
        return trackNum
