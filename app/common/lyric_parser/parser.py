# coding:utf-8
from typing import List, Dict
from pprint import pprint


class LyricParserBase:
    """ 歌词解析器基类 """

    @staticmethod
    def can_parse(lyric) -> bool:
        """ 能否解析歌词 """
        raise NotImplementedError("该方法必须被子类实现")

    @staticmethod
    def parse(lyric) -> Dict[str, List[str]]:
        """ 解析歌词 """
        raise NotImplementedError("该方法必须被子类实现")


class KuWoLyricParser(LyricParserBase):
    """ 酷我音乐歌词解析器 """

    @staticmethod
    def can_parse(lyric: List[Dict[str, str]]) -> bool:
        if lyric is None:
            return True

        if isinstance(lyric, list):
            # 可以解析空列表
            if not lyric:
                return True

            return list(lyric[0].keys()) == ['lineLyric', 'time']

        return False

    @staticmethod
    def parse(lyric: List[Dict[str, str]]) -> Dict[str, List[str]]:
        if not lyric:
            return {'0.0': ['暂无歌词']}

        times = [i['time'] for i in lyric]

        # 判断是否有翻译
        times_ = times[1:]+[times[-1]]
        is_trans = [t1 == t2 and t1 != '0.0' for t1, t2 in zip(times, times_)]
        is_trans[-1] = sum(is_trans) > 1

        # 制作歌词
        lyrics = {}  # Dict[str, List[str]]
        for i, trans in enumerate(is_trans):
            if trans:
                times[i] = times[i-1]

            line = lyric[i]['lineLyric']

            if not lyrics.get(times[i]):
                lyrics[times[i]] = [line]
            else:
                lyrics[times[i]].append(line)

        return lyrics


def parse_lyric(lyric) -> Dict[str, List[str]]:
    """ 解析歌词 """
    parsers = [KuWoLyricParser]
    available_parsers = [i for i in parsers if i.can_parse(lyric)]

    if not available_parsers:
        raise ValueError('没有可用于解析该歌词的解析器')

    parser = available_parsers[0]
    return parser.parse(lyric)
