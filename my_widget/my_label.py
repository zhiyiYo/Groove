import sys

from PyQt5.QtCore import QEvent, QPoint, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QEnterEvent, QMouseEvent, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QToolTip, QWidget

from my_functions.get_pressed_pos import getPressedPos
from my_functions.is_not_leave import isNotLeave
from my_functions.perspective_transform import PerspectiveTransform
from my_widget.my_toolTip import ToolTip


class ClickableLabel(QLabel):
    """ 定义可发出点击信号的Label """
    # 创建点击信号
    clicked = pyqtSignal()

    def __init__(self, text='', parent=None, isSendEventToParent:bool=True):
        super().__init__(text, parent)
        self.isSendEventToParent = isSendEventToParent
        #储存原始的text
        self.rawText=text
        self.customToolTip = None

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


class PerspectiveTransformLabel(QLabel):
    """ 可以进行透视变换的Label """

    def __init__(self, picPath, picSize:tuple, parent):
        super().__init__(parent=parent)
        self.resize(picSize[0],picSize[1])
        self.picPath = picPath
        self.picSize = picSize
        self.pressedPix = None
        self.pressedPos = None
        self.perspectiveTrans = None
        self.picPix = QPixmap(self.picPath).scaled(
            self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(self.picPix)

    def mousePressEvent(self, e):
        """ 鼠标点击时对封面进行透视变换 """
        super().mousePressEvent(e)
        # 获取鼠标点击位置
        self.pressedPos = getPressedPos(self, e)
        if not self.perspectiveTrans:
            self.perspectiveTrans = PerspectiveTransform(
                self.picPath, (200, 200))  # type:PerspectiveTransform
            self.perspectiveTrans.pressedPos = None
        # 根据鼠标点击位置的不同设置背景封面的透视变换
        if self.perspectiveTrans.pressedPos != self.pressedPos:
            if self.pressedPos == 'left':
                self.perspectiveTrans.setDstPoints(
                    [5, 4], [self.perspectiveTrans.width - 2, 1],
                    [3, self.perspectiveTrans.height - 3],
                    [self.perspectiveTrans.width - 2, self.perspectiveTrans.height - 1])
            elif self.pressedPos == 'left-top':
                self.perspectiveTrans.setDstPoints(
                    [6, 5], [self.perspectiveTrans.width - 1, 1],
                    [1, self.perspectiveTrans.height - 2],
                    [self.perspectiveTrans.width - 2, self.perspectiveTrans.height - 1])
            elif self.pressedPos == 'left-bottom':
                self.perspectiveTrans.setDstPoints(
                    [2, 3], [self.perspectiveTrans.width - 3, 0],
                    [2, self.perspectiveTrans.height - 4],
                    [self.perspectiveTrans.width - 2, self.perspectiveTrans.height - 2])
            elif self.pressedPos == 'top':
                self.perspectiveTrans.setDstPoints(
                    [3, 5], [self.perspectiveTrans.width - 4, 5],
                    [1, self.perspectiveTrans.height - 2],
                    [self.perspectiveTrans.width - 2, self.perspectiveTrans.height - 2])
            elif self.pressedPos == 'center':
                self.perspectiveTrans.setDstPoints(
                    [3, 4], [self.perspectiveTrans.width - 4, 4],
                    [3, self.perspectiveTrans.height - 3],
                    [self.perspectiveTrans.width - 4, self.perspectiveTrans.height - 3])
            elif self.pressedPos == 'bottom':
                self.perspectiveTrans.setDstPoints(
                    [2, 2], [self.perspectiveTrans.width - 3, 3],
                    [3, self.perspectiveTrans.height - 3],
                    [self.perspectiveTrans.width - 4, self.perspectiveTrans.height - 3])
            elif self.pressedPos == 'right-bottom':
                self.perspectiveTrans.setDstPoints(
                    [2, 0], [self.perspectiveTrans.width - 3, 3],
                    [1, self.perspectiveTrans.height - 2],
                    [self.perspectiveTrans.width - 5, self.perspectiveTrans.height - 3])
            elif self.pressedPos == 'right-top':
                self.perspectiveTrans.setDstPoints(
                    [0, 1], [self.perspectiveTrans.width - 7, 5],
                    [2, self.perspectiveTrans.height - 1],
                    [self.perspectiveTrans.width - 2, self.perspectiveTrans.height - 2])
            elif self.pressedPos == 'right':
                self.perspectiveTrans.setDstPoints(
                    [1, 1], [self.perspectiveTrans.width - 6, 4],
                    [2, self.perspectiveTrans.height - 1],
                    [self.perspectiveTrans.width - 4, self.perspectiveTrans.height - 3])
            self.pressedPix = self.perspectiveTrans.getPerspectiveTransform(
                self.perspectiveTrans.width, self.perspectiveTrans.height, True).scaled(
                    self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.perspectiveTrans.pressedPos = self.pressedPos
        self.setPixmap(self.pressedPix)

    def mouseReleaseEvent(self, e):
        """ 鼠标送回恢复原图像 """
        self.setPixmap(self.picPix)
        super().mouseReleaseEvent(e)


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
