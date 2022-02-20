# coding:utf-8
from typing import List, Dict


class LyricParserBase:
    """ Lyrics parser base class """

    none_lyric = {'0.0': ['暂无歌词']}
    error_lyric = {'0.0': ['无法解析歌词']}

    @staticmethod
    def can_parse(lyric) -> bool:
        """ can the parser parse the lyrics """
        raise NotImplementedError("该方法必须被子类实现")

    @classmethod
    def parse(cls, lyric) -> Dict[str, List[str]]:
        """ parse lyrics """
        raise NotImplementedError("该方法必须被子类实现")


class KuWoLyricParser(LyricParserBase):
    """ Lyric parser for KuWo Music """

    @staticmethod
    def can_parse(lyric: List[Dict[str, str]]) -> bool:
        if lyric is None:
            return True

        if isinstance(lyric, list):
            if not lyric:
                return True

            return list(lyric[0].keys()) == ['lineLyric', 'time']

        return False

    @classmethod
    def parse(cls, lyric: List[Dict[str, str]]) -> Dict[str, List[str]]:
        if not lyric:
            return cls.none_lyric

        times = [i['time'] for i in lyric]

        # determine if there is a translation
        times_ = times[1:] + [times[-1]]
        is_trans = [t1 == t2 and t1 != '0.0' for t1, t2 in zip(times, times_)]
        is_trans[-1] = sum(is_trans) > 1

        # make lyrics
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
    """ Lyric parser for KuGou Music """

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
            return cls.none_lyric

        lyric = lyric.split('\r\n')[:-1]  # type:list

        # make lyrics
        lyrics = {}
        for line in lyric:
            time, text = line.split(']')
            time = time[1:]
            minutes, seconds = time.split(':')
            if minutes.isnumeric():
                time = str(float(minutes)*60 + float(seconds))
                lyrics[time] = [text]

        return lyrics


class WanYiLyricParser(LyricParserBase):
    """ Lyric parser for WanYiYun Music """

    @staticmethod
    def can_parse(lyric) -> bool:
        if lyric is None:
            return True

        if isinstance(lyric, dict):
            if not lyric:
                return True

            return list(lyric.keys()) == ['lyric', 'tlyric']

        return False

    @classmethod
    def parse(cls, lyric: dict) -> Dict[str, List[str]]:
        if not lyric:
            return cls.none_lyric

        lyrics_ = {}

        # original lyrics
        for line in lyric['lyric'].split('\n'):
            if ']' not in line:
                continue

            time, text = line.split(']')
            if text and time[1:]:
                lyrics_[time[1:]] = [text]

        # translate lyrics
        for line in lyric['tlyric'].split('\n'):
            if ']' not in line:
                continue

            time, text = line.split(']')
            if time[1:] in lyrics_:
                lyrics_[time[1:]].append(text)

        lyrics = {}
        for time, v in lyrics_.items():
            minutes, seconds = time.split(':')
            time = str(float(minutes)*60 + float(seconds))
            lyrics[time] = v

        return lyrics


def parse_lyric(lyric) -> Dict[str, List[str]]:
    """ parse lyrics """
    parsers = [KuWoLyricParser, WanYiLyricParser, KuGouLyricParser]

    for parser in parsers:
        if parser.can_parse(lyric):
            return parser.parse(lyric)

    return LyricParserBase.error_lyric