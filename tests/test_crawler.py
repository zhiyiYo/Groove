# coding:utf-8
import sys
sys.path.append('./app')

from unittest import TestCase
from app.common.crawler import KuGouMusicCrawler, KuWoMusicCrawler, WanYiMusicCrawler, QQMusicCrawler
from pprint import pprint


class TestKuGouMusicCrawler(TestCase):
    """ 测试酷狗爬虫 """

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.crawler = KuGouMusicCrawler()
        self.keyWord = 'aiko'

    def test_get_song_infos(self):
        """ 测试获取歌曲信息列表 """
        songInfos, _ = self.crawler.getSongInfos(self.keyWord, 1, 20)
        self.assertEqual(len(songInfos), 20)

    def test_get_song_url(self):
        """ 测试获取歌曲播放地址 """
        songInfos, _ = self.crawler.getSongInfos('aiko 食べた愛', 1, 1)
        url = self.crawler.getSongUrl(songInfos[0])
        print(url)

    def test_get_lyric(self):
        """ 测试获取歌词 """
        lyric = self.crawler.getLyric('aiko 食べた愛')
        pprint(lyric)

    def test_get_mv_infos(self):
        """ 测试获取 MV 信息 """
        songInfos, _ = self.crawler.getMvInfos('aiko 食べた愛')
        self.assertEqual(len(songInfos), 2)

    def test_get_mv_url(self):
        """ 测试获取 MV 播放地址 """
        mvInfos, _ = self.crawler.getMvInfos('aiko 食べた愛')
        url = self.crawler.getMvUrl(mvInfos[0])
        print(url)


class TestKuWoMusicCrawler(TestCase):
    """ 测试酷我爬虫 """

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.crawler = KuWoMusicCrawler()
        self.keyWord = 'aiko'

    def test_get_song_infos(self):
        """ 测试获取歌曲信息列表 """
        songInfos, _ = self.crawler.getSongInfos(self.keyWord, 1, 20)
        self.assertEqual(len(songInfos), 20)

    def test_get_song_url(self):
        """ 测试获取歌曲播放地址 """
        songInfos, _ = self.crawler.getSongInfos('aiko 食べた愛', 1, 1)
        url = self.crawler.getSongUrl(songInfos[0])
        print(url)

    def test_get_lyric(self):
        """ 测试获取歌词 """
        lyric = self.crawler.getLyric('aiko 食べた愛')
        pprint(lyric)

    def test_get_mv_infos(self):
        """ 测试获取 MV 信息 """
        songInfos, _ = self.crawler.getMvInfos('aiko 食べた愛')
        self.assertEqual(len(songInfos), 1)

    def test_get_mv_url(self):
        """ 测试获取 MV 播放地址 """
        mvInfos, _ = self.crawler.getMvInfos('aiko 食べた愛')
        url = self.crawler.getMvUrl(mvInfos[0])
        print(url)


class TestWanYiMusicCrawler(TestCase):
    """ 测试网易爬虫 """

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.crawler = WanYiMusicCrawler()
        self.keyWord = 'aiko'

    def test_get_song_infos(self):
        """ 测试获取歌曲信息列表 """
        songInfos, _ = self.crawler.getSongInfos(self.keyWord, 1, 20)
        self.assertEqual(len(songInfos), 20)

    def test_get_song_url(self):
        """ 测试获取歌曲播放地址 """
        songInfos, _ = self.crawler.getSongInfos('aiko 食べた愛', 1, 1)
        url = self.crawler.getSongUrl(songInfos[0])
        print(url)

    def test_get_lyric(self):
        """ 测试获取歌词 """
        lyric = self.crawler.getLyric('aiko 食べた愛')
        pprint(lyric)

    def test_get_mv_infos(self):
        """ 测试获取 MV 信息 """
        songInfos, _ = self.crawler.getMvInfos('aiko 食べた愛')
        self.assertEqual(len(songInfos), 1)

    def test_get_mv_url(self):
        """ 测试获取 MV 播放地址 """
        mvInfos, _ = self.crawler.getMvInfos('aiko 食べた愛')
        url = self.crawler.getMvUrl(mvInfos[0])
        print(url)


class TestQQMusicCrawler(TestCase):
    """ 测试QQ音乐爬虫 """

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.crawler = QQMusicCrawler()
        self.keyWord = 'aiko'

    def test_get_song_infos(self):
        """ 测试获取歌曲信息列表 """
        songInfos, _ = self.crawler.getSongInfos(self.keyWord, 1, 20)
        self.assertEqual(len(songInfos), 20)

    def test_get_song_url(self):
        """ 测试获取歌曲播放地址 """
        songInfos, _ = self.crawler.getSongInfos('aiko 食べた愛', 1, 1)
        url = self.crawler.getSongUrl(songInfos[0])
        print(url)

    def test_get_lyric(self):
        """ 测试获取歌词 """
        lyric = self.crawler.getLyric('aiko 食べた愛')
        self.assertTrue(lyric)
        pprint(lyric)

    def test_get_mv_infos(self):
        """ 测试获取 MV 信息 """
        songInfos, _ = self.crawler.getMvInfos('aiko 食べた愛')
        self.assertEqual(len(songInfos), 1)

    def test_get_mv_url(self):
        """ 测试获取 MV 播放地址 """
        mvInfos, _ = self.crawler.getMvInfos('aiko 食べた愛')
        url = self.crawler.getMvUrl(mvInfos[0])
        print(url)
