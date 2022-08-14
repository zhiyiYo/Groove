# coding:utf-8
import base64
import json
from pathlib import Path
from typing import Union

import requests
from common.database.entity import SongInfo
from fuzzywuzzy import fuzz

from .exception_handler import exceptionHandler
from .crawler_base import CrawlerBase


class QQMusicCrawler(CrawlerBase):
    """ Crawler of QQ Music """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Referer': "https://y.qq.com"
        }
        self.types = {
            "song": 0,
            "singer": 1,
            "album": 2,
            "songlist": 3,  # 播放列表
            "mv": 4
        }

    @exceptionHandler([], 0)
    def getSongInfos(self, key_word: str, page_num=1, page_size=10):
        infos = self.__search(key_word, "song", page_num, page_size)
        song_infos = []
        genres = {
            1: 'Pop',
            2: 'classical',
            3: 'Jazz',
            15: 'Blues',
            19: 'Country',
            20: 'Dance',
            21: 'Easy Listening',
            22: 'Rap/Hip Hop',
            23: 'Folk',
            31: 'New Age',
            33: 'R&B/Soul',
            36: 'Rock',
            37: 'Soundtrack',
            39: 'World Music'
        }
        for info in infos:
            song_info = SongInfo()
            song_info.title = info["name"]
            song_info.album = info["album"]["name"]
            song_info.singer = info["singer"][0]["name"]
            song_info.track = info["index_album"]
            song_info.trackTotal = info["index_album"]
            song_info.disc = info['index_cd'] + 1
            song_info.discTotal = info['index_cd'] + 1
            song_info["albummid"] = info['album']['mid']
            song_info["songmid"] = info['mid']
            song_info.genre = genres.get(info["genre"], 'Pop')
            song_info.duration = info["interval"]
            year = info["time_public"].split('-')[0] #type:str
            if year.isnumeric():
                song_info.year = int(year)

            song_infos.append(song_info)

        return song_infos, len(song_infos)

    @exceptionHandler()
    def getAlbumCoverURL(self, albummid: str, save_path: Union[str, Path]):
        """ get album cover and download it to local

        Parameters
        ----------
        albummid: str
            album ID, returned by `song_info["albummid"]`

        save_path: str or Path
            local save path of album cover

        Returns
        -------
        url: str
            the url of album cover, `None` if no album cover is found
        """
        detail_url = f"https://c.y.qq.com/v8/fcg-bin/musicmall.fcg?_=1628997268750&cmd=get_album_buy_page&albummid={albummid}"
        response = requests.get(detail_url, headers=self.headers)
        response.raise_for_status()
        url = json.loads(response.text[18:-1]
                         )["data"]["headpiclist"][0]["picurl"]

        with open(save_path, 'wb') as f:
            f.write(requests.get(url, headers=self.headers).content)

        return url

    @exceptionHandler('')
    def getLyric(self, key_word: str):
        song_info = self.getSongInfo(key_word)
        if not song_info:
            return

        url = f"https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg?format=json&songmid={song_info['songmid']}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        lyric = json.loads(response.text)['lyric']
        return base64.b64decode(lyric).decode('utf-8')

    @exceptionHandler([])
    def __search(self, key_word: str, search_type: str, page_num=1, page_size=10):
        """ search information """
        url = f"https://u.y.qq.com/cgi-bin/musicu.fcg"
        data = {
            "req_1": {
                "method": "DoSearchForQQMusicDesktop",
                "module": "music.search.SearchCgiService",
                "param": {
                    "search_type": self.types[search_type],
                    "query": key_word,
                    "page_num": page_num,
                    "num_per_page": page_size
                }
            }
        }
        data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        response = requests.post(url, data, headers=self.headers)
        response.raise_for_status()
        infos = json.loads(response.text)[
            "req_1"]["data"]["body"][search_type]["list"]
        return infos or []


# solve circular import problem
CrawlerBase.meta_data_crawler = QQMusicCrawler()
