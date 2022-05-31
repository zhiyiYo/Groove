from .entity import Entity
from .song_info import SongInfo
from .album_info import AlbumInfo
from .singer_info import SingerInfo
from .recent_play import RecentPlay
from .playlist import Playlist, SongPlaylist


class EntityFactory:
    """ Entity factory """

    @staticmethod
    def create(table: str):
        """ create an entity instance

        Parameters
        ----------
        table: str
            database table name corresponding to entity

        Returns
        -------
        entity:
            entity instance
        """
        tables = {
            "tbl_song_info": SongInfo,
            "tbl_album_info": AlbumInfo,
            "tbl_singer_info": SingerInfo,
            "tbl_playlist": Playlist,
            "tbl_song_playlist": SongPlaylist,
            "tbl_recent_play": RecentPlay,
        }
        if table not in tables:
            raise ValueError(f"Table name `{table}` is illegal")

        return tables[table]()
