# coding:utf-8

from copy import deepcopy

from my_album_tab_interface.check_box import CheckBox
from my_functions.auto_wrap import autoWrap
from my_functions.get_cover_path import getCoverPath
from my_functions.get_dominant_color import DominantColor
from my_widget.blur_button import BlurButton
from my_widget.perspective_widget import PerspectiveWidget
from PIL import Image
from PIL.ImageFilter import GaussianBlur
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtGui import (QBrush, QColor, QFont, QFontMetrics, QLinearGradient,
                         QPainter, QPixmap)
from PyQt5.QtWidgets import (QAction, QApplication, QGraphicsOpacityEffect,
                             QLabel, QWidget)

from .playlist_card_context_menu import PlaylistCardContextMenu


class PlaylistCard(PerspectiveWidget):
    """ 播放列表信息卡 """
    playSig = pyqtSignal(list)
    nextToPlaySig = pyqtSignal(list)
    deleteCardSig = pyqtSignal(dict)
    hideBlurBackgroundSig = pyqtSignal()
    renamePlaylistSig = pyqtSignal(dict)
    checkedStateChanged = pyqtSignal(QWidget, bool)
    switchToPlaylistInterfaceSig = pyqtSignal(str)
    showBlurBackgroundSig = pyqtSignal(QPoint, str)

    def __init__(self, playlist: dict, parent=None):
        super().__init__(parent, True)
        # 初始化标志位
        self.isChecked = False
        self.isInSelectionMode = False
        self.__getPlaylistInfo(playlist)
        # 创建小部件
        self.playlistCover = PlaylistCover(self)
        self.playButton = BlurButton(
            self, (35, 70), r'resource\images\album_tab_interface\播放按钮_70_70.png', self.playlistCoverPath)
        self.addToButton = BlurButton(
            self, (105, 70), r'resource\images\album_tab_interface\添加到按钮_70_70.png', self.playlistCoverPath)
        self.playlistNameLabel = QLabel(self.playlistName, self)
        self.playlistLenLabel = QLabel(f'{len(self.songInfo_list)} 首歌曲', self)
        # 创建复选框
        self.checkBox = CheckBox(
            self, forwardTargetWidget=self.playlistCover)
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
        # 设置标签字体
        self.playlistNameLabel.setFont(QFont('Microsoft YaHei', 10, 75))
        self.playlistLenLabel.setFont(QFont('Microsoft YaHei', 9))
        # 给小部件添加特效
        self.checkBox.setGraphicsEffect(self.checkBoxOpacityEffect)
        # 设置封面
        self.playlistCover.setPlaylistCover(self.playlistCoverPath)
        # 分配ID和属性
        self.setObjectName('playlistCard')
        self.playlistNameLabel.setObjectName('playlistNameLabel')
        self.playlistLenLabel.setObjectName('playlistLenLabel')
        self.setProperty('isChecked', 'False')
        self.playlistNameLabel.setProperty('isChecked', 'False')
        self.playlistLenLabel.setProperty('isChecked', 'False')
        self.__initLayout()
        # 信号连接到槽
        self.__connectSignalToSlot()

    def __initLayout(self):
        """ 初始化布局 """
        self.checkBox.move(262, 21)
        self.playButton.move(80, 68)
        self.playlistCover.move(5, 5)
        self.addToButton.move(148, 68)
        self.playlistNameLabel.move(5, 213)
        # 调整播放列表标签
        self.__adjustLabel()

    def __getPlaylistInfo(self, playlist: dict):
        """ 获取播放列表信息 """
        self.playlist = deepcopy(playlist)
        self.playlistName = self.playlist.get('playlistName')       # type:str
        self.songInfo_list = self.playlist.get(
            'songInfo_list', [])  # type:list
        if self.songInfo_list:
            self.playlistCoverPath = getCoverPath(
                self.songInfo_list[0].get('modifiedAlbum'), False)
        else:
            self.playlistCoverPath = r'resource\images\playlist_card_interface\空播放列表封面.jpg'

    def __adjustLabel(self):
        """ 调整标签的文本长度和位置 """
        newText, isWordWrap = autoWrap(self.playlistName, 32)
        if isWordWrap:
            # 添加省略号
            index = newText.index('\n')
            fontMetrics = QFontMetrics(QFont('Microsoft YaHei', 10, 75))
            secondLineText = fontMetrics.elidedText(
                newText[index + 1:], Qt.ElideRight, 288)
            newText = newText[: index + 1] + secondLineText
            self.playlistNameLabel.setText(newText)
        self.playlistNameLabel.adjustSize()
        self.playlistLenLabel.adjustSize()
        self.playlistLenLabel.move(
            5, self.playlistNameLabel.y() + self.playlistNameLabel.height() + 5)

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
        self.playlistLenLabel.setText(f'{len(self.songInfo_list)} 首歌曲')
        self.playButton.setBlurPic(self.playlistCoverPath, 26)
        self.addToButton.setBlurPic(self.playlistCoverPath, 26)
        self.__adjustLabel()

    def __checkedStateChangedSlot(self):
        """ 复选框选中状态改变对应的槽函数 """
        self.isChecked = self.checkBox.isChecked()
        # 发送信号
        self.checkedStateChanged.emit(self, self.isChecked)
        # 更新属性和背景色
        self.setProperty('isChecked', str(self.isChecked))
        self.playlistNameLabel.setProperty('isChecked', str(self.isChecked))
        self.playlistLenLabel.setProperty('isChecked', str(self.isChecked))
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
        self.checkBox.stateChanged.connect(self.__checkedStateChangedSlot)
        self.playButton.clicked.connect(
            lambda: self.playSig.emit(self.songInfo_list))

    def contextMenuEvent(self, e):
        """ 显示右击菜单 """
        menu = PlaylistCardContextMenu(parent=self)
        menu.playAct.triggered.connect(
            lambda: self.playSig.emit(self.songInfo_list))
        menu.nextToPlayAct.triggered.connect(
            lambda: self.nextToPlaySig.emit(self.songInfo_list))
        menu.deleteAct.triggered.connect(
            lambda: self.deleteCardSig.emit(self.playlist))
        menu.renameAct.triggered.connect(
            lambda: self.renamePlaylistSig.emit(self.playlist))
        menu.selectAct.triggered.connect(self.__selectActSlot)
        menu.exec(e.globalPos())

    def __selectActSlot(self):
        """ 右击菜单选择动作对应的槽函数 """
        self.setSelectionModeOpen(True)
        self.setChecked(True)


