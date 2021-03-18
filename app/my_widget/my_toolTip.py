# coding:utf-8
import sys
from random import choice

from app.my_functions.auto_wrap import autoWrap
from PyQt5.QtCore import QEvent, Qt, QTimer
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen
from PyQt5.QtWidgets import (QApplication, QGraphicsDropShadowEffect,
                             QHBoxLayout, QLabel, QWidget)


class ToolTip(QWidget):
    """ 气泡的父级窗口 """

    def __init__(self, text: str = '', parent=None):
        super().__init__(parent)

        # 实例化气泡子窗口
        self.subToolTip = SubToolTip(text, parent=self)
        # 实例化布局和定时器
        self.all_h_layout = QHBoxLayout()
        self.timer = QTimer(self)
        # 初始化部件和布局
        self.initWidget()
        self.initLayout()

    def initWidget(self):
        """ 初始化小部件 """
        # 设置自己为无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        # 设置背景透明和鼠标穿透
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet('background:transparent')
        self.setAutoFillBackground(False)
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.timeoutEvent)
        # 引用子窗口的setText成员函数
        self.setText = self.subToolTip.setText
        self.isWordWrap = self.subToolTip.isWordWrap

    def initLayout(self):
        """ 初始化布局 """
        self.all_h_layout.addWidget(self.subToolTip, 0, Qt.AlignCenter)
        self.all_h_layout.setContentsMargins(40,40,40,40)
        # 根据布局的内小部件大小调整窗体大小
        self.all_h_layout.setSizeConstraint(QHBoxLayout.SetFixedSize)
        self.setLayout(self.all_h_layout)

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
        """ 隐藏提示条并停止定时器 """
        if not self.timer.isActive():
            self.timer.stop()
        super().hide()

    def leaveEvent(self, e):
        # 由于自己会捕获leaveEvent，所以如果自己leaveEvent被触发说明兄弟部件的leaveEvent也被触发了
        self.hide()


class SubToolTip(QWidget):
    """ 自定义圆角提示气泡子窗口 """

    def __init__(self,text='',parent=None):
        super().__init__(parent)

        # 换行标志位
        self.isWordWrap = False

        # 实例化小部件
        self.timer = QTimer(self)
        self.label = QLabel(text, self)
        self.all_h_layout = QHBoxLayout()
        self.dropShadowEffect = QGraphicsDropShadowEffect(self)
        # 初始化小部件
        self.initLayout()
        self.initWidget()
        self.setText(text)

    def initWidget(self):
        """ 初始化小部件 """
        self.setMaximumSize(400,60)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.label.setStyleSheet(""" QLabel{font:15px "Microsoft YaHei";
                                            background:transparent} """)
        # 设置阴影
        self.dropShadowEffect.setBlurRadius(40)
        self.dropShadowEffect.setOffset(0,5)
        self.setGraphicsEffect(self.dropShadowEffect)

    def initLayout(self):
        """ 初始化布局 """
        self.all_h_layout.addWidget(self.label, 0, Qt.AlignCenter)
        self.all_h_layout.setContentsMargins(9, 9, 9, 9)
        # 根据布局的内小部件大小调整窗体大小
        self.all_h_layout.setSizeConstraint(QHBoxLayout.SetFixedSize)
        self.setLayout(self.all_h_layout)

    def setText(self,text:str):
        """ 设置提示文字 """
        newText, self.isWordWrap = autoWrap(text, 48)
        self.label.setText(newText)
        # 如果有换行发生就调整宽度
        if self.isWordWrap:
            self.setMaximumHeight(60)
        else:
            self.setMaximumHeight(38)

    def paintEvent(self, e):
        """ 绘制圆角背景 """
        pen = QPen(QColor(204, 204, 204))
        painter = QPainter(self)
        # 反锯齿
        painter.setRenderHint(QPainter.Antialiasing)
        # 绘制边框
        painter.setPen(pen)
        # 绘制背景
        brush = QBrush(QColor(242, 242, 242))
        painter.setBrush(brush)
        painter.drawRoundedRect(self.rect(), 7, 7)


class Demo(QWidget):
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
        self.label.move(250, 75)
        self.setStyleSheet('background:white')
        self.label.installEventFilter(self)

    def eventFilter(self, obj, e):
        if obj == self.label:
            if e.type() == QEvent.Enter:
                self.toolTip.setText(choice(self.text_list))
                self.toolTip.move(self.cursor().pos().x()-25,self.cursor().pos().y()-30)
                self.toolTip.show()
                return True
        return super().eventFilter(obj,e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
