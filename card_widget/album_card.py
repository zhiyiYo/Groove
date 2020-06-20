import re
import sys

from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtGui import (QBitmap, QBrush, QColor, QContextMenuEvent, QIcon,
                         QPainter, QPen, QPixmap)
from PyQt5.QtWidgets import (
    QAction, QApplication, QLabel,QVBoxLayout, QWidget,QGraphicsBlurEffect)
    
sys.path.append('..')

from Groove.my_widget.my_button import SongerAddToButton, SongerPlayButton
from Groove.my_widget.my_label import ClickableLabel
from Groove.my_widget.my_menu import Menu
from Groove.my_functions.auto_wrap import autoWrap


class AlbumCard(QWidget):
    """ 定义包含专辑歌手名的窗口 """

    def __init__(self, albumInfo, parent=None):
        super().__init__(parent)
        self.albumInfo = albumInfo

        # 实例化专辑名和歌手名
        self.albumName = ClickableLabel(albumInfo['album'], self)
        self.songerName = ClickableLabel(albumInfo['songer'], self)

        # 实例化专辑封面
        self.albumCover = AlbumCover(albumInfo['cover_path'], self)

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

        # 设置悬浮提示
        self.songerName.setToolTip(self.songerName.text())
        self.albumName.setToolTip(self.albumName.text())

        self.albumCover.move(10, 10)
        self.albumName.move(10, 218)
        self.songerName.move(10, 244)
        self.adjustLabel()

        # 分配ID
        self.albumName.setObjectName('albumName')
        self.songerName.setObjectName('songerName')

        # 设置监听
        self.installEventFilter(self)

    def eventFilter(self, obj, e):
        """ 鼠标进入窗口时显示阴影和按钮，否则不显示 """
        if obj == self:
            if e.type() == QEvent.Enter:
                #显示磨砂背景
                if self.parent():
                    self.blurBackground = self.parent().albumBlurBackground
                    self.blurBackground.move(self.x()-20, self.y()+8)
                    self.blurBackground.subWindow.setPic(self.albumInfo['cover_path'])
                    self.blurBackground.show()
                self.albumCover.addToButton.show()
                self.albumCover.playButton.show()
            elif e.type() == QEvent.Leave:
                #隐藏磨砂背景
                if self.parent():
                    self.parent().albumBlurBackground.hide()
                self.albumCover.addToButton.hide()
                self.albumCover.playButton.hide()

        return False

    def contextMenuEvent(self, event: QContextMenuEvent):
        """ 显示右击菜单 """
        menu = Menu(parent=self)
        addToMenu = Menu('添加到', self)
        addToMenu.setProperty('subMenu', 'true')
        playAct = QAction('播放', self)
        deleteAct = QAction('删除', self)
        chooseAct = QAction('选择', self)
        playingAct = QAction(QIcon('resource\\images\\正在播放.svg'), '正在播放', self)
        editInfoAct = QAction('编辑信息', self)
        showSongerAct = QAction('显示歌手', self)
        newPlayList = QAction(
            QIcon('resource\\images\\黑色加号.svg'), '新的播放列表', self)
        nextToPlayAct = QAction('下一首播放', self)
        pinToStartMenuAct = QAction('固定到"开始"菜单', self)
        # 将动作添加到菜单中
        addToMenu.addAction(playingAct)
        addToMenu.addSeparator()
        addToMenu.addAction(newPlayList)
        menu.addActions([playAct, nextToPlayAct])
        menu.addMenu(addToMenu)
        menu.addActions([showSongerAct, pinToStartMenuAct,
                         editInfoAct, deleteAct])
        menu.addSeparator()
        menu.addAction(chooseAct)
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


class AlbumCover(QWidget):
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
        # 设置画刷的内容为封面图
        brush = QBrush(Qt.white)
        painter.setBrush(brush)
        # 在指定区域画圆
        painter.drawRect(0, 0, self.width(), self.height())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    albumInfo = {'album': '星之回响 (2020 bilibili拜年祭单品)', 'songer': 'HALCA',
                 'cover_path': r"D:\Python_Study\Groove\resource\Album Cover\魔杰座\魔杰座.jpg"}
    demo = AlbumCard(albumInfo)
    demo.show()
    sys.exit(app.exec_())
