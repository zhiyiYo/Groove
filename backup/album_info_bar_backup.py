# coding:utf-8

from PyQt5.QtCore import Qt, QPoint,pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont, QFontMetrics, QPixmap, QPalette
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

from my_functions.get_dominant_color import DominantColor

from .album_interface_buttons import BasicButton
from .album_interface_menus import MoreActionsMenu,AddToMenu


class AlbumInfoBar(QWidget):
    """ 专辑信息栏 """
    editInfoSig = pyqtSignal()

    def __init__(self, albumInfo: dict, parent=None):
        super().__init__(parent)
        self.setAlbumInfo(albumInfo)
        self.backgroundColor = None
        self.dominantColor=DominantColor()
        # 实例化小部件
        self.__createWidgets()
        # 初始化
        self.__initWidget()

    def __createWidgets(self):
        """ 创建小部件 """
        self.addToMenu = AddToMenu(self)
        self.moreActionsMenu = MoreActionsMenu(self)
        self.albumCover = QLabel(self)
        self.albumNameLabel = QLabel(self.albumName, self)
        self.songerNameLabel = QLabel(self.songerName, self)
        self.yearTconLabel = QLabel(self.year + ' • ' + self.tcon, self)
        self.playAllBt = BasicButton(
            r'resource\images\album_interface\全部播放.png', '全部播放', self)
        self.addToBt = BasicButton(
            r'resource\images\album_interface\添加到.png', '添加到', self)
        self.showSongerBt = BasicButton(
            r'resource\images\album_interface\显示歌手.png', '显示歌手', self)
        self.pinToStartMenuBt = BasicButton(
            r'resource\images\album_interface\固定到开始菜单.png', '固定到"开始"菜单', self)
        self.editInfoBt = BasicButton(
            r'resource\images\album_interface\编辑信息.png', '编辑信息', self)
        self.moreActionsBt = BasicButton(
            r'resource\images\album_interface\更多操作.png', '', self)
        self.albumCover.setPixmap(QPixmap(self.albumCoverPath).scaled(
            204, 204, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1230, 284)
        # 禁止从父级窗口继承背景
        self.setAutoFillBackground(True)
        # 设置小部件位置
        self.__initLayout()
        # 设置主色调
        self.__setBackgroundColor()
        # 分配ID
        self.albumNameLabel.setObjectName('albumNameLabel')
        self.songerNameLabel.setObjectName('songerNameLabel')
        self.yearTconLabel.setObjectName('yearTconLabel')
        # 设置层叠样式
        self.__setQss()
        # 信号连接到槽
        self.addToBt.clicked.connect(self.showAddToMenu)
        self.moreActionsBt.clicked.connect(self.showMoreActionsMenu)

    def __initLayout(self):
        """ 初始化布局 """
        self.albumCover.move(45, 42)
        self.albumNameLabel.move(294, 37)
        self.__adjustLabelPos()
        self.playAllBt.move(271, 211)
        self.addToBt.move(414, 211)
        self.showSongerBt.move(540, 211)
        self.pinToStartMenuBt.move(685, 211)
        self.editInfoBt.move(888, 211)
        self.__adjustButtonPos()

    def __adjustLabelPos(self):
        """ 根据专辑名是否换行来调整标签位置 """
        maxWidth = self.width() - 232 - 294
        # 设置专辑名歌手名标签的长度
        fontMetrics = QFontMetrics(QFont('Microsoft YaHei', 22, 63))
        albumLabelWidth = sum([fontMetrics.width(i)
                               for i in self.albumName])
        self.albumNameLabel.setFixedWidth(min(maxWidth, albumLabelWidth))
        newAlbumName_list = list(self.albumName)  # type:list
        totalWidth = 0
        isWrap = False
        for i in range(len(self.albumName)):
            totalWidth += fontMetrics.width(self.albumName[i])
            if totalWidth > maxWidth:
                newAlbumName_list.insert(i, '\n')
                isWrap = True
                break
        if isWrap:
            index = newAlbumName_list.index('\n')
            # 再次根据换行后的长度决定是否使用省略号
            newAlbumName = ''.join(newAlbumName_list)
            secondLineText = fontMetrics.elidedText(
                newAlbumName[index + 1:], Qt.ElideRight, maxWidth)
            newAlbumName = newAlbumName[: index + 1] + secondLineText
            self.albumNameLabel.setText(newAlbumName)
            self.albumNameLabel.setFixedSize(maxWidth, 108)
            self.songerNameLabel.move(294, 155)
            self.yearTconLabel.move(294, 177)
        else:
            self.albumNameLabel.setText(self.albumName)
            self.albumNameLabel.setFixedSize(totalWidth, 54)
            self.songerNameLabel.move(294, 98)
            self.yearTconLabel.move(294, 119)

    def __adjustButtonPos(self):
        """ 根据窗口宽度隐藏部分按钮并调整更多操作按钮位置 """
        if self.width() >= 1200:
            self.moreActionsMenu.setActionNum(1)
            self.moreActionsBt.move(1031, 211)
            self.pinToStartMenuBt.show()
            self.editInfoBt.show()
        elif 1058 <= self.width() < 1200:
            self.moreActionsMenu.setActionNum(2)
            self.moreActionsBt.move(888, 211)
            self.editInfoBt.hide()
            self.pinToStartMenuBt.show()
        elif self.width() < 1058:
            self.moreActionsMenu.setActionNum(3)
            self.moreActionsBt.move(685, 211)
            self.pinToStartMenuBt.hide()
            self.editInfoBt.hide()

    def updateWindow(self, albumInfo: dict):
        """ 更新界面 """
        self.setAlbumInfo(albumInfo)
        self.albumNameLabel.setText(self.albumName)
        self.songerNameLabel.setText(self.songerName)
        self.yearTconLabel.setText(self.year + ' • ' + self.tcon)
        self.albumCover.setPixmap(QPixmap(self.albumCoverPath).scaled(
            204, 204, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.__adjustLabelWidth()
        self.__setBackgroundColor()
        self.__adjustLabelPos()

    def setAlbumInfo(self, albumInfo: dict):
        """ 设置专辑信息 """
        self.albumInfo = albumInfo if albumInfo else {}
        self.year = albumInfo.get('year', '未知年份')
        self.tcon = albumInfo.get('tcon', '未知流派')
        self.albumName = albumInfo.get('album', '未知专辑')
        self.songerName = albumInfo.get('songer', '未知歌手')
        self.albumCoverPath = albumInfo.get(
            'cover_path', r'resource\images\未知专辑封面_200_200.png')

    def resizeEvent(self, e):
        """ 窗口调整大小时 """
        super().resizeEvent(e)
        self.__adjustLabelPos()
        self.__adjustButtonPos()

    def __setQss(self):
        """ 设置层叠样式 """
        with open(r'resource\css\albumInterface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __setBackgroundColor(self):
        """ 设置背景颜色 """
        self.backgroundColor = self.dominantColor.getDominantColor(
            self.albumCoverPath, resType=tuple)
        r, g, b = self.backgroundColor
        palette = QPalette()
        palette.setColor(self.backgroundRole(), QColor(r, g, b))
        self.setPalette(palette)

    def __adjustLabelWidth(self):
        """ 调整标签长度 """
        maxWidth = self.width() - 232 - 294
        fontMetrics = QFontMetrics(QFont('Microsoft YaHei', 9))
        songerWidth = sum([fontMetrics.width(i) for i in self.songerName])
        yearTconWidth = sum([fontMetrics.width(i)
                             for i in self.yearTconLabel.text()])
        self.songerNameLabel.setFixedWidth(min(maxWidth, songerWidth))
        self.yearTconLabel.setFixedWidth(min(maxWidth, yearTconWidth))
        # 加省略号
        self.songerNameLabel.setText(fontMetrics.elidedText(
            self.songerName, Qt.ElideRight, maxWidth))
        self.yearTconLabel.setText(fontMetrics.elidedText(
            self.yearTconLabel.text(), Qt.ElideRight, maxWidth))

    def showAddToMenu(self):
        """ 显示添加到菜单 """
        addToGlobalPos = self.mapToGlobal(self.addToBt.pos())
        x = addToGlobalPos.x() + self.addToBt.width() + 5
        y = addToGlobalPos.y() + int(self.addToBt.height() / 2 - 141 / 2)
        self.addToMenu.exec(QPoint(x, y))

    def showMoreActionsMenu(self):
        """ 显示更多操作菜单 """
        if self.moreActionsMenu.actionNum >= 2:
            self.moreActionsMenu.editInfoAct.triggered.connect(self.editInfoSig)
        globalPos = self.mapToGlobal(self.moreActionsBt.pos())
        x = globalPos.x() + self.moreActionsBt.width() + 5
        y = globalPos.y() + int(
            self.moreActionsBt.height() / 2 - self.moreActionsMenu.currentHeight / 2)
        self.moreActionsMenu.exec(QPoint(x, y))
