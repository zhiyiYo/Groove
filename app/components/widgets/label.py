# coding:utf-8
from typing import Union

from common.picture import Cover
from common.thread.blur_cover_thread import BlurCoverThread
from PyQt5.QtCore import QPropertyAnimation, Qt, pyqtProperty, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QImage, QImageReader, QMouseEvent, QPainter, QPixmap
from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtSvg import QSvgWidget


class ClickableLabel(QLabel):
    """ Clickable label """

    clicked = pyqtSignal()

    def __init__(self, text="", parent=None, isSendEventToParent: bool = True):
        super().__init__(text, parent)
        self.isSendEventToParent = isSendEventToParent

    def mousePressEvent(self, e):
        if self.isSendEventToParent:
            super().mousePressEvent(e)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.isSendEventToParent:
            super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self.clicked.emit()


class AvatarLabel(QLabel):
    """ Circle avatar label """

    def __init__(self, imagePath: str, parent=None):
        super().__init__(parent)
        self.__pixmap = QPixmap(imagePath)
        self.setScaledContents(True)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def setPixmap(self, pixmap: QPixmap) -> None:
        self.__pixmap = pixmap
        self.update()

    def paintEvent(self, e):
        """ paint avatar """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        w = self.width()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.__pixmap.scaled(
            w, w, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)))
        painter.drawRoundedRect(self.rect(), w//2, w//2)


class FadeInLabel(QLabel):
    """ Fade in label """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.__opacity = 0
        self.__pixmap = None
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.ani = QPropertyAnimation(self, b'opacity', self)
        self.ani.setDuration(400)

    def getOpacity(self):
        return self.__opacity

    def setOpacity(self, opacity: float):
        self.__opacity = opacity
        self.update()

    def setPixmap(self, pixmap: QPixmap):
        self.__opacity = 0
        self.__pixmap = pixmap
        self.update()

    def pixmap(self):
        return self.__pixmap

    def paintEvent(self, e):
        """ paint label """
        if not self.__pixmap:
            return

        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        painter.setOpacity(self.__opacity)
        painter.drawPixmap(0, 0, self.__pixmap)

    opacity = pyqtProperty(float, getOpacity, setOpacity)


class FadeOutMaskLabel(FadeInLabel):
    """ fade out mask label """

    def fadeOut(self):
        """ show and fade out mask """
        if self.ani.state() == self.ani.Running:
            return

        self.ani.setStartValue(1)
        self.ani.setEndValue(0)
        self.ani.setDuration(300)
        self.ani.start()

    def resizeEvent(self, e):
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.black)
        self.setPixmap(pixmap)


class AcrylicTextureLabel(QLabel):
    """ Acrylic texture label """

    def __init__(self, tintColor: QColor, luminosityColor: QColor = Qt.white, tintOpacity=0.7,
                 noiseOpacity=0.03, parent=None):
        """
        Parameters
        ----------
        tintColor: QColor
            RGB tint color

        luminosityColor: QColor
            luminosity color

        tintOpacity: float
            opacity of tint color layer

        noiseOpacity: float
            opacity of noise layer

        parent:
            parent window
        """
        super().__init__(parent=parent)
        self.tintColor = QColor(tintColor)
        self.luminosityColor = QColor(luminosityColor)
        self.tintOpacity = tintOpacity
        self.noiseOpacity = noiseOpacity
        self.noiseImage = QImage(':/images/acrylic/noise.png')
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.luminosityColor.setAlpha(0)

    def setTintColor(self, color: QColor):
        """ set tint color """
        self.tintColor = color
        self.update()

    def paintEvent(self, e):
        """ paint acrylic texture """
        acrylicTexture = QImage(64, 64, QImage.Format_ARGB32_Premultiplied)

        # paint luminosity layer
        acrylicTexture.fill(self.luminosityColor)

        # paint tint color layer
        painter = QPainter(acrylicTexture)
        painter.setOpacity(self.tintOpacity)
        painter.fillRect(acrylicTexture.rect(), self.tintColor)

        # paint noise layer
        painter.setOpacity(self.noiseOpacity)
        painter.drawImage(acrylicTexture.rect(), self.noiseImage)

        acrylicBrush = QBrush(acrylicTexture)
        painter = QPainter(self)
        painter.fillRect(self.rect(), acrylicBrush)


