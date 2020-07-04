import sys

from PyQt5.QtCore import Qt,QPoint
from PyQt5.QtGui import QPen, QColor, QBrush, QPainter,QFont,QPolygon
from PyQt5.QtWidgets import QPushButton, QApplication,QWidget

sys.path.append('..')
from Groove.my_functions.get_pressed_pos import getPressedPos


class TabButton(QPushButton):
    """ 标签按钮，点击即可换页 """
    def __init__(self, text:str, parent=None, tabIndex=0):
        super().__init__(parent)
        self.text = text
        self.isSelected = False
        self.pressedPos = None
        self.tabIndex = tabIndex
        self.setFixedSize(50,40)

    def mousePressEvent(self, e):
        """ 鼠标点击时记录位置 """
        self.pressedPos = getPressedPos(self, e)
        self.update()
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        """ 鼠标松开更新样式 """
        self.pressedPos = None
        super().mouseReleaseEvent(e)

    def paintEvent(self, QPaintEvent):
        """ 绘制背景 """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        painter.setFont(QFont('Microsoft YaHei', 16))
        if not self.isSelected:
            painter.drawText(1, 5+18, self.text)
        else:
            if not self.pressedPos:
                self.paintText(painter, 0, 0)
                self.paintLine(painter, 1, self.height() - 3, self.width() - 1, self.height() - 3,
                               self.width() - 1, self.height(), 1, self.height())
            elif self.pressedPos in ['left-top', 'right-bottom']:
                self.paintText(painter, -0.03, 0)
                self.paintLine(painter, 1, self.height() - 3, self.width() - 1, self.height()-4,
                               self.width() - 1, self.height()-1, 1, self.height())
            elif self.pressedPos in ['left', 'center', 'right', 'top', 'bottom']:
                self.paintText(painter, 0, 0, y=4)
                self.paintLine(painter, 2, self.height() - 4, self.width() - 2, self.height() - 4,
                               self.width() - 2, self.height() - 1, 2, self.height() - 1)
            elif self.pressedPos in ['left-bottom', 'right-top']:
                self.paintText(painter, 0.03, 0)
                self.paintLine(painter, 1, self.height() - 4, self.width() - 1, self.height()-3,
                               self.width() - 1, self.height(), 1, self.height() - 1)
                
        
    def paintText(self, painter, shearX, shearY, x=1, y=5):
        """ 绘制文本 """
        painter.shear(shearX, shearY)
        painter.drawText(x, y+18, self.text)

    def paintLine(self, painter, x1, y1, x2, y2, x3, y3, x4, y4):
        """ 绘制选中标志 """
        painter.setPen(Qt.NoPen)
        brush = QBrush(QColor(0, 153, 188))
        painter.setBrush(brush)
        points = [QPoint(x1, y1), QPoint(x2, y2), QPoint(x3, y3), QPoint(x4, y4)]
        painter.drawPolygon(QPolygon(points), 4)
        

class Demo(QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.bt1 = TabButton('歌手',self)
        self.bt2 = TabButton('歌曲',self)
        self.resize(300,300)
        self.bt1.move(50, 50)
        self.bt2.move(150,50)
        self.updatableButton_list=[self.bt1,self.bt2]
        for bt in self.updatableButton_list:
            bt.clicked.connect(self.buttonClickedEvent)

    def buttonClickedEvent(self):
        """ 按钮点击事件 """
        sender = self.sender()
        # 更新自己按钮的标志位
        for button in self.updatableButton_list:
            if sender == button:
                button.isSelected = True
            else:
                button.isSelected = False
        # 更新按钮的样式
        for button in self.updatableButton_list:
            button.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
