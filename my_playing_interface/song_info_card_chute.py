# coding:utf-8

import sys

from PyQt5.QtCore import Qt, QPoint,QPropertyAnimation,QEasingCurve
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QWidget

from song_info_card import SongInfoCard


class SongInfoCardChute(QWidget):
    """ 歌曲卡滑槽 """

    def __init__(self, parent=None, playlist=None):
        super().__init__(parent)
        # 引用播放列表
        self.playlist = playlist
        self.songInfoCard_list = []
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1300, 970)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.__createSongCards()

    def __createSongCards(self):
        """ 创建歌曲卡 """
        self.currentSongInfoCard = None
        self.lastSongInfoCard = None
        self.nextSongInfoCard = None
        if not self.playlist:
            return
        else:
            # 创建当前歌曲卡
            self.currentSongInfoCard = SongInfoCard(self, self.playlist[0])
            self.currentSongInfoCard.move(0, self.height() - 204)
            self.currentSongInfoCard.resize(self.width(), 136)
            self.songInfoCard_list.append(self.currentSongInfoCard)
            if len(self.playlist) >= 2:
                self.nextSongInfoCard = SongInfoCard(self, self.playlist[1])
                self.nextSongInfoCard.move(self.width(), self.height() - 204)
                self.nextSongInfoCard.resize(self.width(), 136)
                self.songInfoCard_list.append(self.nextSongInfoCard)

    def mousePressEvent(self, e: QMouseEvent):
        """ 按钮按下时记录鼠标位置 """
        self.mousePressPosX = e.pos().x()
        self.lastMousePosX = e.pos().x()

    def mouseMoveEvent(self, e: QMouseEvent):
        """ 鼠标按下可拖动歌曲信息卡 """
        if self.currentSongInfoCard:
            self.currentSongInfoCard.move(self.currentSongInfoCard.x(
            )-(self.lastMousePosX-e.pos().x()), self.currentSongInfoCard.y())
        if self.nextSongInfoCard:
            self.nextSongInfoCard.move(self.nextSongInfoCard.x(
            ) - (self.lastMousePosX - e.pos().x()), self.nextSongInfoCard.y())
        # 更新鼠标位置
        self.lastMousePosX = e.pos().x()

    def mouseReleaseEvent(self, e: QMouseEvent):
        """ 鼠标松开时重新设置歌曲卡位置 """
        if self.lastMousePosX - self.mousePressPosX >= int(self.width() / 2):
            

    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    playlist = [{'songName': 'ハッピーでバッドな眠りは浅い',
                 'songer': '鎖那',
                 'album': ['ハッピーでバッドな眠りは浅い']},
                {'songName': '猫じゃらし',
                 'songer': 'RADWIMPS',
                 'album': ['猫じゃらし - Single']}]
    demo = SongInfoCardChute(playlist=playlist)
    demo.show()
    sys.exit(app.exec_())
