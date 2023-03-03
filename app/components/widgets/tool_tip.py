# coding:utf-8
from common.icon import drawSvgIcon
from common.style_sheet import setStyleSheet
from components.buttons.three_state_button import ThreeStateButton
from PyQt5.QtCore import (QEasingCurve, QPoint, QPropertyAnimation, QSize, Qt,
                          QTimer, pyqtSignal, QRect)
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import (QApplication, QFrame, QGraphicsDropShadowEffect,
                             QGraphicsOpacityEffect, QHBoxLayout, QLabel,
                             QWidget)
from PyQt5.QtSvg import QSvgWidget


class ToolTip(QFrame):
    """ Tool tip """

    def __init__(self, text='', parent=None):
        super().__init__(parent=parent)
        self.__text = text
        self.__duration = 1000
        self.container = QFrame(self)
        self.timer = QTimer(self)

        self.setLayout(QHBoxLayout())
        self.containerLayout = QHBoxLayout(self.container)
        self.label = QLabel(text, self)

        # set layout
        self.layout().setContentsMargins(12, 8, 15, 12)
        self.layout().addWidget(self.container)
        self.containerLayout.addWidget(self.label)
        self.containerLayout.setContentsMargins(10, 7, 10, 7)

        # add shadow
        self.shadowEffect = QGraphicsDropShadowEffect(self)
        self.shadowEffect.setBlurRadius(32)
        self.shadowEffect.setColor(QColor(0, 0, 0, 60))
        self.shadowEffect.setOffset(0, 5)
        self.container.setGraphicsEffect(self.shadowEffect)

        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

        # set style
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setDarkTheme(False)
        self.__setQss()

    def text(self):
        return self.__text

    def setText(self, text):
        """ set text on tooltip """
        self.__text = text
        self.label.setText(text)
        self.container.adjustSize()
        self.adjustSize()

    def duration(self):
        return self.__duration

    def setDuration(self, duration):
        """ set tooltip duration in milliseconds """
        self.__duration = abs(duration)

    def __setQss(self):
        """ set style sheet """
        self.container.setObjectName("container")
        self.label.setObjectName("contentLabel")
        setStyleSheet(self, 'tool_tip')
        self.label.adjustSize()
        self.adjustSize()

    def setDarkTheme(self, dark=False):
        """ set dark theme """
        self.setProperty('dark', dark)
        self.setStyle(QApplication.style())

    def showEvent(self, e):
        self.timer.stop()
        self.timer.start(self.__duration)
        super().showEvent(e)

    def hideEvent(self, e):
        self.timer.stop()
        super().hideEvent(e)

    def adjustPos(self, pos, size):
        """ adjust the position of tooltip relative to widget

        Parameters
        ----------
        pos: QPoint
            global position of widget

        size: QSize
            size of widget
        """
        x = pos.x() + size.width()//2 - self.width()//2
        y = pos.y() - self.height() + 5

        # adjust postion to prevent tooltips from appearing outside the screen
        desk = QApplication.desktop()
        x = min(max(0, x), desk.width() - self.width() - 2)
        y = min(max(0, y), desk.height() - self.height() - 2)

        self.move(x, y)


