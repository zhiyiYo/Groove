# coding:utf-8
import json
from pathlib import Path
from typing import Union

import requests
from common.database.entity import SongInfo
from fuzzywuzzy import fuzz

from .exception_handler import exceptionHandler


class QQMusicCrawler:
    """ Crawler of QQ Music """

    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}

    @exceptionHandler()
    def getSongInfo(self, key_word: str, match_thresh=70):
        """ search song information

        Parameters
        ----------
        key_word: str
            search key word

        match_thresh: int
            matching degree threshold, the song information is returned when the matching degree
            is greater than threshold

        Returns
        -------
        song_info: SongInfo
            song information, `None` if search is fails
        """
        search_url = f"https://c.y.qq.com/soso/fcgi-bin/client_search_cp?new_json=1&p=1&n=5&w={key_word}"
        response = requests.get(search_url, headers=self.headers)

        infos = json.loads(response.text[9:-1])["data"]["song"]["list"]
        if not infos:
            return None

        # only the first item is taken
        info = infos[0]
        match_ratio = fuzz.token_set_ratio(
            f"{info['singer'][0]['name']} - {info['name']}", key_word)
        if match_ratio < match_thresh:
            return

        song_info = SongInfo()
        song_info.title = info["name"]
        song_info.album = info["album"]["name"]
        song_info.year = int(info["time_public"].split('-')[0])
        song_info.singer = info["singer"][0]["name"]
        song_info.track = info["index_album"]
        song_info.trackTotal = info["index_album"]
        song_info.disc= info['index_cd'] + 1
        song_info.discTotal = info['index_cd'] + 1
        song_info["albummid"] = info['album']['mid']

        # genre map of QQ music
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
        song_info.genre = genres.get(info["genre"], 'Pop')

        return song_info

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
        url = json.loads(response.text[18:-1]
                         )["data"]["headpiclist"][0]["picurl"]

        with open(save_path, 'wb') as f:
            f.write(requests.get(url, headers=self.headers).content)

        return url