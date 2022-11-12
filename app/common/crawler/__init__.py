from enum import Enum

from .crawler_base import CrawlerBase, MvQuality, SongQuality
from .kugou_music_crawler import KuGouMusicCrawler
from .kuwo_music_crawler import KuWoFakeSongUrl, KuWoMusicCrawler
from .qq_music_crawler import QQMusicCrawler
from .wanyi_music_crawler import WanYiMusicCrawler


class QueryServerType(Enum):
    """ Query server enumerate class """
    KUWO = 0
    KUGOU = 1
    WANYI = 2
    QQ = 3
