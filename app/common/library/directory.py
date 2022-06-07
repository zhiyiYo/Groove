# coding: utf-8
from typing import Union
from pathlib import Path
from itertools import chain
from common.meta_data.reader import SongInfoReader


class Directory:
    """ Audio directory class """

    audio_formats = list(chain.from_iterable(
        [r.formats for r in SongInfoReader.readers]))

    def __init__(self, path: str):
        """
        Parameters
        ----------
        path: str
            path of audio directory
        """
        self.path = Path(path)
        self.audioFiles = self.glob()

    def glob(self):
        """ get all audio file paths """
        return [i.absolute() for i in self.path.iterdir() if self.isAudio(i)]

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
        changedFiles = {
            "added": list(filesSet - oldFilesSet),
            "removed": list(oldFilesSet - filesSet)
        }
        self.audioFiles = files
        return changedFiles

    @classmethod
    def isAudio(cls, path: Union[str, Path]):
        """ determine whether a path is an audio file """
        if not isinstance(path, Path):
            path = Path(path)

        return path.is_file() and path.suffix.lower() in cls.audio_formats
