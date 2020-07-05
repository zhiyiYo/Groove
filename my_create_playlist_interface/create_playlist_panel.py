# coding:utf-8

import sys

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QEnterEvent, QFont, QPixmap,QPen,QPainter,QColor
from PyQt5.QtWidgets import (QApplication, QGraphicsDropShadowEffect, QLabel,
                             QLineEdit, QPushButton, QWidget)

sys.path.append('..')
from Groove.my_dialog_box.sub_panel_frame import SubPanelFrame
from Groove.my_widget.my_label import ClickableLabel
from Groove.my_create_playlist_interface.line_edit import LineEdit


class CreatePlaylistPanel(SubPanelFrame):
    """ 选择歌曲文件夹面板 """

    def __init__(self, parent):
        super().__init__(parent)
        # 实例化子属性面板
        self.subCreatePlaylistPanel = SubCreatePlaylistPanel(self)
        # 初始化
        self.showMask()
        self.setSubWindowPos()

    def setSubWindowPos(self):
        """ 设置子窗口的位置 """
        self.subCreatePlaylistPanel.move(int(self.width() / 2 - self.subCreatePlaylistPanel.width() / 2),
                                           int(self.height() / 2 - self.subCreatePlaylistPanel.height() / 2))


class SubCreatePlaylistPanel(QWidget):
    """ 创建播放列表面板 """

    def __init__(self, parent):
        super().__init__(parent)
        # 创建小部件
        self.createWidgets()
        # 初始化
        self.initWidget()
        self.initLayout()
        self.setQss()

    def createWidgets(self):
        """ 创建小部件 """
        self.iconPic = QLabel(self)
        self.lineEdit = LineEdit(parent=self)
        self.cancelLabel = ClickableLabel('取消', self)
        self.yourCreationLabel = QLabel('您创建的', self)
        self.createPlaylistButton = QPushButton('创建播放列表', self)
        
    def initWidget(self):
        """ 初始化小部件 """
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedSize(586, 644)
        self.setShadowEffect()
        self.createPlaylistButton.resize(313, 48)
        self.iconPic.setPixmap(QPixmap(r'resource\images\createPlaylistPanel\playList_icon.png'))
        # 分配ID
        self.setObjectName('subCreatePlaylistPanel')
        self.cancelLabel.setObjectName('cancelLabel')
        self.yourCreationLabel.setObjectName('yourCreationLabel')
        self.createPlaylistButton.setObjectName('createPlaylistButton')
        # 信号连接到槽函数
        self.cancelLabel.clicked.connect(self.parent().deleteLater)

    def initLayout(self):
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

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\createPlaylistPanel.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1280, 800)
        self.label = QLabel(self)
        self.label.setPixmap(QPixmap(r"D:\hzz\图片\硝子\硝子 (3).jpg").scaled(
            1280, 800, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.bt = QPushButton('点击打开歌曲文件夹选择面板', self)
        self.bt.move(480, 355)
        self.bt.clicked.connect(self.showPanel)

    def showPanel(self):
        # 读取信息
        panel = CreatePlaylistPanel(self)
        panel.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
