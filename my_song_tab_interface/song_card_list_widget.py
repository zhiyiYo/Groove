import sys
from json import dump

from PyQt5.QtCore import (QAbstractAnimation, QEasingCurve, QEvent, QPoint,
                          QPropertyAnimation, QSize, Qt, pyqtSignal)
from PyQt5.QtGui import (QBrush, QColor, QContextMenuEvent, QIcon, QPixmap,
                         QWheelEvent)
from PyQt5.QtWidgets import (
    QAbstractItemView, QAction, QApplication, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QWidget)

from get_info.get_song_info import SongInfo
from my_dialog_box import PropertyPanel, SongInfoEditPanel
from my_widget.my_listWidget import ListWidget

from .song_card import SongCard
from .song_card_list_context_menu import SongCardListContextMenu


class SongCardListWidget(ListWidget):
    """ 定义一个歌曲卡列表视图 """

    playSignal = pyqtSignal(dict)
    nextPlaySignal = pyqtSignal(dict)
    removeItemSignal = pyqtSignal(int)
    addSongToPlaylistSignal = pyqtSignal(dict)

    def __init__(self, target_path_list: list, parent=None):
        super().__init__(parent)
        self.target_path_list = target_path_list
        self.songInfo = SongInfo(self.target_path_list)
        self.currentIndex = 0
        self.previousIndex = 0
        self.playingIndex = 0  # 正在播放的歌曲卡下标
        self.playingSongInfo = None
        if self.songInfo.songInfo_list:
            self.playingSongInfo = self.songInfo.songInfo_list[0]
        self.sortMode = '添加时间'
        self.resize(1267, 758)
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
        # self.setDragEnabled(True)
        self.__adjustHeight()
        self.setAlternatingRowColors(True)
        # self.setSelectionMode(QListWidget.ExtendedSelection)
        # 将滚动模式改为以像素计算
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        # 分配ID
        self.setObjectName('songCardList')
        # 设置层叠样式
        self.__setQss()
        # 信号连接到槽
        self.__connectSignalToSlot()

    def createSongCards(self):
        """ 清空列表并创建新歌曲卡 """
        for songCard in self.songCard_list:
            SongCard.deleteLater()
        self.songCard_list.clear()
        self.item_list.clear()
        self.clear()
        # 对歌曲进行排序
        self.songInfo.sortByCreateTime()
        # 引用排序完的字典
        # self.songInfo_list = self.songInfo.songInfo_list
        for i in range(len(self.songInfo.songInfo_list)):
            # 添加空项目
            songInfo_dict = self.songInfo.songInfo_list[i]
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
        self.placeholderItem = QListWidgetItem(self)
        self.placeholderItem.setSizeHint(QSize(1150, 145))
        self.placeholderItem.setBackground(QBrush(Qt.white))
        self.addItem(self.placeholderItem)

    def __playButtonSlot(self, index):
        """ 歌曲卡播放按钮槽函数 """
        self.playSignal.emit(self.songCard_list[index].songInfo)
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
        # 如果歌曲卡太少就调整高度
        self.__adjustHeight()

    def __emitCurrentChangedSignal(self, index):
        """ 发送当前播放的歌曲卡变化信号，同时更新样式和歌曲信息卡 """
        # 发送歌曲信息更新信号
        self.playSignal.emit(self.songCard_list[index].songInfo)
        self.setPlay(index)

    def setPlay(self, index):
        """ 设置播放状态 """
        if self.songCard_list:
            self.songCard_list[self.playingIndex].setPlay(False)
            self.songCard_list[self.currentIndex].setSelected(False)
            self.songCard_list[index].setPlay(True)
            self.currentIndex = index
            self.playingIndex = index  # 更新正在播放的下标
            self.playingSongInfo = self.songInfo.songInfo_list[index]

    def showPropertyPanel(self):
        """ 显示属性面板 """
        propertyPanel = PropertyPanel(
            self.songCard_list[self.currentRow()].songInfo, self.window())
        propertyPanel.exec_()

    def showSongInfoEditPanel(self):
        """ 显示编辑歌曲信息面板 """
        current_dict = self.songInfo.songInfo_list[self.currentRow()]
        songInfoEditPanel = SongInfoEditPanel(current_dict, self.window())
        songInfoEditPanel.exec_()
        # 更新歌曲卡
        self.songCard_list[self.currentRow()].updateSongCard(current_dict)
        # 将修改的信息存入json文件
        with open('Data\\songInfo.json', 'w', encoding='utf-8') as f:
            dump(self.songInfo.songInfo_list, f)
        # 更新歌曲信息
        self.songInfo = SongInfo(self.target_path_list)

    def __setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\songTabInterfaceSongListWidget.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def resizeEvent(self, e):
        """ 更新item的尺寸 """
        for item in self.item_list:
            item.setSizeHint(QSize(self.width()-117, 60))
        super().resizeEvent(e)

    def updateSongCardInfo(self):
        """ 重新扫描歌曲文件夹并更新歌曲卡信息 """
        self.songInfo = SongInfo(self.target_path_list)
        self.setSortMode(self.sortMode)

    def setSortMode(self, sortMode: str):
        """ 根据当前的排序模式来排序歌曲开 """
        self.sortMode = sortMode
        if self.sortMode == '添加时间':
            self.songInfo.sortByCreateTime()
        elif self.sortMode == 'A到Z':
            self.songInfo.sortByDictOrder()
        elif self.sortMode == '歌手':
            self.songInfo.sortBySonger()
        self.updateSongCards(self.songInfo.songInfo_list)
        if self.playingSongInfo in self.songInfo.songInfo_list:
            self.setPlay(self.songInfo.songInfo_list.index(
                self.playingSongInfo))

    def updateSongCards(self, songInfoDict_list: list):
        """ 更新所有歌曲卡的信息 """
        for i in range(len(songInfoDict_list)):
            songInfo_dict = songInfoDict_list[i]
            self.songCard_list[i].updateSongCard(songInfo_dict)

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.contextMenu.playAct.triggered.connect(
            lambda: self.playSignal.emit(self.songCard_list[self.currentRow()].songInfo))
        self.contextMenu.nextSongAct.triggered.connect(
            lambda: self.nextPlaySignal.emit(self.songCard_list[self.currentRow()].songInfo))
        self.contextMenu.editInfoAct.triggered.connect(
            self.showSongInfoEditPanel)
        self.contextMenu.showPropertyAct.triggered.connect(
            self.showPropertyPanel)
        self.contextMenu.deleteAct.triggered.connect(
            lambda: self.__removeSongCard(self.currentRow()))
        self.contextMenu.addToMenu.playingAct.triggered.connect(
            lambda: self.addSongToPlaylistSignal.emit(self.songCard_list[self.currentRow()].songInfo))

    def __adjustHeight(self):
        """ 如果歌曲卡数量太少就调整自己的高度 """
        if self.parent():
            if len(self.songCard_list) * 60 < self.parent().height() - 60:
                self.resize(self.width(), len(self.songCard_list) * 60 + 145)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = SongCardListWidget(['D:\\KuGou'])
    demo.show()

    sys.exit(app.exec_())
