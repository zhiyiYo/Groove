# coding:utf-8
from typing import List, Dict


class LyricParserBase:
    """ 歌词解析器基类 """

    default_lyric = {'0.0': ['暂无歌词']}
    error_lyric = {'0.0': ['无法解析歌词']}

    @staticmethod
    def can_parse(lyric) -> bool:
        """ 能否解析歌词 """
        raise NotImplementedError("该方法必须被子类实现")

    @classmethod
    def parse(cls, lyric) -> Dict[str, List[str]]:
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

    @classmethod
    def parse(cls, lyric: List[Dict[str, str]]) -> Dict[str, List[str]]:
        if not lyric:
            return cls.default_lyric

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


class KuGouLyricParser(LyricParserBase):
    """ 酷狗音乐歌词解析器 """

    @staticmethod
    def can_parse(lyric) -> bool:
        if lyric is None:
            return True

        if isinstance(lyric, str):
            if not lyric:
                return True

            for i in ['[id:$', '[ti:', '[ar:', '[al:', '[by:', '[offset:']:
                if i in lyric:
                    return True

        return False

    @classmethod
    def parse(cls, lyric: str) -> Dict[str, List[str]]:
        if not lyric:
            return cls.default_lyric

        lyric = lyric.split('\r\n')[:-1]  # type:list

        # 制作歌词
        lyrics = {}
        for line in lyric:
            time, text = line.split(']')
            time = time[1:]
            minutes, seconds = time.split(':')
            if minutes.isnumeric():
                time = str(float(minutes)*60 + float(seconds))
                lyrics[time] = [text]

        return lyrics


def parse_lyric(lyric) -> Dict[str, List[str]]:
    """ 解析歌词 """
    parsers = [KuWoLyricParser, KuGouLyricParser]
    available_parsers = [i for i in parsers if i.can_parse(lyric)]

    if not available_parsers:
        return LyricParserBase.error_lyric

    parser = available_parsers[0]
    return parser.parse(lyric)
