from .entity import Entity
from .song_info import SongInfo
from .album_info import AlbumInfo
from .singer_info import SingerInfo
from .playlist import Playlist, SongPlaylist


class EntityFactory:
    """ 实体类工厂 """

    @staticmethod
    def create(table: str):
        """ 创建一个实体类对象

        Parameters
        ----------
        table: str
            实体类对应的表名

        Returns
        -------
        entity:
            实体类对象
        """
        tables = {
            "tbl_song_info": SongInfo,
            "tbl_album_info": AlbumInfo,
            "tbl_singer_info": SingerInfo,
            "tbl_playlist": Playlist,
            "tbl_song_playlist": SongPlaylist
        }
        if table not in tables:
            raise ValueError(f"表名 `{table}` 非法")

        return tables[table]()
