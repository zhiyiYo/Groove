# coding:utf-8
from typing import List, Tuple


class CrawlerBase:
    """ 爬虫抽象类 """

    def __init__(self):
        self.qualities = ['Standard quality', 'High quality', 'Super quality']

    def getSongInfoList(self, key_word: str, page_num=1, page_size=10) -> Tuple[List[dict], int]:
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
            歌曲信息列表，没找到任何歌曲时为空列表

        total: int
            数据库中符合搜索条件的歌曲总数
        """
        raise NotImplementedError("该方法必须被子类实现")

    def getLyric(self, key_word: str):
        """ 获取歌词

        Parameters
        ----------
        key_word: str
            关键词

        Returns
        -------
        lyric:
            歌词，如果没找到则返回 `None`
        """
        raise NotImplementedError("该方法必须被子类实现")

    def getSongUrl(self, song_info: dict, quality: str = 'Standard quality') -> str:
        """ 获取歌曲下载链接

        Parameters
        ----------
        song_info: dict
            歌曲信息

        quality: str
            歌曲音质，有 `Standard quality`、`High quality` 和 `Super quality` 三种

        Returns
        -------
        url: str
            歌曲下载链接，没找到时为空字符串

        Raises
        ------
        QualityException:
            当音质非法时引发的异常
        """
        raise NotImplementedError("该方法必须被子类实现")

    def downloadSong(self, song_info: dict, save_dir: str, quality: str = 'Standard quality') -> str:
        """ 下载歌曲

        Parameters
        ----------
        song_info: dict
            歌曲信息

        save_dir: str
            保存歌曲文件的目录

        quality: str
            歌曲音质，有 `Standard quality`、`High quality` 和 `Super quality` 三种

        Returns
        -------
        song_path: str
            歌曲保存路径，下载失败时返回空字符串

        Raises
        ------
        QualityException:
            当音质非法时引发的异常
        """
        raise NotImplementedError("该方法必须被子类实现")

    def getSingerAvatar(self, singer: str, save_dir: str):
        """ 获取歌手头像

        Parameters
        ----------
        singer: str
            歌手名称

        save_dir: str
            头像保存目录

        Returns
        -------
        save_path: str
            头像保存路径，头像获取失败则返回空字符串
        """
        raise NotImplementedError("该方法必须被子类实现")

    def search(self, key_word: str, page_num=1, page_size=10, quality: str = 'Standard quality') -> Tuple[List[dict], int]:
        """ 搜索歌曲并获得歌曲下载地址

        Parameters
        ----------
        key_word: str
            搜索关键词

        page_num: int
            当前页码

        page_size: int
            每一页最多显示的条目数量

        quality: str
            歌曲音质，有 `Standard quality`、`High quality` 和 `Super quality` 三种

        Returns
        -------
        song_info_list: List[dict]
            歌曲信息列表，没找到任何歌曲时为空列表

        total: int
            数据库中符合搜索条件的歌曲总数

        Raises
        ------
        QualityException:
            当音质非法时引发的异常
        """
        raise NotImplementedError("该方法必须被子类实现")


class QualityException(Exception):
    """ 音质异常 """

    def __init__(self, *args: object):
        super().__init__(*args)
