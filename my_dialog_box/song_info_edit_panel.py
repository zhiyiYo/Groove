# coding:utf-8

import json
from copy import deepcopy

from mutagen import File, MutagenError
from my_functions.adjust_album_name import adjustAlbumName
from my_functions.auto_wrap import autoWrap
from my_functions.modify_songInfo import modifySongInfo
from my_widget.my_label import ErrorIcon
from my_widget.my_lineEdit import LineEdit
from my_widget.perspective_button import PerspectivePushButton
from PyQt5.QtCore import QRegExp, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPen, QRegExpValidator
from PyQt5.QtWidgets import (QApplication, QGraphicsDropShadowEffect, QLabel,
                             QWidget)

from .sub_panel_frame import SubPanelFrame


class SongInfoEditPanel(SubPanelFrame):
    """ 歌曲信息编辑面板 """

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(parent)
        # 实例化子属性面板
        self.subSongInfoEditPanel = SubSongInfoEditPanel(songInfo, self)
        # 初始化
        self.__initWidget()
        self.__initLayout()

    def __initWidget(self):
        """ 初始化小部件 """
        # deleteLater才能真正释放内存
        self.subSongInfoEditPanel.cancelButton.clicked.connect(
            self.deleteLater)
        self.saveInfoSig = self.subSongInfoEditPanel.saveInfoSig
        self.showMask()

    def __initLayout(self):
        """ 初始化布局 """
        self.subSongInfoEditPanel.move(
            int(self.width() / 2 - self.subSongInfoEditPanel.width() / 2),
            int(self.height() / 2 - self.subSongInfoEditPanel.height() / 2))


