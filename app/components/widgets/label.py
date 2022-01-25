# coding:utf-8
from common.thread.blur_cover_thread import BlurCoverThread
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, pyqtProperty
from PyQt5.QtGui import (QBrush, QColor, QImage, QMouseEvent, QPainter,
                         QPalette, QPixmap)
from PyQt5.QtWidgets import QLabel


class ClickableLabel(QLabel):
    """ 定义可发出点击信号的Label """

    # 创建点击信号
    clicked = pyqtSignal()

    def __init__(self, text="", parent=None, isSendEventToParent: bool = True):
        super().__init__(text, parent)
        self.isSendEventToParent = isSendEventToParent

    def mousePressEvent(self, e):
        """ 处理鼠标点击 """
        if self.isSendEventToParent:
            super().mousePressEvent(e)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """ 鼠标松开时发送信号 """
        if self.isSendEventToParent:
            super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self.clicked.emit()


class ErrorIcon(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPixmap(
            QPixmap(":/images/song_tab_interface/Info_red.png"))
        self.setFixedSize(19, 19)


class AvatarLabel(QLabel):
    """ 圆形头像 """

    def __init__(self, imagePath: str, parent=None):
        super().__init__(parent)
        self.__pixmap = QPixmap(imagePath)
        self.setScaledContents(True)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def setPixmap(self, pixmap: QPixmap) -> None:
        self.__pixmap = pixmap
        self.update()

    def paintEvent(self, e):
        """ 绘制头像 """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        w = self.width()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.__pixmap.scaled(
            w, w, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)))
        painter.drawRoundedRect(self.rect(), w//2, w//2)


class FadeInLabel(QLabel):
    """ 淡入标签 """

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

    def paintEvent(self, e):
        """ 绘制图像 """
        painter = QPainter(self)
        painter.setOpacity(self.__opacity)
        painter.drawPixmap(0, 0, self.__pixmap)

    opacity = pyqtProperty(float, getOpacity, setOpacity)


class FadeOutMaskLabel(FadeInLabel):
    """ 淡出遮罩 """

    def fadeOut(self):
        """ 显示并淡出遮罩 """
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
    """ 亚克力纹理标签 """

    def __init__(self, tintColor: QColor, luminosityColor: QColor = Qt.white, tintOpacity=0.7,
                 noiseOpacity=0.03, parent=None):
        """
        Parameters
        ----------
        tintColor: QColor
            RGB 主色调

        luminosityColor: QColor
            亮度层颜色

        tintOpacity: float
            主色调层透明度

        noiseOpacity: float
            噪声层透明度

        parent:
            父级窗口
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
        """ 设置主色调 """
        self.tintColor = color
        self.update()

    def paintEvent(self, e):
        """ 绘制亚克力纹理 """
        acrylicTexture = QImage(64, 64, QImage.Format_ARGB32_Premultiplied)

        # 绘制亮度层
        acrylicTexture.fill(self.luminosityColor)

        # 绘制主色调
        painter = QPainter(acrylicTexture)
        painter.setOpacity(self.tintOpacity)
        painter.fillRect(acrylicTexture.rect(), self.tintColor)

        # 绘制噪声
        painter.setOpacity(self.noiseOpacity)
        painter.drawImage(acrylicTexture.rect(), self.noiseImage)

        acrylicBrush = QBrush(acrylicTexture)
        painter = QPainter(self)
        painter.fillRect(self.rect(), acrylicBrush)


class BlurCoverLabel(QLabel):
    """ 磨砂封面标签 """

    def __init__(self, blurRadius=6, maxBlurSize=(450, 450), parent=None):
        """
        Parameters
        ----------
        blurRadius: int
            磨砂半径

        maxBlurSize: tuple
            最大磨砂尺寸，越小磨砂速度越快

        parent:
            父级窗口
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
        """ 磨砂完成槽函数 """
        self.acrylicTextureLabel.setTintColor(color)
        self.blurPixmap = blurPixmap
        self.adjustCover()

    def setCover(self, coverPath: str):
        """ 设置封面 """
        if coverPath == self.coverPath:
            return

        self.coverPath = coverPath
        self.blurThread.setCover(coverPath, self.blurRadius, self.maxBlurSize)
        self.blurThread.start()

    def adjustCover(self):
        """ 调整封面尺寸 """
        if self.blurPixmap.isNull():
            return

        widget = self.parent() or self
        w = max(widget.height(), widget.width())
        self.setPixmap(self.blurPixmap.scaled(
            w, w, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))

    def setForegroundColor(self, color: QColor):
        """ 设置前景色 """
        self.acrylicTextureLabel.setTintColor(color)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.acrylicTextureLabel.resize(self.size())


class TimeLabel(QLabel):
    """ 时间标签 """

    def __init__(self, time: int, parent=None):
        """
        Parameters
        ----------
        time: int
            时长，以秒为单位

        parent:
            父级窗口
        """
        super().__init__(self.__parseTime(time), parent)

    def setTime(self, time: int):
        """ 设置时间，以秒为单位 """
        self.setText(self.__parseTime(time))

    @staticmethod
    def __parseTime(time: int):
        """ 解析时长为字符串 """
        minutes = time // 60
        seconds = time % 60
        t = f"{minutes}:{str(seconds).rjust(2,'0')}"
        return t