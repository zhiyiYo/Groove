# coding:utf-8

import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QLabel, QWidget

from .line_edit import LineEdit
from my_widget.my_label import ClickableLabel
from my_widget.perspective_button import PerspectivePushButton


class BasicPlaylistPanel(QWidget):
    """ 播放列表面板基类 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建小部件
        self.__createWidgets()
        # 初始化
        self.__initWidget()

    def __createWidgets(self):
        """ 创建小部件 """
        self.iconPic = QLabel(self)
        self.lineEdit = LineEdit(parent=self)
        self.cancelLabel = ClickableLabel('取消', self)
        self.button = PerspectivePushButton(parent=self)
        self.playlistExistedLabel = QLabel('此名称已经存在。请尝试其他名称。', self)

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(586, 644)
        self.button.resize(313, 48)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setShadowEffect()
        self.playlistExistedLabel.hide()
        self.iconPic.setPixmap(
            QPixmap(r'resource\images\createPlaylistPanel\playList_icon.png'))
        # 分配ID
        self.setObjectName('basicPlaylistPanel')
        self.cancelLabel.setObjectName('cancelLabel')
        # 信号连接到槽函数
        self.cancelLabel.clicked.connect(self.parent().deleteLater)

    def setShadowEffect(self):
        """ 添加阴影 """
        self.shadowEffect = QGraphicsDropShadowEffect(self)
        self.shadowEffect.setBlurRadius(60)
        self.shadowEffect.setOffset(0, 5)
        self.setGraphicsEffect(self.shadowEffect)

    def paintEvent(self, e):
        """ 绘制边框 """
        pen = QPen(QColor(172, 172, 172))
        pen.setWidth(2)
        painter = QPainter(self)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

    def _setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\playlistPanel.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def _isPlaylistExist(self, playlistName) -> bool:
        """ 检测播放列表是否已经存在，如果已存在就显示提示标签 """
        # 扫描播放列表文件夹下的播放列表名字
        if not os.path.exists('Playlists'):
            os.mkdir('Playlists')
        playlistName_list = [os.path.splitext(
            i)[0] for i in os.listdir('Playlists')]
        isExist = playlistName in playlistName_list
        # 如果播放列表名字已存在显示提示标签
        self.playlistExistedLabel.setVisible(isExist)
        self.button.setEnabled(not isExist)
        return isExist
