# coding:utf-8
import json
import os
from urllib import parse

import requests
from common.os_utils import adjustName
from common.meta_data_writer import writeAlbumCover, writeSongInfo


def exceptionHandler(func):
    """ 处理请求异常装饰器 """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            print('发生异常')
            return []

    return wrapper


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

    @exceptionHandler
    def getSongInfoList(self, key_word: str, page_size=10):
        """ 获取歌曲列表

        Parameters
        ----------
        key_word: str
            搜索关键词

        page_size: int
            返回的最多歌曲数量
        """
        key_word = parse.quote(key_word)

        # 配置请求头
        headers = self.headers.copy()
        headers["Referer"] = 'http://www.kuwo.cn/search/list?key='+key_word

        # 请求歌曲信息列表
        url = f'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord?key={key_word}&pn=1&rn={page_size}&reqId=c06e0e50-fe7c-11eb-9998-47e7e13a7206'
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # 获取歌曲信息
        song_info_list = []
        info_list = json.loads(response.text)['data']['list']
        for info in info_list:
            song_info = {}
            song_info['rid'] = info['rid']
            song_info['songPath'] = ''
            song_info['songName'] = info['name']
            song_info['singer'] = info['artist']
            song_info['album'] = info['album']
            song_info['year'] = info['releaseDate'].split('-')[0]
            song_info['tracknumber'] = str(info['track'])
            song_info['coverPath'] = info['albumpic']
            song_info['coverName'] = adjustName(
                info['artist']+'_'+info['album'])
            song_info['genre'] = ''

            # 格式化时长
            d = info["duration"]
            song_info["duration"] = f"{int(d//60)}:{int(d%60):02}"

            song_info_list.append(song_info)

        return song_info_list

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
        url = f'http://www.kuwo.cn/url?rid={rid}&type=convert_url3&br={br}mp3'
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            play_url = json.loads(response.text)['url']
        except:
            play_url = ''

        return play_url

    @exceptionHandler
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

    @exceptionHandler
    def searchSong(self, key_word: str, quality='Standard quality', page_size=10):
        """ 搜索音乐

        Parameters
        ----------
        key_word: str
            搜索关键词

        quality: str
            歌曲音质，有 `Standard quality`、`High quality` 和 `Super quality` 三种

        page_size: int
            最多返回歌曲下载地址数
        """
        song_info_list = self.getSongInfoList(key_word, page_size)

        for song_info in song_info_list:
            song_info['songPath'] = self.getSongUrl(song_info['rid'], quality)

        return song_info_list

    @exceptionHandler
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


if __name__ == '__main__':
    crawler = KuWoMusicCrawler()
    song_info_list = crawler.search('aiko 微熱')
    if song_info_list:
        crawler.downloadSong(song_info_list[0], './')
