# coding:utf-8
from common.auto_wrap import autoWrap
from common.style_sheet import setStyleSheet
from common.os_utils import showInFolder, getLyricPath
from common.database.entity import SongInfo
from common.config import config
from common.lyric import Lyric
from common.meta_data.reader import AlbumCoverReader, SongInfoReader
from common.meta_data.writer import MetaDataWriter
from common.thread.get_meta_data_thread import GetSongMetaDataThread
from components.buttons.perspective_button import PerspectivePushButton
from components.buttons.switch_button import SwitchButton
from components.widgets.label import ErrorIcon, ClickableLabel
from components.widgets.line_edit import LineEdit, VLineEdit
from components.widgets.tooltip import StateTooltip
from mutagen.id3 import TCON
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QCompleter, QGridLayout, QLabel,
                             QVBoxLayout)

from .mask_dialog_base import MaskDialogBase


class SongInfoEditDialog(MaskDialogBase):
    """ Song information edit dialog box """

    saveInfoSig = pyqtSignal(SongInfo, SongInfo)

    def __init__(self, songInfo: SongInfo, parent):
        super().__init__(parent)
        self.songInfo = songInfo.copy()
        self.oldSongInfo = songInfo
        self.writer = MetaDataWriter()
        self.__createWidgets()
        self.__initWidget()
        self.__initLayout()

    def __createWidgets(self):
        """ create widgets """
        # buttons
        self.saveButton = PerspectivePushButton(self.tr("Save"), self.widget)
        self.cancelButton = PerspectivePushButton(
            self.tr("Cancel"), self.widget)
        self.getMetaDataSwitchButton = SwitchButton(
            self.tr('Off'), self.widget)

        # labels
        self.yearLabel = QLabel(self.tr("Year"), self.widget)
        self.genreLabel = QLabel(self.tr("Genre"), self.widget)
        self.discLabel = QLabel(self.tr("Disc"), self.widget)
        self.trackLabel = QLabel(self.tr("Track"), self.widget)
        self.songNameLabel = QLabel(self.tr("Song title"), self.widget)
        self.songPathLabel = QLabel(self.tr("File location"), self.widget)
        self.albumNameLabel = QLabel(self.tr("Album title"), self.widget)
        self.singerNameLabel = QLabel(self.tr("Song artist"), self.widget)
        self.albumSongerLabel = QLabel(self.tr("Album artist"), self.widget)
        self.editInfoLabel = QLabel(self.tr("Edit Song Info"), self.widget)
        self.songPath = ClickableLabel(self.songInfo.file, self.widget)
        self.getMetaDataLabel = QLabel(
            self.tr('Automatically retrieve metadata'), self.widget)
        self.bottomErrorIcon = ErrorIcon(self.widget)
        self.bottomErrorLabel = QLabel(self.widget)

        # line edits
        self.genreLineEdit = LineEdit(self.songInfo.genre, self.widget)
        self.songNameLineEdit = LineEdit(self.songInfo.title, self.widget)
        self.albumNameLineEdit = LineEdit(self.songInfo.album, self.widget)
        self.singerNameLineEdit = LineEdit(self.songInfo.singer, self.widget)
        self.albumSingerLineEdit = LineEdit(self.songInfo.singer, self.widget)
        self.trackLineEdit = VLineEdit(
            r"(\d)|([1-9]\d{1,2})",
            self.tr("The track must be a number below 1000"),
            str(self.songInfo.track),
            self.widget
        )
        self.discLineEdit = VLineEdit(
            r"\d{1,4}",
            self.tr("The disc must be a number below 1000"),
            str(self.songInfo.disc),
            self.widget
        )
        self.yearLineEdit = VLineEdit(
            r"\d{1,4}",
            self.tr("The year must be a number between 1 and 9999"),
            str(self.songInfo.year or ''),
            self.widget
        )

        # state tooltip
        self.stateToolTip = None

        # auto completion of genre
        self.genreCompleter = QCompleter(TCON.GENRES, self.widget)
        self.genreCompleter.setCompletionMode(QCompleter.InlineCompletion)
        self.genreCompleter.setCaseSensitivity(Qt.CaseInsensitive)
        self.genreLineEdit.setCompleter(self.genreCompleter)
        self.__setQss()

    def __initWidget(self):
        """ initialize widgets """
        self.widget.setFixedSize(932, 740)
        for child in self.widget.findChildren(LineEdit):
            child.setFixedSize(408, 40)

        self.songNameLineEdit.setFocus()
        self.songNameLineEdit.clearButton.show()
        self.songPath.setCursor(Qt.PointingHandCursor)

        self.bottomErrorLabel.setFixedWidth(self.widget.width()-60)
        self.bottomErrorIcon.hide()
        self.bottomErrorLabel.hide()
        self.bottomErrorLabel.setWordWrap(True)

        # connect signal to slot
        self.__connectSignalToSlot()

    def __initLayout(self):
        """ initialize layout """
        self.editInfoLabel.move(30, 30)
        self.getMetaDataLabel.move(30, 465)
        self.getMetaDataSwitchButton.move(30, 498)
        self.songPathLabel.move(30, 560)
        self.songPath.move(30, 590)

        # set the position of labels and line edits
        self.gridLayout_1 = QGridLayout()
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_4 = QGridLayout()
        self.vBoxLayout = QVBoxLayout(self.widget)
        self.vBoxLayout.setSpacing(10)

        self.gridLayouts = [
            self.gridLayout_1, self.gridLayout_2, self.gridLayout_3, self.gridLayout_4]
        for gridLayout in self.gridLayouts:
            gridLayout.setContentsMargins(0, 0, 0, 0)
            gridLayout.setVerticalSpacing(4)
            gridLayout.setHorizontalSpacing(55)
            self.vBoxLayout.addLayout(gridLayout)

        self.gridLayout_1.addWidget(self.songNameLabel, 0, 0)
        self.gridLayout_1.addWidget(self.singerNameLabel, 0, 1)
        self.gridLayout_1.addWidget(self.songNameLineEdit, 1, 0)
        self.gridLayout_1.addWidget(self.singerNameLineEdit, 1, 1)

        self.gridLayout_2.addWidget(self.trackLabel, 0, 0)
        self.gridLayout_2.addWidget(self.discLabel, 0, 1)
        self.gridLayout_2.addWidget(self.trackLineEdit, 1, 0)
        self.gridLayout_2.addWidget(self.discLineEdit, 1, 1)

        self.gridLayout_3.addWidget(self.albumNameLabel, 0, 0)
        self.gridLayout_3.addWidget(self.albumSongerLabel, 0, 1)
        self.gridLayout_3.addWidget(self.albumNameLineEdit, 1, 0)
        self.gridLayout_3.addWidget(self.albumSingerLineEdit, 1, 1)

        self.gridLayout_4.addWidget(self.genreLabel, 0, 0)
        self.gridLayout_4.addWidget(self.yearLabel, 0, 1)
        self.gridLayout_4.addWidget(self.genreLineEdit, 1, 0)
        self.gridLayout_4.addWidget(self.yearLineEdit, 1, 1)

        # adjust dialog height
        newSongPath, isWordWrap = autoWrap(self.songPath.text(), 110)
        if isWordWrap:
            self.songPath.setText(newSongPath)
            self.songPath.adjustSize()
            self.widget.setFixedHeight(self.widget.height() + 25)

        # set button position
        self.cancelButton.move(
            self.widget.width()-self.cancelButton.width()-30,
            self.widget.height()-self.cancelButton.height()-15)
        self.saveButton.move(
            self.cancelButton.x()-self.saveButton.width()-5,
            self.cancelButton.y())

        self.bottomErrorIcon.move(30, self.widget.height() - 108)
        self.bottomErrorLabel.move(55, self.widget.height() - 112)
        self.vBoxLayout.setContentsMargins(
            30, 87, 30, self.widget.height()-87-335)

    def __setQss(self):
        """ set style sheet """
        self.editInfoLabel.setObjectName("editSongInfo")
        self.singerNameLineEdit.setObjectName("singer")
        self.albumSingerLineEdit.setObjectName("singer")
        self.songPath.setObjectName("songPath")
        self.bottomErrorLabel.setObjectName("bottomErrorLabel")

        setStyleSheet(self, 'song_info_edit_dialog')

        self.saveButton.adjustSize()
        self.cancelButton.adjustSize()
        self.songPath.adjustSize()
        self.editInfoLabel.adjustSize()
        self.getMetaDataLabel.adjustSize()

    def __saveInfo(self):
        """ save song information """
        if not self.__validate():
            return

        self.songInfo.genre = self.genreLineEdit.text()
        self.songInfo.title = self.songNameLineEdit.text()
        self.songInfo.year = int(self.yearLineEdit.text())
        self.songInfo.disc = int(self.discLineEdit.text())
        self.songInfo.album = self.albumNameLineEdit.text()
        self.songInfo.track = int(self.trackLineEdit.text())
        self.songInfo.singer = self.singerNameLineEdit.text()

        # write album cover
        success = True
        if self.songInfo.get('coverPath'):
            success = self.writer.writeAlbumCover(
                self.songInfo.file, self.songInfo['coverPath'])
            AlbumCoverReader.getAlbumCover(self.songInfo)

        # embed lyrics
        if config.get(config.embedLyricWhenSave):
            path = getLyricPath(self.songInfo.singer, self.songInfo.title)
            if path.exists() and Lyric.load(path).isValid():
                success &= self.writer.writeLyrics(
                    self.songInfo.file, Lyric.load(path).serialize())

        # write other meta data
        if not (success and self.writer.writeSongInfo(self.songInfo)):
            self.__setErrorMessageVisible(
                self.tr("An unknown error was encountered. Please try again later"), True)
            return

        self.setEnabled(False)
        QApplication.processEvents()
        self.songInfo.modifiedTime = SongInfoReader.getModifiedTime(
            self.songInfo.file)
        self.saveInfoSig.emit(self.oldSongInfo, self.songInfo)
        self.close()

    def __validate(self) -> bool:
        """ validate the text of line edits """
        illegal = False
        message = ''
        for lineEdit in self.findChildren(VLineEdit):
            if not lineEdit.validate():
                illegal = True
                message = message or lineEdit.errorMessage

        self.__setErrorMessageVisible(message, illegal)
        return not illegal

    def __setErrorMessageVisible(self, message: str, isVisible: bool):
        """ show error message at the bottom """
        self.bottomErrorLabel.setText(message)
        self.bottomErrorLabel.adjustSize()
        self.saveButton.setDisabled(isVisible)
        self.bottomErrorLabel.setVisible(isVisible)
        self.bottomErrorIcon.setVisible(isVisible)

    def __onGetMetaDataCheckedChanged(self, isChecked: bool):
        """ get meta data checked state changed """
        if not isChecked:
            return

        self.getMetaDataSwitchButton.setText(self.tr('On'))
        self.getMetaDataSwitchButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.cancelButton.setEnabled(False)

        # create state tooltip
        self.stateToolTip = StateTooltip(self.tr('Retrieve metadata...'),
                                         self.tr('Please wait patiently'), self)
        self.stateToolTip.show()

        # create crawler thread
        crawler = GetSongMetaDataThread(self.songInfo.file, self)
        crawler.crawlFinished.connect(self.__onCrawlFinished)
        crawler.finished.connect(self.__onCrawlThreadFinished)
        crawler.start()

    def __onCrawlFinished(self, success: bool, songInfo: SongInfo):
        """ crawl meta data finished slot """
        if success:
            self.stateToolTip.setTitle(
                self.tr('Successfully retrieved metadata'))
            self.stateToolTip.setContent(self.tr('Please check metadata'))

            # update line edit
            self.songNameLineEdit.setText(songInfo.title)
            self.singerNameLineEdit.setText(songInfo.singer)
            self.albumSingerLineEdit.setText(songInfo.singer)
            self.trackLineEdit.setText(str(songInfo.track))
            self.yearLineEdit.setText(
                str(songInfo.year if songInfo.year else ''))
            self.genreLineEdit.setText(songInfo.genre)
            self.albumNameLineEdit.setText(songInfo.album)
            self.songInfo['coverPath'] = songInfo.get('coverPath')
        else:
            self.stateToolTip.setTitle(
                self.tr('Failed to retrieve metadata'))
            self.stateToolTip.setContent(self.tr("Please check your network"))

        self.stateToolTip.setState(True)
        self.stateToolTip = None

        self.getMetaDataSwitchButton.setText(self.tr('Off'))
        self.getMetaDataSwitchButton.setChecked(False)
        self.getMetaDataSwitchButton.setEnabled(True)
        self.saveButton.setEnabled(True)
        self.cancelButton.setEnabled(True)

    def __onCrawlThreadFinished(self):
        """ delete crawler thread """
        self.sender().quit()
        self.sender().wait()
        self.sender().deleteLater()

    def __connectSignalToSlot(self):
        self.trackLineEdit.textChanged.connect(self.__validate)
        self.discLineEdit.textChanged.connect(self.__validate)
        self.yearLineEdit.textChanged.connect(self.__validate)
        self.getMetaDataSwitchButton.checkedChanged.connect(
            self.__onGetMetaDataCheckedChanged)
        self.saveButton.clicked.connect(self.__saveInfo)
        self.cancelButton.clicked.connect(self.close)
        self.songPath.clicked.connect(lambda: showInFolder(self.songInfo.file))
