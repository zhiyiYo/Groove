# coding:utf-8

from copy import deepcopy

from PyQt5.QtCore import QEvent, QPoint, Qt, pyqtSignal
from PyQt5.QtGui import (QBrush, QColor, QContextMenuEvent, QFont,
                         QFontMetrics, QIcon, QMoveEvent, QPainter, QPen,
                         QPixmap)
from PyQt5.QtWidgets import (QAction, QApplication, QGraphicsOpacityEffect,
                             QLabel, QVBoxLayout, QWidget)

from my_dialog_box.album_info_edit_panel import AlbumInfoEditPanel
from my_functions.auto_wrap import autoWrap
from my_functions.get_pressed_pos import getPressedPos
from my_functions.is_not_leave import isNotLeave
from my_widget.blur_button import BlurButton
from my_widget.my_label import ClickableLabel
from my_widget.perspective_widget import PerspectiveWidget

from .album_card_context_menu import AlbumCardContextMenu
from .check_box import CheckBox


class AlbumCard(PerspectiveWidget):
    """ 定义包含专辑歌手名的窗口 """
    playSignal = pyqtSignal(list)
    nextPlaySignal = pyqtSignal(list)
    addToPlaylistSignal = pyqtSignal(list)
    switchToAlbumInterfaceSig = pyqtSignal(dict)
    saveAlbumInfoSig = pyqtSignal(dict, dict)
    updateAlbumInfoSig = pyqtSignal(dict, dict)
    checkedStateChanged = pyqtSignal(QWidget, bool)  # 发送 albumCard 和 isChecked
    showBlurAlbumBackgroundSig = pyqtSignal(QPoint, str)  # 发送专辑卡全局坐标
    hideBlurAlbumBackgroundSig = pyqtSignal()

    def __init__(self, albumInfo: dict, parent):
        super().__init__(parent)
        self.albumInfo = albumInfo
        self.songInfo_list = self.albumInfo.get('songInfo_list')  # type:list
        self.picPath = self.albumInfo.get('cover_path')           # type:str
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
        self.albumNameLabel = ClickableLabel(self.albumInfo['album'], self)
        self.songerNameLabel = ClickableLabel(self.albumInfo['songer'], self)
        # 实例化封面和按钮
        self.albumPic = QLabel(self)
        self.playButton = BlurButton(
            self, (37, 71), r'resource\images\album_tab_interface\播放按钮_70_70.png', self.picPath)
        self.addToButton = BlurButton(
            self, (109, 71), r'resource\images\album_tab_interface\添加到按钮_70_70.png', self.picPath)
        # 创建复选框
        self.checkBox = CheckBox(self, forwardTargetWidget=self.albumPic)
        # 创建动画和窗口特效
        self.checkBoxOpacityEffect = QGraphicsOpacityEffect(self)

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedSize(210, 290)
        self.setAttribute(Qt.WA_StyledBackground)
        self.albumPic.setFixedSize(200, 200)
        self.albumPic.setPixmap(QPixmap(self.picPath).scaled(
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
        self.setObjectName('albumCard')
        self.albumNameLabel.setObjectName('albumName')
        self.songerNameLabel.setObjectName('songerName')
        self.setProperty('isChecked', 'False')
        self.albumNameLabel.setProperty('isChecked', 'False')
        self.songerNameLabel.setProperty('isChecked', 'False')
        # 将信号连接到槽函数
        self.playButton.clicked.connect(
            lambda: self.playSignal.emit(self.albumInfo['songInfo_list']))
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
        self.showBlurAlbumBackgroundSig.emit(albumCardPos, self.picPath)
        # 处于选择模式下按钮不可见
        if not self.isInSelectionMode:
            self.addToButton.show()
            self.playButton.show()

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
            lambda: self.playSignal.emit(self.albumInfo['songInfo_list']))
        menu.nextToPlayAct.triggered.connect(
            lambda: self.nextPlaySignal.emit(self.albumInfo['songInfo_list']))
        menu.addToMenu.playingAct.triggered.connect(
            lambda: self.addToPlaylistSignal.emit(self.albumInfo['songInfo_list']))
        menu.editInfoAct.triggered.connect(self.showAlbumInfoEditPanel)
        menu.selectAct.triggered.connect(self.__selectActSlot)
        menu.exec(event.globalPos())

    def __adjustLabel(self):
        """ 根据专辑名的长度决定是否换行和添加省略号 """
        newText, isWordWrap = autoWrap(self.albumNameLabel.text(), 22)
        if isWordWrap:
            # 添加省略号
            index = newText.index('\n')
            fontMetrics = QFontMetrics(QFont('Microsoft YaHei', 10, 75))
            secondLineText = fontMetrics.elidedText(
                newText[index + 1:], Qt.ElideRight, 200)
            newText = newText[: index + 1] + secondLineText
            self.albumNameLabel.setText(newText)
        # 给歌手名添加省略号
        fontMetrics = QFontMetrics(QFont('Microsoft YaHei', 10, 25))
        newSongerName = fontMetrics.elidedText(
            self.songerNameLabel.text(), Qt.ElideRight, 200)
        self.songerNameLabel.setText(newSongerName)
        self.songerNameLabel.adjustSize()
        self.albumNameLabel.adjustSize()
        self.songerNameLabel.move(
            5, self.albumNameLabel.y() + self.albumNameLabel.height()-4)

    def __setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\albumCard.qss', 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def mouseReleaseEvent(self, e):
        """ 鼠标松开发送切换到专辑界面信号或者取反选中状态 """
        super().mouseReleaseEvent(e)
        if e.button() == Qt.LeftButton:
            if self.isInSelectionMode:
                self.setChecked(not self.isChecked)
            else:
                # 不处于选择模式时且鼠标松开事件不是复选框发来的才发送切换到专辑界面的信号
                self.switchToAlbumInterfaceSig.emit(self.albumInfo)

    def updateWindow(self, oldAlbumInfo: dict, newAlbumInfo: dict):
        """ 更新专辑卡窗口信息 """
        self.albumInfo = newAlbumInfo
        self.songInfo_list = self.albumInfo['songInfo_list']
        self.picPath = newAlbumInfo['cover_path']
        self.albumPic.setPixmap(QPixmap(self.picPath).scaled(
            200, 200, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        self.albumNameLabel.setText(newAlbumInfo['album'])
        self.songerNameLabel.setText(newAlbumInfo['songer'])
        self.playButton.setBlurPic(newAlbumInfo['cover_path'], 26)
        self.addToButton.setBlurPic(newAlbumInfo['cover_path'], 26)
        self.__adjustLabel()
        # 同时更新专辑列表的信息
        self.updateAlbumInfoSig.emit(oldAlbumInfo, newAlbumInfo)

    def showAlbumInfoEditPanel(self):
        """ 显示专辑信息编辑面板 """
        oldAlbumInfo = deepcopy(self.albumInfo)
        infoEditPanel = AlbumInfoEditPanel(self.albumInfo, self.window())
        infoEditPanel.saveInfoSig.connect(
            lambda newAlbumInfo: self.__saveAlbumInfoSlot(oldAlbumInfo, newAlbumInfo))
        infoEditPanel.setStyle(QApplication.style())
        infoEditPanel.exec_()

    def __sortAlbum(self, songInfo):
        """ 以曲序为基准排序歌曲卡 """
        trackNum = songInfo['tracknumber']  # type:str
        # 处理m4a
        if not trackNum[0].isnumeric():
            return eval(trackNum)[0]
        return int(trackNum)

    def __saveAlbumInfoSlot(self, oldAlbumInfo: dict, newAlbumInfo: dict):
        """ 保存专辑信息并更新界面 """
        newAlbumInfo_copy = deepcopy(newAlbumInfo)
        self.albumInfo['songInfo_list'].sort(key=self.__sortAlbum)
        self.updateWindow(oldAlbumInfo, newAlbumInfo)
        self.saveAlbumInfoSig.emit(oldAlbumInfo, newAlbumInfo_copy)

    def __checkedStateChangedSlot(self):
        """ 复选框选中状态改变对应的槽函数 """
        self.isChecked = self.checkBox.isChecked()
        # 发送信号
        self.checkedStateChanged.emit(self, self.isChecked)
        # 更新属性和背景色
        self.setProperty('isChecked', str(self.isChecked))
        self.albumNameLabel.setProperty('isChecked', str(self.isChecked))
        self.songerNameLabel.setProperty('isChecked', str(self.isChecked))
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