class BlurCoverLabel(QLabel):
    """ Blur cover label """

    def __init__(self, blurRadius=6, maxBlurSize=(450, 450), parent=None):
        """
        Parameters
        ----------
        blurRadius: int
            blur radius

        maxBlurSize: tuple
            the maximum size of image, if the actual picture exceeds this size,
            it will be scaled to speed up the computation speed.

        parent:
            parent window
        """
        super().__init__(parent=parent)
        self.blurRadius = blurRadius
        self.maxBlurSize = maxBlurSize
        self.coverPath = ''
        self.acrylicTextureLabel = AcrylicTextureLabel(
            Qt.black, tintOpacity=0.4, parent=self)
        self.blurPixmap = QPixmap()
        self.blurThread = BlurCoverThread(self)
        self.blurThread.blurFinished.connect(self.__onBlurFinished)

    def __onBlurFinished(self, blurPixmap: QPixmap, color: QColor):
        """ blur finished slot """
        self.acrylicTextureLabel.setTintColor(color)
        self.blurPixmap = blurPixmap
        self.adjustCover()

    def setCover(self, cover: Union[str, Cover]):
        """ set the cover to blur """
        if isinstance(cover, Cover):
            cover = cover.path()

        if cover == self.coverPath:
            return

        self.coverPath = cover
        self.blurThread.setCover(cover, self.blurRadius, self.maxBlurSize)
        self.blurThread.start()

    def adjustCover(self):
        """ adjust cover size """
        if self.blurPixmap.isNull():
            return

        widget = self.parent() or self
        w = max(widget.height(), widget.width())
        self.setPixmap(self.blurPixmap.scaled(
            w, w, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))

    def setForegroundColor(self, color: QColor):
        """ set foreground color """
        self.acrylicTextureLabel.setTintColor(color)

    def setBlurRadius(self, radius: int):
        """ set blur radius """
        self.blurRadius = max(0, radius)
        self.blurThread.setCover(self.coverPath, self.blurRadius, self.maxBlurSize)
        self.blurThread.start()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.acrylicTextureLabel.resize(self.size())


class TimeLabel(QLabel):
    """ Time label """

    def __init__(self, time: int, parent=None):
        """
        Parameters
        ----------
        time: int
            time in seconds

        parent:
            parent window
        """
        super().__init__(self.__parseTime(time), parent)

    def setTime(self, time: int):
        """ set time

        Parameters
        ----------
        time: int
            time in seconds
        """
        self.setText(self.__parseTime(time))

    @staticmethod
    def __parseTime(time: int):
        """ parse integer time to string """
        minutes = time // 60
        seconds = time % 60
        t = f"{minutes}:{str(seconds).rjust(2,'0')}"
        return t


class MaskLabel(QLabel):
    """ Mask label """

    def __init__(self, color: QColor, parent=None):
        """
        Parameters
        ----------
        color: QColor
            mask color

        parent:
            parent window
        """
        super().__init__(parent=parent)
        self.color = color
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, e):
        """ paint mask """
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.color)
        painter.drawRect(self.rect())


class PixmapLabel(QLabel):
    """ Label for high dpi pixmap """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__pixmap = QPixmap()

    def setPixmap(self, pixmap: QPixmap):
        self.__pixmap = pixmap
        self.setFixedSize(pixmap.size())
        self.update()

    def pixmap(self):
        return self.__pixmap

    def paintEvent(self, e):
        if self.__pixmap.isNull():
            return

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        painter.drawPixmap(self.rect(), self.__pixmap)


class ErrorIcon(QSvgWidget):
    """ Error icon """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(19, 19)
        self.load(":/images/song_list_widget/Info_red.svg")


class AlbumCover(QWidget):
    """ Album cover """

    def __init__(self, imagePath: str, size=(200, 200), parent=None):
        """
        Parameters
        ----------
        imagePath: str
            album cover path

        size: tuple
            cover size

        parent:
            parent window
        """
        super().__init__(parent=parent)
        self.setFixedSize(*size)
        self.setCover(imagePath)

    def setCover(self, imagePath: str):
        """ update album cover """
        self.imagePath = imagePath
        # lazy load
        self.__image = QImage()
        self.update()

    def paintEvent(self, e):
        if self.__image.isNull():
            reader = QImageReader(self.imagePath)
            reader.setScaledSize(self.size())
            reader.setAutoTransform(True)
            self.__image = reader.read()

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        painter.drawImage(self.rect(), self.__image)

