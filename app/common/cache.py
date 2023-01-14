# encoding:utf-8
from pathlib import Path


cacheFolder = Path("cache")
logFolder = cacheFolder / "Log"
dbPath = cacheFolder / "cache.db"
lyricFolder = cacheFolder / "Lyric"
albumCoverFolder = cacheFolder / "AlbumCover"
lastPlaylistFolder = cacheFolder / "LastPlaylist"
singerAvatarFolder = cacheFolder / "SingerAvatar"
crawlAlbumCoverFolder = cacheFolder / "CrawlAlbumCover"