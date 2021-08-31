# coding:utf-8
from common.auto_wrap import autoWrap
from common.image_process_utils import DominantColor
from common.os_utils import getCoverPath
from components.buttons.blur_button import BlurButton
from components.check_box import CheckBox
from components.menu import AddToMenu, DWMMenu
from components.perspective_widget import PerspectiveWidget
from PIL import Image
from PIL.ImageFilter import GaussianBlur
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QGraphicsOpacityEffect,
                             QLabel, QVBoxLayout, QWidget)


class PlaylistCard(PerspectiveWidget):
    """ 播放列表信息卡 """

    playSig = pyqtSignal(list)
    nextToPlaySig = pyqtSignal(list)
    deleteCardSig = pyqtSignal(str)
    hideBlurBackgroundSig = pyqtSignal()
    renamePlaylistSig = pyqtSignal(dict)
    checkedStateChanged = pyqtSignal(QWidget, bool)
    switchToPlaylistInterfaceSig = pyqtSignal(str)
    showBlurBackgroundSig = pyqtSignal(QPoint, str)
    addSongsToPlayingPlaylistSig = pyqtSignal(list)      # 添加歌曲到正在播放
    addSongsToNewCustomPlaylistSig = pyqtSignal(list)    # 添加歌曲到新的自定义的播放列表中
    addSongsToCustomPlaylistSig = pyqtSignal(str, list)  # 添加歌曲到自定义的播放列表中

    def __init__(self, playlist: dict, parent=None):
        super().__init__(parent, True)
        # 初始化标志位
        self.isChecked = False
        self.isInSelectionMode = False
        self.__getPlaylistInfo(playlist)
        # 创建小部件
        self.vBoxLayout = QVBoxLayout(self)
        self.playlistCover = PlaylistCover(self)
        self.playButton = BlurButton(
            self,
            (35, 70),
            ":/images/album_tab_interface/Play.png",
            self.playlistCoverPath,
        )
        self.addToButton = BlurButton(
            self,
            (105, 70),
            ":/images/album_tab_interface/Add.png",
            self.playlistCoverPath,
        )
        self.playlistNameLabel = QLabel(self.playlistName, self)
        self.playlistLenLabel = QLabel(
            str(len(self.songInfo_list))+self.tr(" songs"), self)
        # 创建复选框
        self.checkBox = CheckBox(self, forwardTargetWidget=self.playlistCover)
        # 创建动画和窗口特效
        self.checkBoxOpacityEffect = QGraphicsOpacityEffect(self)
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedSize(298, 288)
        self.setAttribute(Qt.WA_StyledBackground)
        # 隐藏按钮和复选框
        self.checkBox.hide()
        self.playButton.hide()
        self.addToButton.hide()
        self.playlistLenLabel.setMinimumWidth(200)
        # 给小部件添加特效
        self.checkBox.setGraphicsEffect(self.checkBoxOpacityEffect)
        # 设置封面
        self.playlistCover.setPlaylistCover(self.playlistCoverPath)
        # 分配ID和属性
        self.setObjectName("playlistCard")
        self.playlistNameLabel.setObjectName("playlistNameLabel")
        self.playlistLenLabel.setObjectName("playlistLenLabel")
        self.setProperty("isChecked", "False")
        self.playlistNameLabel.setProperty("isChecked", "False")
        self.playlistLenLabel.setProperty("isChecked", "False")
        self.__initLayout()
        # 信号连接到槽
        self.__connectSignalToSlot()

    def __initLayout(self):
        """ 初始化布局 """
        self.vBoxLayout.setContentsMargins(5, 5, 0, 0)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addWidget(self.playlistCover)
        self.vBoxLayout.addSpacing(11)
        self.vBoxLayout.addWidget(self.playlistNameLabel)
        self.vBoxLayout.addSpacing(5)
        self.vBoxLayout.addWidget(self.playlistLenLabel)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.checkBox.move(262, 21)
        self.playButton.move(80, 68)
        self.addToButton.move(148, 68)
        # 调整播放列表标签
        self.__adjustLabel()

    def __getPlaylistInfo(self, playlist: dict):
        """ 获取播放列表信息 """
        self.playlist = playlist
        self.playlistName = playlist.get(
            "playlistName", self.tr("Unknown playlist"))

        self.songInfo_list = playlist.get("songInfo_list", [])  # type:list
        songInfo = self.songInfo_list[0] if self.songInfo_list else {}
        name = songInfo.get('coverName', '未知歌手_未知专辑')
        self.playlistCoverPath = getCoverPath(name, 'playlist_small')

    def __adjustLabel(self):
        """ 调整标签的文本长度和位置 """
        newText, isWordWrap = autoWrap(self.playlistName, 32)
        if isWordWrap:
            # 添加省略号
            index = newText.index("\n")
            fontMetrics = self.playlistNameLabel.fontMetrics()
            secondLineText = fontMetrics.elidedText(
                newText[index + 1:], Qt.ElideRight, 288)
            newText = newText[: index + 1] + secondLineText
            self.playlistNameLabel.setText(newText)

        self.playlistNameLabel.adjustSize()
        self.playlistLenLabel.adjustSize()

    def enterEvent(self, e):
        """ 鼠标进入窗口时显示磨砂背景和按钮 """
        # 显示磨砂背景
        playlistCardPos = self.mapToGlobal(QPoint(0, 0))  # type:QPoint
        self.showBlurBackgroundSig.emit(
            playlistCardPos, self.playlistCoverPath)
        # 处于选择模式下按钮不可见
        self.playButton.setHidden(self.isInSelectionMode)
        self.addToButton.setHidden(self.isInSelectionMode)

    def leaveEvent(self, e):
        """ 鼠标离开时隐藏磨砂背景和按钮 """
        # 隐藏磨砂背景
        self.hideBlurBackgroundSig.emit()
        self.addToButton.hide()
        self.playButton.hide()

    def mouseReleaseEvent(self, e):
        """ 鼠标松开发送切换到专辑界面信号或者取反选中状态 """
        super().mouseReleaseEvent(e)
        if e.button() == Qt.LeftButton:
            if self.isInSelectionMode:
                self.setChecked(not self.isChecked)
            else:
                # 切换到播放列表界面
                self.switchToPlaylistInterfaceSig.emit(self.playlistName)

    def updateWindow(self, playlist: dict):
        """ 更新专辑卡窗口信息 """
        self.__getPlaylistInfo(playlist)
        self.playlistCover.setPlaylistCover(self.playlistCoverPath)
        self.playlistNameLabel.setText(self.playlistName)
        self.playlistLenLabel.setText(
            str(len(self.songInfo_list))+self.tr(" songs"))
        self.playButton.setBlurPic(self.playlistCoverPath, 40)
        self.addToButton.setBlurPic(self.playlistCoverPath, 40)
        self.__adjustLabel()

    def __onCheckedStateChanged(self):
        """ 复选框选中状态改变对应的槽函数 """
        self.isChecked = self.checkBox.isChecked()
        # 发送信号
        self.checkedStateChanged.emit(self, self.isChecked)
        # 更新属性和背景色
        self.setProperty("isChecked", str(self.isChecked))
        self.playlistNameLabel.setProperty("isChecked", str(self.isChecked))
        self.playlistLenLabel.setProperty("isChecked", str(self.isChecked))
        self.setStyle(QApplication.style())

    def setChecked(self, isChecked: bool):
        """ 设置歌曲卡的选中状态 """
        self.checkBox.setChecked(isChecked)

    def setSelectionModeOpen(self, isOpenSelectionMode: bool):
        """ 设置是否进入选择模式, 处于选择模式下复选框一直可见，按钮不可见 """
        if self.isInSelectionMode == isOpenSelectionMode:
            return
        # 进入选择模式时显示复选框
        if isOpenSelectionMode:
            self.checkBoxOpacityEffect.setOpacity(1)
            self.checkBox.show()
        self.isInSelectionMode = isOpenSelectionMode

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.checkBox.stateChanged.connect(self.__onCheckedStateChanged)
        self.playButton.clicked.connect(
            lambda: self.playSig.emit(self.songInfo_list))
        self.addToButton.clicked.connect(self.__showAddToMenu)

    def contextMenuEvent(self, e):
        """ 显示右击菜单 """
        menu = PlaylistCardContextMenu(parent=self)
        menu.playAct.triggered.connect(
            lambda: self.playSig.emit(self.songInfo_list))
        menu.nextToPlayAct.triggered.connect(
            lambda: self.nextToPlaySig.emit(self.songInfo_list))
        menu.deleteAct.triggered.connect(
            lambda: self.deleteCardSig.emit(self.playlistName))
        menu.renameAct.triggered.connect(
            lambda: self.renamePlaylistSig.emit(self.playlist))
        menu.selectAct.triggered.connect(self.__onSelectActTriggered)
        menu.addToMenu.playingAct.triggered.connect(
            lambda: self.addSongsToPlayingPlaylistSig.emit(self.songInfo_list))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(self.songInfo_list))
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(name, self.songInfo_list))
        menu.exec(e.globalPos())

    def __showAddToMenu(self):
        """ 显示添加到菜单 """
        menu = AddToMenu(parent=self)
        pos = self.mapToGlobal(QPoint(
            self.addToButton.x(), self.addToButton.y()))
        x = pos.x() + self.addToButton.width() + 5
        y = pos.y() + int(
            self.addToButton.height() / 2 - (13 + 38 * menu.actionCount()) / 2)
        menu.playingAct.triggered.connect(
            lambda: self.addSongsToPlayingPlaylistSig.emit(self.songInfo_list))
        menu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(self.songInfo_list))
        menu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(name, self.songInfo_list))
        menu.exec(QPoint(x, y))

    def __onSelectActTriggered(self):
        """ 右击菜单选择动作对应的槽函数 """
        self.setSelectionModeOpen(True)
        self.setChecked(True)


