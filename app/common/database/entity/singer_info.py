# coding:utf-8
from typing import List
from .entity import Entity
from .album_info import AlbumInfo
from dataclasses import dataclass, field


@dataclass
class SingerInfo(Entity):
    """ 歌手信息实体类 """

    id: str = None
    singer: str = None
    genre: str = None
    albumInfos: List[AlbumInfo] = field(default_factory=list)
