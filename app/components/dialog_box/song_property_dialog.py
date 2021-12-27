# coding:utf-8
from common.auto_wrap import autoWrap
from components.buttons.perspective_button import PerspectivePushButton
from PyQt5.QtCore import QFile, Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QGridLayout, QHBoxLayout

from .mask_dialog_base import MaskDialogBase


class SongPropertyDialog(MaskDialogBase):
    """ 歌曲属性对话框 """

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(parent)
        self.songInfo = songInfo

        # 标题标签
        self.yearTitleLabel = QLabel(self.tr("Year"), self.widget)
        self.discTitleLabel = QLabel(self.tr("Disc"), self.widget)
        self.genreTitleLabel = QLabel(self.tr("Genre"), self.widget)
        self.durationTitleLabel = QLabel(self.tr("Length"), self.widget)
        self.propertyTitleLabel = QLabel(self.tr("Properties"), self.widget)
        self.singerTitleLabel = QLabel(self.tr("Song artist"), self.widget)
        self.songNameTitleLabel = QLabel(self.tr("Song title"), self.widget)
        self.trackNumberTitleLabel = QLabel(self.tr("Track"), self.widget)
        self.songPathTitleLabel = QLabel(self.tr("File location"), self.widget)
        self.albumNameTitleLabel = QLabel(self.tr("Album title"), self.widget)
        self.albumSingerTitleLabel = QLabel(
            self.tr("Album artist"), self.widget)

        # 内容标签
        self.discLabel = SelectableLabel(
            songInfo.get('disc', "1"), self.widget)
        self.yearLabel = SelectableLabel(songInfo.get(
            "year", self.tr('Unknown year')), self.widget)
        self.genreLabel = SelectableLabel(songInfo.get(
            "genre", self.tr('Unknown genre')), self.widget)
        self.singerLabel = SelectableLabel(songInfo.get(
            "singer", self.tr("Unknown artist")), self.widget)
        self.albumNameLabel = SelectableLabel(songInfo.get(
            "album", self.tr('Unknown album')), self.widget)
        self.durationLabel = SelectableLabel(
            songInfo.get("duration", "0:00"), self.widget)
        self.songNameLabel = SelectableLabel(songInfo.get(
            "songName", self.tr("Unknown song")), self.widget)
        self.albumSingerLabel = SelectableLabel(songInfo.get(
            "singer", self.tr('Unknown artist')), self.widget)
        self.trackNumberLabel = SelectableLabel(
            songInfo.get("tracknumber", ''), self.widget)
        self.songPathLabel = SelectableLabel(songInfo.get(
            "songPath", '').replace("\\", "/"), self.widget)

        # 关闭按钮
        self.closeButton = PerspectivePushButton(self.tr("Close"), self.widget)

        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件的属性 """
        self.__setQss()
        self.widget.setFixedWidth(942)

        # 设置宽度
        self.songNameLabel.setFixedWidth(523)
        self.trackNumberLabel.setFixedWidth(523)
        self.albumNameLabel.setFixedWidth(523)
        self.genreLabel.setFixedWidth(523)
        self.songPathLabel.setFixedWidth(847)
        self.durationLabel.setFixedWidth(43)

        # 调整高度
        self.__adjustText()
        self.__initLayout()

        # 将关闭信号连接到槽函数
        self.closeButton.clicked.connect(self.close)

    def __initLayout(self):
        """ 初始化布局 """
        vBoxLayout = QVBoxLayout(self.widget)
        vBoxLayout.setSizeConstraint(QVBoxLayout.SetFixedSize)
        vBoxLayout.setAlignment(Qt.AlignTop)
        vBoxLayout.setContentsMargins(30, 30, 30, 15)
        vBoxLayout.addWidget(self.propertyTitleLabel, 0, Qt.AlignTop)
        vBoxLayout.addSpacing(30)

        gridLayout_1 = QGridLayout()
        gridLayout_2 = QGridLayout()
        gridLayout_3 = QGridLayout()
        gridLayout_4 = QGridLayout()

        for layout in [gridLayout_1, gridLayout_2, gridLayout_3, gridLayout_4]:
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setVerticalSpacing(8)
            layout.setHorizontalSpacing(30)
            vBoxLayout.addLayout(layout)
            vBoxLayout.addSpacing(14)

        # 歌曲名和歌曲歌手
        gridLayout_1.addWidget(self.songNameTitleLabel, 0, 0, Qt.AlignTop)
        gridLayout_1.addWidget(self.songNameLabel, 1, 0, Qt.AlignTop)
        gridLayout_1.addWidget(self.singerTitleLabel, 0, 1, Qt.AlignTop)
        gridLayout_1.addWidget(self.singerLabel, 1, 1, Qt.AlignTop)

        # 曲目和光盘
        gridLayout_2.addWidget(self.trackNumberTitleLabel, 0, 0, Qt.AlignTop)
        gridLayout_2.addWidget(self.trackNumberLabel, 1, 0, Qt.AlignTop)
        gridLayout_2.addWidget(self.discTitleLabel, 0, 1, Qt.AlignTop)
        gridLayout_2.addWidget(self.discLabel, 1, 1, Qt.AlignTop)

        # 专辑标题和专辑歌手
        gridLayout_3.addWidget(self.albumNameTitleLabel, 0, 0, Qt.AlignTop)
        gridLayout_3.addWidget(self.albumNameLabel, 1, 0, Qt.AlignTop)
        gridLayout_3.addWidget(self.albumSingerTitleLabel, 0, 1, Qt.AlignTop)
        gridLayout_3.addWidget(self.albumSingerLabel, 1, 1, Qt.AlignTop)

        # 类型、时长和年份
        gridLayout_4.addWidget(self.genreTitleLabel, 0, 0, Qt.AlignTop)
        gridLayout_4.addWidget(self.genreLabel, 1, 0, Qt.AlignTop)
        gridLayout_4.addWidget(self.durationTitleLabel, 0, 1, Qt.AlignTop)
        gridLayout_4.addWidget(self.durationLabel, 1, 1, Qt.AlignTop)
        gridLayout_4.addWidget(self.yearTitleLabel, 0, 2, Qt.AlignTop)
        gridLayout_4.addWidget(self.yearLabel, 1, 2, Qt.AlignTop)

        # 文件路径
        vBoxLayout.addWidget(self.songPathTitleLabel, 0, Qt.AlignTop)
        vBoxLayout.addSpacing(0)
        vBoxLayout.addWidget(self.songPathLabel, 0, Qt.AlignTop)
        vBoxLayout.addSpacing(80)

        # 按钮
        hBoxLayout = QHBoxLayout()
        hBoxLayout.setContentsMargins(0, 0, 0, 0)
        hBoxLayout.addStretch(1)
        hBoxLayout.addWidget(self.closeButton)
        vBoxLayout.addLayout(hBoxLayout)

    def __adjustText(self):
        """ 如果有换行的发生就调整高度 """
        songName, isSongNameWrap = autoWrap(self.songNameLabel.text(), 57)
        singer, isSingerWrap = autoWrap(self.singerLabel.text(), 33)
        albumName, isAlbumNameWrap = autoWrap(
            self.albumNameLabel.text(), 57)
        albumSinger, isAlbumSingerWrap = autoWrap(
            self.albumSingerLabel.text(), 33)
        songPath, isSongPathWrap = autoWrap(self.songPathLabel.text(), 110)

        if isSongNameWrap or isSingerWrap:
            self.songNameLabel.setText(songName)
            self.singerLabel.setText(singer)

        if isAlbumNameWrap or isAlbumSingerWrap:
            self.albumNameLabel.setText(albumName)
            self.albumSingerLabel.setText(albumSinger)

        if isSongPathWrap:
            self.songPathLabel.setText(songPath)

    def __setQss(self):
        """ 设置层叠样式表 """
        self.songNameLabel.setObjectName('valueLabel')
        self.singerLabel.setObjectName("valueLabel")
        self.trackNumberLabel.setObjectName('valueLabel')
        self.discLabel.setObjectName('valueLabel')
        self.albumNameLabel.setObjectName('valueLabel')
        self.albumSingerLabel.setObjectName("valueLabel")
        self.genreLabel.setObjectName('valueLabel')
        self.yearLabel.setObjectName("valueLabel")
        self.durationLabel.setObjectName("valueLabel")
        self.songPathLabel.setObjectName("valueLabel")
        self.propertyTitleLabel.setObjectName("propertyTitleLabel")

        f = QFile(":/qss/song_property_dialog.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

        self.closeButton.adjustSize()
        for label in self.findChildren(QLabel):
            label.adjustSize()


class SelectableLabel(QLabel):
    """ 可用鼠标选中的标签 """

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)

    def contextMenuEvent(self, e):
        return
