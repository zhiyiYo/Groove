# coding: utf-8
import json
import re
from hashlib import md5
from time import time
from typing import List, Tuple

import requests
from common.database.entity import SongInfo

from .crawler_base import AudioQualityError, CrawlerBase, VideoQualityError
from .exception_handler import exceptionHandler


class KuGouMusicCrawler(CrawlerBase):
    """ Crawler of KuGou Music """

    def __init__(self):
        super().__init__()
        self.quality_hash_map = {
            "Standard quality": "fileHash",
            "High quality": "HQFileHash",
            "Super quality": "SQFileHash",
        }
        self.video_qualities = {
            "Full HD": "fhd_hash",
            "HD": "hd_hash",
            "SD": "qhd_hash",
            "LD": "sd_hash"
        }

    def __getSearchParams(self, key_word: str, page_num, page_size):
        """ get the request parameters of search function """
        k = int(round(time()*1000))
        infos = ["NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt", "bitrate=0", "callback=callback123",
                 f"clienttime={k}", "clientver=2000", "dfid=-", "inputtype=0",
                 "iscorrection=1", "isfuzzy=0", f"keyword={key_word}", f"mid={k}",
                 f"page={page_num}", f"pagesize={page_size}", "platform=WebFilter", "privilege_filter=0",
                 "srcappid=2919", "tag=em", "userid=-1", f"uuid={k}", "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt"]

        # generate signature
        params = {i.split('=')[0]: i.split('=')[1] for i in infos[1:-1]}
        params['signature'] = md5(
            ''.join(infos).encode('utf-8')).hexdigest().upper()
        return params

    def __getMvHashParams(self, mv_id: int):
        """ get the parameters for requesting MV hash """
        k = int(round(time()*1000))
        form_data = '{"fields":"base,h264","data":[{"entity_id":"' + str(
            mv_id) + '"}]}'
        infos = ["NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt", "appid=1014", f"clienttime={k}",
                 "clientver=20000", "dfid=1JdLvZ3dfbCk2E8NIV2D4Pzu",
                 "mid=56cb044b6d6a53f53c3d163912749c79", "srcappid=2919", "token=",
                 "userid=0", "uuid=56cb044b6d6a53f53c3d163912749c79", form_data,
                 "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt"]

        # generate signature
        params = {i.split('=')[0]: i.split('=')[1] for i in infos[1:-2]}
        params['signature'] = md5(
            ''.join(infos).encode('utf-8')).hexdigest().lower()
        return params

    def __getMvUrlParams(self, mv_hash: str):
        """ get the parameters for requesting play url of MV """
        k = int(round(time()*1000))
        infos = ["NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt", "appid=1014", f"clienttime={k}",
                 "clientver=20000", "cmd=123", "dfid=-", "ext=mp4", f"hash={mv_hash}",
                 "ismp3=0", "key=kugoumvcloud", f"mid={k}", "pid=6", "srcappid=2919",
                 "ssl=1", f"uuid={k}", "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt"]

        # generate signature
        params = {i.split('=')[0]: i.split('=')[1] for i in infos[1:-1]}
        params['signature'] = md5(
            ''.join(infos).encode('utf-8')).hexdigest().lower()
        return params

    def search(self, key_word: str, page_num=1, page_size=10, quality: str = 'Standard quality') -> Tuple[List[dict], int]:
        if quality not in self.qualities:
            raise AudioQualityError(
                f'`{quality}` is not on the supported quality list `{self.qualities}`')

        # search song information
        song_infos, total = self.getSongInfos(
            key_word, page_num, page_size)
        if not song_infos:
            return [], 0

        # get play urls and album cover urls
        for song_info in song_infos:
            file_hash = song_info[self.quality_hash_map[quality]]
            data = self.getSongDetails(
                file_hash, song_info["albumID"])

            song_info["songPath"] = data.get('play_url', '')
            song_info["coverPath"] = data.get('img', '')

        return song_infos, total

    @exceptionHandler([], 0)
    def getSongInfos(self, key_word: str, page_num=1, page_size=10) -> Tuple[List[SongInfo], int]:
        # send request for song information
        url = 'https://complexsearch.kugou.com/v2/search/song'
        params = self.__getSearchParams(key_word, page_num, page_size)
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        # parse the response data
        data = json.loads(response.text[12:-2])["data"]
        song_infos = []
        for info in data["lists"]:
            song_info = SongInfo()
            pattern = r'(<em>)|(</em>)'
            song_info.file = self.song_url_mark
            song_info.title = re.sub(pattern, '', info["SongName"])
            song_info.singer = re.sub(pattern, '', info["SingerName"])
            song_info.album = info["AlbumName"]
            song_info.duration = info["Duration"]
            song_info["albumID"] = info["AlbumID"]
            song_info["coverPath"] = ''

            # hash value of each play url, corresponding to standard, high and super quality
            song_info["fileHash"] = info["FileHash"]
            song_info["HQFileHash"] = info["HQFileHash"]
            song_info["SQFileHash"] = info["SQFileHash"]

            song_infos.append(song_info)

        return song_infos, data['total']

    @exceptionHandler({})
    def getSongDetails(self, file_hash: str, album_id: str) -> dict:
        """ get the details of song

        Parameters
        ----------
        file_hash: str
            hash value of online song, it can be:
            * `song_info["fileHash"]`
            * `song_info["HQFileHash"]`
            * `song_info["SQFileHash"]`

        album_id: str
            album ID, returned by `song_info["albumID"]`

        Returns
        -------
        data: dict
            details of song
        """
        url = f'https://wwwapi.kugou.com/yy/index.php?r=play/getdata&hash={file_hash}&mid=68aa6f0242d4192a2a9e2b91e44c226d&album_id={album_id}'

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        return json.loads(response.text)["data"]

    def getSongUrl(self, song_info: SongInfo, quality: str = 'Standard quality') -> str:
        if quality not in self.qualities:
            raise AudioQualityError(
                f'`{quality}` is not on the supported quality list `{self.qualities}`')

        data = self.getSongDetails(
            song_info[self.quality_hash_map[quality]], song_info["albumID"])

        return data.get('play_url', '')

    @exceptionHandler('')
    def downloadSong(self, song_info: SongInfo, save_dir: str, quality: str = 'Standard quality') -> str:
        # get play url
        url = self.getSongUrl(song_info, quality)
        if not url:
            return ''

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        # save audio file
        return self.saveSong(song_info, save_dir, '.mp3', response.content)

    @exceptionHandler('')
    def getLyric(self, key_word: str) -> str:
        song_info = self.getSongInfo(key_word)
        if not song_info:
            return

        lyric = self.getSongDetails(
            song_info['fileHash'], song_info['albumID']).get('lyrics')

        return lyric

    @exceptionHandler([], 0)
    def getMvInfos(self, key_word: str, page_num=1, page_size=10) -> Tuple[List[dict], int]:
        # send request for MV information
        url = 'https://complexsearch.kugou.com/v1/search/mv'
        params = self.__getSearchParams(key_word, page_num, page_size)
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        # parse the response data
        data = json.loads(response.text[12:-2])["data"]
        mv_info_list = []
        pattern = r'(<em>)|(</em>)'
        for info in data['lists']:
            mv_info = {}
            mv_info['MvID'] = info['MvID']
            mv_info['MvHash'] = info['MvHash']
            mv_info['name'] = re.sub(pattern, '', info['MvName'])
            mv_info['singer'] = re.sub(pattern, '', info["SingerName"])
            mv_info['coverPath'] = info['ThumbGif']
            mv_info_list.append(mv_info)

        return mv_info_list, data['total']

    @exceptionHandler('')
    def getMvUrl(self, mv_info: dict, quality: str = 'SD') -> str:
        """ get the play url of MV

        Parameters
        ----------
        mv_info: dict
            MV information

        quality: str
            MV quality, including `Full HD`, `HD`, `SD` and `LD`

        Returns
        -------
        play_url: str
            the play url of MV, empty string when no url is found

        Raises
        ------
        VideoQualityError:
            thrown when the MV quality is illegal
        """
        if quality not in self.video_qualities:
            raise VideoQualityError(
                f"`{quality}` is not in supported quality list `{list(self.video_qualities.keys())}`")

        # send request for available MV qualities
        url = "https://gateway.kugou.com/openapi/kmr/v1/mv"
        params = self.__getMvHashParams(mv_info['MvID'])
        form_data = '{"fields":"base,h264","data":[{"entity_id":"' + str(
            mv_info["MvID"]) + '"}]}'
        headers = self.headers.copy()
        headers['kg-tid'] = "317"
        response = requests.post(
            url, form_data, params=params, headers=headers)
        response.raise_for_status()

        # parse the response data
        data = json.loads(response.text)['data'][0]['h264']
        available_hashes = {}
        for k, hash_key in self.video_qualities.items():
            hash_value = data[hash_key]
            if hash_value:
                available_hashes[k] = hash_value

        if not available_hashes:
            return ''

        # get MV hash value
        if quality in available_hashes:
            mv_hash = available_hashes[quality]
        else:
            mv_hash = available_hashes[list(available_hashes.keys())[0]]

        # send request for the play url of MV
        url = "https://gateway.kugou.com/v2/interface/index"
        params = self.__getMvUrlParams(mv_hash)
        headers = self.headers.copy()
        headers['x-router'] = 'trackermv.kugou.com'
        response = requests.get(url, params, headers=headers)
        response.raise_for_status()

        data = json.loads(response.text)['data']
        return data[list(data.keys())[0]]['downurl']