class StateToolTip(QWidget):
    """ State tooltip """

    closedSignal = pyqtSignal()

    def __init__(self, title, content, parent=None):
        """
        Parameters
        ----------
        title: str
            title of tooltip

        content: str
            content of tooltip

        parant:
            parent window
        """
        super().__init__(parent)
        self.title = title
        self.content = content

        self.titleLabel = QLabel(self.title, self)
        self.contentLabel = QLabel(self.content, self)
        self.rotateTimer = QTimer(self)
        self.closeTimer = QTimer(self)
        self.opacityEffect = QGraphicsOpacityEffect(self)
        self.slideAni = QPropertyAnimation(self, b'pos')
        self.opacityAni = QPropertyAnimation(self.opacityEffect, b"opacity")
        self.busyIconPath = ":/images/state_tool_tip/running.svg"
        self.doneIconPath = ":/images/state_tool_tip/completed.svg"
        self.closeButton = ThreeStateButton(
            {
                'normal': ':/images/state_tool_tip/close_normal.svg',
                'hover': ':/images/state_tool_tip/close_hover.svg',
                'pressed': ':/images/state_tool_tip/close_pressed.svg',
            },
            parent=self,
            buttonSize=(14, 14)
        )

        self.isDone = False
        self.rotateAngle = 0
        self.deltaAngle = 20

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setAttribute(Qt.WA_StyledBackground)
        self.rotateTimer.setInterval(50)
        self.closeTimer.setInterval(1000)
        self.contentLabel.setMinimumWidth(250)
        self.setGraphicsEffect(self.opacityEffect)
        self.opacityEffect.setOpacity(1)

        # connect signal to slot
        self.closeButton.clicked.connect(self.__onCloseButtonClicked)
        self.rotateTimer.timeout.connect(self.__rotateTimerFlowSlot)
        self.closeTimer.timeout.connect(self.__slowlyClose)

        self.__setQss()
        self.__initLayout()

        self.rotateTimer.start()

    def __initLayout(self):
        """ initialize layout """
        self.setFixedSize(max(self.titleLabel.width(),
                          self.contentLabel.width()) + 70, 64)
        self.titleLabel.move(40, 11)
        self.contentLabel.move(15, 34)
        self.closeButton.move(self.width() - 30, 23)

    def __setQss(self):
        """ set style sheet """
        self.titleLabel.setObjectName("titleLabel")
        self.contentLabel.setObjectName("contentLabel")
        setStyleSheet(self, 'state_tool_tip')
        self.titleLabel.adjustSize()
        self.contentLabel.adjustSize()

    def setTitle(self, title: str):
        """ set the title of tooltip """
        self.title = title
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def setContent(self, content: str):
        """ set the content of tooltip """
        self.content = content
        self.contentLabel.setText(content)

        # adjustSize() will mask spinner get stuck
        # self.contentLabel.adjustSize()

    def setState(self, isDone=False):
        """ set the state of tooltip """
        self.isDone = isDone
        self.update()
        if self.isDone:
            self.closeTimer.start()

    def __onCloseButtonClicked(self):
        """ close button clicked slot """
        self.closedSignal.emit()
        self.hide()

    def __slowlyClose(self):
        """ fade out """
        self.rotateTimer.stop()
        self.opacityAni.setEasingCurve(QEasingCurve.Linear)
        self.opacityAni.setDuration(300)
        self.opacityAni.setStartValue(1)
        self.opacityAni.setEndValue(0)
        self.opacityAni.finished.connect(self.deleteLater)
        self.opacityAni.start()

    def __rotateTimerFlowSlot(self):
        """ rotate timer time out slot """
        self.rotateAngle = (self.rotateAngle + self.deltaAngle) % 360
        self.update()

    def getSuitablePos(self):
        """ get suitable position in main window """
        for i in range(10):
            dy = i*(self.height() + 20)
            pos = QPoint(self.window().width() - self.width() - 30, 63+dy)
            widget = self.window().childAt(pos + QPoint(2, 2))
            if isinstance(widget, (StateToolTip, ToastToolTip)):
                pos += QPoint(0, self.height() + 20)
            else:
                break

        return pos

    def showEvent(self, e):
        pos = self.getSuitablePos()
        self.slideAni.setDuration(200)
        self.slideAni.setEasingCurve(QEasingCurve.OutQuad)
        self.slideAni.setStartValue(QPoint(self.window().width(), pos.y()))
        self.slideAni.setEndValue(pos)
        self.slideAni.start()
        super().showEvent(e)

    def paintEvent(self, e):
        """ paint state tooltip """
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        if not self.isDone:
            painter.translate(24, 23)
            painter.rotate(self.rotateAngle)
            drawSvgIcon(self.busyIconPath, painter, QRect(-10, -10, 20, 20))
        else:
            drawSvgIcon(self.doneIconPath, painter, QRect(14, 13, 20, 20))


class DownloadStateToolTip(StateToolTip):
    """ Download state tooltip """

    def __init__(self, title, content, downloadTaskNum=1, parent=None):
        super().__init__(title=title, content=content, parent=parent)
        self.downloadTaskNum = downloadTaskNum

    def completeOneDownloadTask(self):
        """ complete a download task """
        self.downloadTaskNum -= 1
        if self.downloadTaskNum > 0:
            content = self.tr('There are') + f' {self.downloadTaskNum} ' + \
                self.tr('left. Please wait patiently')
            self.setContent(content)
        else:
            self.setTitle(self.tr('Download complete'))
            self.setContent(self.tr('Download completed, please check'))
            self.setState(True)

    def appendOneDownloadTask(self):
        """ add a download task """
        self.downloadTaskNum += 1
        content = self.tr('There are') + f' {self.downloadTaskNum} ' + \
            self.tr('left. Please wait patiently')
        self.setContent(content)


