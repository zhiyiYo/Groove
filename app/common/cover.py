# coding:utf-8
from enum import Enum
from pathlib import Path
from .cache import albumCoverFolder
from .os_utils import adjustName
from .image_utils import getPicSuffix


class CoverType(Enum):
    """ Cover type """

    ALBUM_BIG = ":/images/default_covers/album_200_200.png"
    ALBUM_SMALL = ":/images/default_covers/album_113_113.png"
    PLAYLIST_BIG = ":/images/default_covers/playlist_275_275.png"
    PLAYLIST_SMALL = ":/images/default_covers/playlist_135_135.png"


class Cover:
    """ Album cover """

    def __init__(self, singer: str, album: str):
        """
        Parameters
        ----------
        singer: str
            singer name

        album: str
            album name
        """
        self.singer = singer or ''
        self.album = album or ''
        self.name = adjustName(self.singer + "_" + self.album)
        self.folder = albumCoverFolder / self.name

    def path(self, coverType=CoverType.ALBUM_BIG) -> str:
        """ get cover path

        Parameters
        ----------
        coverType: CoverType
            cover type
        """
        cover = coverType.value
        folder = albumCoverFolder / self.name
        files = [i for i in folder.glob('*') if i.is_file()]

        # use the first image file in directory
        if files and files[0].suffix.lower() in (".png", ".jpg", ".jpeg", ".jiff", ".gif"):
            cover = str(files[0])

        return cover

    def isExists(self):
        """ Whether this cover exists """
        return Path(self.path()).exists()

    def save(self, data: bytes):
        """ save cover

        Parameters
        ----------
        data: bytes
            album cover data

        Returns
        -------
        path: str
            save path of album cover
        """
        self.folder.mkdir(exist_ok=True, parents=True)
        path = self.folder / ("cover" + getPicSuffix(data))
        with open(path, "wb") as f:
            f.write(data)

        return str(path)