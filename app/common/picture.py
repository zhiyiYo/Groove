# coding:utf-8
from enum import Enum
from pathlib import Path
from .cache import albumCoverFolder, singerAvatarFolder
from .os_utils import adjustName
from .image_utils import getPicSuffix


class CoverType(Enum):
    """ Cover type """

    ALBUM_BIG = ":/images/default_covers/album_200_200.png"
    ALBUM_SMALL = ":/images/default_covers/album_113_113.png"
    PLAYLIST_BIG = ":/images/default_covers/playlist_275_275.png"
    PLAYLIST_SMALL = ":/images/default_covers/playlist_135_135.png"


class AvatarType(Enum):
    """ Singer Avatar type """

    BIG = ":/images/default_covers/singer_295_295.png"
    SMALL = ":/images/default_covers/singer_200_200.png"


class Picture:
    """ Picture class """

    parentFolder = Path()
    pictureName = "picture"

    def __init__(self, name: str):
        """
        Parameters
        ----------
        name: str
            picture folder name
        """
        self.name = adjustName(name)
        self.folder = self.parentFolder/self.name

    @classmethod
    def listNames(cls):
        """ list all picture names """
        return [i.name for i in cls.parentFolder.glob("*") if i.is_dir()]

    def path(self, pictureType: Enum) -> str:
        """ get picture path

        Parameters
        ----------
        pictureType: Enum
            picture type

        Returns
        -------
        picPath: str
            picture path
        """
        picPath = pictureType.value
        files = [i for i in self.folder.glob('*') if i.is_file()]

        # use the first image file in directory
        if files and files[0].suffix.lower() in (".png", ".jpg", ".jpeg", ".jiff", ".gif"):
            picPath = str(files[0])

        return picPath

    def isExists(self):
        """ Whether this cover exists """
        return Path(self.path()).exists()

    def save(self, data: bytes):
        """ save picture

        Parameters
        ----------
        data: bytes
            picture data

        Returns
        -------
        path: str
            save path of picture
        """
        self.folder.mkdir(exist_ok=True, parents=True)
        path = self.folder / (self.pictureName + getPicSuffix(data))
        with open(path, "wb") as f:
            f.write(data)

        return str(path)


class Cover(Picture):
    """ Album cover """

    parentFolder = albumCoverFolder
    pictureName = "cover"

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
        super().__init__(self.singer + "_" + self.album)

    def path(self, coverType=CoverType.ALBUM_BIG) -> str:
        return super().path(coverType)


class Avatar(Picture):
    """ Singer avatar """

    parentFolder = singerAvatarFolder
    pictureName = "avatar"

    def __init__(self, singer: str):
        """
        Parameters
        ----------
        singer: str
            singer name
        """
        self.singer = singer or ''
        super().__init__(self.singer)

    def path(self, avatarType=AvatarType.SMALL) -> str:
        return super().path(avatarType)
