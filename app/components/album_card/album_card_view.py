# coding:utf-8
from typing import List

from common.database.entity import AlbumInfo
from common.library import Library
from common.thread.save_album_info_thread import SaveAlbumInfoThread
from components.dialog_box.album_info_edit_dialog import AlbumInfoEditDialog
from components.dialog_box.message_dialog import MessageDialog
from components.layout.grid_layout import GridLayout
from components.widgets.label import ClickableLabel
from PyQt5.QtCore import (QParallelAnimationGroup, QPoint, QPropertyAnimation,
                          Qt, pyqtSignal)
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QWidget

from .album_blur_background import AlbumBlurBackground
from .album_card import AlbumCardBase, AlbumCardFactory, AlbumCardType


class AlbumCardViewBase(QWidget):
    """ 专辑卡视图基类 """

    playSig = pyqtSignal(str, str)                         # 播放
    nextPlaySig = pyqtSignal(list)                         # 下一首播放
    deleteAlbumSig = pyqtSignal(str, str)                  # 删除专辑
    addAlbumToPlayingSig = pyqtSignal(list)                # 添加到正在播放
    addAlbumToNewCustomPlaylistSig = pyqtSignal(list)      # 添加到新建的播放列表
    addAlbumToCustomPlaylistSig = pyqtSignal(str, list)    # 添加到自定义播放列表
    checkedStateChanged = pyqtSignal(AlbumCardBase, bool)  # 专辑卡选中状态改变
    switchToSingerInterfaceSig = pyqtSignal(str)           # 切换到歌手界面
    switchToAlbumInterfaceSig = pyqtSignal(str, str)       # 切换到专辑界面
    showBlurAlbumBackgroundSig = pyqtSignal(QPoint, str)   # 显示磨砂背景
    hideBlurAlbumBackgroundSig = pyqtSignal()              # 隐藏磨砂背景

    def __init__(self, library: Library, albumInfos: List[AlbumInfo], cardType: AlbumCardType, create=True, parent=None):
        """
        Parameters
        ----------
        library: Library
            歌曲库

        albumInfos: List[AlbumInfo]
            专辑信息列表

        cardType: AlbumCardType
            专辑卡类型

        create: bool
            是否直接创建歌曲卡

        parent:
            父级窗口
        """
        super().__init__(parent=parent)
        self.library = library
        self.albumInfos = albumInfos
        self.cardType = cardType
        self.albumCards = []  # type:List[AlbumCardBase]
        self.hideCheckBoxAniGroup = QParallelAnimationGroup(self)
        self.hideCheckBoxAniGroup.finished.connect(self.__hideAllCheckBox)

        if create:
            for albumInfo in self.albumInfos:
                self.__createAlbumCard(albumInfo)
                QApplication.processEvents()

    def __createAlbumCard(self, albumInfo: AlbumInfo):
        """ 创建一个专辑卡 """
        card = AlbumCardFactory.create(self.cardType, albumInfo, self)
        self.hideCheckBoxAniGroup.addAnimation(card.hideCheckBoxAni)

        # 信号连接到槽
        self._connectCardSignalToSlot(card)

    def setAlbumCards(self, albumCards: List[AlbumCardBase]):
        """ 设置视图中的专辑卡 """
        raise NotImplementedError

    def _connectCardSignalToSlot(self, card: AlbumCardBase):
        """ 将专辑卡信号连接到槽函数 """
        card.playSignal.connect(self.playSig)
        card.deleteCardSig.connect(self.__showDeleteCardDialog)
        card.showAlbumInfoEditDialogSig.connect(self.__showAlbumInfoEditDialog)
        card.switchToAlbumInterfaceSig.connect(self.switchToAlbumInterfaceSig)
        card.nextPlaySignal.connect(
            lambda s, a: self.nextPlaySig.emit(self.__getAlbumSongInfos(s, a)))
        card.addToPlayingSignal.connect(
            lambda s, a: self.addAlbumToPlayingSig.emit(self.__getAlbumSongInfos(s, a)))
        card.addAlbumToCustomPlaylistSig.connect(
            lambda n, s, a: self.addAlbumToCustomPlaylistSig.emit(n, self.__getAlbumSongInfos(s, a)))
        card.addAlbumToNewCustomPlaylistSig.connect(
            lambda s, a: self.addAlbumToNewCustomPlaylistSig.emit(self.__getAlbumSongInfos(s, a)))
        card.checkedStateChanged.connect(self.checkedStateChanged)
        card.showBlurAlbumBackgroundSig.connect(
            self.showBlurAlbumBackgroundSig)
        card.hideBlurAlbumBackgroundSig.connect(
            self.hideBlurAlbumBackgroundSig)
        card.switchToSingerInterfaceSig.connect(
            self.switchToSingerInterfaceSig)

    def __getAlbumSongInfos(self, singer: str, album: str):
        """ 获取一张专辑的歌曲信息列表 """
        albumInfo = self.library.albumInfoController.getAlbumInfo(
            singer, album)
        if not albumInfo:
            return []

        return albumInfo.songInfos

    def __showDeleteCardDialog(self, singer: str, album: str):
        """ 显示删除一张专辑对话框 """
        title = self.tr("Are you sure you want to delete this?")
        content = self.tr("If you delete") + f' "{album}" ' + \
            self.tr("it won't be on be this device anymore.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(lambda: self.deleteAlbumSig.emit(singer, album))
        w.exec_()

    def __showAlbumInfoEditDialog(self, singer: str, album: str):
        """ 显示专辑信息编辑界面信号 """
        albumInfo = self.library.albumInfoController.getAlbumInfo(
            singer, album)
        if not albumInfo:
            return

        # 创建线程和对话框
        thread = SaveAlbumInfoThread(self)
        w = AlbumInfoEditDialog(albumInfo, self.window())

        # 信号连接到槽
        w.saveInfoSig.connect(thread.setAlbumInfo)
        w.saveInfoSig.connect(thread.start)
        thread.saveFinishedSignal.connect(w.onSaveComplete)
        thread.saveFinishedSignal.connect(self.__onSaveAlbumInfoFinished)

        # 显示对话框
        w.setStyle(QApplication.style())
        w.exec_()

    def __hideAllCheckBox(self):
        """ 隐藏所有复选框 """
        for albumCard in self.albumCards:
            albumCard.checkBox.hide()

    def __onSaveAlbumInfoFinished(self, oldAlbumInfo: AlbumInfo, newAlbumInfo: AlbumInfo, coverPath: str):
        """ 保存专辑信息槽函数 """
        # 删除线程
        self.sender().quit()
        self.sender().wait()
        self.sender().deleteLater()

        # TODO:更新所有专辑卡并发送信号
        self.updateOneAlbumInfo(oldAlbumInfo, newAlbumInfo, coverPath)

    # TODO:使用数据库来更新
    def updateOneAlbumInfo(self, oldAlbumInfo: AlbumInfo, newAlbumInfo: AlbumInfo, coverPath: str):
        """ 更新一张专辑信息 """


class GridAlbumCardView(AlbumCardViewBase):
    """ 网格布局专辑卡视图 """

    titleClicked = pyqtSignal()

    def __init__(self, library: Library, albumInfos: List[AlbumInfo], cardType: AlbumCardType,
                 title: str = None, create=True, parent=None):
        """
        Parameters
        ----------
        library: Library
            歌曲库

        albumInfos: List[AlbumInfo]
            专辑信息列表

        cardType: AlbumCardType
            专辑卡类型

        title: str
            标题

        create: bool
            是否立即创建专辑卡

        parent:
            父级窗口
        """
        super().__init__(library, albumInfos, cardType, create, parent)
        self.column = 5
        self.title = title or ''
        self.titleLabel = ClickableLabel(self.title, self)
        self.gridLayout = GridLayout(self)
        self.gridLayout.setVerticalSpacing(20)
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setAlignment(Qt.AlignLeft)
        self.gridLayout.setContentsMargins(0, 45*bool(self.title), 0, 0)

        self.titleLabel.setVisible(bool(self.title))
        self.titleLabel.move(8, 6)
        self.titleLabel.clicked.connect(self.titleClicked)
        self.titleLabel.setStyleSheet(
            "font: 22px 'Segoe UI Semilight', 'Microsoft YaHei Light'; font-weight: bold; color: rgb(0, 153, 188)")
        self.titleLabel.adjustSize()

        if create:
            self.__addAlbumCardsToLayout()

        self.resize(1255, 300)

    def __addAlbumCardsToLayout(self):
        """ 将所有专辑卡添加到布局 """
        for i, card in enumerate(self.albumCards):
            row = i//self.column
            column = i-row*self.column
            self.gridLayout.addWidget(card, row, column)
            QApplication.processEvents()

    def setAlbumCards(self, albumCards: List[AlbumCardBase]):
        self.albumCards = albumCards
        self.albumInfos = [i.albumInfo for i in albumCards]

        self.hideCheckBoxAniGroup.clear()
        for card in self.albumCards:
            self.hideCheckBoxAniGroup.addAnimation(card.hideCheckBoxAni)
            self._connectCardSignalToSlot(card)

        self.__addAlbumCardsToLayout()

    def resizeEvent(self, e):
        column = 2 if self.width() <= 670 else (self.width()-670)//220+3
        if self.column == column:
            return

        self.column = column
        self.gridLayout.updateColumnNum(column, 210, 290)
