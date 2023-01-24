# coding: utf-8
from typing import Union
from pathlib import Path
from common.meta_data.reader import SongInfoReader

from PyQt5.QtCore import QObject, pyqtSignal


class Directory(QObject):
    """ Audio directory class """

    formats = SongInfoReader.formats

    fileAdded = pyqtSignal(list)
    fileRemoved = pyqtSignal(list)

    def __init__(self, path: str):
        """
        Parameters
        ----------
        path: str
            path of audio directory
        """
        super().__init__()
        self.path = Path(path)
        self.audioFiles = self.glob()

    def glob(self, recursive=False):
        """ get all audio file paths """
        if not self.path.exists():
            return []

        paths = self.path.rglob('*') if recursive else self.path.iterdir()
        return [i.absolute() for i in paths if self.isAudio(i)]

    def update(self):
        """ update audio directory

        Returns
        -------
        changedFiles: Dict[str, List[Path]]
            a dict containing a list of files added and deleted
        """
        files = self.glob()
        filesSet = set(files)
        oldFilesSet = set(self.audioFiles)
        self.audioFiles = files

        added = list(filesSet - oldFilesSet)
        if added:
            self.fileAdded.emit(added)

        removed = list(oldFilesSet - filesSet)
        if removed:
            self.fileRemoved.emit(removed)

    @classmethod
    def isAudio(cls, path: Union[str, Path]):
        """ determine whether a path is an audio file """
        if not isinstance(path, Path):
            path = Path(path)

        return path.is_file() and path.suffix.lower() in cls.formats
