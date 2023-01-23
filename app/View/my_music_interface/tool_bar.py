# coding:utf-8
from common.config import config
from common.get_pressed_pos import getPressedPos, Position
from common.style_sheet import setStyleSheet
from components.buttons.three_state_button import RandomPlayAllButton
from components.widgets.menu import AeroMenu
from PyQt5.QtCore import QFile, QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPolygon
from PyQt5.QtWidgets import QAction, QLabel, QPushButton, QWidget


class ToolBar(QWidget):
    """ Tool bar """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__createWidgets()
        self.__initWidget()

    def __createWidgets(self):
        """ create widgets """
        self.myMusicLabel = QLabel(self.tr("My music"), self)

        # create tab buttons
        self.songTabButton = TabButton(self.tr("Songs"), self, 0)
        self.singerTabButton = TabButton(self.tr("Artists"), self, 1)
        self.albumTabButton = TabButton(self.tr("Albums"), self, 2)

        self.randomPlayAllButton = RandomPlayAllButton(parent=self)
        self.sortModeLabel = QLabel(self.tr("Sort by:"), self)
        self.songSortModeButton = QPushButton(self.tr("Date added"), self)
        self.singerSortModeButton = QPushButton(self.tr("A to Z"), self)
        self.albumSortModeButton = QPushButton(self.tr("Date added"), self)

        # create menu
        self.songSortModeMenu = AeroMenu(parent=self)
        self.albumSortModeMenu = AeroMenu(parent=self)

        # create actions
        self.songSortBySongerAct = QAction(self.tr("Artist"), self)
        self.songSortByDictOrderAct = QAction(self.tr("A to Z"), self)
        self.songSortByCratedTimeAct = QAction(self.tr("Date added"), self)
        self.albumSortByDictOrderAct = QAction(self.tr("A to Z"), self)
        self.albumSortByCratedTimeAct = QAction(self.tr("Date added"), self)
        self.albumSortByYearAct = QAction(self.tr("Release year"), self)
        self.albumSortBySongerAct = QAction(self.tr("Artist"), self)
        self.songSortActions = [
            self.songSortByCratedTimeAct,
            self.songSortByDictOrderAct,
            self.songSortBySongerAct,
        ]
        self.albumSortActions = [
            self.albumSortByCratedTimeAct,
            self.albumSortByDictOrderAct,
            self.albumSortByYearAct,
            self.albumSortBySongerAct,
        ]

    def __initWidget(self):
        """ initialize widgets """
        self.__setQss()
        self.__initLayout()
        self.resize(1200, 245)
        self.setAttribute(Qt.WA_StyledBackground)
        self.albumSortModeButton.hide()
        self.singerSortModeButton.hide()

        # add actions to menu
        self.songSortModeMenu.addActions(self.songSortActions)
        self.albumSortModeMenu.addActions(self.albumSortActions)

        # set properties
        self.songSortByCratedTimeAct.setProperty('mode', 'Date added')
        self.songSortByDictOrderAct.setProperty('mode', 'A to Z')
        self.songSortBySongerAct.setProperty('mode', 'Artist')
        self.albumSortByCratedTimeAct.setProperty('mode', 'Date added')
        self.albumSortByDictOrderAct.setProperty('mode', 'A to Z')
        self.albumSortBySongerAct.setProperty('mode', 'Artist')
        self.albumSortByYearAct.setProperty('mode', 'Release year')

    def __initLayout(self):
        """ initialize layout """
        self.myMusicLabel.move(30, 54)

        self.songTabButton.move(33, 136)
        self.singerTabButton.move(
            self.songTabButton.geometry().right()+55, 136)
        self.albumTabButton.move(
            self.singerTabButton.geometry().right()+55, 136)

        self.randomPlayAllButton.move(31, 199)
        self.sortModeLabel.move(
            self.randomPlayAllButton.geometry().right()+50, 200)
        self.songSortModeButton.move(
            self.sortModeLabel.geometry().right()+7, 195)
        self.singerSortModeButton.move(self.songSortModeButton.x(), 195)
        self.albumSortModeButton.move(self.songSortModeButton.x(), 195)

    def paintEvent(self, QPaintEvent):
        """ paint horizontal line """
        super().paintEvent(QPaintEvent)
        painter = QPainter(self)
        r = 46 if config.theme == 'dark' else 229
        painter.setPen(QColor(r, r, r))
        painter.drawLine(30, 176, self.width()-20, 176)

    def __setQss(self):
        """ set style sheet """
        self.myMusicLabel.setObjectName("myMusicLabel")
        self.sortModeLabel.setObjectName("sortModeLabel")
        self.songSortModeMenu.setObjectName("sortModeMenu")
        self.albumSortModeMenu.setObjectName("sortModeMenu")
        self.songSortModeButton.setObjectName("sortModeButton")
        self.singerSortModeButton.setObjectName("sortModeButton")
        self.albumSortModeButton.setObjectName("sortModeButton")
        self.albumSortModeMenu.setProperty("modeNumber", "4")
        setStyleSheet(self, 'my_music_interface_toolBar')
        self.randomPlayAllButton.adjustSize()
        self.sortModeLabel.adjustSize()
        self.songSortModeButton.adjustSize()


