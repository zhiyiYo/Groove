# coding:utf-8
import re
import sys
from pathlib import Path
from platform import platform
from typing import Union

from PyQt5.QtCore import QDir, QFileInfo, QProcess, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtSql import QSqlDatabase

from common.database import DBInitializer
from common.database.service import PlaylistService


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
    db = QSqlDatabase.database(DBInitializer.connectionName)
    service = PlaylistService(db)
    return [i.name for i in service.listAll()]


def getWindowsVersion():
    if "Windows-7" in platform():
        return 7

    build = sys.getwindowsversion().build
    version = 10 if build < 22000 else 11
    return version


def showInFolder(path: Union[str, Path]):
    """ show file in file explorer """
    if isinstance(path, Path):
        path = str(path.absolute())

    if not path or path.lower() == 'http':
        return

    if path.startswith('http'):
        QDesktopServices.openUrl(QUrl(path))
        return

    info = QFileInfo(path)   # type:QFileInfo
    if sys.platform == "win32":
        args = [QDir.toNativeSeparators(path)]
        if not info.isDir():
            args.insert(0, '/select,')

        QProcess.startDetached('explorer', args)
    elif sys.platform == "darwin":
        args = [
            "-e", 'tell application "Finder"', "-e", "activate",
            "-e", f'select POSIX file "{path}"', "-e", "end tell",
            "-e", "return"
        ]
        QProcess.execute("/usr/bin/osascript", args)
    else:
        url = QUrl.fromLocalFile(path if info.isDir() else info.path())
        QDesktopServices.openUrl(url)
