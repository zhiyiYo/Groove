# coding:utf-8

import json
import re
import sys
from ctypes import cdll, c_bool
from ctypes.wintypes import HWND

from mutagen import File
from PyQt5.QtCore import QEvent, QRegExp, Qt
from PyQt5.QtGui import (QColor, QContextMenuEvent,QPainter, QPen,
                         QPixmap, QRegExpValidator, QFont)
from PyQt5.QtWidgets import (QApplication, QDialog,QLabel,
                             QLineEdit,QPushButton)
sys.path.append('..')

from .modify_songInfo import modifySongInfo
from Groove.my_widget.my_lineEdit import LineEdit
from Groove.my_widget.my_label import ErrorLabel

class SongInfoEditPanel(QDialog):
    """ 定义一个用来编辑歌曲信息的对话框 """

    def __init__(self, songInfo, parent=None):
        super().__init__(parent)

        self.songInfo = songInfo
        # 设置画笔和阴影宽度
        self.pen = QPen(QColor(0, 153, 188))

        # 实例化标签卡
        self.id_card = File(songInfo['song_path'])

        # 实例化按钮
        self.saveButton = QPushButton('保存', self)
        self.cancelButton = QPushButton('取消', self)

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
        self.songPath = QLabel(songInfo['song_path'], self)
        self.emptyTrackErrorLabel = ErrorLabel(self)

        # 实例化单行输入框
        self.diskEditLine = LineEdit('1', self)
        self.tconEditLine = LineEdit(songInfo['tcon'], self)
        self.yearEditLine = LineEdit(songInfo['year'], self)
        self.albumNameEditLine = LineEdit(songInfo['album'][0], self)
        self.songNameEditLine = LineEdit(songInfo['songname'], self)
        self.songerNameEditLine = LineEdit(songInfo['songer'], self)
        self.albumSongerEditLine = LineEdit(songInfo['songer'], self)
        if songInfo['suffix'] in ['.flac', '.mp3']:
            self.trackNumEditLine = LineEdit(songInfo['tracknumber'], self)
        elif songInfo['suffix'] == '.m4a':
            trackNUm = str(eval(songInfo['tracknumber'])[0])
            self.trackNumEditLine = LineEdit(trackNUm, self)

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

        # 初始化小部件
        self.initWidget()
        self.initLayout()
        self.setDropShadowEffect()

        # 设置层叠样式
        self.setQss()

    def initWidget(self):
        """ 初始化小部件的属性 """
        self.setFixedSize(932, 652)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # 默认选中歌名编辑框
        self.songNameEditLine.setFocus()
        self.songNameEditLine.clearButton.show()
        """ if self.songerNameLabel.text():
            self.songerNameEditLine.setReadOnly(True) """
        # 给每个单行输入框设置大小、添加清空动作
        for editLine in self.editLine_list:
            editLine.setFixedSize(408, 40)

        # 设置按钮的大小
        self.saveButton.setFixedSize(165, 41)
        self.cancelButton.setFixedSize(165, 41)

        # 如果曲目为空就禁用保存按钮
        if not self.trackNumEditLine.text():
            self.saveButton.setEnabled(False)

        # 设置报警标签的大小和位置
        self.emptyTrackErrorLabel.setPixmap(
            QPixmap('resource\\images\\empty_lineEdit_error.png'))
        self.emptyTrackErrorLabel.setFixedSize(21, 21)
        self.emptyTrackErrorLabel.move(7, 224)
        self.emptyTrackErrorLabel.setHidden(True)
        # self.emptyTrackErrorLabel.setToolTip('曲目必须是1000以下的数字')
        self.installEventFilter(self)

        # 给输入框设置过滤器
        rex_trackNum = QRegExp(r'(\d)|([1-9]\d*)')
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
        self.cancelButton.clicked.connect(self.close)

        # 分配ID
        self.editInfoLabel.setObjectName('editSongInfo')
        self.songerNameEditLine.setObjectName('songer')
        self.albumSongerEditLine.setObjectName('songer')
        self.songPath.setObjectName('songPath')

    def initLayout(self):
        """ 初始化小部件的排版 """
        self.editInfoLabel.move(30, 30)
        self.songPathLabel.move(30, 470)
        self.songPath.move(30, 502)
        self.saveButton.move(566, 595)
        self.cancelButton.move(736, 595)

        label_top_y = 95
        i = 0
        for label_left, label_right in zip(self.leftLabel_list, self.rightLabel_list):
            label_left.setObjectName('infoTypeLabel')
            label_right.setObjectName('infoTypeLabel')
            label_left.move(30, label_top_y + i * 87)
            label_right.move(494, label_top_y + i*87)
            i += 1

        editLine_top_y = 127
        i = 0
        for editLine_left, editLine_right in zip(self.leftEditLine_list, self.rightEditLine_list):
            editLine_left.move(30, editLine_top_y + i * 87)
            editLine_right.move(494, editLine_top_y + i * 87)
            i += 1

    def setQss(self):
        """ 设置层叠样式表 """
        with open('resource\css\songInfoEditPanel.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def paintEvent(self, event):
        """ 绘制背景和阴影 """
        painter = QPainter(self)
        # 绘制边框
        painter.setPen(self.pen)
        painter.drawRect(0, 0, self.width()-1, self.height()-1)

    def setDropShadowEffect(self):
        """ 添加阴影 """
        self.class_amended = c_bool(False)
        self.hWnd = HWND(int(self.winId()))
        dll = cdll.LoadLibrary('acrylic_dll\\acrylic.dll')
        dll.addWindowShadow(c_bool(1), self.hWnd)
        #dll.setShadow(self.class_amended,self.hWnd)

    def saveInfo(self):
        """ 保存标签卡信息 """
        self.songInfo['songname'] = self.songNameEditLine.text()
        self.songInfo['songer'] = self.songerNameEditLine.text()
        self.songInfo['album'][0] = self.albumNameEditLine.text()
        # 根据后缀名选择曲目标签的写入方式
        if self.songInfo['suffix'] == '.m4a':
            track_tuple = (int(self.trackNumEditLine.text()),
                           eval(self.songInfo['tracknumber'])[1])
            self.songInfo['tracknumber'] = str(track_tuple)
        else:
            self.songInfo['tracknumber'] = self.trackNumEditLine.text()

        self.songInfo['tcon'] = self.tconEditLine.text()
        self.songInfo['year'] = self.yearEditLine.text()[:4]+'年'
        modifySongInfo(self.id_card, self.songInfo)
        self.id_card.save()
        self.close()

    def checkTrackEditLine(self):
        """ 检查曲目输入框的内容是否为空 """
        if not self.trackNumEditLine.text():
            self.emptyTrackErrorLabel.show()
            self.saveButton.setEnabled(False)
            self.trackNumEditLine.setStyleSheet(
                "QLineEdit{border:1px solid rgb(197,5,0)}")
        else:
            qss = """ QLineEdit {
                            padding: 9px 14px 8px 14px;
                            font: 16px 'Microsoft YaHei';
                            selection-background-color: rgb(0, 153, 188);
                        }
                        QLineEdit:focus {
                            border: 1px solid rgb(0, 153, 188);
                        } """
            self.trackNumEditLine.setStyleSheet(qss)
            self.emptyTrackErrorLabel.setHidden(True)
            self.saveButton.setEnabled(True)



if __name__ == "__main__":
    with open('Data\\songInfo.json', 'r', encoding='utf-8') as f:
        songInfo_list = json.load(f)
    songInfo = songInfo_list[0]
    app = QApplication(sys.argv)
    demo = SongInfoEditPanel(songInfo)
    demo.show()
    sys.exit(app.exec_())
