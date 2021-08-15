# coding:utf-8

from app.components.label import ClickableLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QLabel

from .basic_song_card import BasicSongCard
from .song_card_type import SongCardType


class SongTabSongCard(BasicSongCard):
    """ 我的音乐歌曲界面的歌曲卡 """

    switchToAlbumInterfaceSig = pyqtSignal(str, str)  # 发送专辑名和歌手名

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(songInfo, SongCardType.SONG_TAB_SONG_CARD, parent)
        # 创建小部件
        self.singerLabel = ClickableLabel(self.singer, self, False)
        self.albumLabel = ClickableLabel(self.album, self, False)
        self.yearLabel = QLabel(self.year, self)
        self.genreLabel = QLabel(self.genre, self)
        self.durationLabel = QLabel(self.duration, self)
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.yearLabel.setFixedWidth(60)
        self.addLabels(
            [
                self.singerLabel,
                self.albumLabel,
                self.yearLabel,
                self.genreLabel,
                self.durationLabel,
            ],
            [30, 15, 27, 19, 70],
        )
        # 年份的宽度固定为60，时长固定距离窗口右边界45px
        self.setScalableWidgets(
            [self.songNameCard, self.singerLabel,
                self.albumLabel, self.genreLabel],
            [326, 191, 191, 178],
            105,
        )
        self.setDynamicStyleLabels(self.label_list)
        # 设置歌曲卡点击动画
        self.setAnimation(self.widget_list, [13, 6, -3, -6, -8, -13])
        self.setAttribute(Qt.WA_StyledBackground)
        # 设置鼠标样式
        self.setClickableLabels([self.singerLabel, self.albumLabel])
        self.setClickableLabelCursor(Qt.PointingHandCursor)
        # 分配ID和属性
        self.setWidgetState("notSelected-leave")
        self.setCheckBoxBtLabelState("notSelected-notPlay")
        # 信号连接到槽
        self.albumLabel.clicked.connect(
            lambda: self.switchToAlbumInterfaceSig.emit(self.album, self.singer))

    def updateSongCard(self, songInfo: dict):
        """ 更新歌曲卡信息 """
        if self.songInfo == songInfo:
            return
        self._getInfo(songInfo)
        self.songNameCard.updateSongNameCard(self.songName)
        self.singerLabel.setText(self.singer)
        self.albumLabel.setText(self.album)
        self.yearLabel.setText(self.year)
        self.genreLabel.setText(self.genre)
        self.durationLabel.setText(self.duration)
        # 调整小部件宽度
        self.adjustWidgetWidth()

    def resizeEvent(self, e):
        """ 窗口改变大小时调整小部件位置 """
        super().resizeEvent(e)
        # 再次调整时长标签的位置
        self.durationLabel.move(self.width() - 45, 20)
        self.getAniTargetX_list()


class AlbumInterfaceSongCard(BasicSongCard):
    """ 专辑界面的歌曲卡 """

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(songInfo, SongCardType.ALBUM_INTERFACE_SONG_CARD, parent)
        # 创建小部件
        self.singerLabel = ClickableLabel(songInfo["singer"], self, False)
        self.durationLabel = QLabel(songInfo["duration"], self)
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.addLabels([self.singerLabel, self.durationLabel], [16, 70])
        # 设置可伸缩的小部件及其初始化长度
        self.setScalableWidgets(
            [self.songNameCard, self.singerLabel], [554, 401], 45)
        self.setDynamicStyleLabels(self.label_list)
        # 设置动画
        self.setAnimation(self.widget_list, [13, -3, -13])
        self.setAttribute(Qt.WA_StyledBackground)
        # 设置可点击标签列表
        self.setClickableLabels([self.singerLabel])
        self.setClickableLabelCursor(Qt.PointingHandCursor)
        # 分配ID和属性
        self.setWidgetState("notSelected-leave")
        self.setCheckBoxBtLabelState("notSelected-notPlay")

    def updateSongCard(self, songInfo: dict):
        """ 更新歌曲卡信息 """
        if self.songInfo == songInfo:
            return
        self._getInfo(songInfo)
        self.songNameCard.updateSongNameCard(
            songInfo["songName"], songInfo["tracknumber"])
        self.singerLabel.setText(songInfo["singer"])
        self.durationLabel.setText(songInfo["duration"])
        # 调整宽度
        self.adjustWidgetWidth()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        # 再次调整时长标签的位置
        self.durationLabel.move(self.width() - 45, 20)
        self.getAniTargetX_list()


