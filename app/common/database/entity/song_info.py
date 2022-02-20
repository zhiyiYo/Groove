# coding:utf-8
from .entity import Entity
from dataclasses import dataclass


@dataclass
class SongInfo(Entity):
    """ Song information """

    file: str = None
    title: str = None
    singer: str = None
    album: str = None
    year: int = None
    genre: str = None
    duration: int = None
    track: int = None
    trackTotal: int = None
    disc: int = None
    discTotal: int = None
    createTime: int = None
    modifiedTime: int = None
