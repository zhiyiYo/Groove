import sys
import time
from json import dump
from PyQt5.QtCore import QAbstractAnimation,QPoint, QSize, Qt, QEvent,QPropertyAnimation,QEasingCurve
from PyQt5.QtGui import QContextMenuEvent, QIcon, QBrush, QColor, QPixmap,QWheelEvent
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QApplication, QHBoxLayout, QLabel,
                             QListWidget, QListWidgetItem, QWidget)
sys.path.append('..')
from Groove.get_info.get_song_info import SongInfo
from Groove.card_widget.songcard import SongCard
from Groove.my_dialog_box.property_panel import PropertyPanel
from Groove.my_dialog_box.song_info_edit_panel import SongInfoEditPanel
from Groove.my_widget.my_menu import Menu,AddToMenu


class SongCardListWidget(QListWidget):
    """ 定义一个歌曲卡列表视图 """

    def __init__(self, songs_folder):
        super().__init__()
        self.resize(1267, 781-23)
        self.songs_folder = songs_folder
        # 实例化控制滚动效果的动画
        self.animation = QPropertyAnimation(self.verticalScrollBar(), b'value')

        # 创建一个项目列表
        self.songCard_list = []
        self.item_list = []
        # 初始化之前选中的item
        self.preItem = None
        # 设置之前和当前选中的歌曲卡
        self.preSongCard = None
        self.currentSongCard = None
        # 设置是否处于批量操作模式状态位
        self.isSelectingMode = False
        
        # 将歌曲信息设置为属性
        self.songInfo = SongInfo(self.songs_folder)
        # 默认排序方式为添加时间
        self.sortMode = '添加时间'
        # 添加项目
        self.addListWidgetItem()
        # 初始化小部件的属性
        self.initActions()
        self.initWidget()
        # 设置层叠样式
        self.setQss()

    def initWidget(self):
        """ 初始化小部件 """
        # 设置列表视图的属性
        self.setDragEnabled(True)
        self.setMouseTracking(True)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QListWidget.ExtendedSelection)
        # 将滚动模式改为以像素计算
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.scrollStep = 50
        self.verticalScrollBar().setSingleStep(self.scrollStep)
        
        # 初始化动画效果
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        self.animation.finished.connect(self.aniFinishedEvent)
        # 分配ID
        self.setObjectName('songCardList')
        self.verticalScrollBar().setObjectName('LWidgetVScrollBar')
        # 选中中的item改变时改变样式
        self.itemSelectionChanged.connect(self.updateItemQss)

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
        self.selectAct = QAction('选择', self, triggered=self.selectedModeEvent)
        # 创建菜单和子菜单
        self.contextMenu = Menu(parent=self)
        self.addToMenu = AddToMenu('添加到', self)
        # 将动作添加到菜单中
        self.contextMenu.addActions([self.playAct, self.nextSongAct])
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
            songInfo_dict = self.songInfo.songInfo_list[i]
            songInfo_dict['index'] = i
            self.item = QListWidgetItem()

            # 将项目的内容重置为自定义类
            self.songCard = SongCard(songInfo_dict)
            self.songCard.resize(1150, 61)
            self.item.setSizeHint(QSize(self.songCard.width(), 61))
            self.addItem(self.item)
            self.setItemWidget(self.item, self.songCard)
            # 通过whatsthis记录每个项目对应的路径和下标
            self.item.setWhatsThis(str(songInfo_dict))
            # 将项目添加到项目列表中
            self.songCard_list.append(self.songCard)
            self.item_list.append(self.item)

    def contextMenuEvent(self, e: QContextMenuEvent):
        """ 重写鼠标右击时间的响应函数 """
        # 显示右击菜单
        if self.count() > 0:
            self.contextMenu.exec(self.cursor().pos())

    def deleteItem(self):
        """ 删除选中的歌曲卡 """
        copy_songInfo_list = self.songInfo.songInfo_list.copy()
        copy_song_card_list = self.songCard_list.copy()
        copy_item_list = self.item_list.copy()

        for selectedItem in self.selectedItems():
            self.takeItem(self.row(selectedItem))
            # 删除songInfo中对应的元素
            self.songInfo.songInfo_list.remove(
                copy_songInfo_list[eval(selectedItem.whatsThis())['index']])
            self.songCard_list.remove(
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
        # 获取祖父级窗口的引用
        try:
            self.grandparent = self.parent().parent().parent().parent()
        except:
            self.grandparent = self.parent()
        # 在祖父窗口中居中显示
        propertyPanel = PropertyPanel(info,self.grandparent)
        propertyPanel.exec_()

    def showSongInfoEditPanel(self):
        """ 显示编辑歌曲信息面板 """
        info = eval(self.selectedItems()[0].whatsThis())
        # 创建一个指向当前字典的临时属性
        for info_dict in self.songInfo.songInfo_list:
            if info['song_path'] == info_dict['song_path']:
                self.current_dict = info_dict
                break

        # 获取祖父级窗口的引用
        try:
            self.grandparent = self.parent().parent().parent().parent()
        except:
            self.grandparent = self
        # 在祖父窗口中居中显示
        self.songInfoEditPanel = SongInfoEditPanel(self.current_dict,self.grandparent)
        self.songInfoEditPanel.exec_()

        # 更新item的信息
        self.selectedItems()[0].setWhatsThis(str(self.current_dict))
        if self.currentSongCard:
            self.currentSongCard.updateSongCard(self.current_dict)
            self.update()
        # 将修改的信息存入json文件
        with open('Data\\songInfo.json', 'w', encoding='utf-8') as f:
            dump(self.songInfo.songInfo_list, f)

        # 更新歌曲信息
        self.songInfo = SongInfo(self.songs_folder)

    def selectedModeEvent(self):
        """ 点击选择时的槽函数 """
        # 显示复选框
        # time.sleep(0.4)
        # 进入批量选中操作模式
        self.isSelectingMode = True
        for songCard in self.songCard_list:
            # 更改选中状态标志位
            songCard.songNameCard.contextMenuSelecting = True
            songCard.songNameCard.songNameCheckBox.setProperty(
                'state', 'enter and unClicked')
        # 显示所有的复选框
        self.setStyle(QApplication.style())
        # 将选中的项目设置为checked状态
        for selectedItem in self.selectedItems():
            index = eval(selectedItem.whatsThis())['index']
            self.songCard_list[index].songNameCard.songNameCheckBox.setChecked(
                Qt.Checked)

    def updateItemQss(self):
        """ 更新item样式 """
        """ 有待更新批量操作的样式 """
        if not self.isSelectingMode and not (self.preItem is self.currentItem()):
            if self.preItem:
                # 如果旧的item不为空，就更新样式和之前选中的歌曲卡
                index = eval(self.preItem.whatsThis())['index']
                self.preSongCard = self.songCard_list[index]
                self.preSongCard.isClicked = False
                self.preSongCard.setLeaveStateQss()
            self.preItem = self.currentItem()
        # 更新当前的歌曲卡
        index = eval(self.currentItem().whatsThis())['index']
        self.currentSongCard = self.songCard_list[index]

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\songCardListWidget.qss', 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def wheelEvent(self, e:QWheelEvent):
        """ 实现滚动动画效果 """
        # 滚轮转动一次|angleDelta().y()|=120，为负表示向下，为正表示向上,120对应3个singleStep()
        # 获取滚动前的值
        super().wheelEvent(e)
        """ preValue = self.verticalScrollBar().value()
        deltaValue = int(e.angleDelta().y() / 120 * 3 * self.scrollStep)
        newValue = preValue - deltaValue
        if self.animation.state() == QAbstractAnimation.Stopped:
            self.animation.setStartValue(self.verticalScrollBar().value())
            self.animation.setEndValue(newValue)
            # 开始滚动
            self.animation.start()
        else:
            self.animation.pause()
            self.animation.setDuration(self.animation.duration() + 300)
            self.animation.setEndValue(newValue)
            #self.verticalScrollBar().setValue(self.animation.endValue())
            self.animation.start()
            #self.animation.setStartValue(self.verticalScrollBar().value()) """
            
    def aniFinishedEvent(self):
        if self.animation.duration() > 300:
            self.animation.setDuration(300)

            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = SongCardListWidget('D:\\KuGou')
    demo.show()

    sys.exit(app.exec_())
