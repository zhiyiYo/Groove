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
from PyQt5.QtWidgets import (QApplication, QDialog, QGraphicsDropShadowEffect, QLabel,QWidget,
                             QLineEdit, QPushButton)
sys.path.append('..')

from Groove.my_dialog_box.modify_songInfo import modifySongInfo
from Groove.my_widget.my_lineEdit import LineEdit
from Groove.my_widget.my_label import ErrorLabel
from Groove.my_widget.my_toolTip import ToolTip
from Groove.my_functions.auto_wrap import autoWrap


class SongInfoEditPanel(QDialog):
    """ 歌曲信息编辑面板 """

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(parent)

        # 实例化子属性面板
        self.subSongInfoEditPanel = SubSongInfoEditPanel(songInfo, self)
        # 初始化
        self.initWidget()
        self.initLayout()

    def initWidget(self):
        """ 初始化小部件 """
        self.resize(self.subSongInfoEditPanel.size())
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        # deleteLater才能真正释放内存
        self.subSongInfoEditPanel.cancelButton.clicked.connect(self.deleteLater)
        if self.parent():
            parent_rect = self.parent().geometry()
            self.setGeometry(parent_rect.x(), parent_rect.y(),
                             parent_rect.width(), parent_rect.height())
            self.createWindowMask()

    def initLayout(self):
        """ 初始化布局 """
        self.subSongInfoEditPanel.move(int(self.width() / 2 - self.subSongInfoEditPanel.width() / 2),
                                   int(self.height() / 2 - self.subSongInfoEditPanel.height() / 2))

    def createWindowMask(self):
        """ 创建白色透明遮罩 """
        self.windowMask = QWidget(self)
        self.windowMask.setStyleSheet('background:rgba(255,255,255,177)')
        self.windowMask.resize(self.size())
        self.windowMask.lower()


