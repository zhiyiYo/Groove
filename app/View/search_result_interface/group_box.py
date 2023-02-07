# coding:utf-8
from common.icon import getIconColor, drawSvgIcon
from common.library import Library
from common.style_sheet import setStyleSheet
from components.buttons.three_state_button import ThreeStatePushButton
from PyQt5.QtCore import (QEasingCurve, QParallelAnimationGroup, QPropertyAnimation,
                          Qt, pyqtSignal, pyqtProperty, QEvent, QRect)
from PyQt5.QtGui import QColor, QPixmap, QPainter
from PyQt5.QtWidgets import QPushButton, QScrollArea, QToolButton, QWidget


class ToolButton(QToolButton):
    """ Tool button with opacity effect """

    def __init__(self, iconPath: str, parent=None):
        super().__init__(parent)
        self.__opacity = 1
        self.isEnter = False
        self.isPressed = False
        self.iconPath = iconPath
        self.setFixedSize(25, 301)
        self.installEventFilter(self)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setOpacity(self.__opacity)

        # draw background
        painter.setPen(Qt.NoPen)
        color = QColor(getIconColor())
        if self.isPressed:
            color.setAlpha(0.6*255)
        elif self.isEnter:
            color.setAlpha(0.5*255)
        else:
            color.setAlpha(0.4*255)

        painter.setBrush(color)
        painter.drawRect(self.rect())

        # draw icon
        drawSvgIcon(self.iconPath, painter, QRect(5, 143, 15, 15))

    def eventFilter(self, obj, e):
        if obj is self:
            if e.type() == QEvent.Enter:
                self.isEnter = True
                self.update()
            elif e.type() == QEvent.Leave:
                self.isEnter = False
                self.isPressed = False
                self.update()
            elif e.type() == QEvent.MouseButtonPress:
                self.isPressed = True
                self.update()
            elif e.type() == QEvent.MouseButtonRelease:
                self.isPressed = False
                self.update()

        return super().eventFilter(obj, e)

    def getOpacity(self):
        return self.__opacity

    def setOpacity(self, opacity):
        self.__opacity = opacity
        self.update()

    opacity = pyqtProperty(float, getOpacity, setOpacity)


