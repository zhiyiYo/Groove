import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QBrush, QEnterEvent, QPixmap, QScreen,QLinearGradient,QColor,QBitmap
from PyQt5.QtWidgets import (QApplication, QGraphicsBlurEffect, QLabel, QWidget,QGraphicsDropShadowEffect,
                             QPushButton)
from win32api import GetModuleHandle,GetProcAddress

class BlurShadow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(220, 220)
        self.setWindowOpacity(0.9)
        self.setStyleSheet('background:white')
        
        self.blurEffect = QGraphicsBlurEffect(self)
        self.maskImage=QBitmap('resource\\images\\遮罩.png')

        self.blurEffect.setBlurRadius(30)
        self.backLabel = QLabel(self)
        self.backLabel.resize(220,230)
        self.backLabel.setScaledContents(True)
        self.backLabel.setPixmap(
            QPixmap(r'resource\Album Cover\人間開花\人間開花.jpg'))
        self.backLabel.setGraphicsEffect(self.blurEffect)
        self.setMask(self.maskImage)
        print(self.windowHandle())
        self.hinst = GetModuleHandle("user32.dll")
        self.setWindowCompositionAttribute = GetProcAddress(
            self.hinst, 'SetWindowCompositionAttribute')
        print(self.setWindowCompositionAttribute)
        print(self.hinst)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = BlurShadow()
    demo.show()
    sys.exit(app.exec_())

        
