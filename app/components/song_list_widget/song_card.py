# coding:utf-8
from common.database.entity import SongInfo
from common.signal_bus import signalBus
from components.widgets.label import ClickableLabel
from components.widgets.menu import DownloadMenu
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtWidgets import QLabel

from .basic_song_card import BasicSongCard
from .song_card_type import SongCardType


class DurationSongCard(BasicSongCard):
    """ 有时长标签的歌曲卡 """

    def __init__(self, songInfo: SongInfo, songCardType, parent=None):
        super().__init__(songInfo, songCardType, parent)
        self.durationLabel = QLabel(self.duration, self)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setWidgetState("notSelected-leave")
        self.setCheckBoxBtLabelState("notSelected-notPlay")

    def resizeEvent(self, e):
        """ 窗口改变大小时调整小部件位置 """
        super().resizeEvent(e)
        self.durationLabel.move(self.width() - 45, 20)
        self._getAniTargetX()

    def updateSongCard(self, songInfo: SongInfo):
        """ 更新歌曲卡信息 """
        self.setSongInfo(songInfo)
        self.durationLabel.setText(self.duration)


class SongTabSongCard(DurationSongCard):
    """ 我的音乐歌曲界面的歌曲卡 """

    def __init__(self, songInfo: SongInfo, parent=None):
        super().__init__(songInfo, SongCardType.SONG_TAB_SONG_CARD, parent)
        self.singerLabel = ClickableLabel(self.singer, self, False)
        self.albumLabel = ClickableLabel(self.album, self, False)
        self.yearLabel = QLabel(self.year, self)
        self.genreLabel = QLabel(self.genre, self)
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
        self.setDynamicStyleLabels(self.labels)

        # 设置歌曲卡点击动画
        self.setAnimation(self.widgets, [13, 6, -3, -6, -8, -13])

        # 设置鼠标样式
        self.setClickableLabels([self.singerLabel, self.albumLabel])
        self.setClickableLabelCursor(Qt.PointingHandCursor)

        # 信号连接到槽
        self.addToButton.clicked.connect(self._showAddToMenu)
        self.checkBox.stateChanged.connect(self._onCheckedStateChanged)
        self.singerLabel.clicked.connect(
            lambda: signalBus.switchToSingerInterfaceSig.emit(self.singer))
        self.albumLabel.clicked.connect(
            lambda: signalBus.switchToAlbumInterfaceSig.emit(self.singer, self.album))

    def updateSongCard(self, songInfo: SongInfo):
        """ 更新歌曲卡信息 """
        if self.songInfo == songInfo:
            return

        super().updateSongCard(songInfo)
        self.songNameCard.updateSongNameCard(self.songName)
        self.singerLabel.setText(self.singer)
        self.albumLabel.setText(self.album)
        self.yearLabel.setText(str(self.year))
        self.genreLabel.setText(self.genre)
        self._adjustWidgetWidth()


class AlbumInterfaceSongCard(DurationSongCard):
    """ 专辑界面的歌曲卡 """

    def __init__(self, songInfo: SongInfo, parent=None):
        super().__init__(songInfo, SongCardType.ALBUM_INTERFACE_SONG_CARD, parent)
        self.singerLabel = ClickableLabel(self.singer, self, False)
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.addLabels([self.singerLabel, self.durationLabel], [16, 70])

        # 设置可伸缩的小部件及其初始化长度
        self.setScalableWidgets(
            [self.songNameCard, self.singerLabel], [554, 401], 45)
        self.setDynamicStyleLabels(self.labels)

        # 设置动画
        self.setAnimation(self.widgets, [13, -3, -13])

        # 设置可点击标签列表
        self.setClickableLabels([self.singerLabel])
        self.setClickableLabelCursor(Qt.PointingHandCursor)

        # 信号连接到槽
        self.singerLabel.clicked.connect(
            lambda: signalBus.switchToSingerInterfaceSig.emit(self.singer))
        self.addToButton.clicked.connect(self._showAddToMenu)
        self.checkBox.stateChanged.connect(self._onCheckedStateChanged)

    def updateSongCard(self, songInfo: SongInfo):
        """ 更新歌曲卡信息 """
        if self.songInfo == songInfo:
            return

        super().updateSongCard(songInfo)
        self.songNameCard.updateSongNameCard(self.songName, self.track)
        self.singerLabel.setText(self.singer)
        self._adjustWidgetWidth()


class PlaylistInterfaceSongCard(DurationSongCard):
    """ 播放列表界面的歌曲卡 """

    removeSongSignal = pyqtSignal(int)                # 移除歌曲

    def __init__(self, songInfo: SongInfo, parent=None):
        super().__init__(songInfo, SongCardType.PLAYLIST_INTERFACE_SONG_CARD, parent)
        self.singerLabel = ClickableLabel(self.singer, self, False)
        self.albumLabel = ClickableLabel(self.album, self, False)
        self.yearLabel = QLabel(self.year, self)
        self.genreLabel = QLabel(self.genre, self)
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
        self.setDynamicStyleLabels(self.labels)

        # 设置歌曲卡点击动画
        self.setAnimation(self.widgets, [13, 6, -3, -6, -8, -13])

        # 设置鼠标样式
        self.setClickableLabels([self.singerLabel, self.albumLabel])
        self.setClickableLabelCursor(Qt.PointingHandCursor)

        # 信号连接到槽
        self.singerLabel.clicked.connect(
            lambda: signalBus.switchToSingerInterfaceSig.emit(self.singer))
        self.albumLabel.clicked.connect(
            lambda: signalBus.switchToAlbumInterfaceSig.emit(self.singer, self.album))
        self.addToButton.clicked.connect(
            lambda: self.removeSongSignal.emit(self.itemIndex))
        self.checkBox.stateChanged.connect(self._onCheckedStateChanged)

    def updateSongCard(self, songInfo: SongInfo):
        """ 更新歌曲卡信息 """
        if self.songInfo == songInfo:
            return

        super().updateSongCard(songInfo)
        self.songNameCard.updateSongNameCard(self.songName)
        self.singerLabel.setText(self.singer)
        self.albumLabel.setText(self.album)
        self.yearLabel.setText(self.year)
        self.genreLabel.setText(self.genre)
        self._adjustWidgetWidth()


