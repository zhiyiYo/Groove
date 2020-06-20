import sys

from PyQt5.QtCore import Qt, QTimer,QPoint
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen
from PyQt5.QtWidgets import (QApplication, QDialog, QGraphicsDropShadowEffect,
                             QHBoxLayout, QLabel, QWidget)


class ToolTip(QDialog):
    """ 自定义圆角提示气泡 """

    def __init__(self,text,parent=None):
        super().__init__(parent)
        # 设置窗口类型为ToolTip
        self.setMaximumWidth(387)
        self.setMinimumHeight(38)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.timer = QTimer(self)
        self.text = QLabel(text, self)
        self.h_layout = QHBoxLayout(self)
        self.dropShadowEffect = QGraphicsDropShadowEffect(self)
        self.initWidget()
        self.initLayout()

    def initWidget(self):
        """ 初始化小部件 """
        # 引用设置标签的方法
        self.setText = self.text.setText
        self.text.setStyleSheet(""" QLabel{font:15px "Microsoft YaHei";background:transparent} """)
        # 设置阴影
        self.dropShadowEffect.setBlurRadius(40)
        self.dropShadowEffect.setOffset(0,3)
        self.setGraphicsEffect(self.dropShadowEffect)
        # 设置定时器
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.timeoutEvent)

    def initLayout(self):
        """ 初始化布局 """
        self.h_layout.addWidget(self.text, 0, Qt.AlignCenter)
        self.h_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.h_layout)

    def paintEvent(self, e):
        """ 绘制圆角背景 """
        pen = QPen(QColor(204,204,204))
        painter = QPainter(self)
        # 反锯齿
        painter.setRenderHint(QPainter.Antialiasing)
        # 绘制边框
        painter.setPen(pen)
        painter.drawRoundedRect(self.rect(), 10, 10)
        # 绘制背景
        brush = QBrush(QColor(242, 242, 242))
        painter.setBrush(brush)
        painter.drawRoundedRect(self.rect(), 10, 10)

    def timeoutEvent(self):
        """ 定时器溢出时隐藏提示条 """
        self.hide()
        self.timer.stop()

    def show(self):
        """ 显示提示条并打开定时器 """
        # 窗口置顶
        self.raise_()
        self.timer.start()
        super().show()

    def hide(self):
        """ 隐藏提示条并停止计时器 """
        self.timer.stop()
        super().hide()
        
class Father(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(500, 200)
        self.toolTip = ToolTip('RADWIMPS 2 ～発展途上～', self)
        self.toolTip.hide()
        self.label = QLabel('测试', self)
        self.label.move(150, 100)
        self.setStyleSheet('background:white')

    def enterEvent(self, e):
        self.toolTip.move(150, 100)
        self.toolTip.show()

    def leaveEvent(self, e):
        self.toolTip.hide()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Father()
    demo.show()
    sys.exit(app.exec_())
