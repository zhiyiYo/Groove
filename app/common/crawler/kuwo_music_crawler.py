# coding:utf-8
import json
import re
from typing import List, Tuple
from urllib import parse

from uuid import uuid4
import requests
from common.picture import Avatar
from common.database.entity import SongInfo
from common.url import FakeUrl

from .crawler_base import (AudioQualityError, CrawlerBase, MvQuality,
                           SongQuality)
from .exception_handler import exceptionHandler


class KuWoMusicCrawler(CrawlerBase):
    """ Crawler of KuWo Music """

    name = "kuwo"

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
        try:
            url = f'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord?key={key_word}&pn={page_num}&rn={page_size}&reqId=c06e0e50-fe7c-11eb-9998-47e7e13a7206'
            response = self.send_request(url, headers=headers)
        except:
            url = f'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord?key={key_word}&pn={page_num}&rn={page_size}'
            response = self.send_request(url, headers=headers)

        # parse the response data
        song_infos = []
        data = json.loads(response.text)['data']
        for info in data['list']:
            song_info = SongInfo()
            song_info.file = KuWoFakeSongUrl(info['rid']).url()
            song_info.title = info['name']
            song_info.singer = info['artist']
            song_info.album = info['album']
            song_info.track = info['track']
            song_info.trackTotal = info['track']
            song_info.duration = info["duration"]
            song_info.genre = 'Pop'
            song_info['coverPath'] = info.get('albumpic', '')
            if info.get('releaseDate'):
                year = info['releaseDate'].split('-')[0]
                song_info.year = int(year) if year.isnumeric() else None

            song_infos.append(song_info)

        return song_infos, int(data['total'])

    @exceptionHandler('')
    def getSongUrl(self, song_info: SongInfo, quality=SongQuality.STANDARD) -> str:
        if quality not in SongQuality:
            raise AudioQualityError(f'`{quality}` is not supported.')

        if not FakeUrl.isFake(song_info.file):
            return song_info.file

        rid = KuWoFakeSongUrl.getId(song_info.file)
        br = {
            SongQuality.STANDARD: '128k',
            SongQuality.HIGH: '192k',
            SongQuality.SUPER: '320k',
            SongQuality.LOSSLESS: '320k',
        }[quality]

        # configure request header
        headers = self.headers.copy()
        headers.pop('Referer')
        headers.pop('csrf')

        # send request for play url
        url = f'http://www.kuwo.cn/api/v1/www/music/playUrl?mid={rid}&type=convert_url3&br={br}mp3'
        response = self.send_request(url, headers=headers)
        play_url = json.loads(response.text)['data']['url']

        return play_url

    @exceptionHandler('')
    def getSongDetailsUrl(self, key_word: str):
        song_info = self.getSongInfo(key_word)
        if not song_info:
            return ''

        return f"http://www.kuwo.cn/play_detail/{KuWoFakeSongUrl.getId(song_info.file)}"

    @exceptionHandler('')
    def downloadSong(self, song_info: SongInfo, save_dir: str, quality=SongQuality.STANDARD) -> str:
        # get play url
        url = self.getSongUrl(song_info, quality)
        if not url:
            return ''

        # send request for binary data of audio
        headers = self.headers.copy()
        headers.pop('Referer')
        headers.pop('csrf')
        headers.pop('Host')
        response = self.send_request(url, headers=headers)

        # save audio file
        return self.saveSong(song_info, save_dir, '.mp3', response.content)

    @exceptionHandler([], 0)
    def search(self, key_word: str, page_num=1, page_size=10, quality=SongQuality.STANDARD) -> Tuple[List[SongInfo], int]:
        song_infos, total = self.getSongInfos(
            key_word, page_num, page_size)

        for song_info in song_infos:
            song_info['songPath'] = self.getSongUrl(song_info, quality)

        return song_infos, total

    @exceptionHandler('')
    def getSingerAvatar(self, singer):
        singer_ = parse.quote(singer)

        # configure request header
        headers = self.headers.copy()
        headers["Referer"] = 'http://www.kuwo.cn/search/singers?key='+singer_

        # send request for singer information
        url = f'http://www.kuwo.cn/api/www/search/searchArtistBykeyWord?key={singer_}&pn=1&rn=3&reqId=c06e0e50-fe7c-11eb-9998-47e7e13a7206'
        response = self.send_request(url, headers=headers)

        # send request for singer avatar
        artist_info = json.loads(response.text)["data"]["artistList"][0]
        headers = self.headers.copy()
        headers.pop('Referer')
        headers.pop('csrf')
        headers.pop('Host')
        response = self.send_request(artist_info['pic300'], headers=headers)

        # save avatar
        return Avatar(singer).save(response.content)

    @exceptionHandler()
    def getLyric(self, key_word: str) -> list:
        song_info = self.getSongInfo(key_word)
        if not song_info:
            return

        # send request for lyrics
        url = f"https://m.kuwo.cn/newh5/singles/songinfoandlrc?musicId={KuWoFakeSongUrl.getId(song_info.file)}"
        response = self.send_request(url)

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
        response = self.send_request(url, headers=headers)

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
    def getMvUrl(self, mv_info: dict, quality=MvQuality.SD) -> str:
        # configure request header
        headers = self.headers.copy()
        headers.pop('Referer')
        headers.pop('csrf')

        # send request for HTML file
        url = f"http://www.kuwo.cn/mvplay/{mv_info['id']}"
        response = self.send_request(url, headers=headers)

        # search the play url of mp4
        match = re.search(r'src:"(.+\.mp4)"', response.text)
        return match.group(1).replace(r'\u002F', '/')


class KuWoFakeUrl(FakeUrl):
    """ Kuwo music fake url """

    server_name = "kuwo"


@FakeUrl.register
class KuWoFakeSongUrl(KuWoFakeUrl):
    """ Kuwo music fake song url """

    category = "song"