class PlaylistCover(QWidget):
    """ 播放列表封面 """

    def __init__(self, parent=None, picPath: str = '', picSize: tuple = (135, 135)):
        super().__init__(parent)
        self.resize(288, 196)
        self.__blurPix = None
        self.__playlistCoverPix = None
        self.__dominantColor = DominantColor()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setPlaylistCover(picPath)

    def setPlaylistCover(self, picPath: str):
        """ 设置封面 """
        self.playlistCoverPath = picPath
        if not picPath:
            return
        # 封面磨砂
        img = Image.open(picPath).resize(
            (288, 288)).crop((0, 46, 288, 242))  # type:Image.Image
        self.__blurPix = img.filter(GaussianBlur(50)).toqpixmap()
        self.playlistCoverPix = QPixmap(picPath).scaled(
            135, 135, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)  # type:QPixmap
        # 获取主色调
        self.dominantRgb = self.__dominantColor.getDominantColor(
            picPath, tuple)
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
        painter.drawPixmap(76, 31, self.playlistCoverPix)
        # 绘制封面集
        painter.setBrush(QBrush(QColor(*self.dominantRgb, 100)))
        painter.drawRect(96, 21, self.width() - 192, 5)
        painter.setBrush(QBrush(QColor(*self.dominantRgb, 210)))
        painter.drawRect(86, 26, self.width() - 172, 5)
