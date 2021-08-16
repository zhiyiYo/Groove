# coding: utf-8
import json
import os
import re
from time import time
from hashlib import md5
from urllib import parse
from pprint import pprint

from app.common.adjust_album_name import adjustAlbumName
import requests


def exceptionHandler(func):
    """ 处理请求异常装饰器 """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            print('发生异常')
            return []

    return wrapper


class KuGouMusicCrawler:
    """ 酷狗音乐爬虫 """

    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
        self.cookies = {
            'kg_mid': '68aa6f0242d4192a2a9e2b91e44c226d',
            'kg_dfid': '4DoTYZ0DYq9M3ctVHp0cBghm',
            'kg_dfid_collect': 'd41d8cd98f00b204e9800998ecf8427e',
            'Hm_lvt_aedee6983d4cfc62f509129360d6bb3d': '1618922741,1618923483',
            'Hm_lpvt_aedee6983d4cfc62f509129360d6bb3d': '1618924198'
        }

    @exceptionHandler
    def search(self, key_word: str, page_size: int = 10, quality='normal'):
        """ 搜索音乐

        Parameters
        ----------
        key_word: str
            搜索关键词

        page_size: int
            最多返回歌曲下载地址数

        quality: str
            音频文件音质，可以是 `normal`、`highQuality` 或者 `superQuality`
        """
        if quality not in ['normal', 'HQ', 'SQ']:
            raise ValueError("音质非法")

        hash_keys = {
            "normal": "fileHash",
            "highQuality": "HQFileHash",
            "superQuality": "SQFileHash",
        }

        # 根据关键词搜索歌曲
        song_info_list = self.getSongInfoList(key_word, page_size)
        if not song_info_list:
            return None

        # 获取每一首歌的播放地址和封面地址
        for song_info in song_info_list:
            file_hash = song_info[hash_keys[quality]]
            play_url, cover_url = self.getSongDetails(
                file_hash, song_info["albumID"])
            song_info["songPath"] = play_url
            song_info["coverPath"] = cover_url

        return song_info_list

    @exceptionHandler
    def getSongInfoList(self, key_word, page_size):
        """ 搜索并获取歌曲信息列表 """
        k = int(round(time()*1000))
        infos = ["NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt", "bitrate=0", "callback=callback123",
                 f"clienttime={k}", "clientver=2000", "dfid=-", "inputtype=0",
                 "iscorrection=1", "isfuzzy=0", f"keyword={key_word}", f"mid={k}",
                 "page=1", f"pagesize={page_size}", "platform=WebFilter", "privilege_filter=0",
                 "srcappid=2919", "tag=em", "userid=-1", f"uuid={k}", "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt"]

        # 计算签名参数
        signature = md5(''.join(infos).encode('utf-8')).hexdigest().upper()

        # 请求 URL 获取歌曲信息列表
        url = f'https://complexsearch.kugou.com/v2/search/song?callback=callback123&keyword={parse.quote(key_word)}&page=1&pagesize={page_size}&bitrate=0&isfuzzy=0&tag=em&inputtype=0&platform=WebFilter&userid=-1&clientver=2000&iscorrection=1&privilege_filter=0&srcappid=2919&clienttime={k}&mid={k}&uuid={k}&dfid=-&signature={signature}'
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        # 解析返回的 json 数据
        info_list = json.loads(response.text[12:-2])["data"]["lists"]
        song_info_list = []
        for info in info_list:
            song_info = {}
            pattern = r'(<em>)|(</em>)'
            song_info["songName"] = re.sub(pattern, '', info["SongName"])
            song_info["singer"] = re.sub(pattern, '', info["SingerName"])
            song_info["album"] = info["AlbumName"]
            song_info["modifiedAlbum"] = adjustAlbumName(info["AlbumName"])[1]
            song_info["albumID"] = info["AlbumID"]
            song_info["coverPath"] = ''
            song_info['songPath'] = ''

            # 歌曲请求链接哈希值，对应普通、高音质和无损三种音质
            song_info["fileHash"] = info["FileHash"]
            song_info["HQFileHash"] = info["HQFileHash"]
            song_info["SQFileHash"] = info["SQFileHash"]

            # 格式化时长
            d = info["Duration"]
            song_info["duration"] = f"{int(d//60)}:{int(d%60):02}"

            song_info_list.append(song_info)

        return song_info_list

    def getSongDetails(self, file_hash: str, album_id: str):
        """ 获取歌曲详细信息

        Parameters
        ----------
        file_hash: str
            歌曲的哈希值，可以是 `song_info["fileHash"]`、`song_info["HQFileHash"]` 或者 `song_info["SQFileHash"]`

        album_id: str
            专辑 ID，由 `song_info["albumID"]` 返回

        Returns
        -------
        play_url: str
            歌曲播放地址，请求失败时为空字符串

        cover_url: str
            专辑封面地址，请求失败时为空字符串
        """
        url = f'https://wwwapi.kugou.com/yy/index.php?r=play/getdata&hash={file_hash}&mid=68aa6f0242d4192a2a9e2b91e44c226d&album_id={album_id}'

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
        except:
            print('发生异常')
            return '', ''
        else:
            data = json.loads(response.text)["data"]
            return data["play_url"], data["img"]


if __name__ == '__main__':
    crawler = KuGouMusicCrawler()
    pprint(crawler.search('aiko - 恋をしたのは'))
