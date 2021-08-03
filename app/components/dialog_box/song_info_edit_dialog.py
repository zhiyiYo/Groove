# coding:utf-8
from copy import deepcopy

from app.common.adjust_album_name import adjustAlbumName
from app.common.auto_wrap import autoWrap
from app.common.modify_song_info import modifySongInfo
from app.components.buttons.perspective_button import PerspectivePushButton
from app.components.label import ErrorIcon
from app.components.line_edit import LineEdit
from PyQt5.QtCore import QRegExp, Qt, pyqtSignal
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QApplication, QCompleter, QLabel

from .mask_dialog_base import MaskDialogBase


class SongInfoEditDialog(MaskDialogBase):
    """ 歌曲信息编辑对话框 """

    saveInfoSig = pyqtSignal(dict, dict)

    def __init__(self, songInfo: dict, parent):
        super().__init__(parent)

        self.songInfo = deepcopy(songInfo)
        self.oldSongInfo = deepcopy(songInfo)
        # 实例化小部件
        self.__createWidgets()
        # 初始化小部件
        self.__initWidget()
        self.__initLayout()
        # 设置层叠样式
        self.__setQss()

    def __createWidgets(self):
        """ 实例化小部件 """
        # 实例化按钮
        self.saveButton = PerspectivePushButton("保存", self.widget)
        self.cancelButton = PerspectivePushButton("取消", self.widget)
        # 实例化标签
        self.yearLabel = QLabel("年", self.widget)
        self.tconLabel = QLabel("类型", self.widget)
        self.diskLabel = QLabel("光盘", self.widget)
        self.trackNumLabel = QLabel("曲目", self.widget)
        self.songNameLabel = QLabel("歌曲名", self.widget)
        self.songPathLabel = QLabel("文件位置", self.widget)
        self.albumNameLabel = QLabel("专辑标题", self.widget)
        self.songerNameLabel = QLabel("歌曲歌手", self.widget)
        self.albumSongerLabel = QLabel("专辑歌手", self.widget)
        self.editInfoLabel = QLabel("编辑歌曲信息", self.widget)
        self.songPath = QLabel(self.songInfo["songPath"], self.widget)
        self.emptyTrackErrorIcon = ErrorIcon(self.widget)
        self.bottomErrorIcon = ErrorIcon(self.widget)
        self.bottomErrorLabel = QLabel(self.widget)
        # 实例化单行输入框
        self.diskLineEdit = LineEdit("1", self.widget)
        self.tconLineEdit = LineEdit(self.songInfo["tcon"], self.widget)
        self.yearLineEdit = LineEdit(self.songInfo["year"], self.widget)
        self.albumNameLineEdit = LineEdit(self.songInfo["album"], self.widget)
        self.songNameLineEdit = LineEdit(
            self.songInfo["songName"], self.widget)
        self.songerNameLineEdit = LineEdit(
            self.songInfo["songer"], self.widget)
        self.albumSongerLineEdit = LineEdit(
            self.songInfo["songer"], self.widget)
        self.trackNumLineEdit = LineEdit(
            self.songInfo["tracknumber"], self.widget)
        # 流派补全
        tcons = [
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
        self.tconCompleter = QCompleter(tcons, self.widget)
        self.tconCompleter.setCompletionMode(QCompleter.InlineCompletion)
        self.tconCompleter.setCaseSensitivity(Qt.CaseInsensitive)
        self.tconLineEdit.setCompleter(self.tconCompleter)

        # 创建集中管理小部件的列表
        self.leftLabel_list = [
            self.songNameLabel,
            self.trackNumLabel,
            self.albumNameLabel,
            self.tconLabel,
        ]

        self.rightLabel_list = [
            self.songerNameLabel,
            self.diskLabel,
            self.albumSongerLabel,
            self.yearLabel,
        ]

        self.leftEditLine_list = [
            self.songNameLineEdit,
            self.trackNumLineEdit,
            self.albumNameLineEdit,
            self.tconLineEdit,
        ]

        self.rightEditLine_list = [
            self.songerNameLineEdit,
            self.diskLineEdit,
            self.albumSongerLineEdit,
            self.yearLineEdit,
        ]

        self.editLine_list = [
            self.songNameLineEdit,
            self.songerNameLineEdit,
            self.trackNumLineEdit,
            self.diskLineEdit,
            self.albumNameLineEdit,
            self.albumSongerLineEdit,
            self.tconLineEdit,
            self.yearLineEdit,
        ]

    def __initWidget(self):
        """ 初始化小部件的属性 """
        self.widget.setFixedSize(932, 652)
        # 默认选中歌名编辑框
        self.songNameLineEdit.setFocus()
        self.songNameLineEdit.clearButton.show()
        # 给每个单行输入框设置大小
        for editLine in self.editLine_list:
            editLine.setFixedSize(408, 40)

        # 设置按钮的大小
        self.saveButton.setFixedSize(165, 41)
        self.cancelButton.setFixedSize(165, 41)

        # 设置报警标签位置
        self.bottomErrorLabel.setMinimumWidth(100)
        self.emptyTrackErrorIcon.move(7, 227)
        self.bottomErrorIcon.hide()
        self.bottomErrorLabel.hide()
        self.emptyTrackErrorIcon.hide()

        # 如果曲目为空就禁用保存按钮并更改属性
        self.trackNumLineEdit.setProperty("hasText", "true")
        if not self.trackNumLineEdit.text():
            self.saveButton.setEnabled(False)
            self.emptyTrackErrorIcon.show()
            self.trackNumLineEdit.setProperty("hasText", "false")

        # 给输入框设置过滤器
        rex_trackNum = QRegExp(r"(\d)|([1-9]\d{1,2})")
        rex_year = QRegExp(r"\d{4}年{0,1}")
        validator_tracknum = QRegExpValidator(
            rex_trackNum, self.trackNumLineEdit)
        validator_disk = QRegExpValidator(rex_trackNum, self.diskLineEdit)
        validator_year = QRegExpValidator(rex_year, self.yearLineEdit)
        self.trackNumLineEdit.setValidator(validator_tracknum)
        self.diskLineEdit.setValidator(validator_disk)
        self.yearLineEdit.setValidator(validator_year)

        # 将曲目输入框数字改变的信号连接到槽函数
        self.trackNumLineEdit.textChanged.connect(self.checkTrackEditLine)

        # 将按钮点击信号连接到槽函数
        self.saveButton.clicked.connect(self.saveInfo)
        self.cancelButton.clicked.connect(self.close)

    def __initLayout(self):
        """ 初始化小部件的排版 """
        self.editInfoLabel.move(30, 30)
        self.songPathLabel.move(30, 470)
        self.songPath.move(30, 502)
        self.saveButton.move(566, 595)
        self.cancelButton.move(736, 595)
        label_top_y = 95

        for i, (label_left, label_right) in enumerate(
            zip(self.leftLabel_list, self.rightLabel_list)
        ):
            label_left.setObjectName("infoTypeLabel")
            label_right.setObjectName("infoTypeLabel")
            label_left.move(30, label_top_y + i * 87)
            label_right.move(494, label_top_y + i * 87)

        editLine_top_y = 127

        for i, (editLine_left, editLine_right) in enumerate(
            zip(self.leftEditLine_list, self.rightEditLine_list)
        ):
            editLine_left.move(30, editLine_top_y + i * 87)
            editLine_right.move(494, editLine_top_y + i * 87)

        # 调整高度
        newSongPath, isWordWrap = autoWrap(self.songPath.text(), 100)
        if isWordWrap:
            self.songPath.setText(newSongPath)
            self.setFixedSize(self.widget.width(), self.widget.height() + 25)
            self.cancelButton.move(self.cancelButton.x(),
                                   self.cancelButton.y() + 25)
            self.saveButton.move(self.saveButton.x(), self.saveButton.y() + 25)
        # 调整报错标签的位置
        self.bottomErrorIcon.move(30, self.widget.height() - 110)
        self.bottomErrorLabel.move(55, self.widget.height() - 112)

    def __setQss(self):
        """ 设置层叠样式表 """
        self.editInfoLabel.setObjectName("editSongInfo")
        self.songerNameLineEdit.setObjectName("songer")
        self.albumSongerLineEdit.setObjectName("songer")
        self.songPath.setObjectName("songPath")
        self.bottomErrorLabel.setObjectName("bottomErrorLabel")
        with open("app/resource/css/song_info_edit_dialog.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def saveInfo(self):
        """ 保存标签卡信息 """
        album_list = adjustAlbumName(self.albumNameLineEdit.text())
        self.songInfo["songName"] = self.songNameLineEdit.text()
        self.songInfo["songer"] = self.songerNameLineEdit.text()
        self.songInfo["album"] = album_list[0]
        self.songInfo["modifiedAlbum"] = album_list[-1]
        # 根据后缀名选择曲目标签的写入方式
        self.songInfo["tracknumber"] = self.trackNumLineEdit.text()
        self.songInfo["tcon"] = self.tconLineEdit.text()
        if self.yearLineEdit.text()[:4] != "未知年份":
            self.songInfo["year"] = self.yearLineEdit.text()[:4] + "年"
        else:
            self.songInfo["year"] = "未知年份"
        if not modifySongInfo(self.songInfo):
            self.bottomErrorLabel.setText("遇到未知错误，请稍后再试")
            self.bottomErrorLabel.show()
            self.bottomErrorIcon.show()
        else:
            self.saveInfoSig.emit(self.oldSongInfo, self.songInfo)
            self.close()

    def checkTrackEditLine(self):
        """ 检查曲目输入框的内容是否为空 """
        if not self.trackNumLineEdit.text():
            self.bottomErrorLabel.setText("曲目必须是1000以下的数字")
            self.bottomErrorLabel.show()
            self.emptyTrackErrorIcon.show()
            self.bottomErrorIcon.show()
            self.saveButton.setEnabled(False)
            self.trackNumLineEdit.setProperty("hasText", "false")
        else:
            self.trackNumLineEdit.setProperty("hasText", "true")
            self.bottomErrorLabel.hide()
            self.bottomErrorIcon.hide()
            self.emptyTrackErrorIcon.hide()
            self.saveButton.setEnabled(True)
        self.trackNumLineEdit.setStyle(QApplication.style())
