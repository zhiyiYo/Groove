# coding:utf-8
from common.get_pressed_pos import getPressedPos
from components.buttons.three_state_button import ThreeStatePushButton
from components.widgets.menu import AeroMenu
from PyQt5.QtCore import QFile, QPoint, Qt, pyqtSignal
from PyQt5.QtGui import (QBrush, QColor, QFont, QFontMetrics, QPainter, QPen,
                         QPolygon)
from PyQt5.QtWidgets import QAction, QLabel, QPushButton, QWidget


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
        self.myMusicLabel = QLabel(self.tr("My music"), self)
        # 创建导航按钮
        self.songTabButton = TabButton(self.tr("Songs"), self, 0)
        self.singerTabButton = TabButton(self.tr("Artists"), self, 1)
        self.albumTabButton = TabButton(self.tr("Albums"), self, 1)
        # 创建底部按钮
        self.randomPlayAllButton = ThreeStatePushButton(
            {
                "normal": ":/images/random_play_all/Shuffle_normal.png",
                "hover": ":/images/random_play_all/Shuffle_hover.png",
                "pressed": ":/images/random_play_all/Shuffle_pressed.png",
            },
            parent=self,
            text=self.tr(" Shuffle all")+' (0)',
            iconSize=(20, 20),
        )
        self.sortModeLabel = QLabel(self.tr("Sort by:"), self)
        self.songSortModeButton = QPushButton(self.tr("Date added"), self)
        self.albumSortModeButton = QPushButton(self.tr("Date added"), self)
        # 创建菜单
        self.songSortModeMenu = AeroMenu(parent=self)
        self.albumSortModeMenu = AeroMenu(parent=self)
        # 创建动作
        self.songSortBySongerAct = QAction(self.tr("Artist"), self)
        self.songSortByDictOrderAct = QAction(self.tr("A to Z"), self)
        self.songSortByCratedTimeAct = QAction(self.tr("Date added"), self)
        self.albumSortByDictOrderAct = QAction(self.tr("A to Z"), self)
        self.albumSortByCratedTimeAct = QAction(self.tr("Date added"), self)
        self.albumSortByYearAct = QAction(self.tr("Release year"), self)
        self.albumSortBySongerAct = QAction(self.tr("Artist"), self)
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
        self.__setQss()
        self.__initLayout()
        self.resize(1200, 245)
        self.setAttribute(Qt.WA_StyledBackground)
        # 隐藏专辑排序按钮
        self.albumSortModeButton.hide()
        # 将动作添加到菜单中
        self.songSortModeMenu.addActions(self.songSortAction_list)
        self.albumSortModeMenu.addActions(self.albumSortAction_list)
        # 设置属性
        self.songSortByCratedTimeAct.setProperty('mode', 'Date added')
        self.songSortByDictOrderAct.setProperty('mode', 'A to Z')
        self.songSortBySongerAct.setProperty('mode', 'Artist')
        self.albumSortByCratedTimeAct.setProperty('mode', 'Date added')
        self.albumSortByDictOrderAct.setProperty('mode', 'A to Z')
        self.albumSortBySongerAct.setProperty('mode', 'Artist')
        self.albumSortByYearAct.setProperty('mode', 'Release year')

    def __initLayout(self):
        """ 初始化布局 """
        self.myMusicLabel.move(30, 54)

        # 标签按钮位置
        self.songTabButton.move(33, 136)
        self.singerTabButton.move(
            self.songTabButton.geometry().right()+55, 136)
        self.albumTabButton.move(
            self.singerTabButton.geometry().right()+55, 136)

        self.randomPlayAllButton.move(31, 200)
        self.sortModeLabel.move(
            self.randomPlayAllButton.geometry().right()+50, 200)
        self.songSortModeButton.move(
            self.sortModeLabel.geometry().right()+7, 195)
        self.albumSortModeButton.move(self.songSortModeButton.x(), 195)

    def paintEvent(self, QPaintEvent):
        """ 绘制背景 """
        super().paintEvent(QPaintEvent)
        painter = QPainter(self)
        painter.setPen(QPen(QColor(229, 229, 229)))
        painter.drawLine(30, 176, self.width()-20, 176)

    def __setQss(self):
        """ 设置层叠样式 """
        self.myMusicLabel.setObjectName("myMusicLabel")
        self.sortModeLabel.setObjectName("sortModeLabel")
        self.songSortModeMenu.setObjectName("sortModeMenu")
        self.albumSortModeMenu.setObjectName("sortModeMenu")
        self.songSortModeButton.setObjectName("sortModeButton")
        self.albumSortModeButton.setObjectName("sortModeButton")
        self.randomPlayAllButton.setObjectName("randomPlayButton")
        self.albumSortModeMenu.setProperty("modeNumber", "4")

        f = QFile(":/qss/my_music_interface_toolBar.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

        self.randomPlayAllButton.adjustSize()
        self.sortModeLabel.adjustSize()


class TabButton(QPushButton):
    """ 标签按钮，点击即可换页 """

    buttonSelected = pyqtSignal(int)

    def __init__(self, text: str, parent=None, tabIndex: int = 0):
        """
        Parameters
        ----------
        text: str
            按钮文本

        parent:
            父级窗口

        tabIndex: int
            按钮对应的标签窗口索引，范围为 `0 ~ N-1`"""
        super().__init__(parent)
        self.text = text
        self.isEnter = False
        self.isSelected = False
        self.pressedPos = None
        self.tabIndex = tabIndex

        self.setStyleSheet("QPushButton{font: 25px 'Segoe UI', 'Microsoft YaHei'}")
        self.adjustSize()
        self.setFixedSize(self.fontMetrics().width(text), 40)

    def setSelected(self, isSelected: bool):
        """ 设置选中状态 """
        self.isSelected = isSelected
        self.update()

    def enterEvent(self, e):
        """ 鼠标进入时置位状态位 """
        self.isEnter = True

    def leaveEvent(self, e):
        """ 鼠标进入时清零标志位 """
        self.isEnter = False

    def mousePressEvent(self, e):
        """ 鼠标点击时记录位置 """
        self.pressedPos = getPressedPos(self, e)
        self.update()
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        """ 鼠标松开更新样式 """
        self.pressedPos = None
        super().mouseReleaseEvent(e)
        self.buttonSelected.emit(self.tabIndex)

    def paintEvent(self, e):
        """ 绘制背景 """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.TextAntialiasing)
        painter.setFont(self.font())
        if not self.isSelected:
            self.__paintAllText(painter, 14)
        else:
            self.__paintAllText(painter, 14)
            if not self.pressedPos:
                self.__paintLine(
                    painter,
                    1,
                    self.height() - 3,
                    self.width() - 1,
                    self.height() - 3,
                    self.width() - 1,
                    self.height(),
                    1,
                    self.height(),
                )
            # 左上角和右下角
            elif self.pressedPos in ["left-top", "right-bottom"]:
                self.__paintLine(
                    painter,
                    1,
                    self.height() - 3,
                    self.width() - 1,
                    self.height() - 4,
                    self.width() - 1,
                    self.height() - 1,
                    1,
                    self.height(),
                )
            # 左中右上下
            elif self.pressedPos in ["left", "center", "right", "top", "bottom"]:
                self.__paintLine(
                    painter,
                    2,
                    self.height() - 4,
                    self.width() - 2,
                    self.height() - 4,
                    self.width() - 2,
                    self.height() - 1,
                    2,
                    self.height() - 1,
                )
            # 左下角和右上角
            elif self.pressedPos in ["left-bottom", "right-top"]:
                self.__paintLine(
                    painter,
                    1,
                    self.height() - 4,
                    self.width() - 1,
                    self.height() - 3,
                    self.width() - 1,
                    self.height(),
                    1,
                    self.height() - 1,
                )

    def __paintText(self, painter, shearX, shearY, x=1, y=5):
        """ 绘制文本 """
        painter.shear(shearX, shearY)
        painter.drawText(x, y + 21, self.text)

    def __paintLine(self, painter, x1, y1, x2, y2, x3, y3, x4, y4):
        """ 绘制选中标志 """
        painter.setPen(Qt.NoPen)
        brush = QBrush(QColor(0, 153, 188))
        painter.setBrush(brush)
        points = [QPoint(x1, y1), QPoint(x2, y2),
                  QPoint(x3, y3), QPoint(x4, y4)]
        painter.drawPolygon(QPolygon(points), 4)

    def __paintAllText(self, painter, fontSize=16):
        """ 根据各种点击情况绘制文本 """
        if not self.isSelected:
            pen = QPen(QColor(102, 102, 102))
            painter.setPen(pen)
        if not self.pressedPos:
            if self.isEnter:
                # 鼠标进入时画笔改为黑色
                painter.setPen(QPen(Qt.black))
            self.__paintText(painter, 0, 0)
        else:
            painter.setFont(QFont("Microsoft YaHei", fontSize))
            # 左上角和右下角
            if self.pressedPos in ["left-top", "right-bottom"]:
                self.__paintText(painter, -0.03, 0)
            # 左中右上下
            elif self.pressedPos in ["left", "center", "right", "top", "bottom"]:
                self.__paintText(painter, 0, 0)
            # 左下角和右上角
            elif self.pressedPos in ["left-bottom", "right-top"]:
                self.__paintText(painter, 0.03, 0)
