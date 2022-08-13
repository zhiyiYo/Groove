# coding:utf-8
from common.style_sheet import setStyleSheet
from PyQt5.QtCore import (QEasingCurve, QPoint, QPropertyAnimation, QSize, Qt,
                          QTimer, pyqtSignal)
from PyQt5.QtGui import QColor, QPainter, QPixmap
from PyQt5.QtWidgets import (QApplication, QFrame, QGraphicsDropShadowEffect,
                             QGraphicsOpacityEffect, QHBoxLayout, QLabel,
                             QToolButton, QWidget)


class Tooltip(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.__text = text
        self.__duration = 1000
        self.timer = QTimer(self)
        self.hBox = QHBoxLayout(self)
        self.label = QLabel(text, self)
        self.ani = QPropertyAnimation(self, b'windowOpacity', self)

        # set layout
        self.hBox.addWidget(self.label)
        self.hBox.setContentsMargins(10, 7, 10, 7)

        # add shadow
        self.shadowEffect = QGraphicsDropShadowEffect(self)
        self.shadowEffect.setBlurRadius(32)
        self.shadowEffect.setColor(QColor(0, 0, 0, 60))
        self.shadowEffect.setOffset(0, 5)
        self.setGraphicsEffect(self.shadowEffect)

        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

        # set style
        self.setDarkTheme(False)
        self.__setQss()

    def text(self):
        return self.__text

    def setText(self, text: str):
        """ set text on tooltip """
        if text == self.__text:
            return

        self.__text = text
        self.label.setText(text)
        self.label.adjustSize()
        self.adjustSize()

    def setDuration(self, duration: int):
        """ set tooltip duration in milliseconds """
        self.__duration = abs(duration)

    def __setQss(self):
        """ set style sheet """
        setStyleSheet(self, 'tooltip')
        self.label.adjustSize()
        self.adjustSize()

    def setDarkTheme(self, dark=False):
        """ set dark theme """
        dark = 'true' if dark else 'false'
        self.setProperty('dark', dark)
        self.label.setProperty('dark', dark)
        self.setStyle(QApplication.style())

    def showEvent(self, e):
        self.timer.stop()
        self.timer.start(self.__duration)
        super().showEvent(e)

    def hideEvent(self, e):
        self.timer.stop()
        super().hideEvent(e)

    def adjustPos(self, pos: QPoint, size: QSize):
        """ adjust the position of tooltip relative to widget

        Parameters
        ----------
        pos: QPoint
            the position of widget in main window

        size: QSize
            size of widget
        """
        x = pos.x() + size.width()//2 - self.width()//2
        y = pos.y() - self.height() -2

        # adjust postion to prevent tooltips from appearing outside the window
        w = self.window()
        x = min(max(5, x), w.width() - self.width() - 5)
        y = min(max(5, y), w.height() - self.height() - 5)

        self.move(x, y)



class StateTooltip(QWidget):
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
        self.busyImage = QPixmap(":/images/state_tooltip/running.png")
        self.doneImage = QPixmap(":/images/state_tooltip/completed.png")
        self.closeButton = QToolButton(self)

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
        setStyleSheet(self, 'state_tooltip')
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
            if isinstance(widget, (StateTooltip, ToastTooltip)):
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
        painter.setRenderHints(QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        if not self.isDone:
            painter.translate(24, 23)
            painter.rotate(self.rotateAngle)
            painter.drawPixmap(
                -int(self.busyImage.width() / 2),
                -int(self.busyImage.height() / 2),
                self.busyImage,
            )
        else:
            painter.drawPixmap(14, 13, self.doneImage.width(),
                               self.doneImage.height(), self.doneImage)


class DownloadStateTooltip(StateTooltip):
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


class ToastTooltip(QWidget):
    """ Toast tooltip """

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
        self.icon = f":/images/state_tooltip/{icon}.png"

        self.titleLabel = QLabel(self.title, self)
        self.contentLabel = QLabel(self.content, self)
        self.iconLabel = QLabel(self)
        self.closeButton = QToolButton(self)
        self.closeTimer = QTimer(self)
        self.opacityEffect = QGraphicsOpacityEffect(self)
        self.opacityAni = QPropertyAnimation(self.opacityEffect, b"opacity")
        self.slideAni = QPropertyAnimation(self, b'pos')

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setAttribute(Qt.WA_StyledBackground)
        self.closeTimer.setInterval(2000)
        self.contentLabel.setMinimumWidth(250)

        self.iconLabel.setPixmap(QPixmap(self.icon))
        self.iconLabel.adjustSize()
        self.iconLabel.move(15, 13)

        self.setGraphicsEffect(self.opacityEffect)
        self.opacityEffect.setOpacity(1)

        # connect signal to slot
        self.closeButton.clicked.connect(self.hide)
        self.closeTimer.timeout.connect(self.__fadeOut)

        self.__setQss()
        self.__initLayout()

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
        setStyleSheet(self, 'state_tooltip')
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
            if isinstance(widget, (StateTooltip, ToastTooltip)):
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
        self.closeTimer.start()
