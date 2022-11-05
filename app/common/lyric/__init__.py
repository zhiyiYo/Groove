# encoding: utf-8
import json
from pathlib import Path
from typing import Dict, List, Union

from common.os_utils import adjustName
from common.cache import lyricFolder

from .parser import (KuGouLyricParser, KuWoLyricParser, LyricParserBase,
                     QQLyricParser, WanYiLyricParser)


class Lyric:
    """ lyric """

    def __init__(self, lyric: Dict[str, List[str]]):
        if self._isValidLyric(lyric):
            self.lyric = lyric
        else:
            self.lyric = LyricParserBase.error_lyric

    def __bool__(self):
        return bool(self.lyric)

    def __len__(self):
        return len(self.lyric)

    def __contains__(self, time: str):
        return time in self.lyric

    def __getitem__(self, key: str):
        return self.lyric[key]

    def __setitem__(self, key, value):
        self.lyric[key] = value

    def __eq__(self, other) -> bool:
        if other is None:
            return False

        return self.lyric == other.lyric

    def __repr__(self) -> str:
        return repr(self.lyric)

    def get(self, key, default=None):
        return self.lyric.get(key, default)

    def keys(self):
        return self.lyric.keys()

    def times(self):
        return list(self.keys())

    def values(self):
        return self.lyric.values()

    def texts(self):
        return list(self.values())

    def items(self):
        return self.lyric.items()

    def isError(self):
        """ Is the lyrics equal to `LyricParserBase.error_lyric` """
        return self.lyric == LyricParserBase.error_lyric

    def isEmpty(self):
        """ Is the lyrics empty or equal to `LyricParserBase.none_lyric` """
        return self.lyric in [LyricParserBase.none_lyric, {}]

    def isValid(self):
        """ Is the lyric has available content """
        return not (self.isEmpty() or self.isError())

    def hasTranslation(self):
        return any([len(i) > 1 for i in self.texts()])

    @staticmethod
    def new():
        """ create an lyric whose content is equals to `LyricParserBase.none_lyric` """
        return Lyric(LyricParserBase.none_lyric)

    @staticmethod
    def error():
        """ create an lyric whose content is equals to `LyricParserBase.error_lyric` """
        return Lyric(LyricParserBase.error_lyric)

    @staticmethod
    def parse(lyric):
        """ parse lyric """
        parsers = [KuWoLyricParser, WanYiLyricParser, KuGouLyricParser,
                   QQLyricParser]  # type:List[LyricParserBase]

        for parser in parsers:
            if parser.can_parse(lyric):
                try:
                    parsed_lyric = parser.parse(lyric)
                    if parsed_lyric:
                        return Lyric(parsed_lyric)
                except:
                    pass

        return Lyric.error()

    @staticmethod
    def load(path: Union[str, Path], ignoreError=False):
        """ load lyric from `.json` or `.lrc` lyric file """
        path = Path(path)
        if not path.exists():
            if not ignoreError:
                raise FileNotFoundError(f"The lyric file `{path}` does not exist.")

            return Lyric.error()

        suffix = path.suffix.lower()
        with open(path, encoding='utf-8') as f:
            if suffix == ".lrc":
                return Lyric.parse(f.read())
            elif suffix == ".json":
                return Lyric(json.load(f))

            return Lyric.error()

    @staticmethod
    def path(singer: str, title: str):
        """ get lyrics file path """
        file = adjustName(f'{singer}_{title}.json')
        return lyricFolder / file

    def save(self, path: Union[str, Path]):
        """ save lyric """
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.lyric, f, ensure_ascii=False, indent=4)

    def serialize(self) -> str:
        """ serialize lyrics to string """
        lyrics = []
        for time, lyric in self.lyric.items():
            time = float(time)
            m, s = int(time//60), time % 60
            t = f"[{m:02}:{s:05.2f}]"
            line = t + lyric[0]
            if len(lyric) == 2:
                line += f"\r\n{t}{lyric[1]}"

            lyrics.append(line)

        return "\r\n".join(lyrics)

    @staticmethod
    def _isValidLyric(lyric):
        """ is valid json lyric """
        if not isinstance(lyric, dict):
            return False

        for k, v in lyric.items():
            if not isinstance(k, str):
                return False

            try:
                float(k)
            except:
                return False

            if not isinstance(v, list) or not (v and all([isinstance(i, str) for i in v])):
                return False

        return True

    @staticmethod
    def _isnumeric(key: str):
        try:
            float(key)
            return True
        except:
            return False
