# coding:utf-8
import json
from enum import Enum
from typing import List, Tuple
from urllib import parse

from common.picture import Avatar
from common.database.entity import SongInfo
from common.url import FakeUrl

from .crawler_base import (AudioQualityError, CrawlerBase, MvQuality,
                           SongQuality)
from .exception_handler import exceptionHandler



class KuWoSearchType(Enum):
    """ Kuwo search type """
    SONG = "music"
    SINGER = "artist"
    MV = "video"


class KuWoMusicCrawler(CrawlerBase):
    """ Crawler of KuWo Music """

    name = "kuwo"

    def __init__(self):
        super().__init__()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Referer': '',
        }

    @exceptionHandler([], 0)
    def getSongInfos(self, key_word: str, page_num=1, page_size=10) -> Tuple[List[SongInfo], int]:
        key_word = parse.quote(key_word)

        # send request for song information
        data = self._search(KuWoSearchType.SONG, key_word, page_num, page_size)
        # url = f"http://search.kuwo.cn/r.s?all={key_word}&pn={page_num-1}&rn={page_size}&reqId=85bde120-b7b5-11ec-94ee-75d538904202&client=kt&uid=794762570&ver=kwplayer_ar_9.2.2.1&vipver=1&show_copyright_off=1&newver=1&ft=music&cluster=0&strategy=2012&encoding=utf8&rformat=json&vermerge=1&mobi=1&issubtitle=1"
        # response = self.send_request(url, headers=self.headers)

        # parse the response data
        song_infos = []
        for info in data['abslist']:
            song_info = SongInfo()
            song_info.file = KuWoFakeSongUrl(info['MUSICRID'].split('_')[1]).url()
            song_info.title = info['NAME']
            song_info.singer = info['ARTIST']
            song_info.album = info['ALBUM']
            song_info.track = 0
            song_info.trackTotal = 1
            song_info.duration = int(info["DURATION"])
            song_info.genre = 'Pop'

            # album cover
            if info.get('web_albumpic_short'):
                path = '300/' + '/'.join(info['web_albumpic_short'].split('/')[1:])
                song_info['coverPath'] = "https://img3.kuwo.cn/star/albumcover/" + path
            else:
                song_info['coverPath'] = ''

            # release year
            if info.get('web_timingonline'):
                year = info['web_timingonline'][:4]
                song_info.year = int(year) if year.isnumeric() else None

            song_infos.append(song_info)

        return song_infos, int(data['TOTAL'])

    @exceptionHandler('')
    def getSongUrl(self, song_info: SongInfo, quality=SongQuality.STANDARD) -> str:
        if quality not in SongQuality:
            raise AudioQualityError(f'`{quality}` is not supported.')

        if not FakeUrl.isFake(song_info.file):
            return song_info.file

        # get mobi url
        rid = KuWoFakeSongUrl.getId(song_info.file)
        br = {
            SongQuality.STANDARD: '128k',
            SongQuality.HIGH: '192k',
            SongQuality.SUPER: '320k',
            SongQuality.LOSSLESS: '320k',
        }[quality]

        url = f"https://mobi.kuwo.cn/mobi.s?f=web&source=jiakong&type=convert_url_with_sign&rid={rid}&br={br}mp3"
        response = self.send_request(url, headers=self.headers).json()
        url = response['data']['url']

        return url

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
        response = self.send_request(url, headers=self.headers)

        # save audio file
        return self.saveSong(song_info, save_dir, '.' + self._qualityToFormat(quality), response.content)

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

        # send request for singer information
        data = self._search(KuWoSearchType.SINGER, singer_)

        # send request for singer avatar
        artist_info = data["abslist"][0]
        response = self.send_request(artist_info['hts_PICPATH'], headers=self.headers)

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

        # search MV information
        data = self._search(KuWoSearchType.MV, key_word, page_num, page_size)

        # parse the response data
        mv_info_list = []
        for info in data['abslist']:
            mv_info = {}
            mv_info['id'] = info['id']
            mv_info['name'] = info['SONGNAME']
            mv_info['singer'] = info['ARTIST']
            mv_info['coverPath'] = data['BASEPICPATH'] + info['MVPIC']
            d = int(info["DURATION"])
            mv_info["duration"] = f"{int(d//60)}:{int(d%60):02}"
            mv_info_list.append(mv_info)

        return mv_info_list, data['TOTAL']

    @exceptionHandler('')
    def getMvUrl(self, mv_info: dict, quality=MvQuality.SD) -> str:
        rid = mv_info['id']
        url = f"https://mobi.kuwo.cn/mobi.s?f=web&source=jiakong&type=convert_mv_url2&rid={rid}&format=MP4"
        response = self.send_request(url, headers=self.headers)
        return response.text.split("\r\n")[2][4:]

    def _search(self, type: KuWoSearchType, key_word: str, page_num=1, page_size=30):
        """ search  """
        url = f"http://search.kuwo.cn/r.s?all={key_word}&pn={page_num-1}&rn={page_size}&reqId=85bde120-b7b5-11ec-94ee-75d538904202&client=kt&uid=794762570&ver=kwplayer_ar_9.2.2.1&vipver=1&show_copyright_off=1&newver=1&ft={type.value}&cluster=0&strategy=2012&encoding=utf8&rformat=json&vermerge=1&mobi=1&issubtitle=1"
        response = self.send_request(url, headers=self.headers)
        return json.loads(response.text)

    def _qualityToFormat(self, quality: SongQuality):
        format = {
            SongQuality.STANDARD: 'mp3',
            SongQuality.HIGH: 'aac',
            SongQuality.SUPER: 'flac',
            SongQuality.LOSSLESS: 'flac',
        }[quality]
        return format


class KuWoFakeUrl(FakeUrl):
    """ Kuwo music fake url """

    server_name = "kuwo"


@FakeUrl.register
class KuWoFakeSongUrl(KuWoFakeUrl):
    """ Kuwo music fake song url """

    category = "song"
