# coding:utf-8
from common.meta_data.writer import writeSongInfo, writeAlbumCover
from PyQt5.QtCore import QThread, pyqtSignal


class SaveAlbumInfoThread(QThread):
    """ 保存专辑信息线程 """

    saveFinishedSignal = pyqtSignal(dict, dict, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.oldAlbumInfo = {}
        self.newAlbumInfo = {}
        self.coverPath = ''

    def setAlbumInfo(self, oldAlbumInfo: dict, newAlbumInfo: dict, coverPath: str):
        """ 设置专辑信息 """
        self.oldAlbumInfo = oldAlbumInfo
        self.newAlbumInfo = newAlbumInfo
        self.coverPath = coverPath

    def run(self):
        """ 保存专辑信息 """
        for i, songInfo in enumerate(self.newAlbumInfo["songInfo_list"]):
            # 修改封面数据
            writeAlbumCover(songInfo['songPath'], self.coverPath)

            # 如果歌曲保存失败就重置歌曲信息
            if not writeSongInfo(songInfo):
                self.newAlbumInfo["songInfo_list"][i] = self.oldAlbumInfo["songInfo_list"][i]

        self.saveFinishedSignal.emit(
            self.oldAlbumInfo, self.newAlbumInfo, self.coverPath)
