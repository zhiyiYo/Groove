# coding:utf-8

import sys

from PyQt5.QtCore import QPoint, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent, QFont, QIcon, QResizeEvent
from PyQt5.QtWidgets import (QAction, QApplication, QHBoxLayout, QLabel,
                             QScrollBar, QVBoxLayout, QWidget)

from my_song_tab_interface.selection_mode_bar import \
    SelectionModeBar as SongTabSelectionModeBar

from .my_music_tab_widget import MyMusicTabWidget
from .scroll_bar import ScrollBar


class MyMusicInterface(QWidget):
    """ 创建一个本地音乐分组界面 """
    randomPlayAllSig = pyqtSignal()
    currentIndexChanged = pyqtSignal(int)
    selectionModeStateChanged = pyqtSignal(bool)
    playCheckedSongCardsSig = pyqtSignal(list)
    nextToPlayCheckedSongCardsSig = pyqtSignal(list)

    def __init__(self, target_path_list: list, parent=None):
        super().__init__(parent)
        # 实例化一个包含三个标签界面子界面
        self.myMusicTabWidget = MyMusicTabWidget(target_path_list, self)
        # 创建小部件
        self.__createWidgets()
        # 初始化
        self.__initLayout()
        self.__initWidget()
        self.__setQss()

    def __createWidgets(self):
        """ 创建小部件 """
        # 引用小部件
        self.__referenceWidgets()
        # 实例化一个标签和三个竖直滚动条
        self.myMusicLabel = QLabel(self)
        self.song_scrollBar = ScrollBar(self.songCardList_vScrollBar, self)
        # self.songer_scrollBar = ScrollBar(self.songerViewer_vScrollBar, self)
        self.album_scrollBar = ScrollBar(self.albumViewer_vScrollBar, self)
        self.scrollBar_list = [self.song_scrollBar, self.album_scrollBar]
        # 实例化底部选择栏
        self.songTabSelectionModeBar = SongTabSelectionModeBar(self)

    def __initLayout(self):
        """ 初始化布局 """
        self.myMusicLabel.move(30, 54)
        self.myMusicTabWidget.move(19, 136)
        for scrollBar in self.scrollBar_list:
            scrollBar.move(self.width() - scrollBar.width(), 40)

    def __initWidget(self):
        """ 初始化小部件的属性 """
        self.resize(1300, 970)
        self.setAttribute(Qt.WA_StyledBackground)
        # 设置标签上的字
        self.myMusicLabel.setText('我的音乐')
        # 隐藏列表视图的滚动条
        self.myMusicTabWidget.songTab.songCardListWidget.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        # 设置滚动条高度
        self.adjustScrollBarHeight()
        # 隐藏底部选择栏
        self.songTabSelectionModeBar.hide()
        # 先隐藏歌手视图的滚动条
        # self.songer_scrollBar.hide()
        self.album_scrollBar.hide()
        # 分配ID
        self.setObjectName('musicGroupInterface')
        self.myMusicLabel.setObjectName('myMusicLabel')
        self.song_scrollBar.setObjectName('songScrollBar')
        # self.songer_scrollBar.setObjectName('songerScrollBar')
        self.album_scrollBar.setObjectName('albumScrollBar')
        # 信号连接到槽
        self.__connectSignalToSlot()

    def adjustScrollBarHeight(self):
        """ 调整滚动条高度 """
        self.song_scrollBar.adjustSrollBarHeight()
        # self.songer_scrollBar.adjustSrollBarHeight()
        self.album_scrollBar.adjustSrollBarHeight()

    def __setQss(self):
        """ 设置层叠样式表 """
        with open('resource\\css\\myMusicInterface.qss', 'r',
                  encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)

    def resizeEvent(self, e):
        """ 当窗口大小发生改变时隐藏小部件 """
        self.adjustScrollBarHeight()
        self.myMusicTabWidget.resize(self.width() - 37, self.height() - 136)
        for scrollBar in self.scrollBar_list:
            scrollBar.move(self.width() - scrollBar.width(), 40)
        # 调整选中模式栏的位置和宽度
        self.songTabSelectionModeBar.resize(
            self.width(), self.songTabSelectionModeBar.height())
        self.songTabSelectionModeBar.move(
            0, self.height() - self.songTabSelectionModeBar.height())

    def changeTabSlot(self, index):
        """ 当前标签窗口改变时更改滚动条的绑定对象 """
        if index == 0:
            self.song_scrollBar.show()
            # self.songer_scrollBar.hide()
            self.album_scrollBar.hide()
        elif index == 1:
            self.song_scrollBar.hide()
            # self.songer_scrollBar.hide()
            self.album_scrollBar.show()

    def __checkedCardNumChangedSlot(self, num):
        """ 选中的卡数量发生改变时刷新选择栏 """
        if self.sender() == self.songCardListWidget:
            self.songTabSelectionModeBar.setPartButtonHidden(num > 1)

    def __selectionModeStateChangedSlot(self, isOpenSelectionMode: bool):
        """ 选择模式状态变化槽函数 """
        if self.sender() == self.songCardListWidget:
            self.songTabSelectionModeBar.setHidden(not isOpenSelectionMode)
        self.selectionModeStateChanged.emit(isOpenSelectionMode)

    def __referenceWidgets(self):
        """ 引用小部件 """
        # 引用视图
        self.songCardListWidget = self.myMusicTabWidget.songTab.songCardListWidget
        self.albumCardViewer = self.myMusicTabWidget.albumTab.albumCardViewer
        # 引用三个视图的滚动条
        self.songCardList_vScrollBar = self.myMusicTabWidget.songTab.songCardListWidget.verticalScrollBar(
        )
        """ self.songerViewer_vScrollBar = self.myMusicTabWidget.songerTab.songerHeadPortraitViewer.scrollArea.verticalScrollBar(
        ) """
        self.albumViewer_vScrollBar = self.myMusicTabWidget.albumTab.albumCardViewer.scrollArea.verticalScrollBar(
        )

    def __songTabSelectAllButtonSlot(self):
        """ 全选/取消全选 """
        isChecked = not self.songCardListWidget.isAllSongCardsChecked
        self.songCardListWidget.setAllSongCardCheckedState(isChecked)
        self.songTabSelectionModeBar.checkAllButton.setCheckedState(isChecked)

    def __unCheckSongCards(self):
        """ 取消已选中歌曲卡的选中状态并更新按钮图标 """
        self.songCardListWidget.unCheckSongCards()
        # 更新按钮的图标为全选
        self.songTabSelectionModeBar.checkAllButton.setCheckedState(True)

    def __emitPlaylist(self):
        """ 发送播放列表 """
        songInfo_list = [
            songCard.songInfo for songCard in self.songCardListWidget.checkedSongCard_list]
        self.__unCheckSongCards()
        if self.sender() == self.songTabSelectionModeBar.playButton:
            self.playCheckedSongCardsSig.emit(songInfo_list)
        elif self.sender() == self.songTabSelectionModeBar.nextToPlayButton:
            self.nextToPlayCheckedSongCardsSig.emit(songInfo_list)

    def __switchToAlbumInterface(self):
        """ 切换到专辑界面 """
        if self.sender() == self.songTabSelectionModeBar.showAlbumButton:
            songCard = self.songCardListWidget.checkedSongCard_list[0]
            # 取消选中的歌曲卡的选中状态，隐藏选择栏并显示播放栏
            self.__unCheckSongCards()
            self.songCardListWidget.switchToAlbumInterfaceSig.emit(
                songCard.album, songCard.songer)

    def __editCardInfo(self):
        """ 编辑卡片信息 """
        if self.sender() == self.songTabSelectionModeBar.editInfoButton:
            songCard = self.songCardListWidget.checkedSongCard_list[0]
            self.__unCheckSongCards()
            self.songCardListWidget.showSongInfoEditPanel(songCard)

    def __showCheckedSongCardProperty(self):
        """ 显示选中的歌曲卡的属性 """
        songInfo = self.songCardListWidget.checkedSongCard_list[0].songInfo
        self.__unCheckSongCards()
        self.songCardListWidget.showPropertyPanel(songInfo)

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.myMusicTabWidget.currentIndexChanged.connect(
            self.currentIndexChanged)
        self.myMusicTabWidget.stackedWidget.currentChanged.connect(
            self.changeTabSlot)
        self.myMusicTabWidget.albumTab.sortModeChanged.connect(
            self.album_scrollBar.associateScrollBar)
        self.myMusicTabWidget.albumTab.columnChanged.connect(
            self.album_scrollBar.associateScrollBar)
        self.songCardListWidget.selectionModeStateChanged.connect(
            self.__selectionModeStateChangedSlot)
        self.songCardListWidget.checkedSongCardNumChanged.connect(
            self.__checkedCardNumChangedSlot)
        # 无序播放所有信号连接到槽函数
        self.myMusicTabWidget.songTab.randomPlayAllSig.connect(
            self.randomPlayAllSig)
        self.myMusicTabWidget.albumTab.randomPlayAllSig.connect(
            self.randomPlayAllSig)
        # 歌曲界面选择栏各按钮信号连接到槽函数
        self.songTabSelectionModeBar.cancelButton.clicked.connect(
            self.__unCheckSongCards)
        self.songTabSelectionModeBar.checkAllButton.clicked.connect(
            self.__songTabSelectAllButtonSlot)
        self.songTabSelectionModeBar.playButton.clicked.connect(
            self.__emitPlaylist)
        self.songTabSelectionModeBar.nextToPlayButton.clicked.connect(
            self.__emitPlaylist)
        self.songTabSelectionModeBar.showAlbumButton.clicked.connect(
            self.__switchToAlbumInterface)
        self.songTabSelectionModeBar.editInfoButton.clicked.connect(
            self.__editCardInfo)
        self.songTabSelectionModeBar.propertyButton.clicked.connect(
            self.__showCheckedSongCardProperty)

    def exitSelectionMode(self):
        """ 退出选择模式 """
        self.__unCheckSongCards()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    font = QFont(QApplication.font())
    demo = MyMusicInterface(['D:\\KuGou\\test_audio'])
    demo.show()
    sys.exit(app.exec_())
