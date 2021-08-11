# coding:utf-8
from copy import deepcopy

from app.common.auto_wrap import autoWrap
from app.components.buttons.blur_button import BlurButton
from app.components.check_box import CheckBox
from app.components.dialog_box.album_info_edit_dialog import \
    AlbumInfoEditDialog
from app.components.label import ClickableLabel
from app.components.menu import AddToMenu, DWMMenu
from app.components.perspective_widget import PerspectiveWidget
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent, QFont, QFontMetrics, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QGraphicsOpacityEffect,
                             QLabel, QWidget)


class AlbumCard(PerspectiveWidget):
    """ 定义包含专辑歌手名的窗口 """

    playSignal = pyqtSignal(list)
    deleteCardSig = pyqtSignal(str)
    nextPlaySignal = pyqtSignal(list)
    addToPlayingSignal = pyqtSignal(list)  # 将专辑添加到正在播放
    hideBlurAlbumBackgroundSig = pyqtSignal()
    editAlbumInfoSignal = pyqtSignal(dict, dict)
    switchToAlbumInterfaceSig = pyqtSignal(str, str)  # albumName, songerName
    checkedStateChanged = pyqtSignal(QWidget, bool)
    addAlbumToNewCustomPlaylistSig = pyqtSignal(list)  # 将专辑添加到新建的播放列表
    addAlbumToCustomPlaylistSig = pyqtSignal(str, list)  # 将专辑添加到已存在的自定义播放列表
    showBlurAlbumBackgroundSig = pyqtSignal(QPoint, str)  # 发送专辑卡全局坐标
    showAlbumInfoEditPanelSig = pyqtSignal(AlbumInfoEditDialog)  # 发送显示专辑信息面板信号

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
        # 实例化专辑名和歌手名
        self.albumNameLabel = ClickableLabel(self.albumInfo["album"], self)
        self.songerNameLabel = ClickableLabel(self.albumInfo["songer"], self)
        # 实例化封面和按钮
        self.albumPic = QLabel(self)
        self.playButton = BlurButton(
            self,
            (30, 65),
            r"app\resource\images\album_tab_interface\Play.png",
            self.coverPath,
        )
        self.addToButton = BlurButton(
            self,
            (100, 65),
            r"app\resource\images\album_tab_interface\Add.png",
            self.coverPath,
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
        self.songerNameLabel.setCursor(Qt.PointingHandCursor)
        # 设置部件位置
        self.__initLayout()
        # 分配ID和属性
        self.setObjectName("albumCard")
        self.albumNameLabel.setObjectName("albumName")
        self.songerNameLabel.setObjectName("songerName")
        self.setProperty("isChecked", "False")
        self.albumNameLabel.setProperty("isChecked", "False")
        self.songerNameLabel.setProperty("isChecked", "False")
        # 将信号连接到槽函数
        self.playButton.clicked.connect(
            lambda: self.playSignal.emit(self.songInfo_list)
        )
        self.addToButton.clicked.connect(self.__showAddToMenu)
        self.checkBox.stateChanged.connect(self.__checkedStateChangedSlot)

    def __initLayout(self):
        """ 初始化布局 """
        self.albumPic.move(5, 5)
        self.albumNameLabel.move(5, 213)
        self.songerNameLabel.move(5, 239)
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
        # 创建菜单
        menu = AlbumCardContextMenu(parent=self)
        menu.playAct.triggered.connect(
            lambda: self.playSignal.emit(self.songInfo_list))
        menu.nextToPlayAct.triggered.connect(
            lambda: self.nextPlaySignal.emit(self.songInfo_list))
        menu.addToMenu.playingAct.triggered.connect(
            lambda: self.addToPlayingSignal.emit(self.songInfo_list))
        menu.editInfoAct.triggered.connect(self.showAlbumInfoEditPanel)
        menu.selectAct.triggered.connect(self.__selectActSlot)
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addAlbumToCustomPlaylistSig.emit(name, self.songInfo_list))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: self.addAlbumToNewCustomPlaylistSig.emit(self.songInfo_list))
        menu.deleteAct.triggered.connect(
            lambda: self.deleteCardSig.emit(self.albumName))
        menu.exec(event.globalPos())

    def __adjustLabel(self):
        """ 根据专辑名的长度决定是否换行和添加省略号 """
        newText, isWordWrap = autoWrap(self.albumNameLabel.text(), 22)
        if isWordWrap:
            # 添加省略号
            index = newText.index("\n")
            fontMetrics = QFontMetrics(QFont("Microsoft YaHei", 10, 75))
            secondLineText = fontMetrics.elidedText(
                newText[index + 1:], Qt.ElideRight, 200
            )
            newText = newText[: index + 1] + secondLineText
            self.albumNameLabel.setText(newText)
        # 给歌手名添加省略号
        fontMetrics = QFontMetrics(QFont("Microsoft YaHei", 10, 25))
        newSongerName = fontMetrics.elidedText(
            self.songerNameLabel.text(), Qt.ElideRight, 200
        )
        self.songerNameLabel.setText(newSongerName)
        self.songerNameLabel.adjustSize()
        self.albumNameLabel.adjustSize()
        self.songerNameLabel.move(
            5, self.albumNameLabel.y() + self.albumNameLabel.height() - 4
        )

    def mouseReleaseEvent(self, e):
        """ 鼠标松开发送切换到专辑界面信号或者取反选中状态 """
        super().mouseReleaseEvent(e)
        if e.button() == Qt.LeftButton:
            if self.isInSelectionMode:
                self.setChecked(not self.isChecked)
            else:
                # 不处于选择模式时且鼠标松开事件不是复选框发来的才发送切换到专辑界面的信号
                self.switchToAlbumInterfaceSig.emit(
                    self.albumName, self.songerName)

    def updateWindow(self, newAlbumInfo: dict):
        """ 更新专辑卡窗口信息 """
        if newAlbumInfo == self.albumInfo:
            return
        self.__getAlbumInfo(newAlbumInfo)
        self.albumPic.setPixmap(QPixmap(self.coverPath).scaled(
            200, 200, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        self.albumNameLabel.setText(self.albumName)
        self.songerNameLabel.setText(self.songerName)
        self.playButton.setBlurPic(self.coverPath, 40)
        self.addToButton.setBlurPic(self.coverPath, 40)
        self.__adjustLabel()

    def __getAlbumInfo(self, albumInfo: dict):
        """ 获取专辑信息 """
        self.albumInfo = albumInfo
        self.songInfo_list = self.albumInfo.get("songInfo_list", [])
        self.albumName = albumInfo.get("album", "未知专辑")     # type:str
        self.songerName = albumInfo.get("songer", "未知歌手")   # type:str
        self.coverPath = albumInfo.get(
            "coverPath", "app/resource/images/default_covers/默认专辑封面_200_200.png")

    def showAlbumInfoEditPanel(self):
        """ 显示专辑信息编辑面板 """
        oldAlbumInfo = deepcopy(self.albumInfo)
        infoEditPanel = AlbumInfoEditDialog(self.albumInfo, self.window())
        infoEditPanel.saveInfoSig.connect(
            lambda newAlbumInfo: self.__saveAlbumInfoSlot(
                oldAlbumInfo, newAlbumInfo)
        )
        self.showAlbumInfoEditPanelSig.emit(infoEditPanel)
        infoEditPanel.setStyle(QApplication.style())
        infoEditPanel.exec_()

    def __saveAlbumInfoSlot(self, oldAlbumInfo: dict, newAlbumInfo: dict):
        """ 保存专辑信息并更新界面 """
        newAlbumInfo_copy = deepcopy(newAlbumInfo)
        # self.updateWindow(newAlbumInfo)
        self.editAlbumInfoSignal.emit(oldAlbumInfo, newAlbumInfo_copy)
        self.albumInfo["songInfo_list"].sort(
            key=lambda songInfo: int(songInfo["tracknumber"])
        )
        # 更新专辑封面
        self.updateAlbumCover(newAlbumInfo["coverPath"])

    def updateAlbumCover(self, coverPath: str):
        """ 更新专辑封面 """
        self.coverPath = coverPath
        self.albumPic.setPixmap(
            QPixmap(self.coverPath).scaled(
                200, 200, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
        )
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
        self.songerNameLabel.setProperty("isChecked", str(self.isChecked))
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
        self.playAct = QAction("播放", self)
        self.selectAct = QAction("选择", self)
        self.nextToPlayAct = QAction("下一首播放", self)
        self.pinToStartMenuAct = QAction('固定到"开始"菜单', self)
        self.deleteAct = QAction("删除", self)
        self.editInfoAct = QAction("编辑信息", self)
        self.showSongerAct = QAction("显示歌手", self)
        self.addToMenu = AddToMenu("添加到", self)

        # 添加动作到菜单
        self.addActions([self.playAct, self.nextToPlayAct])
        # 将子菜单添加到主菜单
        self.addMenu(self.addToMenu)
        self.addActions(
            [
                self.showSongerAct,
                self.pinToStartMenuAct,
                self.editInfoAct,
                self.deleteAct,
            ]
        )
        self.addSeparator()
        self.addAction(self.selectAct)
