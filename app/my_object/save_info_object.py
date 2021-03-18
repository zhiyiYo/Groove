# coding:utf-8

from PyQt5.QtCore import QObject, pyqtSignal

from app.my_functions.modify_songInfo import modifySongInfo
from app.my_functions.write_album_cover import writeAlbumCover


class SaveInfoObject(QObject):

    saveAlbumCoverCompleteSig = pyqtSignal()
    saveCompleteSig = pyqtSignal()
    saveErrorSig = pyqtSignal(int)  # 返回错误的下标

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def saveSongInfoSlot(self, songInfo_list: list):
        """ 保存歌曲信息 """
        for i, songInfo in enumerate(songInfo_list):
            if not modifySongInfo(songInfo):
                self.saveErrorSig.emit(i)
                return
        self.saveCompleteSig.emit()

    def saveAlbumInfoSlot(self, songInfo_list: list, newAlbumCoverPath: str = ''):
        """ 保存专辑信息

        Parameters
        ----------
        songInfo_list : list
            歌曲信息列表

        newAlbumCoverPath : str
            新的专辑封面路径，如果为空则不改封面
        """
        # 修改专辑封面
        if newAlbumCoverPath:
            with open(self.newAlbumCoverPath, 'rb') as f:
                picData = f.read()
            # 给专辑中的所有文件写入同一张封面
            for i, songInfo in enumerate(self.songInfo_list):
                if not writeAlbumCover(songInfo['songPath'], self.newAlbumCoverPath):
                    self.saveErrorSig.emit(i)
                    return
            self.saveAlbumCoverCompleteSig.emit()
        self.saveSongInfoSlot(songInfo_list)
