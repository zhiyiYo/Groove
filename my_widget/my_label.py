import sys

from PyQt5.QtCore import QPoint, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QLabel, QToolTip, QWidget


class ClickableLabel(QLabel):
    """ 定义可发出点击信号的Label """
    # 创建点击信号
    clicked = pyqtSignal()

    def __init__(self, text, parent=None,toolTip=None):
        super().__init__(text, parent)
        self.customToolTip = toolTip 

    def mouseReleaseEvent(self, event: QMouseEvent):
        """ 鼠标松开时发送信号 """
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

    def enterEvent(self, e):
        """ 如果有设置提示条的话就显示提示条 """
        if self.customToolTip:
            self.customToolTip.setText(self.text())
            try:
                self.customToolTip.move(self.parent().x() + 10 + -self.customToolTip.width()/2,
                                        self.parent().y() + 266 - 50)
            except:
                print('提示条定位失败')
            else:
                self.customToolTip.show()

    def leaveEvent(self, e):
        """ 鼠标离开按钮时减小按钮并隐藏提示条 """
        if self.customToolTip:
            self.customToolTip.hide()


class ErrorLabel(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.enterTime = 0

        # 定时器用于控制提示条的显示时间
        self.timer = QTimer(self)
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.hideToolTip)

    def enterEvent(self, e):
        if not self.enterTime:
            self.timer.start()
            x = e.globalX()-110
            y = e.globalY() - 80
            QToolTip.showText(QPoint(x, y), '曲目必须是1000以下的数字', self)
            self.enterTime = 1

    def hideToolTip(self):
        QToolTip.hideText()
        self.timer.stop()

    def leaveEvent(self, e):
        self.enterTime = 0
        self.timer.stop()


class Demo(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(100, 100)
        self.label = ClickableLabel('这是一个自定义可点击的标签', self)
        self.label.setCursor(Qt.PointingHandCursor)
        self.label.clicked.connect(lambda: print(self.label.text()))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
