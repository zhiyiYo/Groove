# coding:utf-8
from common.meta_data_getter import *
from PyQt5.QtCore import Qt, pyqtSignal, QThread


class GetInfoThread(QThread):
    """ 获取指定文件夹中音频文件信息线程 """

    scanFinished = pyqtSignal(list, list, dict)

    def __init__(self, folderPaths: list, parent=None):
        super().__init__(parent=parent)
        self.folderPaths = folderPaths

    def run(self):
        """ 获取信息 """
        songInfoGetter = SongInfoGetter(self.folderPaths)
        albumCoverGetter = AlbumCoverGetter(songInfoGetter.songInfo_list)
        albumInfoGetter = AlbumInfoGetter(songInfoGetter.songInfo_list)
        singerInfoGetter = SingerInfoGetter(albumInfoGetter.albumInfo_list)

        self.scanFinished.emit(songInfoGetter.songInfo_list,
                               albumInfoGetter.albumInfo_list, singerInfoGetter.singerInfos)
