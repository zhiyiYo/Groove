# coding:utf-8

import json
import re
import sys

from mutagen import File
from PyQt5.QtCore import QEvent, QRect, QRegExp, QSize, Qt
from PyQt5.QtGui import (QColor, QContextMenuEvent, QIcon, QPainter, QPen,
                         QPixmap, QRegExpValidator)
from PyQt5.QtWidgets import (QAction, QApplication, QDialog,
                             QGraphicsDropShadowEffect, QHBoxLayout, QLabel,
                             QLineEdit, QMenu, QPushButton, QToolButton)

from modify_songInfo import modifySongInfo


class SongInfoEditPanel(QDialog):
    """ 定义一个用来编辑歌曲信息的对话框 """

    def __init__(self, songInfo, parent=None):
        super().__init__(parent)

        self.songInfo = songInfo
        # 设置画笔和阴影宽度
        self.SHADOW_WIDTH = 25
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
        self.emptyTrackErrorLabel = QLabel(self)

        # 实例化单行输入框
        self.diskEditLine = LineEdit('1', self)
        self.tconEditLine = LineEdit(songInfo['tcon'], self)
        self.yearEditLine = LineEdit(songInfo['year'], self)
        self.albumNameEditLine = LineEdit(songInfo['album'], self)
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

        # 设置层叠样式
        self.setQss()

    def initWidget(self):
        """ 初始化小部件的属性 """
        self.setFixedSize(932+2*self.SHADOW_WIDTH, 652+2*self.SHADOW_WIDTH)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.songNameEditLine.setFocus()
        self.songNameEditLine.clearButton.show()
        # 给每个单行输入框设置大小、添加清空动作
        for editLine in self.editLine_list:
            editLine.setFixedSize(408, 40)

        # 设置按钮的大小
        self.saveButton.setFixedSize(165, 41)
        self.cancelButton.setFixedSize(165, 41)

        #如果曲目为空就禁用保存按钮
        if not self.trackNumEditLine.text():
            self.saveButton.setEnabled(False)

        # 设置报警标签的大小和位置
        self.emptyTrackErrorLabel.setPixmap(
            QPixmap('resource\\images\\empty_lineEdit_error.png'))
        self.emptyTrackErrorLabel.setFixedSize(21, 21)
        self.emptyTrackErrorLabel.move(
            7 + self.SHADOW_WIDTH, 224 + self.SHADOW_WIDTH)
        self.emptyTrackErrorLabel.setHidden(True)
        self.emptyTrackErrorLabel.setToolTip('曲目必须是1000以下的数字')

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
        self.editInfoLabel.move(30+self.SHADOW_WIDTH, 30+self.SHADOW_WIDTH)
        self.songPathLabel.move(30+self.SHADOW_WIDTH, 470+self.SHADOW_WIDTH)
        self.songPath.move(30+self.SHADOW_WIDTH, 502+self.SHADOW_WIDTH)
        self.saveButton.move(566+self.SHADOW_WIDTH, 595+self.SHADOW_WIDTH)
        self.cancelButton.move(736+self.SHADOW_WIDTH, 595+self.SHADOW_WIDTH)

        label_top_y = 95+self.SHADOW_WIDTH
        i = 0
        for label_left, label_right in zip(self.leftLabel_list, self.rightLabel_list):
            label_left.setObjectName('infoTypeLabel')
            label_right.setObjectName('infoTypeLabel')
            label_left.move(30+self.SHADOW_WIDTH, label_top_y + i * 87)
            label_right.move(494+self.SHADOW_WIDTH, label_top_y + i*87)
            i += 1

        editLine_top_y = 127+self.SHADOW_WIDTH
        i = 0
        for editLine_left, editLine_right in zip(self.leftEditLine_list, self.rightEditLine_list):
            editLine_left.move(30+self.SHADOW_WIDTH, editLine_top_y + i * 87)
            editLine_right.move(494+self.SHADOW_WIDTH, editLine_top_y + i * 87)
            i += 1

    def setQss(self):
        """ 设置层叠样式表 """
        with open('resource\css\songInfoEditPanel.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def drawShadow(self, painter):
        # 绘制左上角、左下角、右上角、右下角、上、下、左、右边框
        self.pixmaps = list()
        self.pixmaps.append(
            'resource\\images\\property_panel_shadow\\left_top.png')
        self.pixmaps.append(
            str("./resource/images/property_panel_shadow/left_bottom.png"))
        self.pixmaps.append(
            'resource\\images\\property_panel_shadow\\right_top.png')

        self.pixmaps.append(
            'resource\\images\\property_panel_shadow\\right_bottom.png')

        self.pixmaps.append(
            'resource\\images\\property_panel_shadow\\top_mid.png')

        self.pixmaps.append(
            'resource\\images\\property_panel_shadow\\bottom_mid.png')

        self.pixmaps.append(
            'resource\\images\\property_panel_shadow\\left_mid.png')

        self.pixmaps.append(
            'resource\\images\\property_panel_shadow\\right_mid.png')

        painter.drawPixmap(0, 0, self.SHADOW_WIDTH,
                           self.SHADOW_WIDTH, QPixmap(self.pixmaps[0]))  # 左上角

        painter.drawPixmap(self.width()-self.SHADOW_WIDTH, 0, self.SHADOW_WIDTH,
                           self.SHADOW_WIDTH, QPixmap(self.pixmaps[2]))  # 右上角

        painter.drawPixmap(0, self.height()-self.SHADOW_WIDTH, self.SHADOW_WIDTH,
                           self.SHADOW_WIDTH, QPixmap(self.pixmaps[1]))  # 左下角

        painter.drawPixmap(self.width()-self.SHADOW_WIDTH, self.height()-self.SHADOW_WIDTH,
                           self.SHADOW_WIDTH, self.SHADOW_WIDTH, QPixmap(self.pixmaps[3]))  # 右下角

        painter.drawPixmap(0, self.SHADOW_WIDTH, self.SHADOW_WIDTH, self.height()-2*self.SHADOW_WIDTH,
                           QPixmap(self.pixmaps[6]).scaled(self.SHADOW_WIDTH, self.height() - 2*self.SHADOW_WIDTH))  # 左

        painter.drawPixmap(self.width()-self.SHADOW_WIDTH, self.SHADOW_WIDTH, self.SHADOW_WIDTH, self.height()-2 *
                           self.SHADOW_WIDTH, QPixmap(self.pixmaps[7]).scaled(self.SHADOW_WIDTH, self.height() - 2*self.SHADOW_WIDTH))  # 右
        painter.drawPixmap(self.SHADOW_WIDTH, 0, self.width()-2*self.SHADOW_WIDTH, self.SHADOW_WIDTH,
                           QPixmap(self.pixmaps[4]).scaled(self.width() - 2*self.SHADOW_WIDTH, self.SHADOW_WIDTH))  # 上

        painter.drawPixmap(self.SHADOW_WIDTH, self.height()-self.SHADOW_WIDTH, self.width()-2*self.SHADOW_WIDTH,
                           self.SHADOW_WIDTH, QPixmap(self.pixmaps[5]).scaled(self.width()-2*self.SHADOW_WIDTH, self.SHADOW_WIDTH))  # 下

    def paintEvent(self, event):
        """ 绘制背景和阴影 """
        painter = QPainter(self)
        self.drawShadow(painter)
        # 绘制边框
        painter.setPen(self.pen)
        painter.drawRect(self.SHADOW_WIDTH, self.SHADOW_WIDTH, self.width(
        ) - 2*self.SHADOW_WIDTH, self.height() - 2*self.SHADOW_WIDTH)
        # 绘制背景
        painter.setBrush(Qt.white)
        painter.drawRect(QRect(self.SHADOW_WIDTH, self.SHADOW_WIDTH, self.width(
        ) - 2*self.SHADOW_WIDTH, self.height() - 2*self.SHADOW_WIDTH))

    def saveInfo(self):
        """ 保存标签卡信息 """
        self.songInfo['songname'] = self.songerNameEditLine.text()
        self.songInfo['songer'] = self.songerNameEditLine.text()
        self.songInfo['album'] = self.albumSongerEditLine.text()
        track_tuple = (int(self.trackNumEditLine.text()),
                       eval(self.songInfo['tracknumber'])[1])
        self.songInfo['tracknumber'] = str(track_tuple)
        self.songInfo['tcon'] = self.tconEditLine.text()
        self.songInfo['year'] = self.yearEditLine.text()[:4]
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


class LineEdit(QLineEdit):
    """ 定义一个被点击就全选文字的单行输入框 """

    def __init__(self, string=None, parent=None):
        super().__init__(string, parent)

        # 创建右击菜单
        self.createContextMenu()
        # 实例化一个用于清空内容的按钮
        self.clearButton = QToolButton(self)

        # 实例化布局
        self.h_layout = QHBoxLayout()
        self.initWidget()
        self.initLayout()

    def initWidget(self):
        """ 初始化小部件 """
        self.clearButton.setFixedSize(39, 39)
        self.clearButton.setFocusPolicy(Qt.NoFocus)
        self.clearButton.setCursor(Qt.ArrowCursor)
        self.clearButton.setIcon(
            QIcon('resource\\images\\clearInfo_cross.png'))
        self.clearButton.setIconSize(QSize(39, 39))
        self.clearButton.clicked.connect(self.clear)
        self.clearButton.setHidden(True)
        self.clearButton.installEventFilter(self)

    def initLayout(self):
        """ 初始化布局 """
        self.h_layout.addWidget(self.clearButton, 0, Qt.AlignRight)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.h_layout)
        self.setTextMargins(0, 0, self.clearButton.width(), 0)

    def createContextMenu(self):
        """ 创建右击菜单 """
        self.menu = QMenu(self)
        self.cutAct = QAction('剪切', self, shortcut='Ctrl+X')
        self.copyAct = QAction('复制', self, shortcut='Ctrl+C')
        self.pasteAct = QAction('粘贴', self, shortcut='Ctrl+V')
        self.menu.addActions([self.cutAct, self.copyAct, self.pasteAct])

    def mousePressEvent(self, e):
        self.selectAll()
        self.clearButton.show()

    def contextMenuEvent(self, e: QContextMenuEvent):
        """ 设置右击菜单 """
        self.menu.exec_(e.globalPos())

    def focusOutEvent(self, e):
        """ 当焦点移到别的输入框时隐藏按钮 """
        # 调用父类的函数，消除焦点
        super().focusOutEvent(e)
        self.clearButton.setHidden(True)

    def eventFilter(self, obj, e):
        """ 当鼠标进入或离开按钮时改变按钮的图片 """
        if obj == self.clearButton:
            if e.type() == QEvent.Enter:
                self.clearButton.setIcon(
                    QIcon('resource\\images\\clearInfo_cross_hover.png'))
            elif e.type() == QEvent.Leave:
                self.clearButton.setIcon(
                    QIcon('resource\\images\\clearInfo_cross.png'))
        return False


if __name__ == "__main__":
    with open('Data\\songInfo.json', 'r', encoding='utf-8') as f:
        songInfo_list = json.load(f)
    songInfo = songInfo_list[0]
    app = QApplication(sys.argv)
    demo = SongInfoEditPanel(songInfo)
    demo.show()
    sys.exit(app.exec_())
