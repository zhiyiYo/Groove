import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel

sys.path.append('..')

from Groove.my_functions.get_album_cover_path import getAlbumCoverPath
from Groove.my_widget.my_label import ClickableLabel


class SongInfoCard(QWidget):
    """ 歌曲信息卡 """

    def __init__(self, parent=None, songInfo: dict = None):
        super().__init__(parent)
        self.setSongInfo(songInfo)
        self.albumCoverLabel = QLabel(self)
        self.songNameLabel = ClickableLabel(parent=self)
        self.songerAlbumLabel = ClickableLabel(parent=self)
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedHeight(136)
        self.setMinimumWidth(400)
        self.albumCoverLabel.setFixedSize(136, 136)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.updateCard(self.songInfo)
        # 分配ID
        self.songNameLabel.setObjectName('songNameLabel')
        self.songerAlbumLabel.setObjectName('songerAlbumLabel')
        self.__initLayout()
        self.__setQss()

    def __initLayout(self):
        """ 初始化布局 """
        self.albumCoverLabel.move(30, 0)
        self.songNameLabel.move(186, 38)
        self.songerAlbumLabel.move(186, 84)

    def setSongInfo(self, songInfo: dict):
        """ 设置歌曲信息 """
        self.songInfo = songInfo
        if not self.songInfo:
            self.songInfo = {}
        self.album = self.songInfo.get('album', ['未知专辑'])
        self.songName = self.songInfo.get('songName', '未知歌名')
        self.songerName = self.songInfo.get('songer', '未知歌手')
        self.albumCoverPath = getAlbumCoverPath(self.album[-1])

    def updateCard(self, songInfo: dict):
        """ 更新歌曲信息卡 """
        self.setSongInfo(songInfo)
        self.songNameLabel.setText(self.songName)
        self.songerAlbumLabel.setText(self.songerName + ' • ' + self.album[0])
        self.albumCoverLabel.setPixmap(QPixmap(self.albumCoverPath).scaled(
            136, 136, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def __setQss(self):
        """ 设置层叠样式 """
        with open(r'resource\css\playInterfaceSongInfoCard.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

        
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    songInfo = {'songName': 'ハッピーでバッドな眠りは浅い',
                'songer': '鎖那',
                'album': ['ハッピーでバッドな眠りは浅い']}
    demo = SongInfoCard()
    demo.show()
    sys.exit(app.exec_())