class SubSongInfoEditPanel(QWidget):
    """ 歌曲信息编辑面板的子窗口 """

    def __init__(self, songInfo:dict, parent=None):
        super().__init__(parent)

        self.songInfo = songInfo

        # 实例化标签卡
        self.id_card = File(songInfo['song_path'])
        # 实例化小部件
        self.createWidgets()
        # 初始化小部件
        self.initWidget()
        self.initLayout()
        self.setShadowEffect()
        #self.setDropShadowEffect()
        # 设置层叠样式
        self.setQss()

    def createWidgets(self):
        """ 实例化小部件 """
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
        self.songPath = QLabel(self.songInfo['song_path'], self)
        self.emptyTrackErrorLabel = ErrorLabel(self)

        # 实例化提示条
        self.customToolTip = ToolTip(parent=self)

        # 实例化单行输入框
        self.diskEditLine = LineEdit('1', self)
        self.tconEditLine = LineEdit(self.songInfo['tcon'], self)
        self.yearEditLine = LineEdit(self.songInfo['year'], self)
        self.albumNameEditLine = LineEdit(self.songInfo['album'][0], self)
        self.songNameEditLine = LineEdit(self.songInfo['songName'], self)
        self.songerNameEditLine = LineEdit(self.songInfo['songer'], self)
        self.albumSongerEditLine = LineEdit(self.songInfo['songer'], self)
        if self.songInfo['suffix'] in ['.flac', '.mp3']:
            self.trackNumEditLine = LineEdit(
                self.songInfo['tracknumber'], self)
        elif self.songInfo['suffix'] == '.m4a':
            trackNUm = str(eval(self.songInfo['tracknumber'])[0])
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



    def initWidget(self):
        """ 初始化小部件的属性 """
        self.resize(932, 652)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground)
        # 默认选中歌名编辑框
        self.songNameEditLine.setFocus()
        self.songNameEditLine.clearButton.show()
        """ if self.songerNameLabel.text():
            self.songerNameEditLine.setReadOnly(True) """
        # 给每个单行输入框设置大小
        for editLine in self.editLine_list:
            editLine.setFixedSize(408, 40)

        # 设置按钮的大小
        self.saveButton.setFixedSize(165, 41)
        self.cancelButton.setFixedSize(165, 41)

        # 设置报警标签的大小和位置
        self.emptyTrackErrorLabel.move(7, 224)
        self.emptyTrackErrorLabel.hide()
        self.installEventFilter(self)

        # 如果曲目为空就禁用保存按钮并更改属性
        self.trackNumEditLine.setProperty('hasText', 'true')
        if not self.trackNumEditLine.text():
            self.saveButton.setEnabled(False)
            self.emptyTrackErrorLabel.show()
            self.trackNumEditLine.setProperty('hasText', 'false')

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
        if not self.parent():
            self.cancelButton.clicked.connect(self.deleteLater)

        # 分配ID
        self.editInfoLabel.setObjectName('editSongInfo')
        self.songerNameEditLine.setObjectName('songer')
        self.albumSongerEditLine.setObjectName('songer')
        self.songPath.setObjectName('songPath')

        # 设置提示条
        self.setWidgetsToolTip()

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
        # 调整高度
        newSongPath, isWordWrap = autoWrap(self.songPath.text(), 100)
        if isWordWrap:
            self.songPath.setText(newSongPath)
            self.resize(self.width(), self.height() + 25)
            self.cancelButton.move(self.cancelButton.x(), self.cancelButton.y() + 25)
            self.saveButton.move(self.saveButton.x(), self.saveButton.y() + 25)

    def setWidgetsToolTip(self):
        """ 设置小部件的提示条 """
        self.emptyTrackErrorLabel.setCustomToolTip(
            self.customToolTip, '曲目必须是1000以下的数字')
        self.trackNumEditLine.setCustomToolTip(
            self.customToolTip, '曲目必须是1000以下的数字')

    def setQss(self):
        """ 设置层叠样式表 """
        with open(r'resource\css\songInfoEditPanel.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def paintEvent(self, event):
        """ 绘制背景和阴影 """
        # 创建画笔
        self.pen = QPen(QColor(0, 153, 188))
        painter = QPainter(self)
        # 绘制边框
        painter.setPen(self.pen)
        painter.drawRect(0, 0, self.width()-1, self.height()-1)

    def setDropShadowEffect(self):
        """ 添加阴影 """
        self.class_amended = c_bool(False)
        self.hWnd = HWND(int(self.winId()))
        dll = cdll.LoadLibrary('dll\\windowEffect.dll')
        dll.addShadowEffect(c_bool(1), self.hWnd)
        #dll.setShadow(self.class_amended,self.hWnd)

    def saveInfo(self):
        """ 保存标签卡信息 """
        self.songInfo['songName'] = self.songNameEditLine.text()
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
        self.deleteLater()

    def checkTrackEditLine(self):
        """ 检查曲目输入框的内容是否为空 """
        if not self.trackNumEditLine.text():
            self.emptyTrackErrorLabel.show()
            self.saveButton.setEnabled(False)
            self.trackNumEditLine.setProperty('hasText','false')
        else:
            self.trackNumEditLine.setProperty('hasText','true')
            self.emptyTrackErrorLabel.setHidden(True)
            self.saveButton.setEnabled(True)
        self.trackNumEditLine.setStyle(QApplication.style())

    def setShadowEffect(self):
        """ 添加阴影 """
        self.shadowEffect = QGraphicsDropShadowEffect(self)
        self.shadowEffect.setBlurRadius(50)
        self.shadowEffect.setOffset(0, 5)
        self.setGraphicsEffect(self.shadowEffect)


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1200, 800)
        self.setStyleSheet('background:white')
        self.label = QLabel('测试', self)
        self.label.move(0, 100)
        self.bt = QPushButton('点击打开歌曲信息编辑面板', self)
        self.bt.move(550, 375)
        self.bt.clicked.connect(self.showPanel)

    def showPanel(self):
        # 读取信息
        with open('Data\\songInfo.json', 'r', encoding='utf-8') as f:
            songInfo_list = json.load(f)
        songInfo = songInfo_list[77]
        panel = SongInfoEditPanel(songInfo, self)
        panel.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
