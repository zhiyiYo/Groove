# coding:utf-8
from typing import List, Dict


class LyricParserBase:
    """ Lyrics parser base class """

    none_lyric = {'0.0': ['暂无歌词']}
    error_lyric = {'0.0': ['无法解析歌词']}

    @staticmethod
    def can_parse(lyric) -> bool:
        """ can the parser parse the lyrics """
        raise NotImplementedError

    @classmethod
    def parse(cls, lyric) -> Dict[str, List[str]]:
        """ parse lyrics """
        raise NotImplementedError


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
    def parse(cls, lyric: List[Dict[str, str]]):
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

            line = lyric[i]['lineLyric'].replace("&apos;", "'")

            if not lyrics.get(times[i]):
                lyrics[times[i]] = [line]
            else:
                lyrics[times[i]].append(line)

        return lyrics


class KuGouLyricParser(LyricParserBase):
    """ Lyric parser for KuGou Music """

    seperator = "\r\n"

    @staticmethod
    def can_parse(lyric) -> bool:
        if lyric is None:
            return True

        if isinstance(lyric, str):
            if not lyric:
                return True

            for i in ['[id:$', '[ti:', '[ar:', '[al:', '[by:', '[offset:', "\r\n"]:
                if i in lyric:
                    return True

        return False

    @classmethod
    def parse(cls, lyric: str):
        if not lyric:
            return cls.none_lyric

        lyric = lyric.split(cls.seperator)[:-1]  # type:list

        # make lyrics
        lyrics = {}
        for line in lyric:
            time, text = line.split(']')
            time = time[1:]
            minutes, seconds = time.split(':')
            if not minutes.isnumeric():
                continue

            time = str(float(minutes)*60 + float(seconds))
            if time not in lyrics:
                lyrics[time] = [text]
            else:
                lyrics[time].append(text)

        return lyrics


class QQLyricParser(KuGouLyricParser):
    """ Lyric parser for QQ Music """

    seperator = "\n"


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
    def parse(cls, lyric: dict):
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
            minutes, seconds = time.split(':')[:2]
            time = str(float(minutes)*60 + float(seconds))
            lyrics[time] = v

        return lyrics
