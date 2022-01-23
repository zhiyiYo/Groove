# coding:utf-8
from copy import deepcopy

from common.database.entity import SongInfo
from common.auto_wrap import autoWrap
from common.meta_data import AlbumCoverReader, GENRES, SongInfoReader
from common.meta_data.writer import writeSongInfo, writeAlbumCover
from common.os_utils import adjustName
from common.thread.get_meta_data_thread import GetSongMetaDataThread
from components.widgets.state_tooltip import StateTooltip
from components.buttons.perspective_button import PerspectivePushButton
from components.buttons.switch_button import SwitchButton
from components.widgets.label import ErrorIcon
from components.widgets.line_edit import LineEdit
from PyQt5.QtCore import QFile, QRegExp, Qt, pyqtSignal
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import (QApplication, QCompleter, QGridLayout, QLabel,
                             QVBoxLayout)

from .mask_dialog_base import MaskDialogBase


class SongInfoEditDialog(MaskDialogBase):
    """ 歌曲信息编辑对话框 """

    saveInfoSig = pyqtSignal(SongInfo, SongInfo)

    def __init__(self, songInfo: SongInfo, parent):
        super().__init__(parent)
        self.songInfo = songInfo.copy()
        self.oldSongInfo = songInfo

        # 实例化小部件
        self.__createWidgets()

        # 初始化小部件
        self.__initWidget()
        self.__initLayout()

    def __createWidgets(self):
        """ 实例化小部件 """
        # 按钮
        self.saveButton = PerspectivePushButton(self.tr("Save"), self.widget)
        self.cancelButton = PerspectivePushButton(
            self.tr("Cancel"), self.widget)
        self.getMetaDataSwitchButton = SwitchButton(
            self.tr('Off'), self.widget)

        # 标签
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
        self.songPath = QLabel(self.songInfo.file, self.widget)
        self.getMetaDataLabel = QLabel(
            self.tr('Automatically retrieve metadata'), self.widget)
        self.emptyTrackErrorIcon = ErrorIcon(self.widget)
        self.bottomErrorIcon = ErrorIcon(self.widget)
        self.bottomErrorLabel = QLabel(self.widget)

        # 单行输入框
        self.genreLineEdit = LineEdit(self.songInfo.genre, self.widget)
        self.songNameLineEdit = LineEdit(self.songInfo.title, self.widget)
        self.discLineEdit = LineEdit(str(self.songInfo.disc), self.widget)
        self.albumNameLineEdit = LineEdit(self.songInfo.album, self.widget)
        self.trackLineEdit = LineEdit(str(self.songInfo.track), self.widget)
        self.singerNameLineEdit = LineEdit(self.songInfo.singer, self.widget)
        self.albumSingerLineEdit = LineEdit(self.songInfo.singer, self.widget)
        self.yearLineEdit = LineEdit(
            str(self.songInfo.year if self.songInfo.year else ''), self.widget)

        # 进度提示条
        self.stateToolTip = None

        # 流派补全
        self.genreCompleter = QCompleter(GENRES, self.widget)
        self.genreCompleter.setCompletionMode(QCompleter.InlineCompletion)
        self.genreCompleter.setCaseSensitivity(Qt.CaseInsensitive)
        self.genreLineEdit.setCompleter(self.genreCompleter)
        self.__setQss()

    def __initWidget(self):
        """ 初始化小部件的属性 """
        self.widget.setFixedSize(932, 740)
        for child in self.widget.findChildren(LineEdit):
            child.setFixedSize(408, 40)

        # 默认选中歌名编辑框
        self.songNameLineEdit.setFocus()
        self.songNameLineEdit.clearButton.show()

        # 设置报警标签位置
        self.bottomErrorLabel.setMinimumWidth(100)
        self.emptyTrackErrorIcon.move(7, 227)
        self.bottomErrorIcon.hide()
        self.bottomErrorLabel.hide()
        self.emptyTrackErrorIcon.hide()

        # 给输入框设置过滤器
        self.__installValidator()

        # 将曲目输入框数字改变的信号连接到槽函数
        self.trackLineEdit.textChanged.connect(
            self.__onTrackNumLineEditTextChanged)
        self.getMetaDataSwitchButton.checkedChanged.connect(
            self.__onGetMetaDataCheckedChanged)

        # 将按钮点击信号连接到槽函数
        self.saveButton.clicked.connect(self.__saveInfo)
        self.cancelButton.clicked.connect(self.close)

    def __initLayout(self):
        """ 初始化布局 """
        self.editInfoLabel.move(30, 30)
        self.getMetaDataLabel.move(30, 465)
        self.getMetaDataSwitchButton.move(30, 498)
        self.songPathLabel.move(30, 560)
        self.songPath.move(30, 590)

        # 设置对话框和标签位置
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

        # 调整对话框高度
        newSongPath, isWordWrap = autoWrap(self.songPath.text(), 110)
        if isWordWrap:
            self.songPath.setText(newSongPath)
            self.songPath.adjustSize()
            self.widget.setFixedHeight(self.widget.height() + 25)

        # 设置按钮位置
        self.cancelButton.move(
            self.widget.width()-self.cancelButton.width()-30,
            self.widget.height()-self.cancelButton.height()-15)
        self.saveButton.move(
            self.cancelButton.x()-self.saveButton.width()-5,
            self.cancelButton.y())

        # 设置提示标签的位置
        self.bottomErrorIcon.move(30, self.widget.height() - 108)
        self.bottomErrorLabel.move(55, self.widget.height() - 112)
        self.vBoxLayout.setContentsMargins(
            30, 87, 30, self.widget.height()-87-335)

    def __installValidator(self):
        """ 给输入框设置过滤器 """
        trackReg = QRegExp(r"(\d)|([1-9]\d{1,2})")
        yearReg = QRegExp(r"\d{4}")
        trackValidator = QRegExpValidator(trackReg, self.trackLineEdit)
        disValidator = QRegExpValidator(trackReg, self.discLineEdit)
        yearValidator = QRegExpValidator(yearReg, self.yearLineEdit)
        self.trackLineEdit.setValidator(trackValidator)
        self.discLineEdit.setValidator(disValidator)
        self.yearLineEdit.setValidator(yearValidator)

    def __setQss(self):
        """ 设置层叠样式表 """
        self.editInfoLabel.setObjectName("editSongInfo")
        self.singerNameLineEdit.setObjectName("singer")
        self.albumSingerLineEdit.setObjectName("singer")
        self.songPath.setObjectName("songPath")
        self.bottomErrorLabel.setObjectName("bottomErrorLabel")

        f = QFile(":/qss/song_info_edit_dialog.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

        self.saveButton.adjustSize()
        self.cancelButton.adjustSize()
        self.songPath.adjustSize()
        self.editInfoLabel.adjustSize()
        self.getMetaDataLabel.adjustSize()

    def __saveInfo(self):
        """ 保存标签卡信息 """
        self.songInfo.genre = self.genreLineEdit.text()
        self.songInfo.title = self.songNameLineEdit.text()
        self.songInfo.year = int(self.yearLineEdit.text())
        self.songInfo.disc = int(self.discLineEdit.text())
        self.songInfo.album = self.albumNameLineEdit.text()
        self.songInfo.track = int(self.trackLineEdit.text())
        self.songInfo.singer = self.singerNameLineEdit.text()

        # 写入专辑封面
        isOk = True
        if self.songInfo.get('coverPath'):
            isOk = writeAlbumCover(self.songInfo.file,
                                   self.songInfo['coverPath'])
            AlbumCoverReader.getOneAlbumCover(self.songInfo)

        # 写入其他元数据
        if not (isOk and writeSongInfo(self.songInfo)):
            self.bottomErrorLabel.setText(
                self.tr("An unknown error was encountered. Please try again later"))
            self.bottomErrorLabel.adjustSize()
            self.bottomErrorLabel.show()
            self.bottomErrorIcon.show()
        else:
            self.setEnabled(False)
            QApplication.processEvents()
            self.songInfo.modifiedTime = SongInfoReader.getModifiedTime(
                self.songInfo.file)
            self.saveInfoSig.emit(self.oldSongInfo, self.songInfo)
            self.close()

    def __onTrackNumLineEditTextChanged(self):
        """ 检查曲目输入框的内容是否为空 """
        isEmpty = not bool(self.genreLineEdit.text())

        if isEmpty:
            self.bottomErrorLabel.setText(
                self.tr("The track must be a number below 1000"))
            self.bottomErrorLabel.adjustSize()

        # 设置提示标签可见性和按钮是否启用
        self.saveButton.setDisabled(isEmpty)
        self.bottomErrorLabel.setVisible(isEmpty)
        self.bottomErrorIcon.setVisible(isEmpty)
        self.emptyTrackErrorIcon.setVisible(isEmpty)

        # 更新样式
        self.trackLineEdit.setProperty(
            'hasText', 'false' if isEmpty else 'true')
        self.trackLineEdit.setStyle(QApplication.style())

    def __onGetMetaDataCheckedChanged(self, isChecked: bool):
        """ 获取元数据开关按钮选中状态改变槽函数 """
        if not isChecked:
            return

        self.getMetaDataSwitchButton.setText(self.tr('On'))
        self.getMetaDataSwitchButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.cancelButton.setEnabled(False)

        # 创建进度条
        self.stateToolTip = StateTooltip(self.tr('Retrieve metadata...'),
                                         self.tr('Please wait patiently'), self)
        self.stateToolTip.move(self.stateToolTip.getSuitablePos())
        self.stateToolTip.show()

        # 创建爬虫线程
        crawler = GetSongMetaDataThread(self.songInfo.file, self)
        crawler.crawlFinished.connect(self.__onCrawlFinished)
        crawler.finished.connect(self.__onCrawlThreadFinished)
        crawler.start()

    def __onCrawlFinished(self, success: bool, songInfo: SongInfo):
        """ 爬取完成槽函数 """
        if success:
            self.stateToolTip.setTitle(
                self.tr('Successfully retrieved metadata'))
            self.stateToolTip.setContent(self.tr('Please check metadata'))

            # 更新编辑框
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
            self.stateToolTip.setContent(self.tr("Don't mind"))

        self.stateToolTip.setState(True)
        self.stateToolTip = None

        self.getMetaDataSwitchButton.setText(self.tr('Off'))
        self.getMetaDataSwitchButton.setChecked(False)
        self.getMetaDataSwitchButton.setEnabled(True)
        self.saveButton.setEnabled(True)
        self.cancelButton.setEnabled(True)

    def __onCrawlThreadFinished(self):
        """ 爬虫线程结束 """
        self.sender().quit()
        self.sender().wait()
        self.sender().deleteLater()
