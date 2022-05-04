# coding:utf-8
import re
from pathlib import Path

from PyQt5.QtSql import QSqlDatabase
from common.database.service import PlaylistService

from win32gui import GetDC, ReleaseDC
from win32print import GetDeviceCaps
from win32con import DESKTOPHORZRES, HORZRES
from win32com.shell import shell, shellcon


def moveToTrash(path: str):
    """ move file to system recycle bin """
    shell.SHFileOperation((0, shellcon.FO_DELETE, path, None, shellcon.FOF_SILENT |
                           shellcon.FOF_ALLOWUNDO | shellcon.FOF_NOCONFIRMATION, None, None))


def adjustName(name: str):
    """ adjust file name

    Returns
    -------
    name: str
        file name after adjusting
    """
    name = re.sub(r'[\\/:*?"<>|\r\n]+', "_", name).strip()
    return name


def getCoverName(singer: str, album: str):
    """ get album cover name

    Parameters
    ----------
    singer: str
        singer name

    album name: str
        album name

    Returns
    -------
    name: str
        album cover name
    """
    singer = singer or ''
    album = album or ''
    return adjustName(singer + '_' + album)


def getCoverPath(singer: str, album: str, coverType: str) -> str:
    """ get cover path

    Parameters
    ----------
    singer: str
        singer name

    album: str
        album name

    coverType: str
        cover type, including:
        * `album_big` - big default album cover
        * `album_small` - small default album cover
        * `playlist_big` - big default playlist cover
        * `playlist_small` - small default playlist cover
    """
    cover_paths = {
        "album_big": ":/images/default_covers/album_200_200.png",
        "album_small": ":/images/default_covers/album_113_113.png",
        "playlist_big": ":/images/default_covers/playlist_275_275.png",
        "playlist_small": ":/images/default_covers/playlist_135_135.png",
    }
    if coverType not in cover_paths:
        raise ValueError(f"`{coverType}` is not supported")

    cover = cover_paths[coverType]
    folder = Path("cache/Album_Cover") / getCoverName(singer, album)
    files = [i for i in folder.glob('*') if i.is_file()]

    # use the first image file in directory
    if files and files[0].suffix.lower() in (".png", ".jpg", ".jpeg", ".jiff", ".gif"):
        cover = str(files[0])

    return cover


def getSingerAvatarPath(singer: str, size='small'):
    """ get singer avatar path

    Parameters
    ----------
    singer: str
        singer name

    size: str
        size of default avatar, could be `small` or `big`
    """
    avatar_paths = {
        "big": ":/images/default_covers/singer_295_295.png",
        "small": ":/images/default_covers/singer_200_200.png",
    }
    if size not in avatar_paths:
        raise ValueError(f"`{size}` size is not supported")

    avatar = avatar_paths[size]
    singer = adjustName(singer) if singer else ''
    folder = Path("cache/singer_avatar") / singer
    files = [i for i in folder.glob('*') if i.is_file()]

    # use the first image file in directory
    if files and files[0].suffix.lower() in (".png", ".jpg", ".jpeg", ".jiff", ".gif"):
        avatar = str(files[0])

    return avatar


def getPlaylistNames():
    """ get all playlist names in database """
    db = QSqlDatabase.database('main')
    service = PlaylistService(db)
    return [i.name for i in service.listAll()]


def getDevicePixelRatio():
    """ get dpi scale ratio """
    hdc = GetDC(None)
    t = GetDeviceCaps(hdc, DESKTOPHORZRES)
    d = GetDeviceCaps(hdc, HORZRES)
    ReleaseDC(None, hdc)
    return t / d
