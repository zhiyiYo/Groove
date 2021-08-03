# coding:utf-8

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QAction

from .tab_button import TabButton
from app.components.buttons.three_state_button import ThreeStatePushButton
from app.components.menu import AeroMenu


class ToolBar(QWidget):
    """ 工具栏 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建小部件
        self.__createWidgets()
        # 初始化
        self.__initWidget()

    def __createWidgets(self):
        """ 创建小部件 """
        self.myMusicLabel = QLabel("我的音乐", self)
        # 创建导航按钮
        self.songTabButton = TabButton("歌曲", self, 0)
        self.songerTabButton = TabButton("歌手", self, 1)
        self.albumTabButton = TabButton("专辑", self, 1)
        # 创建底部按钮
        self.randomPlayAllButton = ThreeStatePushButton(
            {
                "normal": r"app\resource\images\ramdom_play_all\无序播放所有.png",
                "hover": r"app\resource\images\ramdom_play_all\无序播放所有_hover.png",
                "pressed": r"app\resource\images\ramdom_play_all\无序播放所有_pressed.png",
            },
            parent=self,
            text=" 无序播放所有",
            iconSize=(19, 15),
        )
        self.sortModeLabel = QLabel("排序依据:", self)
        self.songSortModeButton = QPushButton("添加日期", self)
        self.albumSortModeButton = QPushButton("添加日期", self)
        # 创建菜单
        self.songSortModeMenu = AeroMenu(parent=self)
        self.albumSortModeMenu = AeroMenu(parent=self)
        # 创建动作
        self.songSortBySongerAct = QAction("歌手", self)
        self.songSortByDictOrderAct = QAction("A到Z", self)
        self.songSortByCratedTimeAct = QAction("添加日期", self)
        self.albumSortByDictOrderAct = QAction("A到Z", self)
        self.albumSortByCratedTimeAct = QAction("添加日期", self)
        self.albumSortByYearAct = QAction("发行年份", self)
        self.albumSortBySongerAct = QAction("歌手", self)
        self.songSortAction_list = [
            self.songSortByCratedTimeAct,
            self.songSortByDictOrderAct,
            self.songSortBySongerAct,
        ]
        self.albumSortAction_list = [
            self.albumSortByCratedTimeAct,
            self.albumSortByDictOrderAct,
            self.albumSortByYearAct,
            self.albumSortBySongerAct,
        ]

    def __initWidget(self):
        """ 初始化小部件 """
        self.__initLayout()
        self.resize(1200, 245)
        self.setAttribute(Qt.WA_StyledBackground)
        # 隐藏专辑排序按钮
        self.albumSortModeButton.hide()
        # 将动作添加到菜单中
        self.songSortModeMenu.addActions(self.songSortAction_list)
        self.albumSortModeMenu.addActions(self.albumSortAction_list)
        # 分配ID
        self.myMusicLabel.setObjectName("myMusicLabel")
        self.sortModeLabel.setObjectName("sortModeLabel")
        self.songSortModeMenu.setObjectName("sortModeMenu")
        self.albumSortModeMenu.setObjectName("sortModeMenu")
        self.albumSortModeMenu.setProperty("modeNumber", "4")
        self.songSortModeButton.setObjectName("sortModeButton")
        self.albumSortModeButton.setObjectName("sortModeButton")
        self.randomPlayAllButton.setObjectName("randomPlayButton")
        # 设置层叠样式
        self.__setQss()

    def __initLayout(self):
        """ 初始化布局 """
        self.myMusicLabel.move(30, 54)
        self.songTabButton.move(33, 136)
        self.albumTabButton.move(239, 136)
        self.songerTabButton.move(136, 136)
        self.randomPlayAllButton.move(31, 199)
        self.sortModeLabel.move(231, 204)
        self.songSortModeButton.move(306, 199)
        self.albumSortModeButton.move(306, 199)

    def paintEvent(self, QPaintEvent):
        """ 绘制背景 """
        super().paintEvent(QPaintEvent)
        painter = QPainter(self)
        painter.setPen(QPen(QColor(229, 229, 229)))
        painter.drawLine(30, 176, self.width(), 176)

    def __setQss(self):
        """ 设置层叠样式 """
        with open(r"app\resource\css\my_music_interface_toolBar.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())
