# coding:utf-8
from common.meta_data import *
from PyQt5.QtCore import Qt, pyqtSignal, QThread


class GetInfoThread(QThread):
    """ 获取指定文件夹中音频文件信息线程 """

    scanFinished = pyqtSignal(list, list, dict)

    def __init__(self, folderPaths: list, parent=None):
        super().__init__(parent=parent)
        self.folderPaths = folderPaths

    def run(self):
        """ 获取信息 """
        songInfoReader = SongInfoReader(self.folderPaths)
        albumCoverReader = AlbumCoverReader(songInfoReader.songInfos)
        albumInfoReader = AlbumInfoReader(songInfoReader.songInfos)
        singerInfoReader = SingerInfoReader(albumInfoReader.albumInfos)

        self.scanFinished.emit(songInfoReader.songInfos,
                               albumInfoReader.albumInfos, singerInfoReader.singerInfos)
