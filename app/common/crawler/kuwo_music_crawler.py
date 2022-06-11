# coding:utf-8
import json
import re
from urllib import parse
from typing import List, Tuple

import requests
from fuzzywuzzy import fuzz
from common.database.entity import SongInfo

from .crawler_base import CrawlerBase, AudioQualityError
from .exception_handler import exceptionHandler


class KuWoMusicCrawler(CrawlerBase):
    """ Crawler of KuWo Music """

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
    def getSongInfos(self, key_word: str, page_num=1, page_size=10) -> Tuple[List[SongInfo], int]:
        key_word = parse.quote(key_word)

        # configure request header
        headers = self.headers.copy()
        headers["Referer"] = 'http://www.kuwo.cn/search/list?key='+key_word

        # send request for song information
        url = f'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord?key={key_word}&pn={page_num}&rn={page_size}&reqId=c06e0e50-fe7c-11eb-9998-47e7e13a7206'
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # parse the response data
        song_infos = []
        data = json.loads(response.text)['data']
        for info in data['list']:
            song_info = SongInfo()
            song_info['rid'] = info['rid']
            song_info.file = self.song_url_mark  # remark that the play url is not fetched
            song_info.title = info['name']
            song_info.singer = info['artist']
            song_info.album = info['album']
            song_info.year = info['releaseDate'].split('-')[0]
            song_info.track = info['track']
            song_info.trackTotal = info['track']
            song_info.duration = info["duration"]
            song_info.genre = 'Pop'
            song_info['coverPath'] = info.get('albumpic', '')
            song_infos.append(song_info)

        return song_infos, int(data['total'])

    @exceptionHandler('')
    def getSongUrl(self, song_info: SongInfo, quality='Standard quality') -> str:
        if quality not in self.qualities:
            raise AudioQualityError(
                f'`{quality}` is not in the supported quality list `{self.qualities}`')

        rid = song_info['rid']
        br = {
            'Standard quality': '128k',
            'High quality': '192k',
            'Super quality': '320k'
        }[quality]

        # configure request header
        headers = self.headers.copy()
        headers.pop('Referer')
        headers.pop('csrf')

        # send request for play url
        url = f'http://www.kuwo.cn/api/v1/www/music/playUrl?mid={rid}&type=convert_url3&br={br}mp3'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        play_url = json.loads(response.text)['data']['url']

        return play_url

    @exceptionHandler('')
    def getSongDetailsUrl(self, key_word: str):
        song_info = self.__matchSongInfo(key_word)
        if not song_info:
            return ''

        return f"http://www.kuwo.cn/play_detail/{song_info['rid']}"

    @exceptionHandler('')
    def downloadSong(self, song_info: SongInfo, save_dir: str, quality='Standard quality') -> str:
        # get play url
        url = self.getSongUrl(song_info, quality)
        if not url:
            return ''

        # send request for binary data of audio
        headers = self.headers.copy()
        headers.pop('Referer')
        headers.pop('csrf')
        headers.pop('Host')
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # save audio file
        return self.saveSong(song_info, save_dir, '.mp3', response.content)

    @exceptionHandler([], 0)
    def search(self, key_word: str, page_num=1, page_size=10, quality: str = 'Standard quality') -> Tuple[List[SongInfo], int]:
        song_infos, total = self.getSongInfos(
            key_word, page_num, page_size)

        for song_info in song_infos:
            song_info['songPath'] = self.getSongUrl(song_info, quality)

        return song_infos, total

    @exceptionHandler('')
    def getSingerAvatar(self, singer: str, save_dir: str) -> str:
        singer_ = parse.quote(singer)

        # configure request header
        headers = self.headers.copy()
        headers["Referer"] = 'http://www.kuwo.cn/search/singers?key='+singer_

        # send request for singer information
        url = f'http://www.kuwo.cn/api/www/search/searchArtistBykeyWord?key={singer_}&pn=1&rn=3&reqId=c06e0e50-fe7c-11eb-9998-47e7e13a7206'
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # send request for singer avatar
        artist_info = json.loads(response.text)["data"]["artistList"][0]
        headers = self.headers.copy()
        headers.pop('Referer')
        headers.pop('csrf')
        headers.pop('Host')
        response = requests.get(artist_info['pic300'], headers=headers)
        response.raise_for_status()

        # save avatar
        return self.saveSingerAvatar(singer, save_dir, response.content)

    @exceptionHandler()
    def getLyric(self, key_word: str) -> list:
        song_info = self.__matchSongInfo(key_word)
        if not song_info:
            return

        # send request for lyrics
        url = f"https://m.kuwo.cn/newh5/singles/songinfoandlrc?musicId={song_info['rid']}"
        response = requests.get(url)
        response.raise_for_status()

        # lyric could be null, corresponding to None
        return json.loads(response.text)['data']['lrclist']

    @exceptionHandler([], 0)
    def getMvInfos(self, key_word: str, page_num=1, page_size=10) -> Tuple[List[dict], int]:
        key_word = parse.quote(key_word)

        # configure request header
        headers = self.headers.copy()
        headers['csrf'] = '1RTQ5LGVIRZ'
        headers['Cookie'] = 'kw_token=1RTQ5LGVIRZ'
        headers['Referer'] = 'http://www.kuwo.cn/search/mv?'+key_word

        # search MV information
        url = f'http://www.kuwo.cn/api/www/search/searchMvBykeyWord?key={key_word}&pn={page_num}&rn={page_size}&reqId=ba2f7511-6e89-11ec-aa1e-9520a8bfa7a5'
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # parse the response data
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
        # configure request header
        headers = self.headers.copy()
        headers.pop('Referer')
        headers.pop('csrf')

        # send request for HTML file
        url = f"http://www.kuwo.cn/mvplay/{mv_info['id']}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # search the play url of mp4
        match = re.search(r'src:"(.+\.mp4)"', response.text)
        return match.group(1).replace(r'\u002F', '/')

    def __matchSongInfo(self, key_word: str, threshold=90) -> SongInfo:
        """ Get the most matching song information according to keyword

        Parameters
        ----------
        key_word: str
            search key word

        threshold: int
            matching threshold

        Returns
        -------
        songInfo: SongInfo
            the most matching song information, `None` if no one match
        """
        song_infos, _ = self.getSongInfos(key_word, page_size=10)
        if not song_infos:
            return None

        # If the matching degree is less than threshold, return None
        matches = [fuzz.token_set_ratio(
            key_word, i.singer+' '+i.title) for i in song_infos]
        best_match = max(matches)
        if best_match < threshold:
            return None

        return song_infos[matches.index(best_match)]
