# coding:utf-8
from common.auto_wrap import autoWrap
from common.crawler import CrawlerBase
from common.database.entity import SongInfo
from common.style_sheet import setStyleSheet
from common.os_utils import showInFolder
from common.url import FakeUrl
from components.widgets.label import ClickableLabel
from components.buttons.perspective_button import PerspectivePushButton
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout

from .mask_dialog_base import MaskDialogBase


class SongPropertyDialog(MaskDialogBase):
    """ Song information dialog box """

    def __init__(self, songInfo: SongInfo, parent=None):
        super().__init__(parent)
        self.songInfo = songInfo

        # title label
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

        # content label
        self.songNameLabel = SelectableLabel(songInfo.title, self.widget)
        self.singerLabel = SelectableLabel(songInfo.singer, self.widget)
        self.albumNameLabel = SelectableLabel(songInfo.album, self.widget)
        self.albumSingerLabel = SelectableLabel(songInfo.singer, self.widget)
        self.discLabel = SelectableLabel(str(songInfo.disc or ''), self.widget)
        self.genreLabel = SelectableLabel(songInfo.genre or '', self.widget)
        self.trackLabel = SelectableLabel(
            str(songInfo.track or ''), self.widget)
        self.songPathLabel = ClickableLabel(songInfo.file, self.widget)
        self.yearLabel = SelectableLabel(str(songInfo.year or ''), self.widget)
        self.durationLabel = SelectableLabel(
            f"{int(songInfo.duration//60)}:{int(songInfo.duration%60):02}", self.widget)

        # close button
        self.closeButton = PerspectivePushButton(self.tr("Close"), self.widget)

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.__setQss()
        self.widget.setFixedWidth(942)
        self.songPathLabel.setCursor(Qt.PointingHandCursor)
        self.songPathLabel.setHidden(FakeUrl.isFake(self.songInfo.file))

        self.songNameLabel.setFixedWidth(523)
        self.trackLabel.setFixedWidth(523)
        self.albumNameLabel.setFixedWidth(523)
        self.genreLabel.setFixedWidth(523)
        self.songPathLabel.setFixedWidth(847)
        self.durationLabel.setFixedWidth(43)

        self.__adjustText()
        self.__initLayout()

        self.closeButton.clicked.connect(self.close)
        self.songPathLabel.clicked.connect(
            lambda: showInFolder(self.songInfo.file))

    def __initLayout(self):
        """ initialize layout """
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

        # song name and singer
        gridLayout_1.addWidget(self.songNameTitleLabel, 0, 0, Qt.AlignTop)
        gridLayout_1.addWidget(self.songNameLabel, 1, 0, Qt.AlignTop)
        gridLayout_1.addWidget(self.singerTitleLabel, 0, 1, Qt.AlignTop)
        gridLayout_1.addWidget(self.singerLabel, 1, 1, Qt.AlignTop)

        # track number and disc
        gridLayout_2.addWidget(self.trackNumberTitleLabel, 0, 0, Qt.AlignTop)
        gridLayout_2.addWidget(self.trackLabel, 1, 0, Qt.AlignTop)
        gridLayout_2.addWidget(self.discTitleLabel, 0, 1, Qt.AlignTop)
        gridLayout_2.addWidget(self.discLabel, 1, 1, Qt.AlignTop)

        # album and album singer
        gridLayout_3.addWidget(self.albumNameTitleLabel, 0, 0, Qt.AlignTop)
        gridLayout_3.addWidget(self.albumNameLabel, 1, 0, Qt.AlignTop)
        gridLayout_3.addWidget(self.albumSingerTitleLabel, 0, 1, Qt.AlignTop)
        gridLayout_3.addWidget(self.albumSingerLabel, 1, 1, Qt.AlignTop)

        # genre, duration and release year
        gridLayout_4.addWidget(self.genreTitleLabel, 0, 0, Qt.AlignTop)
        gridLayout_4.addWidget(self.genreLabel, 1, 0, Qt.AlignTop)
        gridLayout_4.addWidget(self.durationTitleLabel, 0, 1, Qt.AlignTop)
        gridLayout_4.addWidget(self.durationLabel, 1, 1, Qt.AlignTop)
        gridLayout_4.addWidget(self.yearTitleLabel, 0, 2, Qt.AlignTop)
        gridLayout_4.addWidget(self.yearLabel, 1, 2, Qt.AlignTop)

        # file path
        vBoxLayout.addWidget(self.songPathTitleLabel, 0, Qt.AlignTop)
        vBoxLayout.addSpacing(0)
        vBoxLayout.addWidget(self.songPathLabel, 0, Qt.AlignTop)
        vBoxLayout.addSpacing(80)

        # buttons
        hBoxLayout = QHBoxLayout()
        hBoxLayout.setContentsMargins(0, 0, 0, 0)
        hBoxLayout.addStretch(1)
        hBoxLayout.addWidget(self.closeButton)
        vBoxLayout.addLayout(hBoxLayout)

    def __adjustText(self):
        """ adjust text if it's too long """
        songName, isSongNameWrap = autoWrap(self.songNameLabel.text(), 57)
        singer, isSingerWrap = autoWrap(self.singerLabel.text(), 38)
        albumName, isAlbumNameWrap = autoWrap(
            self.albumNameLabel.text(), 57)
        albumSinger, isAlbumSingerWrap = autoWrap(
            self.albumSingerLabel.text(), 38)
        songPath, isSongPathWrap = autoWrap(self.songPathLabel.text(), 105)

        if isSongNameWrap or isSingerWrap:
            self.songNameLabel.setText(songName)
            self.singerLabel.setText(singer)

        if isAlbumNameWrap or isAlbumSingerWrap:
            self.albumNameLabel.setText(albumName)
            self.albumSingerLabel.setText(albumSinger)

        if isSongPathWrap:
            self.songPathLabel.setText(songPath)

        if songPath == CrawlerBase.song_url_mark:
            self.songPathLabel.setText('')
            self.songPathLabel.setCursor(Qt.ArrowCursor)

    def __setQss(self):
        """ set style sheet """
        self.songNameLabel.setObjectName('valueLabel')
        self.singerLabel.setObjectName("valueLabel")
        self.trackLabel.setObjectName('valueLabel')
        self.discLabel.setObjectName('valueLabel')
        self.albumNameLabel.setObjectName('valueLabel')
        self.albumSingerLabel.setObjectName("valueLabel")
        self.genreLabel.setObjectName('valueLabel')
        self.yearLabel.setObjectName("valueLabel")
        self.durationLabel.setObjectName("valueLabel")
        self.songPathLabel.setObjectName("songPathLabel")
        self.propertyTitleLabel.setObjectName("propertyTitleLabel")

        setStyleSheet(self, 'song_property_dialog')

        self.closeButton.adjustSize()
        for label in self.findChildren(QLabel):
            label.adjustSize()


class SelectableLabel(ClickableLabel):
    """ Selectable label """

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)

    def contextMenuEvent(self, e):
        return
