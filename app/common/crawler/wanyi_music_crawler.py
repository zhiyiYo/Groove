# coding:utf-8
import base64
import json
import random
from datetime import datetime
from typing import List, Tuple
from pprint import pprint

import requests
from fuzzywuzzy import fuzz
from common.os_utils import adjustName
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from .crawler_base import CrawlerBase, AudioQualityError, exceptionHandler, VideoQualityError


class WanYiMusicCrawler(CrawlerBase):
    """ 网易云音乐爬虫 """

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

    # TODO:只能显示前 20 首搜索结果
    @exceptionHandler([], 0)
    def getSongInfoList(self, key_word: str, page_num=1, page_size=10) -> Tuple[List[dict], int]:
        # 发送请求
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

        # 获取歌曲信息
        song_info_list = []
        data = json.loads(text)['result']
        for info in data['songs']:
            song_info = {}
            song_info['id'] = info['id']
            song_info['songPath'] = self.song_url_mark
            song_info['songName'] = info['name']
            song_info['singer'] = info['ar'][0]['name']
            song_info['album'] = info['al']['name']
            song_info['year'] = datetime.fromtimestamp(
                info['publishTime']/1000).year
            song_info['tracknumber'] = '0'
            song_info['trackTotal'] = '1'
            song_info['genre'] = ''
            song_info['disc'] = info['cd']
            song_info['discTotal'] = info['cd']

            # 封面路径
            song_info['coverPath'] = info['al']['picUrl']
            song_info['coverName'] = adjustName(
                song_info['singer'] + '_' + song_info['album'])

            # 格式化时长
            d = info["dt"]/1000
            song_info["duration"] = f"{int(d//60)}:{int(d%60):02}"

            song_info_list.append(song_info)

        return song_info_list, data['songCount']

    def getSongUrl(self, song_info: dict, quality: str = 'Standard quality') -> str:
        urls = self.getSongUrls([song_info], quality)
        url = urls[0] if urls else ''
        return url

    @exceptionHandler([])
    def getSongUrls(self, song_info_list: List[dict], quality: str = 'Standard quality') -> str:
        """ 获取多首歌曲下载链接

        Parameters
        ----------
        song_info_list: List[dict]
            歌曲信息

        quality: str
            歌曲音质，有 `Standard quality`、`High quality`、`Super quality` 和 `Lossless quality` 四种

        Returns
        -------
        urls: List[str]
            歌曲下载链接列表，没找到时为空列表

        Raises
        ------
        AudioQualityError:
            当音质非法时引发的异常
        """
        if quality not in self.qualities:
            raise AudioQualityError(
                f'音质 `{quality}` 不在支持的音质列表 {self.qualities} 中')

        qualities = ['standard', 'higher', 'exhigh', 'lossless']
        quality = qualities[self.qualities.index(quality)]

        # 发送请求
        url = 'https://music.163.com/weapi/song/enhance/player/url/v1'
        form_data = {
            "ids": [i['id'] for i in song_info_list],
            "level": "standard",
            "encodeType": "mp3",
        }
        text = self.send(url, form_data)

        # 解析数据
        data = json.loads(text)['data']
        play_urls = [i['url'] for i in data]

        return play_urls

    @exceptionHandler()
    def getLyric(self, key_word: str):
        """ 获取歌词

        Parameters
        ----------
        key_word: str
            关键词，要求是 `歌手 歌曲名` 形式

        Returns
        -------
        lyric:
            歌词，如果没找到则返回 `None`
        """
        # 搜索歌曲
        song_info_list, _ = self.getSongInfoList(key_word, page_size=20)

        if not song_info_list:
            return

        # 匹配度小于阈值则返回
        matches = [key_word == i['singer']+' '+i['songName']
                   for i in song_info_list]
        if not any(matches):
            return

        # 发送获取歌词的请求
        url = 'https://music.163.com/weapi/song/lyric'
        form_data = {
            "id": song_info_list[matches.index(True)]['id'],
            "lv": -1,
            "tv": -1
        }
        text = self.send(url, form_data)

        # 解析数据
        data = json.loads(text)
        lyrics = {
            "lyric": data['lrc']['lyric'],
            "tlyric": data['tlyric']['lyric']   # 翻译
        }
        return lyrics

    @exceptionHandler('')
    def getSingerAvatar(self, singer: str, save_dir: str):
        # 发送搜索歌手的请求
        url = "https://music.163.com/weapi/cloudsearch/get/web"
        form_data = {
            "s": singer,
            "type": self.types['singer']
        }
        text = self.send(url, form_data)

        # 解析歌手信息
        data = json.loads(text)['result']['artists']
        if not data or fuzz.token_set_ratio(data[0]['name'], singer) < 98:
            return ''

        # 获取头像
        response = requests.get(data[0]['img1v1Url'], headers=self.headers)
        response.raise_for_status()

        # 保存头像
        save_path = self.saveSingerAvatar(singer, save_dir, response.content)
        return save_path

    @exceptionHandler([], 0)
    def getMvInfoList(self, key_word: str, page_num=1, page_size=10) -> Tuple[List[dict], int]:
        # 发送搜索歌手的请求
        url = "https://music.163.com/weapi/cloudsearch/get/web"
        form_data = {
            "s": key_word,
            "type": self.types['video'],
            "offset": str((page_num-1)*page_size),
            "total": "true",
            "limit": str(page_size),
        }
        text = self.send(url, form_data)

        # 解析数据
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
        """ 获取 MV 播放地址

        Parameters
        ----------
        mv_info: dict
            MV 信息

        quality: str
            视频画质，可用的有 `Full HD`、`HD`、`SD` 和 `LD`

        Returns
        -------
        play_url: str
            播放地址，没找到时返回空字符串

        Raises
        ------
        VideoQualityError:
            视频画质错误
        """
        if quality not in self.video_qualities:
            raise VideoQualityError(
                f"画质 `{quality}` 不在支持的画质列表 {self.qualities} 中")

        mv_type = mv_info['type']
        mv_url_func_map = {
            0: self.__getType0MvUrl,
            1: self.__getType1MvUrl
        }

        play_url = mv_url_func_map[mv_type](mv_info, quality)
        return play_url

    def __getType0MvUrl(self, mv_info: dict, quality: str = 'SD'):
        """ 获取类型为 0 的 MV 的播放地址 """
        # 获取可用的清晰度
        form_data = {"id": mv_info['vid']}
        url = "https://music.163.com/weapi/v1/mv/detail"
        data = json.loads(self.send(url, form_data))['data']
        resolutions = sorted([i['br'] for i in data['brs']], reverse=True)

        # 如果清晰度不可用就选取一个可用的
        resolution = self.video_qualities[quality]
        if resolution not in resolutions:
            resolution = resolutions[0]

        # 获取播放地址
        url = "https://music.163.com/weapi/song/enhance/play/mv/url"
        form_data = {
            "id": mv_info['vid'],
            "r": resolution
        }
        play_url = json.loads(self.send(url, form_data))['data']['url']
        return play_url

    def __getType1MvUrl(self, mv_info: dict, quality: str = 'SD'):
        """ 获取类型为 1 的 MV 播放地址 """
        # 获取可用的清晰度
        form_data = {"id": mv_info['vid']}
        url = "https://music.163.com/weapi/cloudvideo/v1/video/detail"
        data = json.loads(self.send(url, form_data))['data']
        resolutions = sorted([i['resolution'] for i in data['resolutions']])

        # 如果清晰度不可用就选取一个可用的
        resolution = self.video_qualities[quality]
        if resolution not in resolutions:
            resolution = resolutions[-1]

        # 获取播放地址
        url = 'https://music.163.com/weapi/cloudvideo/playurl'
        form_data = {
            "ids": str([mv_info['vid']]),
            "resolution": resolution
        }
        text = self.send(url, form_data)
        play_url = [i['url'] for i in json.loads(text)['urls']][0]
        return play_url

    def send(self, url: str, form_data: dict, headers=None) -> str:
        """ 发送 post 请求

        Parameters
        ----------
        url: str
            请求地址

        form_data: dict
            未加密的请求数据

        headers: dict
            请求头，如果为空则使用默认请求头

        Returns
        -------
        text: str
            请求获取到的文本数据
        """
        headers = headers or self.headers
        form_data = self.encryptor.encrypt(str(form_data))
        response = requests.post(url, form_data, headers=headers)
        response.raise_for_status()
        return response.text


