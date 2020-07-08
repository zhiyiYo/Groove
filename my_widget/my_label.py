import sys

from PyQt5.QtCore import QPoint, Qt, QTimer, pyqtSignal, QEvent
from PyQt5.QtGui import QMouseEvent,QEnterEvent,QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QToolTip, QWidget

sys.path.append('..')
from Groove.my_functions.is_not_leave import isNotLeave
from Groove.my_widget.my_toolTip import ToolTip


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

    def setCustomToolTip(self,toolTip,toolTipText:str):
        """ 设置提示条和提示条出现的位置 """
        self.customToolTip = toolTip
        self.customToolTipText = toolTipText
        
    def enterEvent(self, e:QEnterEvent):
        """ 如果有设置提示条的话就显示提示条 """
        #print('鼠标进入标签事件触发')
        if self.customToolTip:
            self.customToolTip.setText(self.customToolTipText)
            # 有折叠发生时需要再加一个偏移量
            self.customToolTip.move(
                e.globalX() - int(self.customToolTip.width() / 2),
                e.globalY() - 100 - self.customToolTip.isWordWrap * 30)
            self.customToolTip.show()

    def leaveEvent(self, e):
        """ 判断鼠标是否离开标签 """
        if self.parent() and self.customToolTip:
            notLeave = isNotLeave(self)
            if notLeave:
                return
            self.customToolTip.hide()


class ErrorIcon(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置提示条
        self.customToolTip = None
        self.setPixmap(
            QPixmap('resource\\images\\empty_lineEdit_error.png'))
        self.setFixedSize(21, 21)

    def setCustomToolTip(self, toolTip, text:str):
        """ 设置提示条和提示条内容 """
        self.customToolTip = toolTip
        self.customToolTipText = text

    def enterEvent(self, e):
        """ 鼠标进入时显示提示条 """
        #print('鼠标进入标签')
        if self.customToolTip:
            self.customToolTip.setText(self.customToolTipText)
            # 有折叠发生时需要再加一个偏移量
            self.customToolTip.move(
                e.globalX() - int(self.customToolTip.width() / 2),
                e.globalY() - 100 - self.customToolTip.isWordWrap * 30)
            self.customToolTip.show()
            self.hasEnter = True

    def leaveEvent(self, e):
        """ 判断鼠标是否离开标签 """
        if self.parent() and self.customToolTip:
            notLeave = isNotLeave(self)
            if notLeave:
                return
            self.customToolTip.hide()
        

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
