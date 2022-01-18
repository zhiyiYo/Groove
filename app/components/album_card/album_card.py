# coding:utf-8
from common.auto_wrap import autoWrap
from components.buttons.blur_button import BlurButton
from components.widgets.check_box import CheckBox
from components.widgets.label import ClickableLabel
from components.widgets.menu import AddToMenu, DWMMenu
from components.widgets.perspective_widget import PerspectiveWidget
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent, QFont, QFontMetrics, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QGraphicsOpacityEffect,
                             QLabel, QWidget, QVBoxLayout)


class AlbumCard(PerspectiveWidget):
    """ 定义包含专辑歌手名的窗口 """

    playSignal = pyqtSignal(list)                           # 播放专辑
    deleteCardSig = pyqtSignal(str)                         # 删除专辑卡
    nextPlaySignal = pyqtSignal(list)                       # 下一首播放
    addToPlayingSignal = pyqtSignal(list)                   # 将专辑添加到正在播放
    checkedStateChanged = pyqtSignal(QWidget, bool)         # 选中状态改变
    switchToSingerInterfaceSig = pyqtSignal(str)            # 切换到歌手界面
    switchToAlbumInterfaceSig = pyqtSignal(str, str)        # 切换到专辑界面
    addAlbumToNewCustomPlaylistSig = pyqtSignal(list)       # 将专辑添加到新建的播放列表
    addAlbumToCustomPlaylistSig = pyqtSignal(str, list)     # 将专辑添加到已存在的自定义播放列表
    showAlbumInfoEditDialogSig = pyqtSignal(dict)           # 显示专辑信息面板信号
    showBlurAlbumBackgroundSig = pyqtSignal(QPoint, str)    # 显示磨砂背景
    hideBlurAlbumBackgroundSig = pyqtSignal()               # 隐藏磨砂背景

    def __init__(self, albumInfo: dict, parent):
        super().__init__(parent, True)
        self.__getAlbumInfo(albumInfo)
        # 初始化标志位
        self.isChecked = False
        self.isInSelectionMode = False
        # 创建小部件
        self.__createWidgets()
        # 初始化
        self.__initWidget()

    def __createWidgets(self):
        """ 创建小部件 """
        self.vBoxLayout = QVBoxLayout(self)
        # 实例化专辑名和歌手名
        self.albumNameLabel = ClickableLabel(self.albumName, self)
        self.contentLabel = ClickableLabel(self.singerName, self, False)
        # 实例化封面和按钮
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
        # 创建复选框
        self.checkBox = CheckBox(self, forwardTargetWidget=self.albumPic)
        # 创建动画和窗口特效
        self.checkBoxOpacityEffect = QGraphicsOpacityEffect(self)

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedSize(210, 290)
        self.setAttribute(Qt.WA_StyledBackground)
        self.albumPic.setFixedSize(200, 200)
        self.contentLabel.setFixedWidth(210)
        self.albumNameLabel.setFixedWidth(210)
        self.playButton.move(35, 70)
        self.addToButton.move(105, 70)
        self.albumPic.setPixmap(QPixmap(self.coverPath).scaled(
            200, 200, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        # 给小部件添加特效
        self.checkBox.setGraphicsEffect(self.checkBoxOpacityEffect)
        # 隐藏按钮
        self.playButton.hide()
        self.addToButton.hide()
        # 设置鼠标光标
        self.contentLabel.setCursor(Qt.PointingHandCursor)
        # 设置部件位置
        self.__initLayout()
        # 分配ID和属性
        self.setObjectName("albumCard")
        self.albumNameLabel.setObjectName("albumNameLabel")
        self.contentLabel.setObjectName("contentLabel")
        self.setProperty("isChecked", "False")
        self.albumNameLabel.setProperty("isChecked", "False")
        self.contentLabel.setProperty("isChecked", "False")
        # 将信号连接到槽函数
        self.playButton.clicked.connect(
            lambda: self.playSignal.emit(self.songInfo_list))
        self.contentLabel.clicked.connect(
            lambda: self.switchToSingerInterfaceSig.emit(self.singerName))
        self.addToButton.clicked.connect(self.__showAddToMenu)
        self.checkBox.stateChanged.connect(self.__checkedStateChangedSlot)

    def __initLayout(self):
        """ 初始化布局 """
        self.vBoxLayout.setContentsMargins(5, 5, 0, 0)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addWidget(self.albumPic)
        self.vBoxLayout.addSpacing(11)
        self.vBoxLayout.addWidget(self.albumNameLabel)
        self.vBoxLayout.addSpacing(2)
        self.vBoxLayout.addWidget(self.contentLabel)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.checkBox.move(178, 8)
        self.checkBox.hide()
        self.__adjustLabel()

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
        # 隐藏磨砂背景
        self.hideBlurAlbumBackgroundSig.emit()
        self.addToButton.hide()
        self.playButton.hide()

    def contextMenuEvent(self, event: QContextMenuEvent):
        """ 显示右击菜单 """
        menu = AlbumCardContextMenu(parent=self)
        menu.playAct.triggered.connect(
            lambda: self.playSignal.emit(self.songInfo_list))
        menu.nextToPlayAct.triggered.connect(
            lambda: self.nextPlaySignal.emit(self.songInfo_list))
        menu.deleteAct.triggered.connect(
            lambda: self.deleteCardSig.emit(self.albumName))
        menu.editInfoAct.triggered.connect(self.showAlbumInfoEditDialog)
        menu.selectAct.triggered.connect(self.__selectActSlot)
        menu.showSingerAct.triggered.connect(
            lambda: self.switchToSingerInterfaceSig.emit(self.singerName))

        menu.addToMenu.playingAct.triggered.connect(
            lambda: self.addToPlayingSignal.emit(self.songInfo_list))
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addAlbumToCustomPlaylistSig.emit(name, self.songInfo_list))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: self.addAlbumToNewCustomPlaylistSig.emit(self.songInfo_list))

        menu.exec(event.globalPos())

    def __adjustLabel(self):
        """ 根据专辑名的长度决定是否换行和添加省略号 """
        newText, isWordWrap = autoWrap(self.albumNameLabel.text(), 22)
        if isWordWrap:
            # 添加省略号
            index = newText.index("\n")
            fontMetrics = QFontMetrics(QFont("Microsoft YaHei", 10, 75))
            secondLineText = fontMetrics.elidedText(
                newText[index + 1:], Qt.ElideRight, 200)
            newText = newText[: index + 1] + secondLineText
            self.albumNameLabel.setText(newText)

        # 给歌手名添加省略号
        fontMetrics = QFontMetrics(QFont("Microsoft YaHei", 10, 25))
        newSongerName = fontMetrics.elidedText(
            self.contentLabel.text(), Qt.ElideRight, 200)
        self.contentLabel.setText(newSongerName)
        self.contentLabel.adjustSize()
        self.albumNameLabel.adjustSize()

    def mouseReleaseEvent(self, e):
        """ 鼠标松开发送切换到专辑界面信号或者取反选中状态 """
        super().mouseReleaseEvent(e)
        if e.button() == Qt.LeftButton:
            if self.isInSelectionMode:
                self.setChecked(not self.isChecked)
            else:
                # 不处于选择模式时且鼠标松开事件不是复选框发来的才发送切换到专辑界面的信号
                self.switchToAlbumInterfaceSig.emit(
                    self.albumName, self.singerName)

    def updateWindow(self, newAlbumInfo: dict):
        """ 更新专辑卡窗口信息 """
        if newAlbumInfo == self.albumInfo:
            return
        self.__getAlbumInfo(newAlbumInfo)
        self.albumPic.setPixmap(QPixmap(self.coverPath).scaled(
            200, 200, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        self.albumNameLabel.setText(self.albumName)
        self.contentLabel.setText(self.singerName)
        self.playButton.setBlurPic(self.coverPath, 40)
        self.addToButton.setBlurPic(self.coverPath, 40)
        self.__adjustLabel()

    def __getAlbumInfo(self, albumInfo: dict):
        """ 获取专辑信息 """
        self.albumInfo = albumInfo
        self.songInfo_list = self.albumInfo.get("songInfo_list", [])
        self.albumName = albumInfo.get("album", self.tr("Unknown album"))
        self.singerName = albumInfo.get("singer", self.tr("Unknown artist"))
        self.year = albumInfo.get('year', self.tr('Unknown year'))
        self.coverPath = albumInfo.get(
            "coverPath", ":/images/default_covers/album_200_200.png")

    def showAlbumInfoEditDialog(self):
        """ 显示专辑信息编辑面板 """
        self.showAlbumInfoEditDialogSig.emit(self.albumInfo)

    def updateAlbumCover(self, coverPath: str):
        """ 更新专辑封面 """
        self.coverPath = coverPath
        self.albumPic.setPixmap(
            QPixmap(self.coverPath).scaled(
                200, 200, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        self.playButton.setBlurPic(coverPath, 40)
        self.addToButton.setBlurPic(coverPath, 40)

    def __checkedStateChangedSlot(self):
        """ 复选框选中状态改变对应的槽函数 """
        self.isChecked = self.checkBox.isChecked()
        # 发送信号
        self.checkedStateChanged.emit(self, self.isChecked)
        # 更新属性和背景色
        self.setProperty("isChecked", str(self.isChecked))
        self.albumNameLabel.setProperty("isChecked", str(self.isChecked))
        self.contentLabel.setProperty("isChecked", str(self.isChecked))
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

    def __selectActSlot(self):
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
            lambda: self.addToPlayingSignal.emit(self.songInfo_list))
        menu.newPlaylistAct.triggered.connect(
            lambda: self.addAlbumToNewCustomPlaylistSig.emit(self.songInfo_list))
        menu.addSongsToPlaylistSig.connect(
            lambda name: self.addAlbumToCustomPlaylistSig.emit(name, self.songInfo_list))
        menu.exec(QPoint(x, y))


class AlbumCardContextMenu(DWMMenu):
    """ 专辑卡右击菜单"""

    def __init__(self, parent):
        super().__init__("", parent)
        # self.setFixedWidth(173)
        # 创建动作
        self.__createActions()
        self.setObjectName("albumCardContextMenu")
        self.setQss()

    def __createActions(self):
        """ 创建动作 """
        # 创建动作
        self.playAct = QAction(self.tr("Play"), self)
        self.selectAct = QAction(self.tr("Select"), self)
        self.nextToPlayAct = QAction(self.tr("Play next"), self)
        self.pinToStartMenuAct = QAction(self.tr('Pin to Start'), self)
        self.deleteAct = QAction(self.tr("Delete"), self)
        self.editInfoAct = QAction(self.tr("Edit info"), self)
        self.showSingerAct = QAction(self.tr("Show artist"), self)
        self.addToMenu = AddToMenu(self.tr("Add to"), self)

        # 添加动作到菜单
        self.addActions([self.playAct, self.nextToPlayAct])
        # 将子菜单添加到主菜单
        self.addMenu(self.addToMenu)
        self.addActions(
            [
                self.showSingerAct,
                self.pinToStartMenuAct,
                self.editInfoAct,
                self.deleteAct,
            ]
        )
        self.addSeparator()
        self.addAction(self.selectAct)
