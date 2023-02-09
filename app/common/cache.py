# encoding:utf-8
from pathlib import Path
from .config import config


cacheFolder = Path(config.get(config.cacheFolder))
dbPath = cacheFolder / "cache.db"
lyricFolder = cacheFolder / "Lyric"
albumCoverFolder = cacheFolder / "AlbumCover"
lastPlaylistFolder = cacheFolder / "LastPlaylist"
singerAvatarFolder = cacheFolder / "SingerAvatar"
crawlAlbumCoverFolder = cacheFolder / "CrawlAlbumCover"