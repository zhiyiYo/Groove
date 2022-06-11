# coding:utf-8
import base64
import json
import random
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Union

import requests
from common.database.entity import SongInfo
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from fuzzywuzzy import fuzz

from .crawler_base import AudioQualityError, CrawlerBase, VideoQualityError
from .exception_handler import exceptionHandler


class WanYiMusicCrawler(CrawlerBase):
    """ Crawler of WanYiYun Music """

    def __init__(self):
        super().__init__()
        self.types = {
            "song": "1",
            "singer": "100",
            "album": "10",
            "lyric": "1006",
            "video": "1014"
        }
        self.encryptor = Encryptor()
        self.qualities = ['Standard quality', 'High quality',
                          'Super quality', 'Lossless quality']
        self.video_qualities = {
            "Full HD": 1080,
            "HD": 720,
            "SD": 480,
            "LD": 240
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Referer': 'https://music.163.com',
        }

    # TODO: can only get the first 20 search results
    @exceptionHandler([], 0)
    def getSongInfos(self, key_word: str, page_num=1, page_size=10) -> Tuple[List[SongInfo], int]:
        # send request for song information
        url = 'https://music.163.com/weapi/cloudsearch/get/web'
        form_data = {
            "s": key_word,
            "type": self.types['song'],    # 单曲
            "offset": str((page_num-1)*page_size),
            "total": "true",
            "limit": str(page_size),
            "more": "true"
        }
        text = self.send(url, form_data)

        # parse the response data
        song_infos = []
        data = json.loads(text)['result']
        for info in data['songs']:
            song_info = SongInfo()
            song_info['id'] = info['id']
            song_info.file = self.song_url_mark
            song_info.title = info['name']
            song_info.singer = info['ar'][0]['name']
            song_info.album = info['al']['name']
            song_info.duration = int(info["dt"]/1000)
            song_info.disc = int(info['cd'])
            song_info.discTotal = int(info['cd'])
            song_info.year = datetime.fromtimestamp(
                info['publishTime']/1000).year
            song_info['coverPath'] = info['al']['picUrl']

            song_infos.append(song_info)

        return song_infos, data['songCount']

    def getSongUrl(self, song_info: SongInfo, quality: str = 'Standard quality') -> str:
        urls = self.getSongUrls([song_info], quality)
        url = urls[0] if urls else ''
        return url

    @exceptionHandler([])
    def getSongUrls(self, song_infos: List[SongInfo], quality: str = 'Standard quality') -> str:
        """ get play urls of multi online songs

        Parameters
        ----------
        song_infos: List[SongInfo]
            song information list

        quality: str
            song sound quality，including `Standard quality`, `High quality`, `Super quality` and `Lossless quality`

        Returns
        -------
        urls: List[str]
            play url list, empty when no urls are found

        Raises
        ------
        AudioQualityError:
            thrown when the sound quality is illegal
        """
        if quality not in self.qualities:
            raise AudioQualityError(
                f'`{quality}` is not in the supported quality list `{self.qualities}`')

        qualities = ['standard', 'higher', 'exhigh', 'lossless']
        quality = qualities[self.qualities.index(quality)]

        # send request for play urls
        url = 'https://music.163.com/weapi/song/enhance/player/url/v1'
        form_data = {
            "ids": [i['id'] for i in song_infos],
            "level": "standard",
            "encodeType": "mp3",
        }
        text = self.send(url, form_data)

        # parse the response data
        data = json.loads(text)['data']
        play_urls = [i['url'] for i in data]

        return play_urls

    @exceptionHandler('')
    def getSongDetailsUrl(self, key_word: str):
        # search song information
        song_infos, _ = self.getSongInfos(key_word, page_size=20)
        if not song_infos:
            return ''

        # If the matching degree is less than threshold, return None
        matches = [fuzz.token_set_ratio(
            key_word, i.singer+' '+i.title) for i in song_infos]
        best_match = max(matches)
        if best_match < 85:
            return ''

        id = song_infos[matches.index(best_match)]['id']
        return f'https://music.163.com/#/song?id={id}'

    @exceptionHandler()
    def getLyric(self, key_word: str):
        # search song information
        song_infos, _ = self.getSongInfos(key_word, page_size=20)
        if not song_infos:
            return None

        # return None when the matching degree is less than threshold(100%)
        matches = [key_word == i.singer+' '+i.title for i in song_infos]
        if not any(matches):
            return

        # send request for lyrics
        url = 'https://music.163.com/weapi/song/lyric'
        form_data = {
            "id": song_infos[matches.index(True)]['id'],
            "lv": -1,
            "tv": -1
        }
        text = self.send(url, form_data)

        # parse the response data
        data = json.loads(text)
        lyrics = {
            "lyric": data['lrc']['lyric'],
            "tlyric": data['tlyric']['lyric']   # translation
        }
        return lyrics

    @exceptionHandler('')
    def getSingerAvatar(self, singer: str, save_dir: Union[str, Path]):
        # send request for singer information
        url = "https://music.163.com/weapi/cloudsearch/get/web"
        form_data = {
            "s": singer,
            "type": self.types['singer']
        }
        text = self.send(url, form_data)

        # parse response data
        data = json.loads(text)['result']['artists']
        if not data or fuzz.token_set_ratio(data[0]['name'], singer) < 98:
            return ''

        # send request for avatar
        response = requests.get(
            data[0]['img1v1Url']+'?param=300y300', headers=self.headers)
        response.raise_for_status()

        # save avatar
        return self.saveSingerAvatar(singer, save_dir, response.content)

    @exceptionHandler([], 0)
    def getMvInfos(self, key_word: str, page_num=1, page_size=10) -> Tuple[List[dict], int]:
        # send request for MV information
        url = "https://music.163.com/weapi/cloudsearch/get/web"
        form_data = {
            "s": key_word,
            "type": self.types['video'],
            "offset": str((page_num-1)*page_size),
            "total": "true",
            "limit": str(page_size),
        }
        text = self.send(url, form_data)

        # parse response data
        data = json.loads(text)['result']
        mv_info_list = []
        for info in data['videos']:
            mv_info = {}
            mv_info['vid'] = info['vid']
            mv_info['name'] = info['title']
            mv_info['singer'] = info['creator'][0]['userName']
            mv_info['coverPath'] = info['coverUrl']
            mv_info['type'] = info['type']
            d = info["durationms"]/1000
            mv_info["duration"] = f"{int(d//60)}:{int(d%60):02}"
            mv_info_list.append(mv_info)

        return mv_info_list, data['videoCount']

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
                f"`{quality}` is not in supported quality list `{self.qualities}`")

        mv_type = mv_info['type']
        mv_url_func_map = {
            0: self.__getType0MvUrl,
            1: self.__getType1MvUrl
        }

        play_url = mv_url_func_map[mv_type](mv_info, quality)
        return play_url

    def __getType0MvUrl(self, mv_info: dict, quality: str = 'SD'):
        """ get the play url of MV whose type if 0  """
        # send request for available qualities
        form_data = {"id": mv_info['vid']}
        url = "https://music.163.com/weapi/v1/mv/detail"
        data = json.loads(self.send(url, form_data))['data']
        resolutions = sorted([i['br'] for i in data['brs']], reverse=True)

        # select an available MV quality
        resolution = self.video_qualities[quality]
        if resolution not in resolutions:
            resolution = resolutions[0]

        # send request for play url of MV
        url = "https://music.163.com/weapi/song/enhance/play/mv/url"
        form_data = {
            "id": mv_info['vid'],
            "r": resolution
        }
        play_url = json.loads(self.send(url, form_data))['data']['url']
        return play_url

    def __getType1MvUrl(self, mv_info: dict, quality: str = 'SD'):
        """ get the play url of MV whose type if 1 """
        # send request for available qualities
        form_data = {"id": mv_info['vid']}
        url = "https://music.163.com/weapi/cloudvideo/v1/video/detail"
        data = json.loads(self.send(url, form_data))['data']
        resolutions = sorted([i['resolution'] for i in data['resolutions']])

        # select an available MV quality
        resolution = self.video_qualities[quality]
        if resolution not in resolutions:
            resolution = resolutions[-1]

        # send request for play url of MV
        url = 'https://music.163.com/weapi/cloudvideo/playurl'
        form_data = {
            "ids": str([mv_info['vid']]),
            "resolution": resolution
        }
        text = self.send(url, form_data)
        play_url = [i['url'] for i in json.loads(text)['urls']][0]
        return play_url

    def send(self, url: str, form_data: dict, headers=None) -> str:
        """ send a request of post method

        Parameters
        ----------
        url: str
            request url

        form_data: dict
            form data to be encrypted

        headers: dict
            request headers, use default headers if the param is not `None`

        Returns
        -------
        text: str
            text data of response
        """
        headers = headers or self.headers
        form_data = self.encryptor.encrypt(str(form_data))
        response = requests.post(url, form_data, headers=headers)
        response.raise_for_status()
        return response.text


