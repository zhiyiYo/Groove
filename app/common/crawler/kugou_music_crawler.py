# coding: utf-8
import json
import re
import os
from hashlib import md5
from time import time
from typing import List, Tuple
from urllib import parse

import requests
from common.meta_data.writer import writeAlbumCover, writeSongInfo
from common.os_utils import adjustName

from .crawler_base import CrawlerBase, QualityException
from .exception_handler import exceptionHandler


class KuGouMusicCrawler(CrawlerBase):
    """ 酷狗音乐爬虫 """

    def __init__(self):
        super().__init__()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
        self.quality_hash_map = {
            "Standard quality": "fileHash",
            "High quality": "HQFileHash",
            "Super quality": "SQFileHash",
        }

    def search(self, key_word: str, page_num=1, page_size=10, quality: str = 'Standard quality') -> Tuple[List[dict], int]:
        if quality not in self.qualities:
            raise QualityException(
                f'音质 `{quality}` 不在支持的音质列表 {self.qualities} 中')

        # 根据关键词搜索歌曲
        song_info_list, total = self.getSongInfoList(
            key_word, page_num, page_size)
        if not song_info_list:
            return [], 0

        # 获取每一首歌的播放地址和封面地址
        for song_info in song_info_list:
            file_hash = song_info[self.quality_hash_map[quality]]
            data = self.getSongDetails(
                file_hash, song_info["albumID"])

            song_info["songPath"] = data.get('play_url', '')
            song_info["coverPath"] = data.get('img', '')

        return song_info_list, total

    @exceptionHandler()
    def getSongInfoList(self, key_word: str, page_num=1, page_size=10) -> Tuple[List[dict], int]:
        k = int(round(time()*1000))
        infos = ["NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt", "bitrate=0", "callback=callback123",
                 f"clienttime={k}", "clientver=2000", "dfid=-", "inputtype=0",
                 "iscorrection=1", "isfuzzy=0", f"keyword={key_word}", f"mid={k}",
                 f"page={page_num}", f"pagesize={page_size}", "platform=WebFilter", "privilege_filter=0",
                 "srcappid=2919", "tag=em", "userid=-1", f"uuid={k}", "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt"]

        # 计算签名参数
        params = {i.split('=')[0]: i.split('=')[1] for i in infos[1:-1]}
        params['signature'] = md5(
            ''.join(infos).encode('utf-8')).hexdigest().upper()

        # 请求 URL 获取歌曲信息列表
        url = 'https://complexsearch.kugou.com/v2/search/song'
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        # 解析返回的 json 数据
        data = json.loads(response.text[12:-2])["data"]
        song_info_list = []
        for info in data["lists"]:
            song_info = {}
            pattern = r'(<em>)|(</em>)'
            song_info["songName"] = re.sub(pattern, '', info["SongName"])
            song_info["singer"] = re.sub(pattern, '', info["SingerName"])
            song_info["album"] = info["AlbumName"]
            song_info["albumID"] = info["AlbumID"]
            song_info['songPath'] = ''
            song_info["coverPath"] = ''
            song_info["coverName"] = adjustName(
                info["SingerName"] + '_' + info["AlbumName"])

            # 歌曲请求链接哈希值，对应普通、高音质和无损三种音质
            song_info["fileHash"] = info["FileHash"]
            song_info["HQFileHash"] = info["HQFileHash"]
            song_info["SQFileHash"] = info["SQFileHash"]

            # 格式化时长
            d = info["Duration"]
            song_info["duration"] = f"{int(d//60)}:{int(d%60):02}"

            song_info_list.append(song_info)

        return song_info_list, data['total']

    @exceptionHandler({})
    def getSongDetails(self, file_hash: str, album_id: str) -> dict:
        """ 获取歌曲详细信息

        Parameters
        ----------
        file_hash: str
            歌曲的哈希值，可以是 `song_info["fileHash"]`、`song_info["HQFileHash"]` 或者 `song_info["SQFileHash"]`

        album_id: str
            专辑 ID，由 `song_info["albumID"]` 返回

        Returns
        -------
        data: dict
            详细信息
        """
        url = f'https://wwwapi.kugou.com/yy/index.php?r=play/getdata&hash={file_hash}&mid=68aa6f0242d4192a2a9e2b91e44c226d&album_id={album_id}'

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        data = json.loads(response.text)["data"]
        return data

    def getSongUrl(self, song_info: dict, quality: str = 'Standard quality') -> str:
        if quality not in self.qualities:
            raise QualityException(
                f'音质 `{quality}` 不在支持的音质列表 {self.qualities} 中')

        data = self.getSongDetails(
            song_info[self.quality_hash_map[quality]], song_info["albumID"])

        return data.get('play_url', '')

    def downloadSong(self, song_info: dict, save_dir: str, quality: str = 'Standard quality') -> str:
        # 获取下载地址
        url = self.getSongUrl(song_info, quality)
        if not url:
            return ''

        response = requests.get(url, headers=self.headers)

        # 保存歌曲文件
        song_path = os.path.join(
            save_dir, f"{song_info['singer']} - {song_info['songName']}.mp3")
        with open(song_path, 'wb') as f:
            f.write(response.content)

        # 修改歌曲元数据
        song_info_ = song_info.copy()
        song_info_['songPath'] = song_path
        writeSongInfo(song_info_)
        writeAlbumCover(song_path, song_info["coverPath"])

        return song_path

    def getLyric(self, key_word: str) -> str:
        """ 获取歌词

        Parameters
        ----------
        key_word: str
            关键词

        Returns
        -------
        lyric: str
            歌词列表，如果没找到则返回 `None`
        """
        song_info_list, _ = self.getSongInfoList(key_word, page_size=1)

        if not song_info_list:
            return None

        song_info = song_info_list[0]
        lyric = self.getSongDetails(
            song_info['fileHash'], song_info['albumID']).get('lyrics')

        return lyric
