import sys

from PyQt5.QtCore import QPoint, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QMouseEvent,QEnterEvent
from PyQt5.QtWidgets import QApplication, QLabel, QToolTip, QWidget
#from my_toolTip import ToolTip


class ClickableLabel(QLabel):
    """ 定义可发出点击信号的Label """
    # 创建点击信号
    clicked = pyqtSignal()

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        #储存原始的text
        self.rawText=text
        self.customToolTip = None 

    def mouseReleaseEvent(self, event: QMouseEvent):
        """ 鼠标松开时发送信号 """
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

    def setCustomToolTip(self,toolTip,toolTipText:str, x, y):
        """ 设置提示条和提示条出现的位置 """
        self.customToolTip = toolTip
        self.customToolTipText = toolTipText
        # 设置提示条的默认显示位置
        self.toolTipX = x
        self.toolTipY = y
        
    def enterEvent(self, e:QEnterEvent):
        """ 如果有设置提示条的话就显示提示条 """
        if self.customToolTip:
            self.customToolTip.setText(self.customToolTipText)
            self.customToolTip.move(
                self.toolTipX + e.x(), self.toolTipY + e.y() - self.customToolTip.isWordWrap * 30)
            self.customToolTip.show()

    def leaveEvent(self, e):
        """ 鼠标离开按钮时减小按钮并隐藏提示条 """
        if self.customToolTip:
            self.customToolTip.hide()


class ErrorLabel(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.enterTime = 0
        # 设置提示条
        self.customToolTip = None

    def enterEvent(self, e):
        """ 鼠标进入时显示提示条 """
        if self.customToolTip:
            self.customToolTip.setText(self.customToolTipText)
            # 有折叠发生时需要再加一个偏移量
            self.customToolTip.move(self.x() + e.x() + 7,self.y() + e.y() - 40)
            self.customToolTip.show()

    def leaveEvent(self, e):
        """ 鼠标移出时隐藏提示条 """
        if self.customToolTip:
            self.customToolTip.hide()

    def setCustomToolTip(self, toolTip, text:str):
        """ 设置提示条和提示条内容 """
        self.customToolTip = toolTip
        self.customToolTipText = text


class Demo(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(600,400)
        toolTipText='这是一个自定义可点击的标签没错他特呃呃呃呃呃呃额别长'*2
        self.label = ClickableLabel('这是一个自定义可点击的标签', self)
        self.customToolTip = ToolTip(toolTipText, self)
        
        self.label.move(50,180)
        self.label.setCursor(Qt.PointingHandCursor)
        self.label.clicked.connect(lambda: print(self.label.text()))
        self.label.setCustomToolTip(self.customToolTip,toolTipText,50,180)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
