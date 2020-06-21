import sys
from random import choice
import time
from PyQt5.QtCore import Qt, QTimer,QPoint
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen
from PyQt5.QtWidgets import (QApplication, QDialog, QGraphicsDropShadowEffect,QLayout,
                             QHBoxLayout, QLabel, QWidget)
sys.path.append('..')
from Groove.my_functions.auto_wrap import autoWrap


class ToolTip(QWidget):
    """ 自定义圆角提示气泡 """

    def __init__(self,text='',parent=None):
        super().__init__(parent)
        
        # 实例化小部件
        self.timer = QTimer(self)
        self.label = QLabel(text, self)
        self.all_h_layout = QHBoxLayout()
        self.dropShadowEffect = QGraphicsDropShadowEffect(self)
        # 初始化小部件
        self.initLayout()
        self.initWidget()
        self.setText(text)
        self.hide()

    def initWidget(self):
        """ 初始化小部件 """
        self.setMaximumWidth(400)
        self.setMinimumHeight(38)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.label.setStyleSheet(""" QLabel{font:15px "Microsoft YaHei";
                                            background:transparent} """)
        # 设置阴影
        self.dropShadowEffect.setBlurRadius(40)
        self.dropShadowEffect.setOffset(0,3)
        self.setGraphicsEffect(self.dropShadowEffect)
        # 设置定时器
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.timeoutEvent)

    def initLayout(self):
        """ 初始化布局 """
        self.all_h_layout.addWidget(self.label, 0, Qt.AlignCenter)
        self.all_h_layout.setContentsMargins(9, 9, 9, 9)
        # 根据布局的内小部件大小调整窗体大小
        self.all_h_layout.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(self.all_h_layout)


    def setText(self,text:str):
        """ 设置提示文字 """
        newText, self.isWordWrap = autoWrap(text, 48)
        # 如果有换行发生就调整宽度
        if self.isWordWrap:
            self.setFixedHeight(60)
        else:
            self.setFixedHeight(38)
        self.label.setText(newText)
        

    def paintEvent(self, e):
        """ 绘制圆角背景 """
        pen = QPen(QColor(204,204,204))
        painter = QPainter(self)
        # 反锯齿
        painter.setRenderHint(QPainter.Antialiasing)
        # 绘制边框
        painter.setPen(pen)
        painter.drawRoundedRect(self.rect(), 7, 7)
        # 绘制背景
        brush = QBrush(QColor(242, 242, 242))
        painter.setBrush(brush)
        painter.drawRoundedRect(self.rect(), 7, 7)

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
        self.resize(600, 200)
        self.text_list = ['劇場版「ずっと前から好きでした。～告白実行委員会～」オリジナルサウンドトラック',
                     '天气之子', 'RADWIMPS 2 ～発展途上～', '全部播放', '齐天周大圣之西游双记 电影歌乐游唱版',
                          '', 'My Songs Know What You Did In the Dark (Light Em Up) – Single']
        self.toolTip = ToolTip(parent=self)
        self.toolTip.hide()
        self.toolTip.setText(choice(self.text_list))
        self.label = QLabel('测试', self)
        self.label.move(150, 100)
        self.setStyleSheet('background:white')

    def enterEvent(self, e):
        self.toolTip.setText(choice(self.text_list))
        self.toolTip.move(150, 100)
        self.toolTip.show()

    def leaveEvent(self, e):
        self.toolTip.hide()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Father()
    demo.show()
    sys.exit(app.exec_())