class PlaylistCover(QWidget):
    """ 播放列表封面 """

    def __init__(self, parent=None, picPath: str = ""):
        super().__init__(parent)
        self.setFixedSize(288, 196)
        self.__blurPix = None
        self.__playlistCoverPix = None
        self.playlistCoverPath = ''
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setPlaylistCover(picPath)

    def setPlaylistCover(self, picPath: str):
        """ 设置封面 """
        if picPath == self.playlistCoverPath:
            return

        # 封面磨砂
        self.playlistCoverPath = picPath

        if not picPath.startswith(':'):
            img = Image.open(picPath)
        else:
            img = Image.fromqpixmap(QPixmap(picPath))

        img = img.resize((288, 288)).crop((0, 46, 288, 242))
        self.__blurPix = img.filter(GaussianBlur(40)).toqpixmap()
        self.__playlistCoverPix = QPixmap(picPath).scaled(
            135, 135, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)  # type:QPixmap

        # 获取主色调
        self.dominantRgb = DominantColor.getDominantColor(picPath)
        self.update()

    def paintEvent(self, e):
        """ 绘制背景 """
        super().paintEvent(e)
        if not self.__blurPix:
            return
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setRenderHints(QPainter.Antialiasing)
        # 绘制磨砂背景
        painter.drawPixmap(0, 0, self.__blurPix)
        # 绘制主题色
        gradientColor = QLinearGradient(0, self.height(), 0, 0)
        gradientColor.setColorAt(0, QColor(*self.dominantRgb, 128))
        gradientColor.setColorAt(1, QColor(*self.dominantRgb, 10))
        painter.setBrush(QBrush(gradientColor))
        painter.drawRect(self.rect())
        # 绘制封面
        painter.drawPixmap(76, 31, self.__playlistCoverPix)
        # 绘制封面集
        painter.setBrush(QBrush(QColor(*self.dominantRgb, 100)))
        painter.drawRect(96, 21, self.width() - 192, 5)
        painter.setBrush(QBrush(QColor(*self.dominantRgb, 210)))
        painter.drawRect(86, 26, self.width() - 172, 5)


class PlaylistCardContextMenu(DWMMenu):
    """ 播放列表卡右击菜单 """

    def __init__(self, parent=None):
        super().__init__("", parent)
        # 创建动作
        self.__createActions()
        self.setObjectName("playlistCardContextMenu")
        self.setQss()

    def __createActions(self):
        """ 创建动作 """
        # 创建动作
        self.playAct = QAction(self.tr("Play"), self)
        self.nextToPlayAct = QAction(self.tr("Play next"), self)
        self.addToMenu = AddToMenu(self.tr("Add to"), self)
        self.renameAct = QAction(self.tr("Rename"), self)
        self.pinToStartMenuAct = QAction(self.tr('Pin to Start'), self)
        self.deleteAct = QAction(self.tr("Delete"), self)
        self.selectAct = QAction(self.tr("Select"), self)

        # 添加动作到菜单
        self.addActions([self.playAct, self.nextToPlayAct])
        # 将子菜单添加到主菜单
        self.addMenu(self.addToMenu)
        self.addActions(
            [self.renameAct, self.pinToStartMenuAct, self.deleteAct])
        self.addSeparator()
        self.addAction(self.selectAct)
