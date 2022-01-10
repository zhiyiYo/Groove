# coding:utf-8
import json
import os
import re
from urllib import parse
from typing import List, Tuple

import requests
from fuzzywuzzy import fuzz
from common.meta_data.writer import writeAlbumCover, writeSongInfo
from common.os_utils import adjustName

from .crawler_base import CrawlerBase, AudioQualityError, exceptionHandler


class KuWoMusicCrawler(CrawlerBase):
    """ 酷我音乐爬虫 """

    def __init__(self):
        super().__init__()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Cookie': 'kw_token=C713RK6IJ8J',
            'csrf': 'C713RK6IJ8J',
            'Host': 'www.kuwo.cn',
            'Referer': ''
        }

    @exceptionHandler([], 0)
    def getSongInfoList(self, key_word: str, page_num=1, page_size=10) -> Tuple[List[dict], int]:
        key_word = parse.quote(key_word)

        # 配置请求头
        headers = self.headers.copy()
        headers["Referer"] = 'http://www.kuwo.cn/search/list?key='+key_word

        # 请求歌曲信息列表
        url = f'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord?key={key_word}&pn={page_num}&rn={page_size}&reqId=c06e0e50-fe7c-11eb-9998-47e7e13a7206'
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # 获取歌曲信息
        song_info_list = []
        data = json.loads(response.text)['data']
        for info in data['list']:
            song_info = {}
            song_info['rid'] = info['rid']
            song_info['songPath'] = ''
            song_info['songName'] = info['name']
            song_info['singer'] = info['artist']
            song_info['album'] = info['album']
            song_info['year'] = info['releaseDate'].split('-')[0]
            song_info['tracknumber'] = str(info['track'])
            song_info['trackTotal'] = str(info['track'])
            song_info['coverPath'] = info.get('albumpic', '')
            song_info['coverName'] = adjustName(
                info['artist'] + '_' + info['album'])
            song_info['genre'] = ''
            song_info['disc'] = '1'
            song_info['discTotal'] = '1'

            # 格式化时长
            d = info["duration"]
            song_info["duration"] = f"{int(d//60)}:{int(d%60):02}"

            song_info_list.append(song_info)

        return song_info_list, int(data['total'])

    @exceptionHandler('')
    def getSongUrl(self, song_info: dict, quality='Standard quality') -> str:
        if quality not in self.qualities:
            raise AudioQualityError(
                f'音质 `{quality}` 不在支持的音质列表 {self.qualities} 中')

        rid = song_info['rid']
        br = {
            'Standard quality': '128k',
            'High quality': '192k',
            'Super quality': '320k'
        }[quality]

        # 构造请求头
        headers = self.headers.copy()
        headers.pop('Referer')
        headers.pop('csrf')

        # 请求歌曲播放地址
        url = f'http://www.kuwo.cn/api/v1/www/music/playUrl?mid={rid}&type=convert_url3&br={br}mp3'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        play_url = json.loads(response.text)['data']['url']

        return play_url

    def downloadSong(self, song_info: dict, save_dir: str, quality='Standard quality') -> str:
        # 获取下载地址
        url = self.getSongUrl(song_info, quality)
        if not url:
            return ''

        # 请求歌曲资源
        headers = self.headers.copy()
        headers.pop('Referer')
        headers.pop('csrf')
        headers.pop('Host')
        response = requests.get(url, headers=headers)

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

    @exceptionHandler([], 0)
    def search(self, key_word: str, page_num=1, page_size=10, quality: str = 'Standard quality') -> Tuple[List[dict], int]:
        song_info_list, total = self.getSongInfoList(
            key_word, page_num, page_size)

        for song_info in song_info_list:
            song_info['songPath'] = self.getSongUrl(song_info, quality)

        return song_info_list, total

    @exceptionHandler('')
    def getSingerAvatar(self, singer: str, save_dir: str) -> str:
        singer_ = parse.quote(singer)

        # 配置请求头
        headers = self.headers.copy()
        headers["Referer"] = 'http://www.kuwo.cn/search/singers?key='+singer_

        # 请求歌手信息列表
        url = f'http://www.kuwo.cn/api/www/search/searchArtistBykeyWord?key={singer_}&pn=1&rn=3&reqId=c06e0e50-fe7c-11eb-9998-47e7e13a7206'
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # 请求歌手头像
        artist_info = json.loads(response.text)["data"]["artistList"][0]
        headers = self.headers.copy()
        headers.pop('Referer')
        headers.pop('csrf')
        headers.pop('Host')
        response = requests.get(artist_info['pic300'], headers=headers)
        response.raise_for_status()

        # 保存头像
        save_path = self.saveSingerAvatar(singer, save_dir, response.content)
        return save_path

    @exceptionHandler()
    def getLyric(self, key_word: str) -> list:
        """ 获取歌词

        Parameters
        ----------
        key_word: str
            关键词，默认形式为 `歌手 歌曲名`

        Returns
        -------
        lyric: list
            歌词列表，如果没找到则返回 `None`
        """
        song_info_list, _ = self.getSongInfoList(key_word, page_size=10)

        if not song_info_list:
            return None

        # 匹配度小于阈值则返回
        matches = [fuzz.token_set_ratio(
            key_word, i['singer']+' '+i['songName']) for i in song_info_list]
        best_match = max(matches)
        if best_match < 90:
            return

        # 发送请求
        rid = song_info_list[matches.index(best_match)]['rid']
        url = f"https://m.kuwo.cn/newh5/singles/songinfoandlrc?musicId={rid}"
        response = requests.get(url)
        response.raise_for_status()

        # 歌词可能为 null，此时返回 None
        lyric = json.loads(response.text)['data']['lrclist']  # type:list
        return lyric

    @exceptionHandler([], 0)
    def getMvInfoList(self, key_word: str, page_num=1, page_size=10) -> Tuple[List[dict], int]:
        key_word = parse.quote(key_word)

        # 配置请求头
        headers = self.headers.copy()
        headers['csrf'] = '1RTQ5LGVIRZ'
        headers['Cookie'] = 'kw_token=1RTQ5LGVIRZ'
        headers['Referer'] = 'http://www.kuwo.cn/search/mv?'+key_word

        # 搜索 MV 信息
        url = f'http://www.kuwo.cn/api/www/search/searchMvBykeyWord?key={key_word}&pn={page_num}&rn={page_size}&reqId=ba2f7511-6e89-11ec-aa1e-9520a8bfa7a5'
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # 解析信息
        mv_info_list = []
        data = json.loads(response.text)['data']
        for info in data['mvlist']:
            mv_info = {}
            mv_info['id'] = info['id']
            mv_info['name'] = info['name']
            mv_info['singer'] = info['artist']
            mv_info['coverPath'] = info['pic']
            d = info["duration"]
            mv_info["duration"] = f"{int(d//60)}:{int(d%60):02}"
            mv_info_list.append(mv_info)

        return mv_info_list, data['total']

    @exceptionHandler('')
    def getMvUrl(self, mv_info: dict, quality: str = 'SD') -> str:
        # 配置请求头
        headers = self.headers.copy()
        headers.pop('Referer')
        headers.pop('csrf')

        # 获取 HTML 页面
        url = f"http://www.kuwo.cn/mvplay/{mv_info['id']}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # 寻找 mp4 链接
        match = re.search(r'src:"(.+\.mp4)"', response.text)
        return match.group(1).replace(r'\u002F', '/')
