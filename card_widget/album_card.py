import re
import sys

from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtGui import (QBitmap, QBrush, QColor, QContextMenuEvent, QIcon,
                         QPainter, QPen, QPixmap,QMoveEvent)
from PyQt5.QtWidgets import (
    QAction, QApplication, QLabel,QVBoxLayout, QWidget,QGraphicsBlurEffect)
    
sys.path.append('..')

from Groove.my_widget.my_button import SongerAddToButton, SongerPlayButton
from Groove.my_widget.my_label import ClickableLabel
from Groove.my_widget.my_menu import AlbumCardContextMenu
from Groove.my_functions.auto_wrap import autoWrap
from Groove.my_functions.is_not_leave import isNotLeave

class AlbumCard(QWidget):
    """ 定义包含专辑歌手名的窗口 """

    def __init__(self, albumInfo, parent=None):
        super().__init__(parent)
        self.albumInfo = albumInfo

        # 设置窗体移动标志位
        self.hasMoved = False

        # 储存未被更改过的专辑名
        self.rawAlbumName = albumInfo['album']

        # 实例化专辑名和歌手名
        self.albumName = ClickableLabel(albumInfo['album'], self)
        self.songerName = ClickableLabel(albumInfo['songer'], self)

        # 实例化专辑封面
        self.albumCoverWindow = AlbumCoverWindow(albumInfo['cover_path'], self)

        # 引用两个按钮
        self.playButton = self.albumCoverWindow.playButton
        self.addToButton = self.albumCoverWindow.addToButton

        # 初始化小部件
        self.initWidget()

        # 初始化样式
        self.setQss()

    def initWidget(self):
        """ 初始化小部件 """
        self.setFixedSize(220, 290)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 设置鼠标光标
        self.songerName.setCursor(Qt.PointingHandCursor)
        # 设置部件位置
        self.albumCoverWindow.move(10, 10)
        self.albumName.move(10, 218)
        self.songerName.move(10, 244)
        self.adjustLabel()

        # 分配ID
        self.albumName.setObjectName('albumName')
        self.songerName.setObjectName('songerName')

    def setWidgetsToolTip(self):
        """ 设置歌手名和专辑名的自定义提示条 """
        if self.parent():
            # 引用父级的提示条
            self.customToolTip = self.parent().customToolTip
            # 设置歌手名的提示条
            self.songerName.setCustomToolTip(
                self.customToolTip, self.songerName.text())
            # 设置专辑名的提示条
            self.albumName.setCustomToolTip(
                self.customToolTip, self.rawAlbumName)
            # 设置两个按钮的提示条
            self.playButton.setCustomToolTip(self.customToolTip, '全部播放')
            self.addToButton.setCustomToolTip(self.customToolTip, '添加到')

    def enterEvent(self, e):
        """ 鼠标进入窗口时显示磨砂背景和按钮 """
        # 窗体移动就更新提示条
        #print('鼠标进入专辑卡')
        if self.hasMoved:
            self.setWidgetsToolTip()
            self.hasMoved = False
        #显示磨砂背景
        if self.parent():
            self.blurBackground = self.parent().albumBlurBackground
            self.blurBackground.move(self.x()-20, self.y()+8)
            self.blurBackground.subWindow.setPic(
                self.albumInfo['cover_path'])
            self.blurBackground.show()
        self.addToButton.show()
        self.playButton.show()

    def leaveEvent(self, e):
        """ 鼠标离开时隐藏磨砂背景和按钮 """
        if self.parent():
            #隐藏磨砂背景
            self.parent().albumBlurBackground.hide()
            # 判断是否离开
            notLeave = isNotLeave(self)
            if notLeave:
                return
        self.addToButton.hide()
        self.playButton.hide()

    def contextMenuEvent(self, event: QContextMenuEvent):
        """ 显示右击菜单 """
        # 创建菜单
        menu = AlbumCardContextMenu(self)
        menu.exec_(event.globalPos())

    def adjustLabel(self):
        """ 根据专辑名的长度决定是否换行 """
        newText, isWordWrap = autoWrap(self.albumName.text(), 22)
        if isWordWrap:
            self.albumName.setText(newText)
            self.songerName.move(10, self.songerName.y()+22)
        
    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\albumCard.qss', 'r', encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)

    def moveEvent(self, e: QMoveEvent):
        """ 检测窗体移动 """
        self.hasMoved = True

class AlbumCoverWindow(QWidget):
    """ 定义专辑封面 """

    def __init__(self, album_path, parent=None):
        super().__init__(parent)

        self.resize(200, 200)
        self.album_path = album_path

        # 隐藏边框并将背景设置为透明
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 实例化封面和按钮
        self.albumPic = QLabel(self)
        self.playButton = SongerPlayButton(self)
        self.addToButton = SongerAddToButton(self)

        # 初始化小部件
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        self.albumPic.setPixmap(
            QPixmap(self.album_path).scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        # 专辑图居中
        self.albumPic.move(int(self.width() / 2 - self.albumPic.pixmap().width() / 2),
                           int(self.height() / 2 - self.albumPic.pixmap().height() / 2))
                           
        self.playButton.move(int(0.5 * self.width() - 36 - 0.5 * self.playButton.width()),
                             int(0.5*self.height() - 0.5*self.playButton.height()+1))

        self.addToButton.move(int(0.5*self.width()+36-0.5*self.playButton.width()),
                              int(0.5*self.height() - 0.5*self.playButton.height()+1))

        # 隐藏按钮
        self.playButton.setHidden(True)
        self.addToButton.setHidden(True)

    def paintEvent(self, e):
        """ 绘制背景 """
        painter = QPainter(self)
        # 设置无描边
        pen = Qt.NoPen
        painter.setPen(pen)
        # 设置画刷的内容为白底
        brush = QBrush(Qt.white)
        painter.setBrush(brush)
        # 在指定区域画图
        painter.drawRect(0, 0, self.width(), self.height())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    albumInfo = {'album': '星之回响 (2020 bilibili拜年祭单品)', 'songer': 'HALCA',
                 'cover_path': r"D:\Python_Study\Groove\resource\Album Cover\魔杰座\魔杰座.jpg"}
    demo = AlbumCard(albumInfo)
    demo.show()
    sys.exit(app.exec_())
