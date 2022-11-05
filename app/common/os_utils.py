# coding:utf-8
import re
import sys
from pathlib import Path
from platform import platform
from typing import Union

from PyQt5.QtCore import QDir, QFileInfo, QProcess, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtSql import QSqlDatabase

from common.cache import lyricFolder
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
    return name.rstrip(".")


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