class GroupBox(QScrollArea):
    """ Group box """

    switchToMoreSearchResultInterfaceSig = pyqtSignal()
    qss = 'album_group_box'

    def __init__(self, library: Library, view, parent=None):
        super().__init__(parent=parent)
        self.setWidget(view)
        self.library = library
        self.titleButton = QPushButton('Title', self)
        self.scrollLeftButton = ToolButton(
            ':/images/search_result_interface/ChevronLeft.svg', self)
        self.scrollRightButton = ToolButton(
            ':/images/search_result_interface/ChevronRight.svg', self)
        self.opacityAniGroup = QParallelAnimationGroup(self)
        self.leftOpacityAni = QPropertyAnimation(
            self.scrollLeftButton, b'opacity', self)
        self.rightOpacityAni = QPropertyAnimation(
            self.scrollRightButton, b'opacity', self)
        self.scrollAni = QPropertyAnimation(
            self.horizontalScrollBar(), b'value', self)

        c = getIconColor()
        self.showAllButton = ThreeStatePushButton(
            {
                "normal": f":/images/search_result_interface/ShowAll_normal_{c}.svg",
                "hover": f":/images/search_result_interface/ShowAll_hover_{c}.svg",
                "pressed": f":/images/search_result_interface/ShowAll_pressed_{c}.svg",
            },
            self.tr(' Show All'),
            (14, 14),
            self,
        )

        self.leftMask = QWidget(self)
        self.rightMask = QWidget(self)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setFixedHeight(343)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollLeftButton.raise_()
        self.scrollRightButton.raise_()

        self.__setQss()
        self.titleButton.move(37, 0)
        self.leftMask.move(0, 47)
        self.leftMask.resize(35, 296)
        self.rightMask.resize(65, 296)
        self.scrollLeftButton.move(35, 42)
        self.scrollLeftButton.hide()
        self.scrollRightButton.hide()
        self.leftMask.hide()
        self.resize(1200, 343)

        self.__connectSignalToSlot()

    def __setQss(self):
        """ set style sheet """
        self.leftMask.setObjectName('leftMask')
        self.rightMask.setObjectName('rightMask')
        self.titleButton.setObjectName('titleButton')
        self.showAllButton.setObjectName('showAllButton')
        setStyleSheet(self, self.qss)
        self.titleButton.adjustSize()
        self.showAllButton.adjustSize()

    def resizeEvent(self, e):
        self.rightMask.move(self.width()-65, 47)
        self.scrollRightButton.move(self.width()-90, 42)
        self.showAllButton.move(self.width()-self.showAllButton.width()-30, 5)

    def __onScrollHorizon(self, value):
        """ scroll horizontally slot """
        self.leftMask.setHidden(value == 0)
        self.rightMask.setHidden(value == self.horizontalScrollBar().maximum())
        self.scrollLeftButton.setHidden(value == 0)
        self.scrollRightButton.setHidden(
            value == self.horizontalScrollBar().maximum())

    def __onScrollRightButtonClicked(self):
        """ scroll right button clicked slot """
        v = self.horizontalScrollBar().value()
        self.scrollAni.setStartValue(v)
        self.scrollAni.setEndValue(
            min(v+868, self.horizontalScrollBar().maximum()))
        self.scrollAni.setDuration(450)
        self.scrollAni.setEasingCurve(QEasingCurve.OutQuad)
        self.scrollAni.start()

    def __onScrollLeftButtonClicked(self):
        """ scroll left button clicked slot """
        v = self.horizontalScrollBar().value()
        self.scrollAni.setStartValue(v)
        self.scrollAni.setEndValue(max(v-868, 0))
        self.scrollAni.setDuration(450)
        self.scrollAni.setEasingCurve(QEasingCurve.OutQuad)
        self.scrollAni.start()

    def enterEvent(self, e):
        if self.horizontalScrollBar().maximum() == 0:
            return

        # remove old animations
        if self.opacityAniGroup.indexOfAnimation(self.leftOpacityAni) >= 0:
            self.opacityAniGroup.removeAnimation(self.leftOpacityAni)
        if self.opacityAniGroup.indexOfAnimation(self.rightOpacityAni) >= 0:
            self.opacityAniGroup.removeAnimation(self.rightOpacityAni)

        v = self.horizontalScrollBar().value()
        if v != 0:
            self.scrollLeftButton.show()
            self.leftOpacityAni.setStartValue(0)
            self.leftOpacityAni.setEndValue(1)
            self.leftOpacityAni.setDuration(200)
            self.opacityAniGroup.addAnimation(self.leftOpacityAni)

        if v != self.horizontalScrollBar().maximum():
            self.scrollRightButton.show()
            self.rightOpacityAni.setStartValue(0)
            self.rightOpacityAni.setEndValue(1)
            self.rightOpacityAni.setDuration(200)
            self.opacityAniGroup.addAnimation(self.rightOpacityAni)

        self.opacityAniGroup.start()

    def leaveEvent(self, e):
        if self.horizontalScrollBar().maximum() == 0:
            return

        # remove old animations
        if self.opacityAniGroup.indexOfAnimation(self.leftOpacityAni) >= 0:
            self.opacityAniGroup.removeAnimation(self.leftOpacityAni)
        if self.opacityAniGroup.indexOfAnimation(self.rightOpacityAni) >= 0:
            self.opacityAniGroup.removeAnimation(self.rightOpacityAni)

        if self.scrollLeftButton.isVisible():
            self.leftOpacityAni.setStartValue(1)
            self.leftOpacityAni.setEndValue(0)
            self.leftOpacityAni.setDuration(200)
            self.opacityAniGroup.addAnimation(self.leftOpacityAni)

        if self.scrollRightButton.isVisible():
            self.rightOpacityAni.setStartValue(1)
            self.rightOpacityAni.setEndValue(0)
            self.leftOpacityAni.setDuration(200)
            self.opacityAniGroup.addAnimation(self.rightOpacityAni)

        self.opacityAniGroup.start()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.titleButton.clicked.connect(
            self.switchToMoreSearchResultInterfaceSig)
        self.showAllButton.clicked.connect(
            self.switchToMoreSearchResultInterfaceSig)

        self.horizontalScrollBar().valueChanged.connect(self.__onScrollHorizon)
        self.scrollLeftButton.clicked.connect(self.__onScrollLeftButtonClicked)
        self.scrollRightButton.clicked.connect(
            self.__onScrollRightButtonClicked)
