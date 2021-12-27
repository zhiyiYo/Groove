# coding:utf-8
import json
import os
from urllib import parse
from copy import deepcopy
from pprint import pprint

import requests
from common.os_utils import adjustName
from common.meta_data.writer import writeAlbumCover, writeSongInfo


def exceptionHandler(*default):
    """ 请求异常处理装饰器

    Parameters
    ----------
    *default:
        发生异常时返回的默认值
    """

    def outer(func):

        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                print('发生异常')
                value = deepcopy(default)
                if len(value) == 0:
                    return None
                elif len(value) == 1:
                    return value[0]
                else:
                    return value

        return inner

    return outer


class KuWoMusicCrawler:
    """ 酷我音乐爬虫 """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Cookie': '_ga=GA1.2.136730414.1610802835; _gid=GA1.2.80092114.1621072767; Hm_lvt_cdb524f'
                      '42f0ce19b169a8071123a4797=1621072767; Hm_lpvt_cdb524f42f0ce19b169a8071123a4797'
                      '=1621073279; _gat=1; kw_token=C713RK6IJ8J',
            'csrf': 'C713RK6IJ8J',
            'Host': 'www.kuwo.cn',
            'Referer': ''
        }

    @exceptionHandler([], 0)
    def getSongInfoList(self, key_word: str, page_num=1, page_size=10):
        """ 获取歌曲列表

        Parameters
        ----------
        key_word: str
            搜索关键词

        page_num: int
            当前页码

        page_size: int
            每一页最多显示的条目数量

        Returns
        -------
        song_info_list: List[dict]
            歌曲信息列表

        total: int
            数据库中符合搜索条件的歌曲总数
        """
        key_word = parse.quote(key_word)

        # 配置请求头
        headers = self.headers.copy()
        headers["Referer"] = 'http://www.kuwo.cn/search/list?key='+key_word

        # 请求歌曲信息列表
        url = f'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord?key={key_word}&pn={page_num}&rn={page_size}&reqId=c06e0e50-fe7c-11eb-9998-47e7e13a7206'
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # 获取歌曲信息
        song_info_list = []
        data = json.loads(response.text)['data']
        for info in data['list']:
            song_info = {}
            song_info['rid'] = info['rid']
            song_info['songPath'] = ''
            song_info['songName'] = info['name']
            song_info['singer'] = info['artist']
            song_info['album'] = info['album']
            song_info['year'] = info['releaseDate'].split('-')[0]
            song_info['tracknumber'] = str(info['track'])
            song_info['coverPath'] = info.get('albumpic', '')
            song_info['coverName'] = adjustName(
                info['artist']+'_'+info['album'])
            song_info['genre'] = ''

            # 格式化时长
            d = info["duration"]
            song_info["duration"] = f"{int(d//60)}:{int(d%60):02}"

            song_info_list.append(song_info)

        return song_info_list, int(data['total'])

    @exceptionHandler('')
    def getSongUrl(self, rid: str, quality='Standard quality'):
        """ 获取歌曲播放地址

        Parameters
        ----------
        rid: str
            歌曲 rid

        quality: str
            歌曲音质，有 `Standard quality`、`High quality` 和 `Super quality` 三种
        """
        br = {
            'Standard quality': '128k',
            'High quality': '192k',
            'Super quality': '320k'
        }[quality]

        # 构造请求头
        headers = self.headers.copy()
        headers.pop('Referer')
        headers.pop('csrf')

        # 请求歌曲播放地址
        url = f'http://www.kuwo.cn/api/v1/www/music/playUrl?mid={rid}&type=convert_url3&br={br}mp3'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        play_url = json.loads(response.text)['data']['url']

        return play_url

    @exceptionHandler('')
    def downloadSong(self, song_info: dict, save_dir: str, quality='Standard quality'):
        """ 下载歌曲 """
        # 获取下载地址
        url = self.getSongUrl(song_info['rid'], quality)
        if not url:
            return ''

        # 请求歌曲资源
        headers = self.headers.copy()
        headers.pop('Referer')
        headers.pop('csrf')
        headers.pop('Host')
        response = requests.get(url, headers=headers)

        # 保存歌曲文件
        song_path = os.path.join(
            save_dir, f"{song_info['singer']} - {song_info['songName']}.mp3")
        with open(song_path, 'wb') as f:
            f.write(response.content)

        # 修改歌曲元数据
        song_info_ = song_info.copy()
        song_info_['songPath'] = song_path
        writeSongInfo(song_info_)
        writeAlbumCover(song_path, song_info["coverPath"])

        return song_path

    @exceptionHandler([], 0)
    def searchSong(self, key_word: str, quality='Standard quality', page_num=1, page_size=10):
        """ 搜索音乐

        Parameters
        ----------
        key_word: str
            搜索关键词

        quality: str
            歌曲音质，有 `Standard quality`、`High quality` 和 `Super quality` 三种

        page_num: int
            当前页码

        page_size: int
            最多返回歌曲下载地址数

        Returns
        -------
        song_info_list: List[dict]
            歌曲信息列表

        total: int
            数据库中符合搜索条件的歌曲总数
        """
        song_info_list, total = self.getSongInfoList(
            key_word, page_num, page_size)

        for song_info in song_info_list:
            song_info['songPath'] = self.getSongUrl(song_info['rid'], quality)

        return song_info_list, total

    @exceptionHandler()
    def getSingerAvatar(self, singer: str, save_dir: str):
        """ 获取歌手头像 """
        singer_ = parse.quote(singer)

        # 配置请求头
        headers = self.headers.copy()
        headers["Referer"] = 'http://www.kuwo.cn/search/singers?key='+singer_

        # 请求歌手信息列表
        url = f'http://www.kuwo.cn/api/www/search/searchArtistBykeyWord?key={singer_}&pn=1&rn=3&reqId=c06e0e50-fe7c-11eb-9998-47e7e13a7206'
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # 请求歌手头像
        artist_info = json.loads(response.text)["data"]["artistList"][0]
        headers = self.headers.copy()
        headers.pop('Referer')
        headers.pop('csrf')
        headers.pop('Host')
        response = requests.get(artist_info['pic300'], headers=headers)
        response.raise_for_status()

        # 保存头像
        os.makedirs(save_dir, exist_ok=True)
        with open(os.path.join(save_dir, singer+'.jpg'), 'wb') as f:
            f.write(response.content)

    @exceptionHandler()
    def getLyric(self, rid: str):
        """ 获取歌词 """
        url = f"https://m.kuwo.cn/newh5/singles/songinfoandlrc?musicId={rid}"
        response = requests.get(url)
        response.raise_for_status()

        # 歌词可能为 null，此时返回 None
        lyric = json.loads(response.text)['data']['lrclist']  # type:list

        return lyric


if __name__ == '__main__':
    crawler = KuWoMusicCrawler()
    song_info_list = crawler.search('aiko 微熱')
    if song_info_list:
        crawler.downloadSong(song_info_list[0], './')
