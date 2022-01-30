# coding:utf-8
from typing import List
from .entity import Entity
from .song_info import SongInfo
from dataclasses import dataclass, field


@dataclass
class Playlist(Entity):
    """ 播放列表实体类 """

    name: str = None
    singer: str = None
    album: str = None
    count: int = 0
    modifiedTime: int = None
    songInfos: List[SongInfo] = field(default_factory=list)


@dataclass
class SongPlaylist(Entity):
    """ 歌曲文件-播放列表中间表实体类 """

    id: str = None
    file: str = None
    name: str = None