class NoCheckBoxSongCard(DurationSongCard):
    """ 没有复选框的歌曲卡 """

    def __init__(self, songInfo: SongInfo, parent=None):
        super().__init__(songInfo, SongCardType.NO_CHECKBOX_SONG_CARD, parent=parent)
        self.singerLabel = ClickableLabel(self.singer, self, False)
        self.albumLabel = ClickableLabel(self.album, self, False)
        self.yearLabel = QLabel(self.year, self)
        self.genreLabel = QLabel(self.genre, self)
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
        self.setDynamicStyleLabels(self.labels)

        # 设置歌曲卡点击动画
        self.setAnimation(self.widgets, [13, 6, -3, -6, -8, -13])

        # 设置鼠标样式
        self.setClickableLabels([self.singerLabel, self.albumLabel])
        self.setClickableLabelCursor(Qt.PointingHandCursor)

        # 信号连接到槽
        self.singerLabel.clicked.connect(
            lambda: signalBus.switchToSingerInterfaceSig.emit(self.singer))
        self.albumLabel.clicked.connect(
            lambda: signalBus.switchToAlbumInterfaceSig.emit(self.singer, self.album))
        self.addToButton.clicked.connect(self._showAddToMenu)

    def updateSongCard(self, songInfo: SongInfo):
        """ 更新歌曲卡信息 """
        if self.songInfo == songInfo:
            return

        super().updateSongCard(songInfo)
        self.songNameCard.updateSongNameCard(self.songName)
        self.singerLabel.setText(self.singer)
        self.albumLabel.setText(self.album)
        self.yearLabel.setText(self.year)
        self.genreLabel.setText(self.genre)
        self._adjustWidgetWidth()


class OnlineSongCard(DurationSongCard):
    """ 在线音乐歌曲卡 """

    downloadSig = pyqtSignal(SongInfo, str)  # songInfo, quality

    def __init__(self, songInfo: SongInfo, parent=None):
        super().__init__(songInfo, SongCardType.ONLINE_SONG_CARD, parent=parent)
        self.singerLabel = QLabel(self.singer, self)
        self.albumLabel = QLabel(self.album, self)
        self.yearLabel = QLabel(self.year, self)
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.addLabels(
            [self.singerLabel, self.albumLabel, self.yearLabel, self.durationLabel],
            [30, 15, 27, 70],
        )

        # 年份的宽度固定为60，时长固定距离窗口右边界45px
        self.setScalableWidgets(
            [self.songNameCard, self.singerLabel, self.albumLabel],
            [326, 191, 191],
            105,
        )
        self.setDynamicStyleLabels(self.labels)

        # 设置歌曲卡点击动画
        self.setAnimation(self.widgets, [13, 6, -3, -6, -13])

        # self.addToButton.setToolTip(self.tr('Download'))

        # 信号连接到槽
        self.addToButton.clicked.connect(self.__showDownloadMenu)

    def updateSongCard(self, songInfo: SongInfo):
        """ 更新歌曲卡信息 """
        if self.songInfo == songInfo:
            return

        super().updateSongCard(songInfo)
        self.songNameCard.updateSongNameCard(self.songName)
        self.singerLabel.setText(self.singer)
        self.albumLabel.setText(self.album)
        self.yearLabel.setText(self.year)
        self._adjustWidgetWidth()

    def __showDownloadMenu(self):
        """ 显示下载音乐菜单 """
        menu = DownloadMenu(parent=self)
        pos = self.mapToGlobal(
            QPoint(self.addToButton.x()+self.buttonGroup.x(), 0))
        x = pos.x() + self.addToButton.width() + 5
        y = pos.y() + int(
            self.addToButton.height() / 2 - (13 + 38 * 3) / 2)
        menu.downloadSig.connect(
            lambda quality: self.downloadSig.emit(self.songInfo, quality))
        menu.exec(QPoint(x, y))


class SongCardFactory:
    """ 歌曲卡工厂 """

    @staticmethod
    def create(songCardType: SongCardType, songInfo: SongInfo, parent=None) -> BasicSongCard:
        """ 创建一个指定类型的歌曲名字卡

        Parameters
        ----------
        songCardType: SongCardType
            歌曲卡类型

        songInfo: SongInfo
            歌曲信息

        parent:
            父级窗口
        """
        songCard_dict = {
            SongCardType.SONG_TAB_SONG_CARD: SongTabSongCard,
            SongCardType.ALBUM_INTERFACE_SONG_CARD: AlbumInterfaceSongCard,
            SongCardType.PLAYLIST_INTERFACE_SONG_CARD: PlaylistInterfaceSongCard,
            SongCardType.NO_CHECKBOX_SONG_CARD: NoCheckBoxSongCard,
            SongCardType.ONLINE_SONG_CARD: OnlineSongCard
        }

        if songCardType not in songCard_dict:
            raise ValueError("歌曲卡类型非法")

        return songCard_dict[songCardType](songInfo, parent)
