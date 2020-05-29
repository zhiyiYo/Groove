import sys
import time
from json import dump
from PyQt5.QtCore import QPoint, QSize, Qt, QEvent
from PyQt5.QtGui import QContextMenuEvent, QIcon, QBrush, QColor, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QHBoxLayout, QLabel,
                             QListWidget, QListWidgetItem, QMenu,
                             QWidget)
sys.path.append('..')
from Groove.get_info.get_song_info import SongInfo
from Groove.card_widget.songcard import SongCard
from Groove.my_dialog_box.property_panel import PropertyPanel
from Groove.my_dialog_box.song_info_edit_panel import SongInfoEditPanel
from Groove.my_dialog_box.window_mask import WindowMask


class SongCardListWidget(QListWidget):
    """ 定义一个歌曲卡列表视图 """

    def __init__(self, songs_folder):
        super().__init__()
        self.resize(1267, 638)
        self.songs_folder = songs_folder

        # 创建一个项目列表
        self.song_card_list = []
        self.item_list = []
        # 将歌曲信息设置为属性
        self.songInfo = SongInfo(self.songs_folder)
        # 默认排序方式为添加时间
        self.sortMode = '添加时间'

        # 添加项目
        self.addListWidgetItem()

        # 初始化小部件的属性
        self.initActions()
        self.initWidget()
        self.times = 0

        # 设置层叠样式
        # self.setQss()

    def initWidget(self):
        """ 初始化小部件 """

        # 设置列表视图的属性
        self.setDragEnabled(True)
        self.setMouseTracking(True)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QListWidget.ExtendedSelection)

        # 设置监听
        # self.installEventFilter(self)

        # 分配ID
        self.setObjectName('songCardList')
        self.verticalScrollBar().setObjectName('LWidgetVScrollBar')

        # 将复选框状态改变的信号连接到槽函数
        for song_card in self.song_card_list:
            song_card.song_name_card.songName.stateChanged.connect(
                self.refreshTextColor)

    def initActions(self):
        """ 创建动作 """
        # 创建主菜单动作
        self.playAct = QAction('播放', self)
        self.nextSongAct = QAction('下一首播放', self)
        self.showAlbumAct = QAction('显示专辑', self)
        self.editInfoAct = QAction(
            '编辑信息', self, triggered=self.showSongInfoEditPanel)
        self.showPropertyAct = QAction(
            '属性', self, triggered=self.showPropertyPanel)
        self.deleteAct = QAction('删除', self, triggered=self.deleteItem)
        self.selectAct = QAction('选择', self, triggered=self.select_func)

        # 创建子菜单的动作

        self.linkPalyingPageAct = QAction(
            QIcon('resource\\images\\正在播放.svg'), '正在播放', self)

        self.createPlaylistAct = QAction(
            QIcon(QPixmap('resource\\images\\黑色加号.svg')), '新的播放列表', self)

        # 创建菜单和子菜单
        self.contextMenu = QMenu(self)
        self.addToMenu = QMenu('添加到', self)

        # 将动作添加到菜单中
        self.contextMenu.addActions([self.playAct, self.nextSongAct])
        self.addToMenu.addActions(
            [self.linkPalyingPageAct, self.createPlaylistAct])
        self.addToMenu.insertSeparator(self.createPlaylistAct)

        # 将子菜单添加到主菜单
        self.contextMenu.addMenu(self.addToMenu)

        # 将其余动作添加到主菜单
        self.contextMenu.addActions(
            [self.showAlbumAct, self.editInfoAct, self.showPropertyAct, self.deleteAct])
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.selectAct)

        # 设置菜单的ID
        self.addToMenu.setObjectName('addToMenu')
        self.contextMenu.setObjectName('songCardContextMenu')

    def addListWidgetItem(self):
        """ 在列表视图中添加项目 """
        # 对歌曲进行排序
        if self.sortMode == '添加时间':
            # 按文件创建时间排序项目
            self.songInfo.sortByCreateTime()
        elif self.sortMode == 'A到Z':
            # 按字典序排序
            self.songInfo.sortByDictOrder()
        elif self.sortMode == '歌手':
            # 按歌手名排序
            self.songInfo.sortBySonger()

        for i in range(len(self.songInfo.songInfo_list)):
            # 添加空项目
            songFile = self.songInfo.songInfo_list[i]
            songFile['index'] = i
            self.item = QListWidgetItem()

            # 将项目的内容重置为自定义类
            self.song_card = SongCard(
                songFile['songname'], songFile['songer'],
                songFile['album'], songFile['tcon'], songFile['year'], songFile['duration'])
            self.song_card.resize(1150, 61)
            self.item.setSizeHint(QSize(self.song_card.width(), 61))
            self.addItem(self.item)
            self.setItemWidget(self.item, self.song_card)
            # 通过whatsthis记录每个项目对应的路径和下标
            self.item.setWhatsThis(str(songFile))
            # 将项目添加到项目列表中
            self.song_card_list.append(self.song_card)
            self.item_list.append(self.item)

    def contextMenuEvent(self, e: QContextMenuEvent):
        """ 重写鼠标右击时间的响应函数 """
        # 显示右击菜单
        if self.count() > 0:
            self.contextMenu.exec(self.cursor().pos())

    def deleteItem(self):
        """ 删除选中的歌曲卡 """
        copy_songInfo_list = self.songInfo.songInfo_list.copy()
        copy_song_card_list = self.song_card_list.copy()
        copy_item_list = self.item_list.copy()

        for selectedItem in self.selectedItems():
            self.takeItem(self.row(selectedItem))
            # 删除songInfo中对应的元素
            self.songInfo.songInfo_list.remove(
                copy_songInfo_list[eval(selectedItem.whatsThis())['index']])
            self.song_card_list.remove(
                copy_song_card_list[eval(selectedItem.whatsThis())['index']])
            self.item_list.remove(
                copy_item_list[eval(selectedItem.whatsThis())['index']])

        # 更新item的下标
        for index, item in enumerate(self.item_list):
            info_dict = eval(item.whatsThis())
            info_dict['index'] = index
            item.setWhatsThis(str(info_dict))

    def showPropertyPanel(self):
        """ 显示属性面板 """
        info = eval(self.selectedItems()[0].whatsThis())
        propertyPanel = PropertyPanel(info)

        # 获取祖父级窗口的引用
        try:
            self.grandparent = self.parent().parent().parent().parent()
        except:
            self.grandparent = self.parent()
        # 在祖父窗口中居中显示
        x = int(self.grandparent.geometry().x() + 0.5 *
                self.grandparent.width() - 0.5 * propertyPanel.width())
        y = int(self.grandparent.geometry().y() + 0.5*self.grandparent.height() -
                0.5 * propertyPanel.height())
        propertyPanel.move(x, y)
        mask = WindowMask(self.grandparent)
        mask.show()
        propertyPanel.exec_()
        mask.close()

    def showSongInfoEditPanel(self):
        """ 显示编辑歌曲信息面板 """
        info = eval(self.selectedItems()[0].whatsThis())
        # 创建一个指向当前字典的临时属性
        for info_dict in self.songInfo.songInfo_list:
            if info['song_path'] == info_dict['song_path']:
                self.current_dict = info_dict
                break
        self.songInfoEditPanel = SongInfoEditPanel(self.current_dict)

        # 获取祖父级窗口的引用
        try:
            self.grandparent = self.parent().parent().parent().parent()
        except:
            self.grandparent = self.parent()
        # 在祖父窗口中居中显示
        x = int(self.grandparent.geometry().x() + 0.5 *
                self.grandparent.width() - 0.5 * self.songInfoEditPanel.width())
        y = int(self.grandparent.geometry().y() + 0.5*self.grandparent.height() -
                0.5 * self.songInfoEditPanel.height())
        self.songInfoEditPanel.move(x, y)
        mask = WindowMask(self.grandparent)
        mask.show()
        self.songInfoEditPanel.exec_()
        mask.close()

        #更新item的信息
        self.selectedItems()[0].setWhatsThis(str(self.current_dict))
        # 将修改的信息存入json文件
        with open('Data\\songInfo.json', 'w', encoding='utf-8') as f:
            dump(self.songInfo.songInfo_list, f)

        # 更新歌曲信息
        self.songInfo = SongInfo(self.songs_folder)

    def select_func(self):
        """ 点击选择时的槽函数 """
        # 显示复选框
        time.sleep(0.4)
        for song_card in self.song_card_list:
            # 更改选中状态标志位
            song_card.song_name_card.contextMenuSelecting = True
            song_card.song_name_card.showIndicator()
        # 将选中的项目设置为checked状态
        for selectedItem in self.selectedItems():
            index = eval(selectedItem.whatsThis())['index']
            self.song_card_list[index].song_name_card.songName.setChecked(
                Qt.Checked)

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\initSongCard.qss', 'r', encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)

    def setClickedQss(self):
        """ 设置鼠标左键时的层叠样式 """
        with open('resource\\css\\clickedSongCard.qss', 'r', encoding='utf-8') as f:
            qss = f.read()
            
            self.setStyleSheet(qss)

    def refreshTextColor(self):
        """ 根据复选框的状态来改变文本颜色 """
        sender = self.sender()

        index = self.song_card_list.index(sender.parent().parent())
        if not sender.isChecked():
            self.setQss()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = SongCardListWidget('D:\\KuGou')
    demo.show()

    sys.exit(app.exec_())
