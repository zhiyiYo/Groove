# coding:utf-8
from copy import deepcopy

from app.common.os_utils import adjustName
from app.common.auto_wrap import autoWrap
from app.common.meta_data_writer import writeSongInfo
from app.components.buttons.perspective_button import PerspectivePushButton
from app.components.label import ErrorIcon
from app.components.line_edit import LineEdit
from PyQt5.QtCore import QRegExp, Qt, pyqtSignal
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QApplication, QCompleter, QLabel, QGridLayout, QVBoxLayout

from .mask_dialog_base import MaskDialogBase


class SongInfoEditDialog(MaskDialogBase):
    """ 歌曲信息编辑对话框 """

    saveInfoSig = pyqtSignal(dict, dict)

    def __init__(self, songInfo: dict, parent):
        super().__init__(parent)

        self.songInfo = deepcopy(songInfo)
        self.oldSongInfo = songInfo
        # 实例化小部件
        self.__createWidgets()
        # 初始化小部件
        self.__initWidget()
        self.__initLayout()
        # 设置层叠样式

    def __createWidgets(self):
        """ 实例化小部件 """
        # 实例化按钮
        self.saveButton = PerspectivePushButton("保存", self.widget)
        self.cancelButton = PerspectivePushButton("取消", self.widget)
        # 实例化标签
        self.yearLabel = QLabel("年", self.widget)
        self.genreLabel = QLabel("类型", self.widget)
        self.diskLabel = QLabel("光盘", self.widget)
        self.trackNumLabel = QLabel("曲目", self.widget)
        self.songNameLabel = QLabel("歌曲名", self.widget)
        self.songPathLabel = QLabel("文件位置", self.widget)
        self.albumNameLabel = QLabel("专辑标题", self.widget)
        self.singerNameLabel = QLabel("歌曲歌手", self.widget)
        self.albumSongerLabel = QLabel("专辑歌手", self.widget)
        self.editInfoLabel = QLabel("编辑歌曲信息", self.widget)
        self.songPath = QLabel(
            self.songInfo["songPath"].replace('\\', '/'), self.widget)
        self.emptyTrackErrorIcon = ErrorIcon(self.widget)
        self.bottomErrorIcon = ErrorIcon(self.widget)
        self.bottomErrorLabel = QLabel(self.widget)
        # 实例化单行输入框
        self.diskLineEdit = LineEdit("1", self.widget)
        self.genreLineEdit = LineEdit(self.songInfo["genre"], self.widget)
        self.yearLineEdit = LineEdit(self.songInfo["year"], self.widget)
        self.albumNameLineEdit = LineEdit(self.songInfo["album"], self.widget)
        self.songNameLineEdit = LineEdit(
            self.songInfo["songName"], self.widget)
        self.singerNameLineEdit = LineEdit(
            self.songInfo["singer"], self.widget)
        self.albumSongerLineEdit = LineEdit(
            self.songInfo["singer"], self.widget)
        self.trackNumLineEdit = LineEdit(
            self.songInfo["tracknumber"], self.widget)
        # 流派补全
        genres = [
            "POP流行",
            "Blues",
            "SOUNDTRACK原声",
            "Japanese Pop & Rock",
            "摇滚",
            "Soundtrack",
            "J-Pop",
            "RAP/HIP HOP",
            "Soundtrack",
            "古典",
            "经典",
            "Country",
            "R&B",
            "ROCK摇滚",
            "anime",
        ]
        self.genreCompleter = QCompleter(genres, self.widget)
        self.genreCompleter.setCompletionMode(QCompleter.InlineCompletion)
        self.genreCompleter.setCaseSensitivity(Qt.CaseInsensitive)
        self.genreLineEdit.setCompleter(self.genreCompleter)
        self.__setQss()

    def __initWidget(self):
        """ 初始化小部件的属性 """
        self.widget.setFixedSize(932, 652)
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
        self.trackNumLineEdit.textChanged.connect(
            self.__onTrackNumLineEditTextChanged)

        # 将按钮点击信号连接到槽函数
        self.saveButton.clicked.connect(self.__saveInfo)
        self.cancelButton.clicked.connect(self.close)

    def __initLayout(self):
        """ 初始化布局 """
        self.editInfoLabel.move(30, 30)
        self.songPathLabel.move(30, 470)
        self.songPath.move(30, 502)

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

        self.gridLayout_2.addWidget(self.trackNumLabel, 0, 0)
        self.gridLayout_2.addWidget(self.diskLabel, 0, 1)
        self.gridLayout_2.addWidget(self.trackNumLineEdit, 1, 0)
        self.gridLayout_2.addWidget(self.diskLineEdit, 1, 1)

        self.gridLayout_3.addWidget(self.albumNameLabel, 0, 0)
        self.gridLayout_3.addWidget(self.albumSongerLabel, 0, 1)
        self.gridLayout_3.addWidget(self.albumNameLineEdit, 1, 0)
        self.gridLayout_3.addWidget(self.albumSongerLineEdit, 1, 1)

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
        self.bottomErrorIcon.move(30, self.widget.height() - 110)
        self.bottomErrorLabel.move(55, self.widget.height() - 112)
        self.vBoxLayout.setContentsMargins(
            30, 87, 30, self.widget.height()-87-335)

    def __installValidator(self):
        """ 给输入框设置过滤器 """
        rex_trackNum = QRegExp(r"(\d)|([1-9]\d{1,2})")
        rex_year = QRegExp(r"\d{4}年{0,1}")
        validator_tracknum = QRegExpValidator(
            rex_trackNum, self.trackNumLineEdit)
        validator_disk = QRegExpValidator(rex_trackNum, self.diskLineEdit)
        validator_year = QRegExpValidator(rex_year, self.yearLineEdit)
        self.trackNumLineEdit.setValidator(validator_tracknum)
        self.diskLineEdit.setValidator(validator_disk)
        self.yearLineEdit.setValidator(validator_year)

    def __setQss(self):
        """ 设置层叠样式表 """
        self.editInfoLabel.setObjectName("editSongInfo")
        self.singerNameLineEdit.setObjectName("singer")
        self.albumSongerLineEdit.setObjectName("singer")
        self.songPath.setObjectName("songPath")
        self.bottomErrorLabel.setObjectName("bottomErrorLabel")
        with open("app/resource/css/song_info_edit_dialog.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())
        self.saveButton.adjustSize()
        self.cancelButton.adjustSize()
        self.songPath.adjustSize()
        self.editInfoLabel.adjustSize()

    def __saveInfo(self):
        """ 保存标签卡信息 """
        self.songInfo["songName"] = self.songNameLineEdit.text()
        self.songInfo["singer"] = self.singerNameLineEdit.text()
        self.songInfo["album"] = self.albumNameLineEdit.text()
        self.songInfo["coverName"] = adjustName(
            self.songInfo["singer"]+'_'+self.songInfo["album"])
        # 根据后缀名选择曲目标签的写入方式
        self.songInfo["tracknumber"] = self.trackNumLineEdit.text()
        self.songInfo["genre"] = self.genreLineEdit.text()
        if self.yearLineEdit.text()[:4] != "未知年份":
            self.songInfo["year"] = self.yearLineEdit.text()[:4] + "年"
        else:
            self.songInfo["year"] = "未知年份"

        if not writeSongInfo(self.songInfo):
            self.bottomErrorLabel.setText("遇到未知错误，请稍后再试")
            self.bottomErrorLabel.adjustSize()
            self.bottomErrorLabel.show()
            self.bottomErrorIcon.show()
        else:
            self.setEnabled(False)
            QApplication.processEvents()
            self.saveInfoSig.emit(self.oldSongInfo, self.songInfo)
            self.close()

    def __onTrackNumLineEditTextChanged(self):
        """ 检查曲目输入框的内容是否为空 """
        isEmpty = bool(self.genreLineEdit.text())

        if isEmpty:
            self.bottomErrorLabel.setText("曲目必须是1000以下的数字")
            self.bottomErrorLabel.adjustSize()

        # 设置提示标签可见性和按钮是否启用
        self.saveButton.setDisabled(isEmpty)
        self.bottomErrorLabel.setVisible(isEmpty)
        self.bottomErrorIcon.setVisible(isEmpty)
        self.emptyTrackErrorIcon.setVisible(isEmpty)

        # 更新样式
        self.trackNumLineEdit.setProperty(
            'hasText', 'false' if isEmpty else 'true')
        self.trackNumLineEdit.setStyle(QApplication.style())