class Encryptor:
    """ 加密器 """

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
        """ 加密数据

        Parameters
        ----------
        text: str
            明文

        Returns
        -------
        result: dict
            加密结果，是包含 `params` 和 `encSecKey` 这两个键的字典
        """
        # 随机生成长度为 16 的字符串
        characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        i = ''.join(random.sample(characters, 16))

        # 获取 params
        params = self.AESEncrypt(text, self.nonce)
        params = self.AESEncrypt(params, i)

        # 获取 encSecKey
        encSecKey = self.RSAEncrypt(i, self.public_key, self.modulus)

        # 加密结果
        result = {
            'params': params,
            'encSecKey': encSecKey
        }
        return result

    def AESEncrypt(self, text: str, key: str):
        """ AES加密

        Parameters
        ----------
        text: str
            明文

        key: str
            密钥

        Returns
        -------
        cipher_text: str
            密文
        """
        # 数据填充
        text = pad(text.encode(), AES.block_size)
        aes = AES.new(key.encode(), AES.MODE_CBC, self.iv.encode())

        # 加密
        cipher_text = aes.encrypt(plaintext=text)
        cipher_text = base64.b64encode(cipher_text).decode()
        return cipher_text

    def RSAEncrypt(self, i, e, n):
        """ RAS 加密 """
        # 加密 C = M^e mod n
        num = pow(int(i[::-1].encode().hex(), 16), int(e, 16), int(n, 16))
        return format(num, 'x')