class Encryptor:
    """ Encryptor for request parameters """

    def __init__(self) -> None:
        self.iv = '0102030405060708'
        self.public_key = '010001'
        self.modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b' \
            '5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417' \
            '629ec4ee341f56135fccf695280104e0312ecbda92557c93' \
                       '870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b' \
                       '424d813cfe4875d3e82047b97ddef52741d546b8e289dc69' \
                       '35b3ece0462db0a22b8e7'
        self.nonce = '0CoJUm6Qyw8W8jud'

    def encrypt(self, text: str):
        """ encrypt data

        Parameters
        ----------
        text: str
            plaintext to be encrypted

        Returns
        -------
        result: dict
            encryption result, contains keys: `params` and `encSecKey`
        """
        # randomly generate a string with a length of 16
        characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        i = ''.join(random.sample(characters, 16))

        # get request parameters
        params = self.AESEncrypt(text, self.nonce)
        params = self.AESEncrypt(params, i)

        # get encSecKey
        encSecKey = self.RSAEncrypt(i, self.public_key, self.modulus)

        # final result
        result = {
            'params': params,
            'encSecKey': encSecKey
        }
        return result

    def AESEncrypt(self, text: str, key: str):
        """ AES encrypt

        Parameters
        ----------
        text: str
            plaintext to be encrypted

        key: str
            secret key

        Returns
        -------
        cipher_text: str
            ciphertext
        """
        # data filling
        text = pad(text.encode(), AES.block_size)
        aes = AES.new(key.encode(), AES.MODE_CBC, self.iv.encode())

        # encrypt
        cipher_text = aes.encrypt(plaintext=text)
        cipher_text = base64.b64encode(cipher_text).decode()
        return cipher_text

    def RSAEncrypt(self, i, e, n):
        """ RAS encrypt """
        # C = M^e mod n
        num = pow(int(i[::-1].encode().hex(), 16), int(e, 16), int(n, 16))
        return format(num, 'x')
