# coding:utf-8
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QIcon, QPainter
from PyQt5.QtWidgets import QWidget, QPushButton


class AppBarButton(QPushButton):

    def __init__(self, iconPath: str, text: str, parent=None):
        super().__init__(parent)
        self.pixmap = QPixmap(iconPath)
        self.__text = text
        styleSheet = """
        QPushButton {
            border: none;
            border-radius: 23px;
            spacing: 10px;
            color: white;
            background: transparent;
            font: 16px "Microsoft YaHei";
            padding: 13px 24px 13px 24px;
        }

        QPushButton:hover {
            background: rgba(255, 255, 255, 0.2)
        }

        QPushButton:pressed {
            background: rgba(255, 255, 255, 0.5)
        }
        """
        self.setStyleSheet(styleSheet)
        self.adjustSize()

    def sizeHint(self):
        spacing = 12*(self.__text != '')
        w = self.pixmap.width() + spacing + self.fontMetrics().width(self.__text) + 46
        size = QSize(w, 46)
        return size

    def paintEvent(self, e):
        """ 绘制图标 """
        super().paintEvent(e)
        painter = QPainter(self)
        y = (self.height()-self.pixmap.height())//2
        painter.drawPixmap(24, y, self.pixmap)
        painter.setPen(Qt.white)
        painter.setFont(self.font())
        painter.drawText(54, 29, self.__text)
