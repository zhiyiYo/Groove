# coding:utf-8
from copy import deepcopy
from pathlib import Path

from common.style_sheet import setStyleSheet
from common.database.entity import AlbumInfo, SongInfo
from common.image_utils import getPicSuffix
from common.os_utils import getCoverName, getCoverPath
from components.buttons.perspective_button import PerspectivePushButton
from components.widgets.label import ErrorIcon, PixmapLabel
from components.widgets.line_edit import LineEdit
from components.widgets.perspective_widget import PerspectiveWidget
from components.widgets.scroll_area import ScrollArea
from mutagen.id3 import TCON
from PyQt5.QtCore import QFile, QRegExp, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import (QBrush, QColor, QLinearGradient, QPainter, QPixmap,
                         QRegExpValidator)
from PyQt5.QtWidgets import (QApplication, QCompleter, QFileDialog, QLabel,
                             QWidget)

from .mask_dialog_base import MaskDialogBase


class AlbumInfoEditDialog(MaskDialogBase):
    """ Album information edit dialog box """

    saveInfoSig = pyqtSignal(AlbumInfo, AlbumInfo, str)
    MAXHEIGHT = 755

    def __init__(self, albumInfo: AlbumInfo, parent):
        super().__init__(parent)
        self.oldAlbumInfo = deepcopy(albumInfo)
        self.albumInfo = deepcopy(albumInfo)
        self.genre = self.albumInfo.genre or ''
        self.singer = self.albumInfo.singer or ''
        self.album = self.albumInfo.album or ''  # type:str
        self.coverPath = getCoverPath(self.singer, self.album, 'album_big')
        self.songInfos = self.albumInfo.songInfos  # type:list
        self.newAlbumCoverPath = ''
        self.__createWidgets()
        self.__initWidget()

    def __createWidgets(self):
        """ create widgets """
        self.delayTimer = QTimer(self)

        # create scroll area and title
        self.scrollArea = ScrollArea(self.widget)
        self.scrollWidget = QWidget()
        self.editAlbumInfoLabel = QLabel(
            self.tr("Edit Album Info"), self.widget)

        # Upper half
        self.albumCover = AlbumCoverWindow(
            self.coverPath, (170, 170), self.scrollWidget)
        self.albumNameLineEdit = LineEdit(self.album, self.scrollWidget)
        self.albumSongerLineEdit = LineEdit(self.singer, self.scrollWidget)
        self.genreLineEdit = LineEdit(self.genre, self.scrollWidget)
        self.albumNameLabel = QLabel(self.tr("Album title"), self.scrollWidget)
        self.albumSongerLabel = QLabel(
            self.tr("Album artist"), self.scrollWidget)
        self.genreLabel = QLabel(self.tr("Genre"), self.scrollWidget)

        # Lower half
        self.songInfoWidgets = []
        for songInfo in self.songInfos:
            songInfoWidget = SongInfoWidget(songInfo, self.scrollWidget)
            songInfoWidget.isTrackNumEmptySig.connect(self.__trackNumEmptySlot)
            self.songInfoWidgets.append(songInfoWidget)

        self.saveButton = PerspectivePushButton(self.tr("Save"), self.widget)
        self.cancelButton = PerspectivePushButton(
            self.tr("Cancel"), self.widget)

    def __initWidget(self):
        """ initialize widgets """
        self.widget.setFixedWidth(936)
        self.widget.setMaximumHeight(self.MAXHEIGHT)
        self.scrollArea.setWidget(self.scrollWidget)
        self.songInfoWidgetNum = len(self.songInfoWidgets)  # type:int

        # initialize timer
        self.delayTimer.setInterval(300)
        self.delayTimer.timeout.connect(self.__showFileDialog)

        # set the size of scroll area
        if self.songInfoWidgetNum <= 4:
            self.scrollArea.resize(931, 216 + self.songInfoWidgetNum * 83)
        else:
            self.scrollArea.resize(931, 595)

        self.__setQss()
        self.__initLayout()
        self.__connectSignalToSlot()

        # auto completion of genre
        self.genreCompleter = QCompleter(TCON.GENRES, self.widget)
        self.genreCompleter.setCompletionMode(QCompleter.InlineCompletion)
        self.genreCompleter.setCaseSensitivity(Qt.CaseInsensitive)
        self.genreLineEdit.setCompleter(self.genreCompleter)

    def __initLayout(self):
        """ initialize layout """
        self.editAlbumInfoLabel.move(30, 30)
        self.scrollArea.move(2, 62)
        self.albumCover.move(30, 13)
        self.albumNameLabel.move(225, 7)
        self.albumSongerLabel.move(578, 7)
        self.genreLabel.move(225, 77)
        self.albumNameLineEdit.move(225, 36)
        self.albumSongerLineEdit.move(578, 36)
        self.genreLineEdit.move(225, 106)

        for i, songInfoWidget in enumerate(self.songInfoWidgets):
            songInfoWidget.move(0, songInfoWidget.height() * i + 216)

        self.scrollWidget.resize(931, self.songInfoWidgetNum * 83 + 216)
        self.albumNameLineEdit.resize(327, 40)
        self.albumSongerLineEdit.resize(326, 40)
        self.genreLineEdit.resize(327, 40)

        self.widget.setFixedSize(
            936, self.scrollArea.y() + self.scrollArea.height() + 98)

        self.cancelButton.move(self.widget.width()-self.cancelButton.width()-30,
                               self.widget.height()-16-self.cancelButton.height())
        self.saveButton.move(self.cancelButton.x() -
                             self.saveButton.width()-5, self.cancelButton.y())

    def __setQss(self):
        """ set style sheet """
        self.scrollArea.setObjectName("infoEditScrollArea")
        self.editAlbumInfoLabel.setObjectName("editAlbumInfo")

        setStyleSheet(self, 'album_info_edit_dialog')

        self.saveButton.adjustSize()
        self.cancelButton.adjustSize()

    def __trackNumEmptySlot(self, isShowErrorMsg: bool):
        """ Disable the save button if the track is empty """
        self.saveButton.setEnabled(not isShowErrorMsg)
        if not self.sender().bottomErrorLabel.isVisible():
            senderIndex = self.songInfoWidgets.index(self.sender())
            self.__adjustWidgetPos(senderIndex, isShowErrorMsg)

    def onSaveError(self, index: int):
        """ save fails slot """
        songInfoWidget = self.songInfoWidgets[index]
        if not songInfoWidget.bottomErrorLabel.isVisible():
            senderIndex = self.songInfoWidgets.index(songInfoWidget)
            self.__adjustWidgetPos(senderIndex, True)

        songInfoWidget.setSaveSongInfoErrorMsgHidden(False)

    def onSaveComplete(self):
        """ save successfully slot """
        self.__saveAlbumCover()
        self.close()

    def __adjustWidgetPos(self, senderIndex, isShowErrorMsg: bool):
        """ 调整小部件位置 """
        # adjust the height of dialog
        dh = 54 if isShowErrorMsg else -54
        if self.widget.height() == self.MAXHEIGHT:
            if dh < 0:
                height = self.scrollWidget.height() + dh
                if height < 600:
                    self.widget.setFixedSize(936, height + 155)
                    self.scrollArea.resize(931, height)
        elif self.MAXHEIGHT - abs(dh) < self.widget.height() < self.MAXHEIGHT:
            if dh > 0:
                self.widget.setFixedSize(936, self.MAXHEIGHT)
                self.scrollArea.resize(931, 600)
            else:
                self.__adjustHeight(dh)
        elif self.widget.height() <= self.MAXHEIGHT - abs(dh):
            self.__adjustHeight(dh)

        self.scrollWidget.resize(931, self.scrollWidget.height() + dh)
        self.saveButton.move(563, self.widget.height() -
                             16-self.saveButton.height())
        self.cancelButton.move(735, self.widget.height() -
                               16-self.saveButton.height())

        # adjust postion of widgets
        for songInfoWidget in self.songInfoWidgets[senderIndex + 1:]:
            songInfoWidget.move(0, songInfoWidget.y() + dh)

    def __adjustHeight(self, deltaHeight):
        """ adjust height """
        self.widget.setFixedSize(936, self.widget.height() + deltaHeight)
        self.scrollArea.resize(931, self.scrollArea.height() + deltaHeight)

    def __saveAlbumInfo(self):
        """ save album information """
        self.__setWidgetEnable(False)

        # update album information
        self.albumInfo["album"] = self.albumNameLineEdit.text()
        self.albumInfo["singer"] = self.albumSongerLineEdit.text()
        self.albumInfo["genre"] = self.genreLineEdit.text()

        for songInfo, widget in zip(self.songInfos, self.songInfoWidgets):
            songInfo["album"] = self.albumNameLineEdit.text()
            songInfo["title"] = widget.songNameLineEdit.text()
            songInfo["singer"] = widget.singerLineEdit.text()
            songInfo["genre"] = self.genreLineEdit.text()
            songInfo["track"] = int(widget.trackLineEdit.text())

        self.saveInfoSig.emit(
            self.oldAlbumInfo, self.albumInfo, self.newAlbumCoverPath)

        self.__setWidgetEnable(True)

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.saveButton.clicked.connect(self.__saveAlbumInfo)
        self.cancelButton.clicked.connect(self.close)
        self.albumCover.clicked.connect(self.delayTimer.start)

    def __showFileDialog(self):
        """ show file dialog to select album cover """
        self.delayTimer.stop()
        path, _ = QFileDialog.getOpenFileName(
            self, self.tr("Open"), "./", self.tr("All files")+"(*.png;*.jpg;*.jpeg;*jpe;*jiff)")

        if not path or Path(self.coverPath).absolute() == Path(path).absolute():
            return

        # update album cover label
        self.newAlbumCoverPath = path
        self.albumCover.setAlbumCover(path)

    def __saveAlbumCover(self):
        """ save album cover """
        if not self.newAlbumCoverPath:
            return

        with open(self.newAlbumCoverPath, "rb") as f:
            picData = f.read()

        # get suffix of new album cover
        suffix = getPicSuffix(picData)

        # modify the cover path if it's default
        if self.coverPath == ":/images/default_covers/album_200_200.png":
            name = getCoverName(self.singer, self.album)
            coverPath = Path(f"cache/Album_Cover/{name}/cover{suffix}")
        else:
            coverPath = Path(self.coverPath)

        coverPath.parent.mkdir(exist_ok=True, parents=True)
        with open(coverPath, "wb") as f:
            f.write(picData)

        if suffix != coverPath.suffix:
            coverPath.rename(coverPath.with_suffix(suffix))

    def __setWidgetEnable(self, isEnable: bool):
        """ set whether widgets is enabled """
        self.setEnabled(isEnable)
        self.setStyle(QApplication.style())


