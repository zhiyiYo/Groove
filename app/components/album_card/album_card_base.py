# coding:utf-8
from common.auto_wrap import autoWrap
from common.database.entity import AlbumInfo
from common.os_utils import getCoverPath
from common.signal_bus import signalBus
from components.buttons.blur_button import BlurButton
from components.widgets.check_box import CheckBox
from components.widgets.label import ClickableLabel
from components.widgets.menu import AddToMenu
from components.widgets.perspective_widget import PerspectiveWidget
from PyQt5.QtCore import QObject, QPoint, QPropertyAnimation, Qt, pyqtSignal
from PyQt5.QtGui import QFont, QFontMetrics, QPixmap
from PyQt5.QtWidgets import (QApplication, QGraphicsOpacityEffect, QLabel,
                             QVBoxLayout, QWidget, qApp)


class AlbumCardBase(PerspectiveWidget):
    """ 专辑卡基类 """

    deleteCardSig = pyqtSignal(str, str)                     # 删除专辑卡
    nextPlaySignal = pyqtSignal(str, str)                    # 下一首播放
    addToPlayingSignal = pyqtSignal(str, str)                # 将专辑添加到正在播放
    checkedStateChanged = pyqtSignal(QWidget, bool)          # 选中状态改变
    addAlbumToNewCustomPlaylistSig = pyqtSignal(str, str)    # 将专辑添加到新建的播放列表
    addAlbumToCustomPlaylistSig = pyqtSignal(str, str, str)  # 将专辑添加到自定义播放列表
    showAlbumInfoEditDialogSig = pyqtSignal(str, str)        # 显示专辑信息面板信号
    showBlurAlbumBackgroundSig = pyqtSignal(QPoint, str)     # 显示磨砂背景
    hideBlurAlbumBackgroundSig = pyqtSignal()                # 隐藏磨砂背景

    def __init__(self, albumInfo: AlbumInfo, parent=None):
        super().__init__(parent, True)
        self.__setAlbumInfo(albumInfo)
        self.isChecked = False
        self.isInSelectionMode = False

        self.vBoxLayout = QVBoxLayout(self)
        self.albumLabel = ClickableLabel(self.album, self)
        self.contentLabel = ClickableLabel(self.singer, self, False)
        self.albumPic = QLabel(self)

        self.playButton = BlurButton(
            self,
            (30, 65),
            ":/images/album_tab_interface/Play.png",
            self.coverPath,
            self.tr('Play')
        )
        self.addToButton = BlurButton(
            self,
            (100, 65),
            ":/images/album_tab_interface/Add.png",
            self.coverPath,
            self.tr('Add to')
        )
        self.checkBox = CheckBox(self)
        self.checkBoxOpacityEffect = QGraphicsOpacityEffect(self)
        self.hideCheckBoxAni = QPropertyAnimation(
            self.checkBoxOpacityEffect, b'opacity', self)

        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedSize(210, 290)
        self.setAttribute(Qt.WA_StyledBackground)
        self.albumPic.setFixedSize(200, 200)
        self.contentLabel.setFixedWidth(210)
        self.albumLabel.setFixedWidth(210)
        self.playButton.move(35, 70)
        self.addToButton.move(105, 70)
        self.albumPic.setPixmap(QPixmap(self.coverPath).scaled(
            200, 200, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))

        # 给小部件添加特效
        self.checkBox.setFocusPolicy(Qt.NoFocus)
        self.checkBox.setGraphicsEffect(self.checkBoxOpacityEffect)

        # 隐藏按钮
        self.playButton.hide()
        self.addToButton.hide()

        # 设置动画
        self.hideCheckBoxAni.setStartValue(1)
        self.hideCheckBoxAni.setEndValue(0)
        self.hideCheckBoxAni.setDuration(150)

        # 设置鼠标光标
        self.contentLabel.setCursor(Qt.PointingHandCursor)

        # 设置部件位置
        self.__initLayout()

        # 分配ID和属性
        self.setObjectName("albumCard")
        self.albumLabel.setObjectName("albumLabel")
        self.contentLabel.setObjectName("contentLabel")
        self.setProperty("isChecked", "False")
        self.albumLabel.setProperty("isChecked", "False")
        self.contentLabel.setProperty("isChecked", "False")

        # 将信号连接到槽函数
        self.playButton.clicked.connect(
            lambda: signalBus.playAlbumSig.emit(self.singer, self.album))
        self.contentLabel.clicked.connect(
            lambda: signalBus.switchToSingerInterfaceSig.emit(self.singer))
        self.addToButton.clicked.connect(self.__showAddToMenu)
        self.checkBox.stateChanged.connect(self.__onCheckedStateChanged)

    def __initLayout(self):
        """ 初始化布局 """
        self.vBoxLayout.setContentsMargins(5, 5, 0, 0)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addWidget(self.albumPic)
        self.vBoxLayout.addSpacing(11)
        self.vBoxLayout.addWidget(self.albumLabel)
        self.vBoxLayout.addSpacing(2)
        self.vBoxLayout.addWidget(self.contentLabel)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.checkBox.move(178, 8)
        self.checkBox.hide()
        self.__adjustLabel()

    def __setAlbumInfo(self, albumInfo: AlbumInfo):
        """ 获取专辑信息 """
        self.albumInfo = albumInfo
        self.album = albumInfo.album
        self.singer = albumInfo.singer
        self.year = str(albumInfo.year)
        self.coverPath = getCoverPath(self.singer, self.album, 'album_big')

    def enterEvent(self, e):
        """ 鼠标进入窗口时显示磨砂背景和按钮 """
        # 显示磨砂背景
        albumCardPos = self.mapToGlobal(QPoint(0, 0))  # type:QPoint
        self.showBlurAlbumBackgroundSig.emit(albumCardPos, self.coverPath)

        # 处于选择模式下按钮不可见
        self.playButton.setHidden(self.isInSelectionMode)
        self.addToButton.setHidden(self.isInSelectionMode)

    def leaveEvent(self, e):
        """ 鼠标离开时隐藏磨砂背景和按钮 """
        self.hideBlurAlbumBackgroundSig.emit()
        self.addToButton.hide()
        self.playButton.hide()

    def mouseReleaseEvent(self, e):
        """ 鼠标松开发送切换到专辑界面信号或者取反选中状态 """
        super().mouseReleaseEvent(e)
        if e.button() == Qt.LeftButton:
            if self.isInSelectionMode:
                self.setChecked(not self.isChecked)
            else:
                # 不处于选择模式时且鼠标松开事件不是复选框发来的才发送切换到专辑界面的信号
                signalBus.switchToAlbumInterfaceSig.emit(self.singer, self.album)

    def showAlbumInfoEditDialog(self):
        """ 显示专辑信息编辑面板 """
        self.showAlbumInfoEditDialogSig.emit(self.singer, self.album)

    def updateAlbumCover(self, coverPath: str):
        """ 更新专辑封面 """
        self.coverPath = coverPath
        self.albumPic.setPixmap(QPixmap(self.coverPath).scaled(
            200, 200, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        self.playButton.setBlurPic(coverPath, 40)
        self.addToButton.setBlurPic(coverPath, 40)

    def updateWindow(self, albumInfo: AlbumInfo):
        """ 更新专辑卡窗口信息 """
        if albumInfo == self.albumInfo:
            return

        self.__setAlbumInfo(albumInfo)
        self.albumPic.setPixmap(QPixmap(self.coverPath).scaled(
            200, 200, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        self.albumLabel.setText(self.album)
        self.contentLabel.setText(self.singer)
        self.playButton.setBlurPic(self.coverPath, 40)
        self.addToButton.setBlurPic(self.coverPath, 40)
        self.__adjustLabel()

    def __adjustLabel(self):
        """ 根据专辑名的长度决定是否换行和添加省略号 """
        newText, isWordWrap = autoWrap(self.albumLabel.text(), 22)
        if isWordWrap:
            # 添加省略号
            index = newText.index("\n")
            fontMetrics = QFontMetrics(QFont("Microsoft YaHei", 10, 75))
            secondLineText = fontMetrics.elidedText(
                newText[index + 1:], Qt.ElideRight, 200)
            newText = newText[: index + 1] + secondLineText
            self.albumLabel.setText(newText)

        # 给歌手名添加省略号
        fontMetrics = QFontMetrics(QFont("Microsoft YaHei", 10, 25))
        newSongerName = fontMetrics.elidedText(
            self.contentLabel.text(), Qt.ElideRight, 200)
        self.contentLabel.setText(newSongerName)
        self.contentLabel.adjustSize()
        self.albumLabel.adjustSize()

    def setChecked(self, isChecked: bool):
        """ 设置歌曲卡的选中状态 """
        self.checkBox.setChecked(isChecked)

    def setSelectionModeOpen(self, isOpen: bool):
        """ 设置是否进入选择模式, 处于选择模式下复选框一直可见，按钮不可见 """
        if self.isInSelectionMode == isOpen:
            return

        if isOpen:
            self.checkBoxOpacityEffect.setOpacity(1)
            self.checkBox.show()

        self.isInSelectionMode = isOpen

    def _onSelectActionTriggered(self):
        """ 右击菜单选择动作对应的槽函数 """
        self.setSelectionModeOpen(True)
        self.setChecked(True)

    def __showAddToMenu(self):
        """ 显示添加到菜单 """
        menu = AddToMenu(parent=self)
        pos = self.mapToGlobal(QPoint(
            self.addToButton.x(), self.addToButton.y()))
        x = pos.x() + self.addToButton.width() + 5
        y = pos.y() + int(
            self.addToButton.height() / 2 - (13 + 38 * menu.actionCount()) / 2)
        menu.playingAct.triggered.connect(
            lambda: self.addToPlayingSignal.emit(self.singer, self.album))
        menu.newPlaylistAct.triggered.connect(
            lambda: self.addAlbumToNewCustomPlaylistSig.emit(self.singer, self.album))
        menu.addSongsToPlaylistSig.connect(
            lambda name: self.addAlbumToCustomPlaylistSig.emit(name, self.singer, self.album))
        menu.exec(QPoint(x, y))

    def __onCheckedStateChanged(self):
        """ 复选框选中状态改变对应的槽函数 """
        self.isChecked = self.checkBox.isChecked()
        self.checkedStateChanged.emit(self, self.isChecked)
        # 更新属性和背景色
        self.setProperty("isChecked", str(self.isChecked))
        self.albumLabel.setProperty("isChecked", str(self.isChecked))
        self.contentLabel.setProperty("isChecked", str(self.isChecked))
        self.setStyle(QApplication.style())