class PlaylistInterfaceSongCard(BasicSongCard):
    """ 我的音乐歌曲界面的歌曲卡 """

    switchToAlbumInterfaceSig = pyqtSignal(str, str)  # 发送专辑名和歌手名

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(songInfo, SongCardType.PLAYLIST_INTERFACE_SONG_CARD, parent)
        # 创建小部件
        self.singerLabel = ClickableLabel(self.singer, self, False)
        self.albumLabel = ClickableLabel(self.album, self, False)
        self.yearLabel = QLabel(self.year, self)
        self.genreLabel = QLabel(self.genre, self)
        self.durationLabel = QLabel(self.duration, self)
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.yearLabel.setFixedWidth(60)
        self.addLabels(
            [
                self.singerLabel,
                self.albumLabel,
                self.yearLabel,
                self.genreLabel,
                self.durationLabel,
            ],
            [30, 15, 27, 19, 70],
        )
        # 年份的宽度固定为60，时长固定距离窗口右边界45px
        self.setScalableWidgets(
            [self.songNameCard, self.singerLabel,
                self.albumLabel, self.genreLabel],
            [326, 191, 191, 178],
            105,
        )
        self.setDynamicStyleLabels(self.label_list)
        # 设置歌曲卡点击动画
        self.setAnimation(self.widget_list, [13, 6, -3, -6, -8, -13])
        self.setAttribute(Qt.WA_StyledBackground)
        # 设置鼠标样式
        self.setClickableLabels([self.singerLabel, self.albumLabel])
        self.setClickableLabelCursor(Qt.PointingHandCursor)
        # 分配ID和属性
        self.setWidgetState("notSelected-leave")
        self.setCheckBoxBtLabelState("notSelected-notPlay")
        # 信号连接到槽
        self.albumLabel.clicked.connect(
            lambda: self.switchToAlbumInterfaceSig.emit(self.album, self.singer))

    def updateSongCard(self, songInfo: dict):
        """ 更新歌曲卡信息 """
        if self.songInfo == songInfo:
            return
        self._getInfo(songInfo)
        self.songNameCard.updateSongNameCard(self.songName)
        self.singerLabel.setText(self.singer)
        self.albumLabel.setText(self.album)
        self.yearLabel.setText(self.year)
        self.genreLabel.setText(self.genre)
        self.durationLabel.setText(self.duration)
        # 调整小部件宽度
        self.adjustWidgetWidth()

    def resizeEvent(self, e):
        """ 窗口改变大小时调整小部件位置 """
        super().resizeEvent(e)
        # 再次调整时长标签的位置
        self.durationLabel.move(self.width() - 45, 20)
        self.getAniTargetX_list()


class NoCheckBoxSongCard(BasicSongCard):
    """ 没有复选框的歌曲卡 """

    switchToAlbumInterfaceSig = pyqtSignal(str, str)  # 发送专辑名和歌手名

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(songInfo, SongCardType.NO_CHECKBOX_SONG_CARD, parent=parent)
        # 创建小部件
        self.singerLabel = ClickableLabel(self.singer, self, False)
        self.albumLabel = ClickableLabel(self.album, self, False)
        self.yearLabel = QLabel(self.year, self)
        self.genreLabel = QLabel(self.genre, self)
        self.durationLabel = QLabel(self.duration, self)
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.yearLabel.setFixedWidth(60)
        self.addLabels(
            [
                self.singerLabel,
                self.albumLabel,
                self.yearLabel,
                self.genreLabel,
                self.durationLabel,
            ],
            [30, 15, 27, 19, 70],
        )
        # 年份的宽度固定为60，时长固定距离窗口右边界45px
        self.setScalableWidgets(
            [self.songNameCard, self.singerLabel,
                self.albumLabel, self.genreLabel],
            [326, 191, 191, 178],
            105,
        )
        self.setDynamicStyleLabels(self.label_list)
        # 设置歌曲卡点击动画
        self.setAnimation(self.widget_list, [13, 6, -3, -6, -8, -13])
        self.setAttribute(Qt.WA_StyledBackground)
        # 设置鼠标样式
        self.setClickableLabels([self.singerLabel, self.albumLabel])
        self.setClickableLabelCursor(Qt.PointingHandCursor)
        # 分配ID和属性
        self.setWidgetState("notSelected-leave")
        self.setCheckBoxBtLabelState("notSelected-notPlay")
        # 信号连接到槽
        self.albumLabel.clicked.connect(
            lambda: self.switchToAlbumInterfaceSig.emit(self.album, self.singer))

    def updateSongCard(self, songInfo: dict):
        """ 更新歌曲卡信息 """
        if self.songInfo == songInfo:
            return
        self._getInfo(songInfo)
        self.songNameCard.updateSongNameCard(self.songName)
        self.singerLabel.setText(self.singer)
        self.albumLabel.setText(self.album)
        self.yearLabel.setText(self.year)
        self.genreLabel.setText(self.genre)
        self.durationLabel.setText(self.duration)
        # 调整小部件宽度
        self.adjustWidgetWidth()

    def resizeEvent(self, e):
        """ 窗口改变大小时调整小部件位置 """
        super().resizeEvent(e)
        # 再次调整时长标签的位置
        self.durationLabel.move(self.width() - 45, 20)
        self.getAniTargetX_list()