class SongInfoWidget(QWidget):
    """ Song information widget """

    isTrackNumEmptySig = pyqtSignal(bool)

    def __init__(self, songInfo: SongInfo, parent=None):
        super().__init__(parent)
        self.songInfo = songInfo
        self.trackLabel = QLabel(self.tr("Track"), self)
        self.songNameLabel = QLabel(self.tr("Song title"), self)
        self.singerLabel = QLabel(self.tr("Song artist"), self)
        self.trackLineEdit = LineEdit(str(songInfo.track or 1), self, False)
        self.songNameLineEdit = LineEdit(songInfo.title or '', self)
        self.singerLineEdit = LineEdit(songInfo.singer or '', self)
        self.errorIcon = ErrorIcon(self)
        self.bottomErrorIcon = ErrorIcon(self)
        self.bottomErrorLabel = QLabel(
            self.tr("The track must be a number below 1000"), self)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setFixedSize(903, 83)
        self.__initLayout()

        # set properties and ID
        self.bottomErrorLabel.setObjectName("bottomErrorLabel")
        self.trackLineEdit.setProperty("hasClearBt", "false")
        self.trackLineEdit.setProperty("hasText", "false")
        self.__setTrackNumEmptyErrorMsgHidden(True)
        self.__checkTrackNum()

        # set filter
        trackReg = QRegExp(r"(\d)|([1-9]\d{1,2})")
        trackValidator = QRegExpValidator(trackReg, self.trackLineEdit)
        self.trackLineEdit.setValidator(trackValidator)

        # connect signal to slot
        self.trackLineEdit.textChanged.connect(self.__checkTrackNum)

    def __initLayout(self):
        """ initialize layout """
        self.trackLabel.move(30, 0)
        self.songNameLabel.move(135, 0)
        self.singerLabel.move(532, 0)
        self.trackLineEdit.move(30, 26)
        self.songNameLineEdit.move(135, 26)
        self.singerLineEdit.move(532, 26)
        self.errorIcon.move(7, 36)
        self.bottomErrorIcon.move(30, 95)
        self.bottomErrorLabel.move(59, 94)
        self.trackLineEdit.resize(80, 41)
        self.singerLineEdit.resize(371, 41)
        self.songNameLineEdit.resize(371, 41)

    def __checkTrackNum(self):
        """ check if the track number line edit is empty """
        text = self.trackLineEdit.text()
        if text and self.trackLineEdit.property("hasText") == "false":
            self.__setTrackNumEmptyErrorMsgHidden(True)
            self.setFixedSize(903, 83)
            self.isTrackNumEmptySig.emit(False)
            self.trackLineEdit.setProperty("hasText", "true")
            self.setStyle(QApplication.style())
        elif not self.trackLineEdit.text():
            self.isTrackNumEmptySig.emit(True)
            self.setFixedSize(903, 137)
            self.__setTrackNumEmptyErrorMsgHidden(False)
            self.trackLineEdit.setProperty("hasText", "false")
            self.setStyle(QApplication.style())

    def __setTrackNumEmptyErrorMsgHidden(self, isHidden: bool):
        """ Set whether the track is empty message is displayed """
        self.errorIcon.setHidden(isHidden)
        self.bottomErrorIcon.setHidden(isHidden)
        self.bottomErrorLabel.setText(
            self.tr("The track must be a number below 1000"))
        self.bottomErrorLabel.adjustSize()
        self.bottomErrorLabel.setHidden(isHidden)

    def setSaveSongInfoErrorMsgHidden(self, isHidden: bool):
        """ set whether save song information error message is hidden """
        if not isHidden:
            self.setFixedSize(903, 137)
        else:
            self.setFixedSize(903, 83)

        self.errorIcon.setHidden(isHidden)
        self.bottomErrorIcon.setHidden(isHidden)
        self.bottomErrorLabel.setText(
            self.tr("An unknown error was encountered. Please try again later"))
        self.bottomErrorLabel.adjustSize()
        self.bottomErrorLabel.setHidden(isHidden)

    def setLineEditEnable(self, isEnable: bool):
        """ set whether line edit is enabled """
        self.songNameLineEdit.setEnabled(isEnable)
        self.singerLineEdit.setEnabled(isEnable)
        self.trackLineEdit.setEnabled(isEnable)


