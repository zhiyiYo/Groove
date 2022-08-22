# encoding: utf-8
import json
from pathlib import Path
from typing import Dict, List, Union

from .parser import (KuGouLyricParser, KuWoLyricParser, LyricParserBase,
                     QQLyricParser, WanYiLyricParser)


class Lyric:
    """ lyric """

    def __init__(self, lyric: Dict[str, List[str]]):
        self.lyric = lyric

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

    def load(self, key, default=None):
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

        return Lyric(LyricParserBase.error_lyric)

    @staticmethod
    def load(path: Union[str, Path]):
        """ load lyric from `.json` or `.lrc` lyric file """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"The lyric file `{path}` does not exist.")

        suffix = path.suffix.lower()
        with open(path, encoding='utf-8') as f:
            if suffix == ".lrc":
                return Lyric.parse(f.read())
            elif suffix == ".json":
                return Lyric(json.load(f))

            return Lyric(LyricParserBase.error_lyric)

    def save(self, path: Union[str, Path]):
        """ save lyric """
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.lyric, f, ensure_ascii=False, indent=4)
