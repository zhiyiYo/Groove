import sys
from json import dump

from PyQt5.QtCore import QEvent, QPoint, QSize, Qt, pyqtSignal
from PyQt5.QtGui import (QBrush, QColor, QContextMenuEvent, QPainter,
                         QPixmap)
from PyQt5.QtWidgets import (QAction, QApplication, QLabel, QListWidgetItem,
                             QWidget)

from get_info.get_song_info import SongInfo
from my_dialog_box import PropertyPanel, SongInfoEditPanel
from my_widget.my_listWidget import ListWidget

from .song_card import SongCard
from .song_card_list_context_menu import SongCardListContextMenu


class SongCardListWidget(ListWidget):
    """ 定义一个歌曲卡列表视图 """

    playSignal = pyqtSignal(int)
    nextToPlaySignal = pyqtSignal(dict)
    removeItemSignal = pyqtSignal(int)
    addSongToPlaylistSignal = pyqtSignal(dict)
    editSongCardSignal = pyqtSignal(dict, dict)       # 编辑歌曲卡完成信号

    def __init__(self, songInfo_list: list, parent=None):
        super().__init__(parent)
        self.songInfo_list = songInfo_list if songInfo_list else []
        self.currentIndex = -1
        self.playingIndex = -1  # 正在播放的歌曲卡下标
        self.playingSongInfo = None
        if self.songInfo_list:
            self.playingSongInfo = self.songInfo_list[0]
        self.resize(1150, 758)
        # 初始化列表
        self.songCard_list = []
        self.item_list = []
        # 创建右击菜单
        self.contextMenu = SongCardListContextMenu(self)
        # 创建歌曲卡
        self.createSongCards()
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setAttribute(Qt.WA_StyledBackground)
        self.setAlternatingRowColors(True)
        # 设置层叠样式
        self.__setQss()
        # 信号连接到槽
        self.__connectSignalToSlot()

    def createSongCards(self):
        """ 清空列表并创建新歌曲卡 """
        for i in range(len(self.songInfo_list)):
            # 添加空项目
            songInfo_dict = self.songInfo_list[i]
            item = QListWidgetItem()
            # 将项目的内容重置为自定义类
            songCard = SongCard(songInfo_dict)
            songCard.itemIndex = i
            songCard.resize(1150, 60)
            item.setSizeHint(QSize(songCard.width(), 60))
            self.addItem(item)
            self.setItemWidget(item, songCard)
            # 通过whatsthis记录每个项目对应的路径和下标
            item.setWhatsThis(str(songInfo_dict))
            # 将项目添加到项目列表中
            self.songCard_list.append(songCard)
            self.item_list.append(item)
            songCard.doubleClicked.connect(self.__emitCurrentChangedSignal)
            songCard.playButtonClicked.connect(self.__playButtonSlot)
            songCard.clicked.connect(self.setCurrentIndex)
        # 添加一个空白item来填补playBar所占高度
        self.__createPlaceHolderItem()

    def __playButtonSlot(self, index):
        """ 歌曲卡播放按钮槽函数 """
        self.playSignal.emit(index)
        self.setCurrentIndex(index)
        self.setPlay(index)

    def setCurrentIndex(self, index):
        """ 设置当前下标 """
        if index != self.currentIndex:
            self.songCard_list[self.currentIndex].setSelected(False)
        self.currentIndex = index
        self.songCard_list[index].setSelected(True)

    def contextMenuEvent(self, e: QContextMenuEvent):
        """ 重写鼠标右击时间的响应函数 """
        hitIndex = self.indexAt(e.pos()).column()
        # 显示右击菜单
        if hitIndex > -1:
            self.contextMenu.exec(self.cursor().pos())

    def __removeSongCard(self, index):
        """ 删除选中的歌曲卡 """
        songCard = self.songCard_list.pop(index)
        songCard.deleteLater()
        self.item_list.pop(index)
        self.takeItem(index)
        # 更新下标
        for i in range(index, len(self.songCard_list)):
            self.songCard_list[i].itemIndex = i
        if self.currentIndex > index:
            self.currentIndex -= 1
        # 发送信号
        self.removeItemSignal.emit(index)
        self.update()

    def __emitCurrentChangedSignal(self, index):
        """ 发送当前播放的歌曲卡变化信号，同时更新样式和歌曲信息卡 """
        self.setPlay(index)
        # 发送歌曲信息更新信号
        self.playSignal.emit(index)

    def setPlay(self, index):
        """ 设置播放状态 """
        if self.songCard_list:
            self.songCard_list[self.playingIndex].setPlay(False)
            self.songCard_list[self.currentIndex].setSelected(False)
            self.currentIndex = index
            self.playingIndex = index  # 更新正在播放的下标
            if index >= 0:
                self.songCard_list[index].setPlay(True)
                self.playingSongInfo = self.songInfo_list[index]

    def showPropertyPanel(self):
        """ 显示属性面板 """
        propertyPanel = PropertyPanel(
            self.songCard_list[self.currentRow()].songInfo, self.window())
        propertyPanel.exec_()

    def showSongInfoEditPanel(self):
        """ 显示编辑歌曲信息面板 """
        current_dict = self.songInfo_list[self.currentRow()] # type:dict
        oldSongInfo = current_dict.copy()
        songInfoEditPanel = SongInfoEditPanel(current_dict, self.window())
        songInfoEditPanel.exec_()
        # 更新歌曲卡
        self.songCard_list[self.currentRow()].updateSongCard(current_dict)
        # 发出更新歌曲卡信息的信号
        self.editSongCardSignal.emit(oldSongInfo, current_dict)

    def __setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\songTabInterfaceSongListWidget.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def resizeEvent(self, e):
        """ 更新item的尺寸 """
        super().resizeEvent(e)
        for item in self.item_list:
            item.setSizeHint(QSize(self.width(), 60))
        self.placeholderItem.setSizeHint(QSize(self.width(), 145))

    def updateSongCardsInfo(self, songInfoDict_list: list):
        """ 更新所有歌曲卡的信息，不增减歌曲卡 """
        self.songInfo_list = songInfoDict_list if songInfoDict_list else [{}]
        for i in range(len(songInfoDict_list)):
            songInfo_dict = songInfoDict_list[i]
            self.songCard_list[i].updateSongCard(songInfo_dict)

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.contextMenu.playAct.triggered.connect(
            lambda: self.playSignal.emit(self.currentRow()))
        self.contextMenu.nextSongAct.triggered.connect(
            lambda: self.nextToPlaySignal.emit(self.songCard_list[self.currentRow()].songInfo))
        self.contextMenu.editInfoAct.triggered.connect(
            self.showSongInfoEditPanel)
        self.contextMenu.showPropertyAct.triggered.connect(
            self.showPropertyPanel)
        self.contextMenu.deleteAct.triggered.connect(
            lambda: self.__removeSongCard(self.currentRow()))
        self.contextMenu.addToMenu.playingAct.triggered.connect(
            lambda: self.addSongToPlaylistSignal.emit(self.songCard_list[self.currentRow()].songInfo))

    def clearSongCards(self):
        """ 清空歌曲卡 """
        self.item_list.clear()
        self.clear()
        # 释放内存
        for songCard in self.songCard_list:
            songCard.deleteLater()
        self.songCard_list.clear()
        self.currentIndex = 0

    def updateSongCards(self, songInfoDict_list):
        """ 更新所有歌曲卡，根据给定的信息决定创建或者删除歌曲卡 """
        self.takeItem(len(self.songCard_list))
        # 长度相等就更新信息，不相等就根据情况创建或者删除item
        if self.songCard_list:
            self.songCard_list[self.currentIndex].setPlay(False)
        deltaLen = len(songInfoDict_list) - len(self.songInfo_list)
        if deltaLen > 0:
            # 添加item
            for i in range(len(self.songInfo_list), len(self.songInfo_list) + deltaLen):
                # 添加空项目
                songInfo_dict = songInfoDict_list[i]
                # 创建item和歌曲卡
                item = QListWidgetItem()
                songCard = SongCard(songInfo_dict)
                # 记录下标
                songCard.itemIndex = i
                songCard.resize(1150, 60)
                item.setSizeHint(QSize(songCard.width(), 60))
                self.addItem(item)
                # 将项目的内容重置为自定义类
                self.setItemWidget(item, songCard)
                # 将item和songCard添加到列表中
                self.songCard_list.append(songCard)
                self.item_list.append(item)
                # 信号连接到槽
                songCard.doubleClicked.connect(self.__emitCurrentChangedSignal)
                songCard.playButtonClicked.connect(self.__playButtonSlot)
                songCard.clicked.connect(self.setCurrentIndex)
        elif deltaLen < 0:
            # 删除多余的item
            for i in range(len(self.songInfo_list) - 1, len(self.songInfo_list) + deltaLen - 1, -1):
                self.item_list.pop()
                songCard = self.songCard_list.pop()
                songCard.deleteLater()
                self.takeItem(i)
        # 更新部分歌曲卡
        self.songInfo_list = songInfoDict_list if songInfoDict_list else []
        iterRange = range(
            len(self.songInfo_list) - deltaLen) if deltaLen > 0 else range(len(self.songInfo_list))
        for i in iterRange:
            songInfo_dict = self.songInfo_list[i]
            self.songCard_list[i].updateSongCard(songInfo_dict)
        # 更新样式和当前下标
        self.currentIndex = -1
        self.playingIndex = -1
        self.playingSongInfo = None
        for songCard in self.songCard_list:
            songCard.setPlay(False)
        # 创建新占位行
        self.__createPlaceHolderItem()
        # 调整高度
        self.update()

    def __createPlaceHolderItem(self):
        """ 创建占位行 """
        self.placeholderItem = QListWidgetItem(self)
        self.placeholderItem.setSizeHint(QSize(self.width(), 145))
        self.addItem(self.placeholderItem)

    def paintEvent(self, e):
        """ 绘制白色背景 """
        super().paintEvent(e)
        painter = QPainter(self.viewport())
        painter.setPen(Qt.white)
        painter.setBrush(Qt.white)
        # 填充不是白色的区域
        painter.drawRect(0, 60 * len(self.songCard_list),
                         self.width(), self.height())

    def updateOneSongCard(self, oldSongInfo, newSongInfo):
        """ 更新一个歌曲卡 """
        if oldSongInfo in self.songInfo_list:
            index = self.songInfo_list.index(oldSongInfo)
            self.songInfo_list[index] = newSongInfo
            self.songCard_list[index].updateSongCard(
                newSongInfo)

    def sortSongCardByTrackNum(self):
        """ 以曲序为基准排序歌曲卡 """
        self.songInfo_list.sort(key=self.__sortAlbum)
        self.updateSongCardsInfo(self.songInfo_list)

    def __sortAlbum(self, songInfo):
        """ 以曲序为基准排序歌曲卡 """
        trackNum = songInfo['tracknumber']  # type:str
        # 处理m4a
        if not trackNum[0].isnumeric():
            return eval(trackNum)[0]
        return int(trackNum)
