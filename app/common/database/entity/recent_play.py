# coding:utf-8
from .entity import Entity
from dataclasses import dataclass


@dataclass
class RecentPlay(Entity):
    """ Recent play """

    file: str = None
    lastPlayedTime: int = None
    frequency: int = 1
