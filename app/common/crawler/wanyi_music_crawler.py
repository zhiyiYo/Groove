# coding:utf-8
import base64
import json
import os
import random
from datetime import datetime
from typing import List, Tuple

import requests
from fuzzywuzzy import fuzz
from common.os_utils import adjustName
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from .crawler_base import CrawlerBase, QualityException, exceptionHandler


class WanYiMusicCrawler(CrawlerBase):
    """ 网易云音乐爬虫 """

    def __init__(self):
        super().__init__()
        self.types = {
            "song": "1",
            "singer": "100",
            "album": "10",
            "lyric": "1006"
        }
        self.encryptor = Encryptor()
        self.qualities = ['Standard quality', 'High quality',
                          'Super quality', 'Lossless quality']
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
        }
        text = self.send(url, form_data)

        # 获取歌曲信息
        song_info_list = []
        data = json.loads(text)['result']
        for info in data['songs']:
            song_info = {}
            song_info['id'] = info['id']
            song_info['songPath'] = ''
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
        QualityException:
            当音质非法时引发的异常
        """
        if quality not in self.qualities:
            raise QualityException(
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
        matches = [key_word==i['singer']+' '+i['songName'] for i in song_info_list]
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

    def send(self, url: str, form_data: dict) -> str:
        """ 发送 post 请求

        Parameters
        ----------
        url: str
            请求地址

        form_data: dict
            未加密的请求数据

        Returns
        -------
        text: str
            请求获取到的文本数据
        """
        form_data = self.encryptor.encrypt(str(form_data))
        response = requests.post(url, form_data, headers=self.headers)
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
