# coding: utf-8
from typing import Union
from pathlib import Path


class Directory:
    """ 文件夹类 """

    audio_formats = ['.mp3', '.flac', '.mp4', '.m4a']

    def __init__(self, path: str):
        """
        Parameters
        ----------
        path: str
            文件夹路径
        """
        self.path = Path(path)

    def glob(self):
        """ 获取所有音频文件路径 """
        return [i.absolute() for i in self.path.glob('*') if self.isAudio(i)]

    def isAudio(self, path: Union[str, Path]):
        """ 判断一个路径是否为音频文件 """
        if not isinstance(path, Path):
            path = Path(path)

        return path.is_file() and path.suffix.lower() in self.audio_formats
