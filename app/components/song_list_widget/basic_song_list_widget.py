# coding:utf-8
from typing import List

from common.database.entity import SongInfo
from common.signal_bus import signalBus
from components.dialog_box.song_info_edit_dialog import SongInfoEditDialog
from components.dialog_box.song_property_dialog import SongPropertyDialog
from components.widgets.list_widget import ListWidget
from PyQt5.QtCore import QMargins, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QApplication, QListWidgetItem, QWidget

from .song_card import BasicSongCard, SongCardFactory
from .song_card_type import SongCardType


class BasicSongListWidget(ListWidget):
    """ 基本歌曲列表控件 """

    emptyChangedSig = pyqtSignal(bool)                   # 歌曲卡是否为空信号
    removeSongSignal = pyqtSignal(SongInfo)              # 刪除歌曲列表中的一首歌
    songCardNumChanged = pyqtSignal(int)                 # 歌曲数量发生改变
    checkedNumChanged = pyqtSignal(int, bool)            # 选中的歌曲卡数量发生改变

    def __init__(self, songInfos: List[SongInfo], songCardType: SongCardType, parent=None,
                 viewportMargins=QMargins(30, 0, 30, 0), paddingBottomHeight: int = 116):
        """
        Parameters
        ----------
        songInfos: List[SongInfo]
            歌曲信息列表

        songCardType: SongCardType
            歌曲卡类型

        parent:
            父级窗口

        viewportMargins: QMargins
            视口的外边距

        paddingBottomHeight: int
            列表视图底部留白，如果为 `0` 或者 `None` 则不添加留白
        """
        super().__init__(parent)
        self.__songCardType = songCardType
        self.paddingBottomHeight = paddingBottomHeight
        self.songInfos = songInfos if songInfos else []
        self.currentIndex = 0
        self.playingIndex = 0  # 正在播放的歌曲卡下标
        self.playingSongInfo = self.songInfos[0] if songInfos else None

        # 是否处于选择模式
        self.isInSelectionMode = False

        # 初始化列表
        self.item_list = []
        self.songCards = []
        self.checkedSongCards = []

        self.setAlternatingRowColors(True)
        self.setViewportMargins(viewportMargins)

    def createSongCards(self):
        """ 清空列表并创建新歌曲卡 """
        self.clearSongCards()
        for songInfo in self.songInfos:
            self.appendOneSongCard(songInfo)
            QApplication.processEvents()

        # 添加一个空白item来填补playBar所占高度
        self.__createPaddingBottomItem()

    def appendOneSongCard(self, songInfo: SongInfo):
        """ 在列表尾部添加一个歌曲卡，注意这不会改变歌曲信息列表

        Parameters
        ----------
        songInfo: SongInfo
            歌曲信息
        """
        item = QListWidgetItem()
        songCard = SongCardFactory.create(self.songCardType, songInfo)
        songCard.itemIndex = len(self.songCards)

        # 调整宽度
        margin = self.viewportMargins()
        size = QSize(self.width()-margin.left()-margin.right(), 60)
        QApplication.sendEvent(songCard, QResizeEvent(size, songCard.size()))
        QApplication.processEvents()
        songCard.resize(size)

        item.setSizeHint(QSize(songCard.width(), 60))

        self.addItem(item)
        self.setItemWidget(item, songCard)
        self.songCards.append(songCard)
        self.item_list.append(item)

        # 信号连接到槽
        self._connectSongCardSignalToSlot(songCard)

    def appendSongCards(self, songInfos: List[SongInfo]):
        """  在列表尾部添加一个歌曲卡，注意这不会改变歌曲信息列表

        Parameters
        ----------
        songInfos: List[SongInfo]
            歌曲信息列表
        """
        self.__removePaddingBottomItem()

        for songInfo in songInfos:
            self.appendOneSongCard(songInfo)

        self.__createPaddingBottomItem()

    def setCurrentIndex(self, index):
        """ 设置当前下标 """
        if not self.isInSelectionMode:
            # 不处于选择模式时将先前选中的歌曲卡设置为非选中状态
            if index != self.currentIndex:
                self.songCards[self.currentIndex].setSelected(False)
                self.songCards[index].setSelected(True)
        else:
            # 如果处于选中模式下点击了歌曲卡则取反选中的卡的选中状态
            songCard = self.songCards[index]
            songCard.setChecked(not songCard.isChecked)

        self.currentIndex = index

    def removeSongCard(self, index: int):
        """ 删除选中的一个歌曲卡 """
        songCard = self.songCards.pop(index)
        songCard.deleteLater()
        self.item_list.pop(index)
        self.songInfos.pop(index)
        self.takeItem(index)

        # 更新下标
        for i in range(index, len(self.songCards)):
            self.songCards[i].itemIndex = i

        if self.currentIndex >= index:
            self.currentIndex -= 1
            self.playingIndex -= 1

        # 发送信号
        self.songCardNumChanged.emit(len(self.songCards))
        self.update()

    def removeSongCards(self, songPaths: List[str]):
        """ 移除多个歌曲卡 """
        for songCard in self.songCards.copy():
            if songCard.songPath in songPaths:
                self.removeSongCard(songCard.itemIndex)

    def setPlay(self, index: int):
        """ 设置歌曲卡播放状态 """
        if not self.songCards:
            return

        self.songCards[self.currentIndex].setSelected(False)
        self.currentIndex = index
        self.songCards[self.playingIndex].setPlay(False)
        self.playingIndex = index  # 更新正在播放的下标
        if index >= 0:
            self.songCards[index].setPlay(True)
            self.playingSongInfo = self.songInfos[index]

    def setPlayBySongInfo(self, songInfo: SongInfo):
        """ 设置歌曲卡播放状态，如果指定的歌曲不在当前歌曲列表中，将正在播放的歌曲卡取消播放状态 """
        index = self.index(songInfo)
        if index is not None:
            self.setPlay(index)
        else:
            self.cancelPlayState()

    def cancelPlayState(self):
        """ 取消正在播放的歌曲卡的播放状态 """
        if not self.songCards or self.playingIndex is None:
            return

        self.songCards[self.playingIndex].setPlay(False)
        self.currentIndex = 0
        self.playingIndex = 0
        self.playingSongInfo = None

    def showSongPropertyDialog(self, songInfo: SongInfo = None):
        """ 显示选中的歌曲卡的属性 """
        if not songInfo:
            songInfo = self.currentSongInfo

        w = SongPropertyDialog(songInfo, self.window())
        w.exec_()

    def showSongInfoEditDialog(self, songInfo: SongInfo = None):
        """ 显示编辑歌曲信息面板 """
        if not songInfo:
            songInfo = self.currentSongInfo

        # 获取歌曲卡下标和歌曲信息
        w = SongInfoEditDialog(songInfo, self.window())
        w.saveInfoSig.connect(signalBus.editSongInfoSig)
        w.exec_()

    def updateOneSongCard(self, newSongInfo: SongInfo):
        """ 更新一个歌曲卡 """
        for i, songInfo in enumerate(self.songInfos):
            if songInfo.file == newSongInfo.file:
                self.songInfos[i] = newSongInfo
                self.songCards[i].updateSongCard(newSongInfo)

    def updateMultiSongCards(self, songInfos: list):
        """ 更新多个歌曲卡 """
        for songInfo in songInfos:
            self.updateOneSongCard(songInfo)

    def resizeEvent(self, e):
        """ 更新item的尺寸 """
        super().resizeEvent(e)

        margins = self.viewportMargins()  # type:QMargins
        size = QSize(self.width() - margins.left() - margins.right(), 60)
        for item in self.item_list:
            item.setSizeHint(size)

        if self.paddingBottomHeight:
            self.paddingBottomItem.setSizeHint(
                QSize(size.width(), self.paddingBottomHeight))

    def onSongCardCheckedStateChanged(self, itemIndex: int, isChecked: bool):
        """ 歌曲卡选中状态改变对应的槽函数 """
        songCard = self.songCards[itemIndex]

        N0 = len(self.checkedSongCards)

        if songCard not in self.checkedSongCards and isChecked:
            self.checkedSongCards.append(songCard)
        elif songCard in self.checkedSongCards and not isChecked:
            self.checkedSongCards.remove(songCard)
        else:
            return

        N1 = len(self.checkedSongCards)

        if N0 == 0 and N1 > 0:
            self.setCurrentIndex(itemIndex)
            self.__setAllSongCardSelectionModeOpen(True)
            self.isInSelectionMode = True
        elif N1 == 0:
            self.__setAllSongCardSelectionModeOpen(False)
            self.isInSelectionMode = False

        isAllChecked = N1 == len(self.songCards)
        self.checkedNumChanged.emit(N1, isAllChecked)

    def __setAllSongCardSelectionModeOpen(self, isOpen: bool):
        """ 设置所有歌曲卡是否进入选择模式 """
        cursor = Qt.ArrowCursor if isOpen else Qt.PointingHandCursor

        for songCard in self.songCards:
            songCard.setSelectionModeOpen(isOpen)
            songCard.setClickableLabelCursor(cursor)

    def setAllChecked(self, isChecked: bool):
        """ 设置所有的歌曲卡checked状态 """
        for songCard in self.songCards:
            songCard.setChecked(isChecked)

    def uncheckAll(self):
        """ 取消所有已处于选中状态的歌曲卡的选中状态 """
        for songCard in self.checkedSongCards.copy():
            songCard.setChecked(False)

    def updateAllSongCards(self, songInfos: List[SongInfo]):
        """ 更新所有歌曲卡

        Parameters
        ----------
        songInfos: List[SongInfo]
            歌曲信息列表
        """
        # 删除旧占位行
        self.__removePaddingBottomItem()

        # 取消当前歌曲卡播放状态
        if self.songCards:
            self.songCards[self.currentIndex].setPlay(False)

        # 长度相等就更新信息，不相等创建或者删除 item
        newSongNum = len(songInfos)
        oldSongNum = len(self.songCards)
        if newSongNum > oldSongNum:
            # 添加item
            for songInfo in songInfos[oldSongNum:]:
                self.appendOneSongCard(songInfo)
                QApplication.processEvents()

        elif newSongNum < oldSongNum:
            # 删除多余的item
            for i in range(oldSongNum - 1, newSongNum - 1, -1):
                self.item_list.pop()
                songCard = self.songCards.pop()
                songCard.deleteLater()
                self.takeItem(i)
                QApplication.processEvents()

        # 当两个列表是否为空的的布尔值不同时发送歌曲卡列表是否为空信号
        if not (bool(self.songInfos) and bool(songInfos)):
            self.emptyChangedSig.emit(not bool(songInfos))

        # 更新部分歌曲卡
        self.songInfos = songInfos
        n = min(oldSongNum, newSongNum)
        for songInfo, songCard in zip(songInfos[:n], self.songCards[:n]):
            songCard.updateSongCard(songInfo)

        # 更新样式和当前下标
        self.currentIndex = 0
        self.playingIndex = 0
        self.playingSongInfo = None
        for songCard in self.songCards:
            songCard.setPlay(False)

        # 创建新占位行
        self.__createPaddingBottomItem()

        # 发出歌曲卡数量改变信号
        if oldSongNum != newSongNum:
            self.songCardNumChanged.emit(len(self.songInfos))

    def clearSongCards(self):
        """ 清空歌曲卡 """
        self.item_list.clear()
        self.clear()

        # 释放内存
        for songCard in self.songCards:
            songCard.deleteLater()

        self.songCards.clear()
        self.currentIndex = 0
        self.playingIndex = 0

    def sortSongInfo(self, key: str, isReverse=True):
        """ 依据指定的键排序歌曲信息列表

        Parameters
        ----------
        key: str
            排序依据，有 `createTime`、`title`、`singer` 和 `track` 四种

        isReverse: bool
            是否降序，只对前三种排序方式有效
        """
        if key != "track":
            songInfo = sorted(
                self.songInfos,
                key=lambda songInfo: songInfo[key],
                reverse=isReverse
            )
        else:
            songInfo = sorted(
                self.songInfos,
                key=lambda songInfo: songInfo.track
            )

        return songInfo

    def __createPaddingBottomItem(self):
        """ 创建底部占位行 """
        if not self.paddingBottomHeight:
            return

        self.paddingBottomItem = QListWidgetItem(self)

        # 创建占位窗口
        self.paddingBottomWidget = QWidget(self)
        self.paddingBottomWidget.setStyleSheet("background:white")
        self.paddingBottomWidget.setFixedHeight(self.paddingBottomHeight)

        # 将窗口加到Item中
        margins = self.viewportMargins()  # type:QMargins
        width = self.width() - margins.left() - margins.right()
        self.paddingBottomWidget.resize(width, self.paddingBottomHeight)
        self.paddingBottomItem.setSizeHint(
            QSize(width, self.paddingBottomHeight))
        self.setItemWidget(self.paddingBottomItem, self.paddingBottomWidget)
        self.addItem(self.paddingBottomItem)

    def __removePaddingBottomItem(self):
        """ 移除底部占位行 """
        if self.paddingBottomHeight:
            self.removeItemWidget(self.paddingBottomItem)
            self.takeItem(len(self.songCards))

    @property
    def songCardType(self) -> SongCardType:
        return self.__songCardType

    def _connectSongCardSignalToSlot(self, songCard):
        """ 将一个歌曲卡的信号连接到槽函数 """
        raise NotImplementedError

    def songCardNum(self) -> int:
        """ 返回歌曲卡数量 """
        return len(self.songCards)

    def index(self, songInfo: SongInfo):
        """ 获取歌曲信息的索引，如果歌曲信息不存在于列表中，则返回 None """
        if songInfo in self.songInfos:
            return self.songInfos.index(songInfo)

        return None

    @property
    def currentSongCard(self) -> BasicSongCard:
        """ 当前歌曲卡 """
        return self.songCards[self.currentRow()]

    @property
    def currentSongInfo(self) -> SongInfo:
        """ 当前选中的歌曲信息 """
        return self.currentSongCard.songInfo
