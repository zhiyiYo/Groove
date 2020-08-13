import sys

import numpy as np

from PyQt5.QtCore import QEvent, QPoint, Qt, pyqtSignal
from PyQt5.QtGui import (QBitmap, QBrush, QColor, QContextMenuEvent, QIcon,
                         QMoveEvent, QPainter, QPen, QPixmap, QFont, QFontMetrics)
from PyQt5.QtWidgets import (QAction, QApplication, QGraphicsBlurEffect,
                             QLabel, QVBoxLayout, QWidget)

from my_functions.auto_wrap import autoWrap
from my_functions.get_pressed_pos import getPressedPos
from my_functions.is_not_leave import isNotLeave
from my_functions.perspective_transform import PerspectiveTransform
from my_widget.blur_button import BlurButton
from my_widget.my_label import ClickableLabel, PerspectiveTransformLabel
from .album_card_context_menu import AlbumCardContextMenu


class AlbumCard(QWidget):
    """ 定义包含专辑歌手名的窗口 """
    playSignal = pyqtSignal(list)
    nextPlaySignal = pyqtSignal(list)
    addToPlaylistSignal = pyqtSignal(list)
    switchToAlbumInterfaceSig = pyqtSignal(dict)

    def __init__(self, albumInfo: dict, parent=None, albumViewWidget=None):
        super().__init__(parent)
        self.albumInfo = albumInfo
        self.songInfo_list = self.albumInfo.get('songInfo_list')
        self.picPath = self.albumInfo.get('cover_path')
        self.albumViewWidget = albumViewWidget
        # 设置窗体移动标志位
        self.hasMoved = False
        # 储存未被更改过的专辑名
        self.rawAlbumName = albumInfo['album']
        # 实例化专辑名和歌手名
        self.albumName = ClickableLabel(albumInfo['album'], self)
        self.songerName = ClickableLabel(albumInfo['songer'], self)
        # 实例化封面和按钮
        self.albumPic = PerspectiveTransformLabel(
            self.picPath, (200, 200), self)
        self.playButton = BlurButton(
            self, (39, 76), 'resource\\images\\播放按钮_70_70.png', self.picPath, blurRadius=26)
        self.addToButton = BlurButton(
            self, (111, 76), 'resource\\images\\添加到按钮_70_70.png', self.picPath, blurRadius=26)
        # 初始化
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        self.setFixedSize(220, 290)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 隐藏按钮
        self.playButton.hide()
        self.addToButton.hide()
        # 设置鼠标光标
        self.songerName.setCursor(Qt.PointingHandCursor)
        # 设置部件位置
        self.albumPic.move(10, 10)
        self.albumName.move(10, 218)
        self.songerName.move(10, 244)
        self.adjustLabel()
        # 分配ID
        self.albumName.setObjectName('albumName')
        self.songerName.setObjectName('songerName')
        # 将信号连接到槽函数
        self.playButton.clicked.connect(
            lambda: self.playSignal.emit(self.songInfo_list))

    def setWidgetsToolTip(self):
        """ 设置歌手名和专辑名的自定义提示条 """
        if self.parent() and hasattr(self.parent(), 'customToolTip'):
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
        if self.hasMoved:
            # self.setWidgetsToolTip()
            self.hasMoved = False
        # 显示磨砂背景
        if self.albumViewWidget:
            self.blurBackground = self.albumViewWidget.albumBlurBackground
            # 需要补上groupBox()的y()
            offsetY = 0 if self.parent() == self.albumViewWidget else self.parent().y()
            self.blurBackground.move(self.x() - 20, self.y() + 8 + offsetY)
            self.blurBackground.subWindow.setPic(self.picPath)
            self.blurBackground.show()
        self.addToButton.show()
        self.playButton.show()

    def leaveEvent(self, e):
        """ 鼠标离开时隐藏磨砂背景和按钮 """
        if self.parent() and hasattr(self, 'blurBackground'):
            # 隐藏磨砂背景
            self.blurBackground.hide()
        self.addToButton.hide()
        self.playButton.hide()

    def contextMenuEvent(self, event: QContextMenuEvent):
        """ 显示右击菜单 """
        # 创建菜单
        menu = AlbumCardContextMenu(parent=self)
        menu.playAct.triggered.connect(
            lambda: self.playSignal.emit(self.songInfo_list))
        menu.nextToPlayAct.triggered.connect(
            lambda: self.nextPlaySignal.emit(self.songInfo_list))
        menu.addToMenu.playingAct.triggered.connect(
            lambda: self.addToPlaylistSignal.emit(self.songInfo_list))
        menu.exec(event.globalPos())

    def adjustLabel(self):
        """ 根据专辑名的长度决定是否换行和添加省略号 """
        newText, isWordWrap = autoWrap(self.albumName.text(), 22)
        if isWordWrap:
            # 添加省略号
            index = newText.index('\n')
            fontMetrics = QFontMetrics(QFont('Microsoft YaHei', 10, 75))
            secondLineText = fontMetrics.elidedText(
                newText[index + 1:], Qt.ElideRight, 200)
            newText = newText[: index + 1] + secondLineText
            self.albumName.setText(newText)
            self.songerName.move(10, self.songerName.y() + 22)
        # 给歌手名添加省略号
        fontMetrics = QFontMetrics(QFont('Microsoft YaHei', 10, 25))
        newSongerName = fontMetrics.elidedText(
            self.songerName.text(), Qt.ElideRight, 200)
        self.songerName.setText(newSongerName)

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\albumCard.qss', 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def moveEvent(self, e: QMoveEvent):
        """ 检测窗体移动 """
        self.hasMoved = True

    def mouseReleaseEvent(self, e):
        """ 鼠标松开发送切换到专辑界面信号 """
        super().mouseReleaseEvent(e)
        if e.button() == Qt.LeftButton:
            self.switchToAlbumInterfaceSig.emit(self.albumInfo)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    albumInfo = {'album': '星之回响 (2020 bilibili拜年祭单品)', 'songer': 'HALCA',
                 'cover_path': r"D:\Python_Study\Groove\resource\Album_Cover\魔杰座\魔杰座.jpg"}
    demo = AlbumCard(albumInfo)
    demo.show()
    sys.exit(app.exec_())
