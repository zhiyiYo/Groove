# coding:utf-8

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import (QApplication, QGraphicsDropShadowEffect, QLabel,
                             QLineEdit, QScrollArea, QWidget, QPushButton, QVBoxLayout)

from .sub_panel_frame import SubPanelFrame
from my_widget.my_label import ErrorIcon, PerspectiveTransformLabel
from my_widget.my_lineEdit import LineEdit
from my_widget.my_scrollArea import ScrollArea


class AlbumInfoEditPanel(SubPanelFrame):
    """ 专辑信息编辑面板 """

    def __init__(self, albumInfo: dict, parent=None):
        super().__init__(parent)
        self.albumInfo = albumInfo
        # 实例化子属性面板
        self.subAlbumInfoEditPanel = SubAlbumInfoEditPanel(albumInfo, self)
        # 初始化
        self.initWidget()
        self.initLayout()

    def initWidget(self):
        """ 初始化小部件 """
        # deleteLater才能真正释放内存
        self.subAlbumInfoEditPanel.cancelButton.clicked.connect(
            self.deleteLater)
        self.showMask()

    def initLayout(self):
        """ 初始化布局 """
        self.subAlbumInfoEditPanel.move(int(self.width() / 2 - self.subAlbumInfoEditPanel.width() / 2),
                                       int(self.height() / 2 - self.subAlbumInfoEditPanel.height() / 2))


class SubAlbumInfoEditPanel(QWidget):
    """ 专辑信息编辑面板主界面 """

    def __init__(self, albumInfo: dict, parent=None):
        super().__init__(parent)
        self.albumInfo = albumInfo
        self.tcon = self.albumInfo['tcon']        # type:str
        self.songer = self.albumInfo['songer']    # type:str
        self.albumName = self.albumInfo['album']  # type:str
        self.cover_path = self.albumInfo['cover_path']  # type:str
        self.songInfo_list = self.albumInfo['songInfo_list']  # type:list
        # 创建小部件
        self.__createWidgets()
        # 初始化
        self.__initWidget()

    def __createWidgets(self):
        """ 创建小部件 """
        # 创建滚动区域和抬头
        self.scrollArea = ScrollArea(self)
        self.scrollWidget = QWidget()
        self.editAlbumInfoLabel = QLabel('编辑专辑信息', self)
        # 上半部分
        self.albumCover = PerspectiveTransformLabel(
            self.cover_path, (170, 170), self.scrollWidget)
        self.albumNameLineEdit = LineEdit(self.albumName, self.scrollWidget)
        self.albumSongerLineEdit = LineEdit(self.songer, self.scrollWidget)
        self.tconLineEdit = LineEdit(self.tcon, self.scrollWidget)
        self.albumNameLabel = QLabel('专辑标题', self.scrollWidget)
        self.albumSongerLabel = QLabel('专辑歌手', self.scrollWidget)
        self.tconLabel = QLabel('类型', self.scrollWidget)
        # 下半部分
        self.songInfoWidget_list = []
        for songInfo in self.songInfo_list:
            songInfoWidget = SongInfoWidget(songInfo, self.scrollWidget)
            self.songInfoWidget_list.append(songInfoWidget)
        self.saveButton = QPushButton('保存', self)
        self.cancelButton = QPushButton('取消', self)

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedWidth(935)
        self.setAttribute(Qt.WA_StyledBackground)
        self.scrollArea.setWidget(self.scrollWidget)
        self.songInfoWidgetNum = len(self.songInfoWidget_list) # type:int
        # 设置滚动区域的大小
        if self.songInfoWidgetNum <= 4:
            self.scrollArea.resize(901, 216 + self.songInfoWidgetNum * 83)
        else:
            self.scrollArea.resize(901, 595)
        # 初始化布局
        self.__initLayout()
        self.resize(935, self.scrollArea.y() + self.scrollArea.height() + 98)
        # 分配ID
        self.editAlbumInfoLabel.setObjectName('editAlbumInfo')
        # 设置阴影和层叠样式
        self.__setShadowEffect()
        self.__setQss()

    def __initLayout(self):
        """ 初始化布局 """
        self.editAlbumInfoLabel.move(30, 30)
        self.scrollArea.move(30, 62)
        self.albumCover.move(0, 13)
        self.albumNameLabel.move(195, 7)
        self.albumSongerLabel.move(548, 7)
        self.tconLabel.move(195, 77)
        self.albumNameLineEdit.move(195, 36)
        self.albumSongerLineEdit.move(548, 36)
        self.tconLineEdit.move(195, 106)
        self.saveButton.move(563, self.scrollArea.y() +
                             self.scrollArea.height() + 38)
        self.cancelButton.move(735, self.scrollArea.y() +
                               self.scrollArea.height() + 38)
        for i, songInfoWidget in enumerate(self.songInfoWidget_list):
            songInfoWidget.move(0, songInfoWidget.height() * i + 216)
        self.scrollWidget.resize(901, self.songInfoWidgetNum * 83 + 216)
        self.albumNameLineEdit.resize(327, 40)
        self.albumSongerLineEdit.resize(326, 40)
        self.tconLineEdit.resize(327, 40)
        self.saveButton.resize(168, 40)
        self.cancelButton.resize(168,40)

    def __setShadowEffect(self):
        """ 添加阴影 """
        self.shadowEffect = QGraphicsDropShadowEffect(self)
        self.shadowEffect.setBlurRadius(50)
        self.shadowEffect.setOffset(0, 5)
        self.setGraphicsEffect(self.shadowEffect)

    def __setQss(self):
        """ 设置层叠样式表 """
        with open(r'resource\css\infoEditPanel.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def paintEvent(self, event):
        """ 绘制背景和阴影 """
        # 创建画笔
        painter = QPainter(self)
        # 绘制边框
        pen = QPen(QColor(0, 153, 188))
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)


class SongInfoWidget(QWidget):
    """ 歌曲信息窗口 """

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(parent)
        self.songInfo = songInfo
        # 创建小部件
        self.trackNumLabel = QLabel('曲目', self)
        self.songNameLabel = QLabel('歌名', self)
        self.songerLabel = QLabel('歌手', self)
        self.trackNumLineEdit = LineEdit(songInfo['tracknumber'], self, False)
        self.songNameLineEdit = LineEdit(songInfo['songName'], self)
        self.songerLineEdit = LineEdit(songInfo['songer'], self)
        if self.songInfo['suffix'] == '.m4a':
            trackNum = str(eval(self.songInfo['tracknumber'])[0])
            self.trackNumLineEdit.setText(trackNum)
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(873, 83)
        self.trackNumLabel.move(0, 0)
        self.songNameLabel.move(105, 0)
        self.songerLabel.move(502, 0)
        self.trackNumLineEdit.move(0, 26)
        self.songNameLineEdit.move(105, 26)
        self.songerLineEdit.move(502, 26)
        self.trackNumLineEdit.resize(80, 41)
        self.songerLineEdit.resize(371, 41)
        self.songNameLineEdit.resize(371, 41)
        self.trackNumLineEdit.setProperty('hasClearBt','False')
