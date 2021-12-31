# coding:utf-8
from common.thread.blur_cover_thread import BlurCoverThread
from PyQt5.QtCore import Qt, pyqtSignal
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
        self.luminosityColor.setAlpha(50)

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
            Qt.black, tintOpacity=0.3, parent=self)
        self.blurPixmap = QPixmap()
        self.blurThread = BlurCoverThread(self)
        self.blurThread.blurFinished.connect(self.__onBlurFinished)

    def __onBlurFinished(self, blurPixmap: QPixmap):
        """ 磨砂完成槽函数 """
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
