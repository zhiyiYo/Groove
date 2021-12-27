# coding:utf-8
import os
import json

from mutagen import File
from tinytag import TinyTag

from common.os_utils import checkDirExists
from common.os_utils import adjustName
from PyQt5.QtCore import QFileInfo, Qt, QObject


class SongInfoReader(QObject):
    """ 创建一个获取和保存歌曲信息的类 """

    def __init__(self, folderPaths: list):
        super().__init__()
        self.folderPaths = folderPaths
        if not folderPaths:
            self.folderPaths = []

        self.songInfo_list = []
        self.getInfo(folderPaths)

    @checkDirExists('data')
    def scanTargetFolderSongInfo(self, folderPaths: list):
        """ 扫描指定文件夹的歌曲信息并更新歌曲信息 """
        self.folderPaths = folderPaths
        with open("data/songInfo.json", "w", encoding="utf-8") as f:
            json.dump([{}], f)
        self.songInfo_list = []
        self.getInfo(folderPaths)

    def rescanSongInfo(self):
        """ 重新扫描歌曲信息，检查是否有歌曲信息的更新 """
        hasSongModified = False

        # 如果歌曲信息被删除了，就重新扫描一遍
        if not os.path.exists("data/songInfo.json"):
            self.scanTargetFolderSongInfo(self.folderPaths)
            return True

        # 利用当前的歌曲信息进行更新
        self.songInfo_list = self.__readSongInfoFromJson()
        self.songPath_list = self.__getSongFilePaths()
        oldSongs = {info.get("songPath") for info in self.songInfo_list}

        # 处理旧的歌曲信息
        for songInfo in self.songInfo_list.copy():
            songPath = songInfo["songPath"]
            if os.path.exists(songPath):
                t1 = songInfo["modifiedTime"]
                t2 = QFileInfo(songPath).lastModified().toString(Qt.ISODate)
                # 歌曲发生修改则重新扫描该歌曲的信息
                if t1 != t2:
                    hasSongModified = True
                    self.songInfo_list.remove(songInfo)
                    self.songInfo_list.append(self.getOneSongInfo(songPath))
            else:
                self.songInfo_list.remove(songInfo)  # 歌曲不存在则移除歌曲信息
                hasSongModified = True

        # 添加新的歌曲信息
        for songPath in set(self.songPath_list) - oldSongs:
            hasSongModified = True
            self.songInfo_list.append(self.getOneSongInfo(songPath))

        # 保存歌曲信息
        self.sortByCreateTime()
        self.save()
        return hasSongModified

    @checkDirExists('data')
    def getInfo(self, folderPaths: list):
        """ 从指定的目录读取符合匹配规则的歌曲的标签卡信息 """
        self.folderPaths = folderPaths
        self.songPath_list = self.__getSongFilePaths()

        # 从json文件读取旧信息
        oldInfo = self.__readSongInfoFromJson()
        oldSongs = {info.get("songPath") for info in oldInfo}
        newSongs = set(self.songPath_list)

        # 如果文件路径完全相等就直接获取以前的文件信息并返回
        if newSongs == oldSongs:
            self.songInfo_list = oldInfo.copy()
            return

        # 根据文件路径并集获取部分文件信息字典
        commonSongs = newSongs & oldSongs
        if commonSongs:
            self.songInfo_list = [
                info for info in oldInfo if info["songPath"] in commonSongs]

        # 如果有差集的存在就需要更新json文件
        for songPath in newSongs - oldSongs:
            self.songInfo_list.append(self.getOneSongInfo(songPath))

        # 排序歌曲
        self.sortByCreateTime()

        # 更新json文件
        self.save()

    def getOneSongInfo(self, songPath: str):
        """ 获取一首歌的信息 """
        tag = TinyTag.get(songPath)
        fileInfo = QFileInfo(songPath)

        # 获取标签信息
        suffix = "." + fileInfo.suffix()
        songName = tag.title if tag.title and tag.title.strip() else fileInfo.baseName()
        singer = tag.artist if tag.artist and tag.artist.strip() else self.tr("Unknown artist")
        album = tag.album if tag.album and tag.album.strip() else self.tr("Unknown album")
        tracknumber = str(tag.track) if tag.track else "0"
        trackTotal = str(tag.track_total) if tag.track_total else '1'
        genre = tag.genre if tag.genre else self.tr("Unknown genre")
        duration = f"{int(tag.duration//60)}:{int(tag.duration%60):02}"
        coverName = adjustName(singer + '_' + album)
        disc = str(tag.disc) if tag.disc else "1"
        discTotal = str(tag.disc_total) if tag.disc_total else "1"

        # 调整曲目序号
        tracknumber = self.__adjustTrackNumber(tracknumber)

        # 获取年份
        if tag.year and tag.year[0] != "0":
            year = tag.year[:4]
        else:
            tag = File(songPath)
            key_dict = {".m4a": "©day", ".mp3": "TDRC", ".flac": "year"}
            year = (
                str(tag.get(key_dict[suffix])[0])[:4]
                if tag.get(key_dict[suffix])
                else ''
            )

        # 获取时间戳
        createTime = fileInfo.birthTime().toString(Qt.ISODate)
        modifiedTime = fileInfo.lastModified().toString(Qt.ISODate)

        # 创建歌曲信息字典
        songInfo = {
            "songPath": songPath,
            "singer": singer,
            "songName": songName,
            "album": album,  # album为原专辑名
            "coverName": coverName,  # 保存下来的封面名字
            "genre": genre,
            "year": year,
            "disc": disc,
            "discTotal": discTotal,
            "tracknumber": tracknumber,
            "trackTotal": trackTotal,
            "duration": duration,
            "suffix": suffix,
            "createTime": createTime,
            "modifiedTime": modifiedTime,
        }
        return songInfo

    def sortByCreateTime(self):
        """ 依据文件创建日期排序文件信息列表 """
        self.songInfo_list.sort(
            key=lambda songInfo: songInfo["createTime"], reverse=True)

    def sortByDictOrder(self):
        """ 以字典序排序文件信息列表 """
        self.songInfo_list.sort(key=lambda songInfo: songInfo["songName"])

    def sortBySonger(self):
        """ 以歌手名排序文件信息列表 """
        self.songInfo_list.sort(key=lambda songInfo: songInfo["singer"])

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

    def __readSongInfoFromJson(self) -> list:
        """ 从 json 文件中读取歌曲信息 """
        try:
            with open("data/songInfo.json", "r", encoding="utf-8") as f:
                songInfo_list = json.load(f)
        except:
            songInfo_list = [{}]
        return songInfo_list

    @checkDirExists('data')
    def save(self):
        """ 保存歌曲信息 """
        with open("data/songInfo.json", "w", encoding="utf-8") as f:
            json.dump(self.songInfo_list, f)

    def __getSongFilePaths(self):
        """ 获取指定歌曲文件夹下的歌曲文件 """
        songPaths = []
        for folderPath in self.folderPaths:
            files = os.listdir(folderPath)
            for file in files:
                if file.endswith(('.mp3', '.flac', '.m4a')):
                    songPaths.append(os.path.join(
                        folderPath, file).replace('\\', '/'))

        return songPaths

    def hasSongModified(self):
        """ 检测是否有歌曲被修改 """
        # 如果歌曲信息被删除了，就重新扫描一遍
        if not os.path.exists("data/songInfo.json"):
            return True

        # 利用当前的歌曲信息进行更新
        songInfo_list = self.__readSongInfoFromJson()
        songPath_list = self.__getSongFilePaths()
        oldSongs = {info.get("songPath") for info in songInfo_list}

        # 处理旧的歌曲信息
        for songInfo in songInfo_list:
            songPath = songInfo["songPath"]
            if os.path.exists(songPath):
                t1 = songInfo["modifiedTime"]
                t2 = QFileInfo(songPath).lastModified().toString(Qt.ISODate)
                # 歌曲发生修改则重新扫描该歌曲的信息
                if t1 != t2:
                    return True
            else:
                return True

        return bool(set(songPath_list)-oldSongs)