class AlbumCoverWindow(PerspectiveWidget):
    """ 显示专辑封面窗口 """

    clicked = pyqtSignal()

    def __init__(self, picPath: str, picSize: tuple, parent=None):
        super().__init__(parent)
        self.__picPath = picPath
        self.__picSize = picSize
        self.albumCoverLabel = PixmapLabel(self)
        self.albumCoverMask = AlbumCoverMask(self)
        self.editAlbumCoverLabel = PixmapLabel(self)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widget """
        self.setFixedSize(*self.__picSize)
        self.albumCoverLabel.setFixedSize(*self.__picSize)
        self.setAlbumCover(self.__picPath)
        self.editAlbumCoverLabel.setAttribute(Qt.WA_TranslucentBackground)
        self.editAlbumCoverLabel.setPixmap(
            QPixmap(":/images/album_interface/Edit.png"))
        self.editAlbumCoverLabel.move(14, 137)

    def setAlbumCover(self, picPath: str):
        """ set album cover """
        self.__picPath = picPath
        self.albumCoverLabel.setPixmap(QPixmap(picPath).scaled(
            self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.clicked.emit()


class AlbumCoverMask(QWidget):
    """ Mask of album cover """

    def __init__(self, parent, size: tuple = (170, 170)):
        super().__init__(parent)
        self.resize(*size)

    def paintEvent(self, e):
        """ paint mask """
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        gradientColor = QLinearGradient(0, self.height(), self.width(), 0)
        gradientColor.setColorAt(0, QColor(0, 0, 0, 128))
        gradientColor.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(gradientColor))
        painter.drawRect(self.rect())
