import sys

from PyQt5.QtCore import QEvent, QSize, Qt, QPoint
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QAction, QApplication, QHBoxLayout, QLabel, QPushButton,
    QVBoxLayout, QWidget)

sys.path.append('..')
from Groove.my_widget.my_button import RandomPlayButton, SortModeButton
from Groove.viewer_widget.album_card_viewer import AlbumCardViewer
from Groove.my_widget.my_menu import Menu

class AlbumTabInterface(QWidget):
    """ 定义专辑卡标签界面 """

    def __init__(self, target_path_list:list, parent=None):
        super().__init__(parent)
        self.resize(1267, 827-23)

        # 实例化专辑视图
        self.albumCardViewer = AlbumCardViewer(target_path_list)

        # 实例化无序播放所有按钮
        self.randomPlayButton = RandomPlayButton(
            slot=self.randomPlay, parent=self)

        # 实例化排序依据标签、按钮和菜单
        self.sortModeMenu = Menu(parent=self)
        self.sortModeLabel = QLabel('排序依据:', self)
        self.sortModeButton = SortModeButton(
            '添加日期', self.showSortModeMenu, self)

        # 实例化布局
        self.h_layout = QHBoxLayout()
        self.all_v_layout = QVBoxLayout()

        # 将动作添加到菜单中
        self.addActionToMenu()

        # 设置初始排序方式
        self.currentSortMode = self.sortByCratedTime
        self.sortModeNum_dict = {'添加日期': 0, 'A到Z': 1, '发行年份': 2, '歌手': 3}
        # 初始化UI界面
        self.initWidget()
        self.initLayout()
        self.setQss()

    def initWidget(self):
        """ 初始化小部件 """

        # 获取专辑总数
        albums_num = len(self.albumCardViewer.albumCardDict_list)
        self.randomPlayButton.setText(f'({albums_num})')

        # 设置鼠标光标
        self.sortModeButton.setCursor(Qt.PointingHandCursor)
        self.randomPlayButton.setCursor(Qt.PointingHandCursor)

        # 分配ID
        self.setObjectName('albumTabInterface')
        self.sortModeMenu.setObjectName('sortModeMenu')
        self.sortModeLabel.setObjectName('sortModeLabel')
        self.sortModeMenu.setProperty('modeNumber','4')

    def initLayout(self):
        """ 初始化布局 """

        self.h_layout.addWidget(self.randomPlayButton, 0, Qt.AlignLeft)
        self.h_layout.addSpacing(38)
        self.h_layout.addWidget(self.sortModeLabel, 0, Qt.AlignLeft)
        self.h_layout.addWidget(self.sortModeButton, 0, Qt.AlignLeft)
        # 不给按钮和标签分配多余的空间
        self.h_layout.addStretch(1)

        self.all_v_layout.addSpacing(7)
        self.all_v_layout.addLayout(self.h_layout)
        self.all_v_layout.addSpacing(0)
        self.all_v_layout.addWidget(self.albumCardViewer)
        self.setLayout(self.all_v_layout)

    def addActionToMenu(self):
        """ 将动作添加到菜单里 """

        # 创建排序列表项目的动作
        self.sortByDictOrder = QAction(
            'A到Z', self, triggered=self.sortAlbumCard)
        self.sortByCratedTime = QAction(
            '添加日期', self, triggered=self.sortAlbumCard)
        self.sortByYear = QAction('发行年份', self, triggered=self.sortAlbumCard)
        self.sortBySonger = QAction('歌手', self, triggered=self.sortAlbumCard)
        # 设置动作的悬浮提醒
        self.sortByCratedTime.setToolTip('添加时间')
        self.sortByDictOrder.setToolTip('A到Z')
        self.sortByYear.setToolTip('发行年份')
        self.sortBySonger.setToolTip('歌手')

        # 将动作添加到菜单中
        self.sortModeMenu.addActions(
            [self.sortByCratedTime, self.sortByDictOrder, self.sortByYear, self.sortBySonger])

    def randomPlay(self):
        """ 改变播放的循环模式 """
        pass

    def sortAlbumCard(self):
        """ 根据所选的排序方式对歌曲卡进行重新排序 """
        sender = self.sender()
        self.currentSortMode = sender
        # 更新分组
        if sender == self.sortByCratedTime and self.albumCardViewer.sortMode != '添加时间':
            self.sortModeButton.setText('添加时间')
            self.albumCardViewer.sortByAddTimeGroup()
        elif sender == self.sortByDictOrder and self.albumCardViewer.sortMode != 'A到Z':
            self.sortModeButton.setText('A到Z')
            self.albumCardViewer.sortMode = 'A到Z'
            self.albumCardViewer.sortByFirsetLetter()
        elif sender == self.sortByYear and self.albumCardViewer.sortMode != '发行年份':
            self.sortModeButton.setText('发行年份')
            self.albumCardViewer.sortMode = '发行年份'
            self.albumCardViewer.sortByYear()
        elif sender == self.sortBySonger and self.albumCardViewer.sortMode != '歌手':
            self.sortModeButton.setText('歌手')
            self.albumCardViewer.sortMode = '歌手'
            self.albumCardViewer.sortBySonger()

    def showSortModeMenu(self):
        """ 显示排序方式菜单 """
        # 设置默认动作
        self.sortModeMenu.setDefaultAction(self.currentSortMode)
        self.sortModeMenu.exec(
            self.mapToGlobal(QPoint(self.sortModeButton.x(),
                                    self.sortModeButton.y() - 37*self.sortModeNum_dict[self.currentSortMode.text()]-1)))

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\albumTabInterface.qss', 'r', encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = AlbumTabInterface(['D:\\KuGou\\test_audio\\'])
    demo.show()
    sys.exit(app.exec_())