class SubSongInfoEditPanel(QWidget):
    """ 歌曲信息编辑面板的子窗口 """
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
        self.setShadowEffect()
        # 设置层叠样式
        self.__setQss()

    def __createWidgets(self):
        """ 实例化小部件 """
        # 实例化按钮
        self.saveButton = PerspectivePushButton('保存', self)
        self.cancelButton = PerspectivePushButton('取消', self)
        # 实例化标签
        self.yearLabel = QLabel('年', self)
        self.tconLabel = QLabel('类型', self)
        self.diskLabel = QLabel('光盘', self)
        self.trackNumLabel = QLabel('曲目', self)
        self.songNameLabel = QLabel('歌曲名', self)
        self.songPathLabel = QLabel('文件位置', self)
        self.albumNameLabel = QLabel('专辑标题', self)
        self.songerNameLabel = QLabel('歌曲歌手', self)
        self.albumSongerLabel = QLabel('专辑歌手', self)
        self.editInfoLabel = QLabel('编辑歌曲信息', self)
        self.songPath = QLabel(self.songInfo['songPath'], self)
        self.emptyTrackErrorIcon = ErrorIcon(self)
        self.bottomErrorIcon = ErrorIcon(self)
        self.bottomErrorLabel = QLabel(self)
        # 实例化单行输入框
        self.diskEditLine = LineEdit('1', self)
        self.tconEditLine = LineEdit(self.songInfo['tcon'], self)
        self.yearEditLine = LineEdit(self.songInfo['year'], self)
        self.albumNameEditLine = LineEdit(self.songInfo['album'], self)
        self.songNameEditLine = LineEdit(self.songInfo['songName'], self)
        self.songerNameEditLine = LineEdit(self.songInfo['songer'], self)
        self.albumSongerEditLine = LineEdit(self.songInfo['songer'], self)
        self.trackNumEditLine = LineEdit(self.songInfo['tracknumber'], self)

        # 创建集中管理小部件的列表
        self.leftLabel_list = [
            self.songNameLabel, self.trackNumLabel, self.albumNameLabel, self.tconLabel]

        self.rightLabel_list = [
            self.songerNameLabel, self.diskLabel, self.albumSongerLabel, self.yearLabel]

        self.leftEditLine_list = [
            self.songNameEditLine, self.trackNumEditLine, self.albumNameEditLine, self.tconEditLine]

        self.rightEditLine_list = [
            self.songerNameEditLine, self.diskEditLine, self.albumSongerEditLine, self.yearEditLine]

        self.editLine_list = [self.songNameEditLine, self.songerNameEditLine,
                              self.trackNumEditLine, self.diskEditLine, self.albumNameEditLine,
                              self.albumSongerEditLine, self.tconEditLine, self.yearEditLine]

    def __initWidget(self):
        """ 初始化小部件的属性 """
        self.resize(932, 652)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground)
        # 默认选中歌名编辑框
        self.songNameEditLine.setFocus()
        self.songNameEditLine.clearButton.show()
        # 给每个单行输入框设置大小
        for editLine in self.editLine_list:
            editLine.setFixedSize(408, 40)

        # 设置按钮的大小
        self.saveButton.setFixedSize(165, 41)
        self.cancelButton.setFixedSize(165, 41)

        # 设置报警标签位置
        self.bottomErrorLabel.setMinimumWidth(100)
        self.emptyTrackErrorIcon.move(7, 224)
        self.bottomErrorIcon.hide()
        self.bottomErrorLabel.hide()
        self.emptyTrackErrorIcon.hide()
        self.installEventFilter(self)

        # 如果曲目为空就禁用保存按钮并更改属性
        self.trackNumEditLine.setProperty('hasText', 'true')
        if not self.trackNumEditLine.text():
            self.saveButton.setEnabled(False)
            self.emptyTrackErrorIcon.show()
            self.trackNumEditLine.setProperty('hasText', 'false')

        # 给输入框设置过滤器
        rex_trackNum = QRegExp(r'(\d)|([1-9]\d{1,2})')
        rex_year = QRegExp(r'\d{4}年{0,1}')
        validator_tracknum = QRegExpValidator(
            rex_trackNum, self.trackNumEditLine)
        validator_disk = QRegExpValidator(rex_trackNum, self.diskEditLine)
        validator_year = QRegExpValidator(rex_year, self.yearEditLine)
        self.trackNumEditLine.setValidator(validator_tracknum)
        self.diskEditLine.setValidator(validator_disk)
        self.yearEditLine.setValidator(validator_year)

        # 将曲目输入框数字改变的信号连接到槽函数
        self.trackNumEditLine.textChanged.connect(self.checkTrackEditLine)

        # 将按钮点击信号连接到槽函数
        self.saveButton.clicked.connect(self.saveInfo)
        if not self.parent():
            self.cancelButton.clicked.connect(self.deleteLater)

        # 分配ID
        self.editInfoLabel.setObjectName('editSongInfo')
        self.songerNameEditLine.setObjectName('songer')
        self.albumSongerEditLine.setObjectName('songer')
        self.songPath.setObjectName('songPath')
        self.bottomErrorLabel.setObjectName('bottomErrorLabel')

    def __initLayout(self):
        """ 初始化小部件的排版 """
        self.editInfoLabel.move(30, 30)
        self.songPathLabel.move(30, 470)
        self.songPath.move(30, 502)
        self.saveButton.move(566, 595)
        self.cancelButton.move(736, 595)
        label_top_y = 95

        for i, (label_left, label_right) in enumerate(zip(self.leftLabel_list, self.rightLabel_list)):
            label_left.setObjectName('infoTypeLabel')
            label_right.setObjectName('infoTypeLabel')
            label_left.move(30, label_top_y + i * 87)
            label_right.move(494, label_top_y + i*87)

        editLine_top_y = 127

        for i, (editLine_left, editLine_right) in enumerate(zip(self.leftEditLine_list, self.rightEditLine_list)):
            editLine_left.move(30, editLine_top_y + i * 87)
            editLine_right.move(494, editLine_top_y + i * 87)

        # 调整高度
        newSongPath, isWordWrap = autoWrap(self.songPath.text(), 100)
        if isWordWrap:
            self.songPath.setText(newSongPath)
            self.resize(self.width(), self.height() + 25)
            self.cancelButton.move(self.cancelButton.x(),
                                   self.cancelButton.y() + 25)
            self.saveButton.move(self.saveButton.x(), self.saveButton.y() + 25)
        # 调整报错标签的位置
        self.bottomErrorIcon.move(30, self.height() - 110)
        self.bottomErrorLabel.move(55, self.height() - 112)

    def __setQss(self):
        """ 设置层叠样式表 """
        with open(r'resource\css\infoEditPanel.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def paintEvent(self, event):
        """ 绘制背景和阴影 """
        # 创建画笔
        self.pen = QPen(QColor(0, 153, 188))
        painter = QPainter(self)
        # 绘制边框
        painter.setPen(self.pen)
        painter.drawRect(0, 0, self.width()-1, self.height()-1)

    def saveInfo(self):
        """ 保存标签卡信息 """
        album_list = adjustAlbumName(self.albumNameEditLine.text())
        self.songInfo['songName'] = self.songNameEditLine.text()
        self.songInfo['songer'] = self.songerNameEditLine.text()
        self.songInfo['album'] = album_list[0]
        self.songInfo['modifiedAlbum'] = album_list[-1]
        # 根据后缀名选择曲目标签的写入方式
        self.songInfo['tracknumber'] = self.trackNumEditLine.text()
        self.songInfo['tcon'] = self.tconEditLine.text()
        if self.yearEditLine.text()[:4] != '未知年份':
            self.songInfo['year'] = self.yearEditLine.text()[:4] + '年'
        else:
            self.songInfo['year'] = '未知年份'
        if not modifySongInfo(self.songInfo):
            self.bottomErrorLabel.setText('遇到未知错误，请稍后再试')
            self.bottomErrorLabel.show()
            self.bottomErrorIcon.show()
        else:
            self.saveInfoSig.emit(self.oldSongInfo, self.songInfo)
            self.parent().deleteLater()

    def checkTrackEditLine(self):
        """ 检查曲目输入框的内容是否为空 """
        if not self.trackNumEditLine.text():
            self.bottomErrorLabel.setText('曲目必须是1000以下的数字')
            self.bottomErrorLabel.show()
            self.emptyTrackErrorIcon.show()
            self.bottomErrorIcon.show()
            self.saveButton.setEnabled(False)
            self.trackNumEditLine.setProperty('hasText', 'false')
        else:
            self.trackNumEditLine.setProperty('hasText', 'true')
            self.bottomErrorLabel.hide()
            self.bottomErrorIcon.hide()
            self.emptyTrackErrorIcon.hide()
            self.saveButton.setEnabled(True)
        self.trackNumEditLine.setStyle(QApplication.style())

    def setShadowEffect(self):
        """ 添加阴影 """
        self.shadowEffect = QGraphicsDropShadowEffect(self)
        self.shadowEffect.setBlurRadius(50)
        self.shadowEffect.setOffset(0, 5)
        self.setGraphicsEffect(self.shadowEffect)
