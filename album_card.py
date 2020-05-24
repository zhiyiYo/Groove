import re
import sys

from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtGui import (QBitmap, QBrush, QColor, QContextMenuEvent,
                         QPainter, QPen, QPixmap,QIcon)
from PyQt5.QtWidgets import QApplication, QLabel, QMenu, QVBoxLayout, QWidget, QAction

from my_button import SongerAddToButton, SongerPlayButton


class AlbumCard(QWidget):
    """ 定义包含专辑歌手名的窗口 """

    def __init__(self, albumInfo, parent=None):
        super().__init__(parent)

        # 实例化背景
        self.backgroundLabel = QLabel(self)

        # 实例化专辑名和歌手名
        self.albumName = QLabel(albumInfo['album'], self)
        self.songerName = QLabel(albumInfo['songer'], self)

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

        # 设置鼠标光标
        self.songerName.setCursor(Qt.PointingHandCursor)

        # 设置悬浮提示
        self.songerName.setToolTip(self.songerName.text())
        self.albumName.setToolTip(self.albumName.text())

        self.albumCover.move(10, 10)
        self.albumName.move(10, 218)
        self.songerName.move(10, 244)
        self.adjustLabel()

        # 设置背景图片
        self.backgroundLabel.setPixmap(
            QPixmap('resource\\images\\专辑封面无阴影.png'))

        # 分配ID
        self.albumName.setObjectName('albumName')
        self.songerName.setObjectName('songerName')

        # 设置监听
        self.installEventFilter(self)

    def adjustLabel(self):
        """ 根据专辑名的长度决定是否换行 """
        # 设置换行标志位
        wordWrap = True
        text = self.albumName.text()
        text_list = list(text)
        alpha_num = 0
        not_alpha_num = 0
        blank_index = 0
        for index, i in enumerate(text):
            Match = re.match(r'[A-Z0-9a-z\(\)\*\.\s]', i)
            if Match:
                alpha_num += 1
                if Match.group() == ' ':
                    # 记录上一个空格的下标
                    blank_index = index
                if alpha_num + 2 * not_alpha_num == 22:
                    # 发生异常就说明正好22个长度
                    try:
                        if text[index + 1] == ' ':
                            # 插入换行符
                            text_list.insert(index + 1, '\n')
                            # 弹出空格
                            text_list.pop(index + 2)
                        else:
                            text_list.insert(blank_index, '\n')
                            text_list.pop(blank_index + 1)
                        break
                    except IndexError:
                        pass

            else:
                not_alpha_num += 1
                if alpha_num + 2 * not_alpha_num == 22:
                    text_list.insert(index + 1, '\n')
                    try:
                        if text_list[index + 2] == ' ':
                            text_list.pop(index + 2)
                        break
                    except:
                        pass
                elif alpha_num + 2 * not_alpha_num > 22:
                    if text_list[index - 1] == ' ':
                        text_list.insert(index - 1, '\n')
                        text_list.pop(index)
                    else:
                        text_list.insert(index, '\n')
                    break
        else:
            wordWrap = False
        if wordWrap:
            self.albumName.setText(''.join(text_list))
            self.songerName.move(10, self.songerName.y()+22)

    def eventFilter(self, obj, e):
        """ 鼠标进入窗口时显示阴影和按钮，否则不显示 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.backgroundLabel.setPixmap(
                    QPixmap('resource\\images\\专辑封面阴影.png'))
                self.albumCover.addToButton.show()
                self.albumCover.playButton.show()
            elif e.type() == QEvent.Leave:
                self.backgroundLabel.setPixmap(
                    QPixmap('resource\\images\\专辑封面无阴影.png'))
                self.albumCover.addToButton.hide()
                self.albumCover.playButton.hide()

        return False

    def contextMenuEvent(self, event: QContextMenuEvent):
        """ 显示右击菜单 """
        menu = QMenu(self)
        addToMenu = QMenu('添加到', self)
        playAct = QAction('播放', self)
        deleteAct = QAction('删除', self)
        chooseAct = QAction('选择', self)
        playingAct = QAction(QIcon('resource\\images\\正在播放.svg'),'正在播放', self)
        editInfoAct = QAction('编辑信息', self)
        showSongerAct = QAction('显示歌手', self)
        newPlayList = QAction(QIcon('resource\\images\\黑色加号.svg'),'新的播放列表', self)
        nextToPlayAct = QAction('下一首播放', self)
        pinToStartMenuAct = QAction('固定到开始菜单', self)
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

        # 隐藏边框并将背景设置为透明
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 实例化按钮
        self.playButton = SongerPlayButton(self)
        self.addToButton = SongerAddToButton(self)

        # 获取封面数据
        self.album_pic = QPixmap(album_path).scaled(
            self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # 初始化小部件
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        self.playButton.move(int(0.5 * self.width() - 36 - 0.5 * self.playButton.width()),
                             int(0.5*self.height() - 0.5*self.playButton.height()+1))

        self.addToButton.move(int(0.5*self.width()+36-0.5*self.playButton.width()),
                              int(0.5*self.height() - 0.5*self.playButton.height()+1))

        # 隐藏按钮
        self.playButton.setHidden(True)
        self.addToButton.setHidden(True)

    def paintEvent(self, e):
        #super(SongerHeadPortrait, self).paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)  # 设置抗锯齿

        # 设置无描边
        pen = Qt.NoPen
        painter.setPen(pen)

        # 设置画刷的内容为封面图
        brush = QBrush(self.album_pic)
        painter.setBrush(brush)

        # 在指定区域画圆
        painter.drawRect(0, 0, self.width(), self.height())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    albumInfo = {'album': '星之回响 (2020 bilibili拜年祭单品)', 'songer': 'HALCA',
                 'cover_path': 'resource\\Album Cover\\天気の子 complete version\\天気の子 complete version.png'}
    demo = AlbumCard(albumInfo)
    demo.show()
    sys.exit(app.exec_())
