# coding:utf-8
import base64
import json
from pathlib import Path
from typing import Union

import requests
from common.database.entity import SongInfo
from common.url import FakeUrl

from .crawler_base import CrawlerBase, MvQuality, VideoQualityError
from .exception_handler import exceptionHandler


class QQMusicCrawler(CrawlerBase):
    """ Crawler of QQ Music """

    name = "qq"

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
        self.video_qualities = {
            MvQuality.FULL_HD: 3,
            MvQuality.HD: 2,
            MvQuality.SD: 1,
            MvQuality.LD: 0
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
            song_info.file = QQFakeSongUrl(info['mid']).url()
            song_info.title = info["name"]
            song_info.album = info["album"]["name"]
            song_info.singer = info["singer"][0]["name"]
            song_info.track = info["index_album"]
            song_info.trackTotal = info["index_album"]
            song_info.disc = info['index_cd'] + 1
            song_info.discTotal = info['index_cd'] + 1
            song_info["albummid"] = info['album']['mid']
            song_info.genre = genres.get(info["genre"], 'Pop')
            song_info.duration = info["interval"]
            year = info["time_public"].split('-')[0]  # type:str
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
        response = self.send_request(detail_url, headers=self.headers)
        url = json.loads(response.text[18:-1])["data"]["headpiclist"][0]["picurl"]

        with open(save_path, 'wb') as f:
            f.write(requests.get(url, headers=self.headers).content)

        return url

    @exceptionHandler('')
    def getLyric(self, key_word: str):
        song_info = self.getSongInfo(key_word)
        if not song_info:
            return

        mid = QQFakeSongUrl.getId(song_info.file)
        url = f"https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg?format=json&songmid={mid}"
        response = self.send_request(url, headers=self.headers)
        lyric = json.loads(response.text)['lyric']
        return base64.b64decode(lyric).decode('utf-8')

    @exceptionHandler([], 0)
    def getMvInfos(self, key_word: str, page_num=1, page_size=10):
        infos = self.__search(key_word, "mv", page_num, page_size)

        # parse the response data
        mv_infos = []
        for info in infos:
            mv_info = {}
            mv_info["id"] = info["v_id"]
            mv_info["name"] = info["mv_name"]
            mv_info["singer"] = info["singer_list"][0]["name"]
            mv_info['coverPath'] = info['mv_pic_url']
            d = info["duration"]
            mv_info["duration"] = f"{int(d//60)}:{int(d%60):02}"
            mv_infos.append(mv_info)

        return mv_infos, len(infos)

    @exceptionHandler('')
    def getMvUrl(self, mv_info: dict, quality=MvQuality.SD):
        if quality not in MvQuality:
            raise VideoQualityError(f"`{quality}` is not supported.")

        mv_id = mv_info["id"]
        data = {
            "mvUrl": {
                "module": "music.stream.MvUrlProxy",
                "method": "GetMvUrls",
                "param": {
                    "vids": [
                        mv_id
                    ],
                    "request_type": 10003,
                    "addrtype": 3,
                    "format": 264
                }
            }
        }
        infos = self.__post(data)["mvUrl"]["data"][mv_id]["mp4"][1:]
        urls = [i["freeflow_url"][0] for i in infos if i["freeflow_url"]]
        if not urls:
            return ''

        index = self.video_qualities[quality]
        return urls[min(index, len(urls)-1)]

    @exceptionHandler([])
    def __search(self, key_word: str, search_type: str, page_num=1, page_size=10):
        """ search information """
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
        infos = self.__post(data)["req_1"]["data"]["body"][search_type]["list"]
        return infos or []

    def __post(self, data: dict):
        url = f"https://u.y.qq.com/cgi-bin/musicu.fcg"
        data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        response = self.send_request(url, method='post', data=data, headers=self.headers)
        return json.loads(response.text)


# solve circular import problem
CrawlerBase.meta_data_crawler = QQMusicCrawler()


class QQFakeUrl(FakeUrl):
    """ QQ music fake url """

    server_name = "qq"


@FakeUrl.register
class QQFakeSongUrl(QQFakeUrl):
    """ QQ music fake song url """

    category = "song"
