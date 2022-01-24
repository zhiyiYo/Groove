# coding:utf-8
from typing import List
from .entity import Entity
from .song_info import SongInfo
from dataclasses import dataclass, field


@dataclass
class AlbumInfo(Entity):
    """ 专辑信息实体类 """

    id: str = None
    singer: str = None
    album: str = None
    year: int = None
    genre: str = None
    modifiedTime: int = None
    songInfos: List[SongInfo] = field(default_factory=list)
