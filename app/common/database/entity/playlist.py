# coding:utf-8
from typing import List
from .entity import Entity
from .song_info import SongInfo
from dataclasses import dataclass, field


@dataclass
class Playlist(Entity):
    """ Custom playlist """

    name: str = None
    singer: str = None
    album: str = None
    count: int = 0
    modifiedTime: int = None
    songInfos: List[SongInfo] = field(default_factory=list)


@dataclass
class SongPlaylist(Entity):
    """ Audio file - playlist """

    id: str = None
    file: str = None
    name: str = None
