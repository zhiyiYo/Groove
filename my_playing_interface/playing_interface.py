import sys

from PyQt5.QtCore import (QEasingCurve, QParallelAnimationGroup,
                          QPropertyAnimation, QRect, Qt)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QGraphicsBlurEffect, QLabel, QWidget

from blur_cover_thread import BlurCoverThread
from play_bar import PlayBar

from song_info_card_chute import SongInfoCardChute


class PlayingInterface(QWidget):
    """ 正在播放界面 """

    def __init__(self, playlist: list = None, parent=None):
        super().__init__(parent)
        self.playlist = playlist
        # 创建小部件
        self.blurPixmap = None
        self.blurBackgroundPic = QLabel(self)
        self.blurCoverThread = BlurCoverThread(self)
        self.songInfoCardChute = SongInfoCardChute(self, playlist)
        self.songInfoCardChuteAni = QPropertyAnimation(
            self.songInfoCardChute, b'geometry')
        self.playBar = PlayBar(self)
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1300, 970)
        self.playBar.move(0,self.height()-self.playBar.height())
        self.playBar.hide()
        # 开启磨砂线程
        self.blurCoverThread.start()
        if self.playlist:
            self.startBlurThread(
                self.songInfoCardChute.curSongInfoCard.albumCoverPath)
        # 将信号连接到槽
        self.blurCoverThread.blurDone.connect(self.setBlurPixmap)
        self.songInfoCardChute.currentSongChanged[str].connect(         # 更换背景封面
            self.startBlurThread)
        self.songInfoCardChute.showPlayBarSignal.connect(self.showPlayBar)
        self.songInfoCardChute.hidePlayBarSignal.connect(self.hidePlayBar)
        # 初始化动画
        self.songInfoCardChuteAni.setDuration(500)
        self.songInfoCardChuteAni.setEasingCurve(QEasingCurve.OutQuart)

    def setBlurPixmap(self, blurPixmap):
        """ 设置磨砂pixmap """
        self.blurPixmap = blurPixmap
        # 更新背景
        self.__resizeBlurPixmap()

    def __resizeBlurPixmap(self):
        """ 调整背景图尺寸 """
        maxWidth = max(self.width(), self.height())
        if self.blurPixmap:
            self.blurBackgroundPic.setPixmap(self.blurPixmap.scaled(
                maxWidth, maxWidth, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def startBlurThread(self, albumCoverPath):
        """ 开启磨砂线程 """
        self.blurCoverThread.setTargetCover(albumCoverPath)
        self.blurCoverThread.start()

    def resizeEvent(self, e):
        """ 改变尺寸时也改变小部件的大小 """
        super().resizeEvent(e)
        self.__resizeBlurPixmap()
        self.songInfoCardChute.resize(self.size())
        self.blurBackgroundPic.setFixedSize(self.size())
        self.playBar.resize(self.width(), self.playBar.height())
        self.playBar.move(0,self.height()-self.playBar.height())

    def showPlayBar(self):
        """ 显示播放栏 """
        self.playBar.show()
        self.songInfoCardChuteAni.setStartValue(self.songInfoCardChute.rect())
        self.songInfoCardChuteAni.setEndValue(
            QRect(0, -self.playBar.height()+68, self.width(), self.height()))
        self.songInfoCardChuteAni.start()

    def hidePlayBar(self):
        """ 显示播放栏 """
        self.playBar.hide()
        self.songInfoCardChuteAni.setStartValue(
            QRect(0, -self.playBar.height()+68, self.width(), self.height()))
        self.songInfoCardChuteAni.setEndValue(
            QRect(0, 0, self.width(), self.height()))
        self.songInfoCardChuteAni.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    playlist = [{'songName': 'ハッピーでバッドな眠りは浅い',
                 'songer': '鎖那',
                 'album': ['ハッピーでバッドな眠りは浅い']},
                {'songName': '猫じゃらし',
                 'songer': 'RADWIMPS',
                 'album': ['猫じゃらし - Single']},
                {'songName': '歩いても歩いても、夜空は僕を追いかけてくる (步履不停，夜空追逐着我)',
                 'songer': '鎖那',
                 'album': ['(un)sentimental spica']},
                {'songName': 'one another',
                 'songer': 'HALCA',
                 'album': ['Assortrip']},
                {'songName': 'オーダーメイド',
                 'songer': 'RADWIMPS',
                 'album': ['オーダーメイド']}, ]
    demo = PlayingInterface(playlist=playlist)
    demo.show()
    sys.exit(app.exec_())
