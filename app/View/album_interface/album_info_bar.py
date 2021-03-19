# coding:utf-8

from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPixmap, QPalette, QResizeEvent
from PyQt5.QtWidgets import QLabel, QWidget

from app.common.get_dominant_color import DominantColor

from .album_interface_buttons import BasicButton
from .album_interface_menus import MoreActionsMenu
from app.components.menu import AddToMenu


class AlbumInfoBar(QWidget):
    """ 专辑信息栏 """

    editInfoSig = pyqtSignal()
    addToPlayingPlaylistSig = pyqtSignal()
    addToNewCustomPlaylistSig = pyqtSignal()
    addToCustomPlaylistSig = pyqtSignal(str)

    def __init__(self, albumInfo: dict, parent=None):
        super().__init__(parent)
        self.setAlbumInfo(albumInfo)
        self.backgroundColor = None
        self.dominantColor = DominantColor()
        # 实例化小部件
        self.__createWidgets()
        # 初始化
        self.__initWidget()

    def __createWidgets(self):
        """ 创建小部件 """
        self.moreActionsMenu = MoreActionsMenu(self)
        self.albumCover = QLabel(self)
        self.albumNameLabel = QLabel(self.albumName, self)
        self.songerNameLabel = QLabel(self.songerName, self)
        self.yearTconLabel = QLabel(self.year + " • " + self.tcon, self)
        self.playAllBt = BasicButton(
            r"app\resource\images\album_interface\全部播放.png", "全部播放", self
        )
        self.addToBt = BasicButton(
            r"app\resource\images\album_interface\添加到.png", "添加到", self
        )
        self.showSongerBt = BasicButton(
            r"app\resource\images\album_interface\显示歌手.png", "显示歌手", self
        )
        self.pinToStartMenuBt = BasicButton(
            r"app\resource\images\album_interface\固定到开始菜单.png", '固定到"开始"菜单', self
        )
        self.editInfoBt = BasicButton(
            r"app\resource\images\album_interface\编辑信息.png", "编辑信息", self
        )
        self.moreActionsBt = BasicButton(
            r"app\resource\images\album_interface\更多操作.png", "", self
        )
        self.deleteButton = BasicButton(
            r"app\resource\images\album_interface\删除.png", "删除", self
        )
        self.albumCover.resize(295, 295)
        self.albumCover.setPixmap(
            QPixmap(self.albumCoverPath).scaled(
                295, 295, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
        )

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1260, 385)
        # 禁止从父级窗口继承背景
        self.setAutoFillBackground(True)
        # 设置小部件位置
        self.__initLayout()
        # 设置主色调
        self.__setBackgroundColor()
        # 分配ID
        self.albumNameLabel.setObjectName("albumNameLabel")
        self.songerNameLabel.setObjectName("songerNameLabel")
        self.yearTconLabel.setObjectName("yearTconLabel")
        # 设置层叠样式
        self.__setQss()
        # 信号连接到槽
        self.addToBt.clicked.connect(self.__showAddToMenu)
        self.moreActionsBt.clicked.connect(self.__showMoreActionsMenu)

    def __initLayout(self):
        """ 初始化布局 """
        self.albumCover.move(45, 45)
        self.albumNameLabel.move(385, 35)
        self.__adjustLabelPos()
        self.playAllBt.move(360, 308)
        self.addToBt.move(503, self.playAllBt.y())
        self.showSongerBt.move(629, self.playAllBt.y())
        self.pinToStartMenuBt.move(774, self.playAllBt.y())
        self.editInfoBt.move(977, self.playAllBt.y())
        self.deleteButton.move(1121, self.playAllBt.y())
        self.__adjustButtonPos(True)

    def __adjustLabelPos(self):
        """ 根据专辑名是否换行来调整标签位置 """
        maxWidth = self.width() - 40 - 385
        # 设置专辑名歌手名标签的长度
        fontMetrics = QFontMetrics(QFont("Microsoft YaHei", 24, 63))
        albumLabelWidth = sum([fontMetrics.width(i) for i in self.albumName])
        self.albumNameLabel.setFixedWidth(min(maxWidth, albumLabelWidth))
        newAlbumName_list = list(self.albumName)  # type:list
        totalWidth = 0
        isWrap = False
        for i in range(len(self.albumName)):
            totalWidth += fontMetrics.width(self.albumName[i])
            if totalWidth > maxWidth:
                newAlbumName_list.insert(i, "\n")
                isWrap = True
                break
        if isWrap:
            index = newAlbumName_list.index("\n")
            # 再次根据换行后的长度决定是否使用省略号
            newAlbumName = "".join(newAlbumName_list)
            secondLineText = fontMetrics.elidedText(
                newAlbumName[index + 1 :], Qt.ElideRight, maxWidth
            )
            newAlbumName = newAlbumName[: index + 1] + secondLineText
            self.albumNameLabel.setText(newAlbumName)
            self.albumNameLabel.resize(maxWidth, 110)
            self.songerNameLabel.move(self.albumNameLabel.x(), 155)
            self.yearTconLabel.move(self.albumNameLabel.x(), 177)
        else:
            self.albumNameLabel.setText(self.albumName)
            self.albumNameLabel.resize(totalWidth, 54)
            self.songerNameLabel.move(self.albumNameLabel.x(), 93)
            self.yearTconLabel.move(self.albumNameLabel.x(), 115)

    def __adjustButtonPos(self, isDeltaWidthPositive: bool):
        """ 根据窗口宽度隐藏部分按钮并调整更多操作按钮位置 """
        if isDeltaWidthPositive and self.width() >= 1315:
            if self.width() >= 1315:
                self.__adjustButtonPosFunc(1, 1120, False, True, True, True)
        elif (isDeltaWidthPositive and 1240 <= self.width() < 1315) or (
            not isDeltaWidthPositive and self.width() >= 1240
        ):
            isDeleteBtVisible = self.deleteButton.isVisible()
            # 保持删除按钮原来的可见性
            self.__adjustButtonPosFunc(
                1, 1120, not isDeleteBtVisible, isDeleteBtVisible, True, True
            )
        if 1200 <= self.width() < 1240:
            self.__adjustButtonPosFunc(1, 1120, True, False, True, True)
        elif 1058 <= self.width() < 1200:
            self.__adjustButtonPosFunc(2, 988, True, False, True, False)
        elif self.width() < 1058:
            self.__adjustButtonPosFunc(3, 785, True, False, False, False)

    def __adjustButtonPosFunc(
        self,
        actionNum,
        x,
        isMoreActBtVisible,
        isDeleteBtVisible,
        isPinToBtVisible,
        isEditInfoBtVisible,
    ):
        """ 设置按钮位置子函数 """
        self.moreActionsMenu.setActionNum(actionNum)
        self.moreActionsBt.move(x, self.playAllBt.y())
        self.moreActionsBt.setVisible(isMoreActBtVisible)
        self.deleteButton.setVisible(isDeleteBtVisible)
        self.pinToStartMenuBt.setVisible(isPinToBtVisible)
        self.editInfoBt.setVisible(isEditInfoBtVisible)

    def updateWindow(self, albumInfo: dict):
        """ 更新界面 """
        self.setAlbumInfo(albumInfo)
        self.albumNameLabel.setText(self.albumName)
        self.songerNameLabel.setText(self.songerName)
        self.yearTconLabel.setText(self.year + " • " + self.tcon)
        self.albumCover.setPixmap(
            QPixmap(self.albumCoverPath).scaled(
                295, 295, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
        )
        self.__adjustLabelText()
        self.__setBackgroundColor()
        self.__adjustLabelPos()

    def setAlbumInfo(self, albumInfo: dict):
        """ 设置专辑信息 """
        self.albumInfo = albumInfo if albumInfo else {}
        self.year = albumInfo.get("year", "未知年份")  # type:str
        self.tcon = albumInfo.get("tcon", "未知流派")  # type:str
        self.albumName = albumInfo.get("album", "未知专辑")  # type:str
        self.songerName = albumInfo.get("songer", "未知歌手")  # type:str
        self.albumCoverPath = albumInfo.get(
            "cover_path", r"app\resource\images\未知专辑封面_200_200.png"
        )

    def resizeEvent(self, e: QResizeEvent):
        """ 窗口调整大小时 """
        # 计算宽度的差值
        deltaWidth = e.size().width() - e.oldSize().width()
        super().resizeEvent(e)
        self.__adjustLabelPos()
        self.__adjustButtonPos(deltaWidth >= 0)

    def __setQss(self):
        """ 设置层叠样式 """
        with open(r"app\resource\css\albumInterface.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def __setBackgroundColor(self):
        """ 设置背景颜色 """
        self.backgroundColor = self.dominantColor.getDominantColor(
            self.albumCoverPath, resType=tuple
        )
        r, g, b = self.backgroundColor
        palette = QPalette()
        palette.setColor(self.backgroundRole(), QColor(r, g, b))
        self.setPalette(palette)

    def __adjustLabelText(self):
        """ 调整歌手名和年份流派标签长度和文本 """
        maxWidth = self.width() - 40 - 294
        fontMetrics = QFontMetrics(QFont("Microsoft YaHei", 9))
        songerWidth = fontMetrics.width(self.songerName)
        yearTconWidth = fontMetrics.width(self.yearTconLabel.text())
        self.songerNameLabel.setFixedWidth(min(maxWidth, songerWidth))
        self.yearTconLabel.setFixedWidth(min(maxWidth, yearTconWidth))
        # 加省略号
        self.songerNameLabel.setText(
            fontMetrics.elidedText(self.songerName, Qt.ElideRight, maxWidth)
        )
        self.yearTconLabel.setText(
            fontMetrics.elidedText(self.yearTconLabel.text(), Qt.ElideRight, maxWidth)
        )

    def __showAddToMenu(self):
        """ 显示添加到菜单 """
        addToMenu = AddToMenu(parent=self)
        addToGlobalPos = self.mapToGlobal(self.addToBt.pos())
        x = addToGlobalPos.x() + self.addToBt.width() + 5
        y = addToGlobalPos.y() + int(
            self.addToBt.height() / 2 - (13 + 38 * addToMenu.actionCount()) / 2
        )
        addToMenu.playingAct.triggered.connect(self.addToPlayingPlaylistSig)
        addToMenu.addSongsToPlaylistSig.connect(self.addToCustomPlaylistSig)
        addToMenu.newPlayList.triggered.connect(self.addToNewCustomPlaylistSig)
        addToMenu.exec(QPoint(x, y))

    def __showMoreActionsMenu(self):
        """ 显示更多操作菜单 """
        if self.moreActionsMenu.actionNum >= 2:
            self.moreActionsMenu.editInfoAct.triggered.connect(self.editInfoSig)
        globalPos = self.mapToGlobal(self.moreActionsBt.pos())
        x = globalPos.x() + self.moreActionsBt.width() + 5
        y = globalPos.y() + int(
            self.moreActionsBt.height() / 2 - self.moreActionsMenu.currentHeight / 2
        )
        self.moreActionsMenu.exec(QPoint(x, y))