class ToastToolTip(QFrame):
    """ Toast tool tip """

    SUCCESS = "completed"
    WARNING = "info"

    def __init__(self, title: str, content: str, icon: str, parent=None):
        """
        Parameters
        ----------
        title: str
            title of tooltip

        content: str
            content of tooltip

        icon: str
            icon of toast, can be `completed` or `info`

        parant:
            parent window
        """
        super().__init__(parent)
        self.title = title
        self.content = content
        self.icon = f":/images/state_tool_tip/{icon}.png"

        self.titleLabel = QLabel(self.title, self)
        self.contentLabel = QLabel(self.content, self)
        self.iconLabel = QSvgWidget(f":/images/state_tool_tip/{icon}.svg", self)
        self.closeButton = ThreeStateButton(
            {
                'normal': ':/images/state_tool_tip/close_normal.svg',
                'hover': ':/images/state_tool_tip/close_hover.svg',
                'pressed': ':/images/state_tool_tip/close_pressed.svg',
            },
            parent=self,
            buttonSize=(14, 14)
        )
        self.opacityEffect = QGraphicsOpacityEffect(self)
        self.opacityAni = QPropertyAnimation(self.opacityEffect, b"opacity")
        self.slideAni = QPropertyAnimation(self, b'pos')

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setAttribute(Qt.WA_StyledBackground)
        self.closeButton.setFixedSize(QSize(14, 14))
        self.closeButton.setIconSize(QSize(14, 14))
        self.contentLabel.setMinimumWidth(250)

        self.iconLabel.setFixedSize(20, 20)
        self.iconLabel.move(15, 13)

        self.setGraphicsEffect(self.opacityEffect)
        self.opacityEffect.setOpacity(1)

        # connect signal to slot
        self.closeButton.clicked.connect(self.hide)

        self.__setQss()
        self.__initLayout()

    def __initLayout(self):
        """ initialize layout """
        self.setFixedSize(max(self.titleLabel.width(),
                          self.contentLabel.width()) + 80, 64)
        self.titleLabel.move(40, 11)
        self.contentLabel.move(15, 34)
        self.closeButton.move(self.width() - 30, 23)

    def __setQss(self):
        """ set style sheet """
        self.titleLabel.setObjectName("titleLabel")
        self.contentLabel.setObjectName("contentLabel")
        setStyleSheet(self, 'state_tool_tip')
        self.titleLabel.adjustSize()
        self.contentLabel.adjustSize()

    def __fadeOut(self):
        """ fade out """
        self.opacityAni.setDuration(300)
        self.opacityAni.setStartValue(1)
        self.opacityAni.setEndValue(0)
        self.opacityAni.finished.connect(self.deleteLater)
        self.opacityAni.start()

    def getSuitablePos(self):
        """ get suitable position in main window """
        for i in range(10):
            dy = i*(self.height() + 20)
            pos = QPoint(self.window().width() - self.width() - 30, 63+dy)
            widget = self.window().childAt(pos + QPoint(2, 2))
            if isinstance(widget, (StateToolTip, ToastToolTip)):
                pos += QPoint(0, self.height() + 20)
            else:
                break

        return pos

    def showEvent(self, e):
        pos = self.getSuitablePos()
        self.slideAni.setDuration(200)
        self.slideAni.setEasingCurve(QEasingCurve.OutQuad)
        self.slideAni.setStartValue(QPoint(self.window().width(), pos.y()))
        self.slideAni.setEndValue(pos)
        self.slideAni.start()
        super().showEvent(e)
        QTimer.singleShot(2000, self.__fadeOut)

    @classmethod
    def success(cls, title: str, content: str, parent=None):
        """ show a success toast """
        cls(title, content, cls.SUCCESS, parent).show()

    @classmethod
    def warn(cls, title: str, content: str, parent=None):
        """ show a warning toast """
        cls(title, content, cls.WARNING, parent).show()