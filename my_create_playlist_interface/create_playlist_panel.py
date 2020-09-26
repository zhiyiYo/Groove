# coding:utf-8

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QEnterEvent, QFont, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (QGraphicsDropShadowEffect, QLabel, QLineEdit,
                             QWidget)

from my_create_playlist_interface.line_edit import LineEdit
from my_dialog_box.sub_panel_frame import SubPanelFrame
from my_widget.my_label import ClickableLabel
from my_widget.perspective_button import PerspectivePushButton


class CreatePlaylistPanel(SubPanelFrame):
    """ 选择歌曲文件夹面板 """

    def __init__(self, text='', parent=None):
        super().__init__(parent)
        # 实例化子属性面板
        self.__subCreatePlaylistPanel = SubCreatePlaylistPanel(text, self)
        self.createPlaylistButton = self.__subCreatePlaylistPanel.createPlaylistButton
        self.createPlaylistSig = self.__subCreatePlaylistPanel.createPlaylistSig
        # 初始化
        self.showMask()
        self.__setSubWindowPos()

    def __setSubWindowPos(self):
        """ 设置子窗口的位置 """
        self.__subCreatePlaylistPanel.move(
            int(self.width() / 2 - self.__subCreatePlaylistPanel.width() / 2),
            int(self.height() / 2 - self.__subCreatePlaylistPanel.height() / 2))


class SubCreatePlaylistPanel(QWidget):
    """ 创建播放列表面板 """
    createPlaylistSig = pyqtSignal(str)

    def __init__(self, text='', parent=None):
        super().__init__(parent)
        self.__lineEditText = text
        # 创建小部件
        self.__createWidgets()
        # 初始化
        self.__initWidget()
        self.__initLayout()
        self.__setQss()

    def __createWidgets(self):
        """ 创建小部件 """
        self.iconPic = QLabel(self)
        self.lineEdit = LineEdit(self.__lineEditText, self)
        self.cancelLabel = ClickableLabel('取消', self)
        self.yourCreationLabel = QLabel('您创建的', self)
        self.createPlaylistButton = PerspectivePushButton('创建播放列表', self)

    def __initWidget(self):
        """ 初始化小部件 """
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedSize(586, 644)
        self.setShadowEffect()
        self.createPlaylistButton.resize(313, 48)
        self.iconPic.setPixmap(
            QPixmap(r'resource\images\createPlaylistPanel\playList_icon.png'))
        # 分配ID
        self.setObjectName('subCreatePlaylistPanel')
        self.cancelLabel.setObjectName('cancelLabel')
        self.yourCreationLabel.setObjectName('yourCreationLabel')
        self.createPlaylistButton.setObjectName('createPlaylistButton')
        # 信号连接到槽函数
        self.cancelLabel.clicked.connect(self.parent().deleteLater)
        self.createPlaylistButton.clicked.connect(self.__createPlaylistButtonSlot)

    def __initLayout(self):
        """ 初始化布局 """
        self.iconPic.move(188, 74)
        self.lineEdit.move(52, 309)
        self.yourCreationLabel.move(255, 398)
        self.createPlaylistButton.move(137, 496)
        self.cancelLabel.move(276, 570)

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

    def __setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\createPlaylistPanel.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __createPlaylistButtonSlot(self):
        """ 发出创建播放列表的信号 """
        text = self.lineEdit.text() if self.lineEdit.text() else '新的播放列表'
        self.createPlaylistSig.emit(text)
        self.parent().deleteLater()