class TabButton(QPushButton):
    """ Tab button """

    selected = pyqtSignal(int)

    def __init__(self, text: str, parent=None, tabIndex: int = 0):
        """
        Parameters
        ----------
        text: str
            button text

        parent:
            parent window

        tabIndex: int
            tab index of button
        """
        super().__init__(parent)
        self.text = text
        self.isEnter = False
        self.isSelected = False
        self.pressedPos = None
        self.tabIndex = tabIndex

        self.setStyleSheet(
            "QPushButton{font: 25px 'Segoe UI', 'Microsoft YaHei'}")
        self.adjustSize()
        self.setFixedSize(self.fontMetrics().width(text), 40)

    def setSelected(self, isSelected: bool):
        """ set selected state """
        self.isSelected = isSelected
        self.update()

    def enterEvent(self, e):
        self.isEnter = True

    def leaveEvent(self, e):
        self.isEnter = False

    def mousePressEvent(self, e):
        self.pressedPos = getPressedPos(self, e)
        self.update()
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.pressedPos = None
        super().mouseReleaseEvent(e)
        self.selected.emit(self.tabIndex)

    def paintEvent(self, e):
        """ paint button """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.TextAntialiasing)
        painter.setFont(self.font())
        self.__paintAllText(painter, 14)

        if not self.isSelected:
            return

        w = self.width()
        h = self.height()

        if not self.pressedPos:
            self.__paintLine(painter, 1, h-3, w-1, h-3, w-1, h, 1, h)
        elif self.pressedPos in [Position.TOP_LEFT, Position.BOTTOM_RIGHT]:
            self.__paintLine(painter, 1, h-3, w-1, h-4, w-1, h-1, 1, h)
        elif self.pressedPos in [Position.LEFT, Position.CENTER, Position.RIGHT, Position.TOP, Position.BOTTOM]:
            self.__paintLine(painter, 2, h-4, w-2, h-4, w-2, h-1, 2, h-1)
        elif self.pressedPos in [Position.BOTTOM_LEFT, Position.TOP_RIGHT]:
            self.__paintLine(painter, 1, h-4, w-1, h-3, w-1, h, 1, h-1)

    def __paintText(self, painter: QPainter, shearX, shearY, x=1, y=5):
        """ paint text """
        painter.shear(shearX, shearY)
        painter.drawText(x, y + 21, self.text)

    def __paintLine(self, painter, x1, y1, x2, y2, x3, y3, x4, y4):
        """ paint bottom border line """
        painter.setPen(Qt.NoPen)
        brush = QBrush(QColor(0, 153, 188))
        painter.setBrush(brush)
        points = [QPoint(x1, y1), QPoint(x2, y2),
                  QPoint(x3, y3), QPoint(x4, y4)]
        painter.drawPolygon(QPolygon(points), 4)

    def __paintAllText(self, painter, fontSize=16):
        """ paint all texts """
        isDark = config.theme == 'dark'

        if not self.isSelected:
            r = 153 if isDark else 102
            painter.setPen(QColor(r, r, r))

        if not self.pressedPos:
            if self.isEnter:
                color = Qt.white if isDark else Qt.black
                painter.setPen(QPen(color))

            self.__paintText(painter, 0, 0)
        else:
            painter.setFont(QFont("Microsoft YaHei", fontSize))
            if self.pressedPos in [Position.TOP_LEFT, Position.BOTTOM_RIGHT]:
                self.__paintText(painter, -0.03, 0)
            elif self.pressedPos in [Position.LEFT, Position.CENTER, Position.RIGHT, Position.TOP, Position.BOTTOM]:
                self.__paintText(painter, 0, 0)
            elif self.pressedPos in [Position.BOTTOM_LEFT, Position.TOP_RIGHT]:
                self.__paintText(painter, 0.03, 0)
