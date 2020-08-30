import sys

from PyQt5.QtCore import Qt, QEvent, QRect
from PyQt5.QtGui import QPen, QBrush, QPainter, QColor, QPixmap, QFont, QFontMetrics
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton


class BasicSelectionModeBar(QWidget):
    """ 基本选择模式栏 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.button_list = []
        self.__buttonToHide_list = []
        self.__alwaysVisibleButton_list = []
        self.__currentVisibleButton_list = []
        self.__separatorIndex_list = []
        self.hasHidePartButton = False

    def addButton(self, button):
        """ 向窗口右侧添加按钮 """
        # 更新列表
        self.button_list.append(button)
        self.__currentVisibleButton_list.append(button)
        self.__adjustButtonPos()

    def addSeparator(self):
        """ 添加分隔符 """
        if not self.button_list:
            return
        self.__separatorIndex_list.append(len(self.button_list))

    def insertSeparator(self, index: int):
        """ 在指定位置插入分隔符 """
        if index < 1:
            return
        self.__separatorIndex_list.append(index)
        self.__separatorIndex_list.sort()

    def addButtons(self, button_list: list):
        """ 向窗口添加多个按钮 """
        self.button_list.extend(button_list)
        self.__currentVisibleButton_list.extend(button_list)
        self.__adjustButtonPos()

    def setToHideButtons(self, button_list: list):
        """ 设置在多选模式下需要隐藏的按钮 """
        self.__buttonToHide_list = button_list
        self.__alwaysVisibleButton_list = [
            button for button in self.button_list if button not in button_list]

    def setPartButtonHidden(self, isHidden: bool):
        """ 隐藏指定的隐藏列表中的按钮 """
        if self.hasHidePartButton == isHidden:
            return
        self.hasHidePartButton = isHidden
        for button in self.__buttonToHide_list:
            button.setHidden(isHidden)
        if not isHidden:
            self.__currentVisibleButton_list = self.button_list
        else:
            self.__currentVisibleButton_list = self.__alwaysVisibleButton_list
        self.__adjustButtonPos()

    def __adjustButtonPos(self):
        """ 调整此时可见的按钮的位置 """
        for index, button in enumerate(self.__currentVisibleButton_list[::-1]):
            rawIndex = self.button_list.index(button)
            isRightHasSeparator = (rawIndex + 1 in self.__separatorIndex_list)
            button.move(self.width() - (index + 1) * button.width() -
                        41 * isRightHasSeparator, 0)
        # 调整窗口高度
        height_list = [button.height()
                       for button in self.__currentVisibleButton_list]
        height = max(height_list) if height_list else 70
        self.resize(self.width(), height)
        # 刷新界面
        self.update()

    def resizeEvent(self, e):
        """ 改变尺寸时移动按钮 """
        self.__adjustButtonPos()

    def paintEvent(self, e):
        """ 绘制分隔符 """
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(230, 230, 230)))
        painter.drawRect(self.rect())
        painter.setPen(QPen(QColor(203, 203, 203)))
        for index in self.__separatorIndex_list:
            x = self.button_list[index - 1].x(
            ) + self.button_list[index - 1].width() + 20
            painter.drawLine(x, 15, x + 1, self.height() - 15)


class BasicButton(QPushButton):
    """ 选择模式栏按钮 """

    def __init__(self, iconPath: str, text: str, parent=None, buttonSize: tuple = (84, 70)):
        super().__init__(parent)
        self.resize(buttonSize[0], buttonSize[1])
        self.__iconPath = iconPath
        self.__iconPixmap = QPixmap(iconPath)
        self.buttonText = text
        self.__isEnter = False
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.installEventFilter(self)
        # 计算字符串宽度
        self.fontMetrics = QFontMetrics(QFont('Microsoft YaHei', 9))
        self.__textWidth = self.fontMetrics.width(self.buttonText)
        # 调整字符串
        self.__adjustText()

    def setText(self, text: str):
        """ 设置按钮文字 """
        self.buttonText = text
        self.__adjustText()
        self.update()

    def setIcon(self, iconPath: str):
        """ 设置按钮图标 """
        self.__iconPath = iconPath
        self.__iconPixmap = QPixmap(iconPath)
        self.update()

    def __adjustText(self):
        """ 根据字符串宽度调整按钮高度和字符串换行 """
        maxWidth = self.width() - 8
        buttonChar_list = list(self.buttonText)
        # 计算宽度
        textWidth = 0
        for index, char in enumerate(self.buttonText):
            if textWidth + self.fontMetrics.width(char) > maxWidth:
                textWidth = 0
                self.__textWidth = maxWidth
                # 插入换行符并调整尺寸
                buttonChar_list.insert(index, '\n')
                self.resize(self.width(), self.height() + 20)
            textWidth += self.fontMetrics.width(char)
        # 更新字符串和字符串所占rect
        self.buttonText = ''.join(buttonChar_list)
        self.__textRect = QRect(0, 40, self.width(), self.height() - 40)

    def eventFilter(self, obj, e: QEvent):
        """ 过滤事件 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.__isEnter = True
                self.update()
                return False
            elif e.type() == QEvent.Leave:
                self.__isEnter = False
                self.update()
                return False
        return super().eventFilter(obj, e)

    def paintEvent(self, e):
        """ 绘制图标和文字 """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        if self.__isEnter:
            # 绘制深色背景和边框
            painter.setPen(QPen(QColor(170, 170, 170)))
            painter.setBrush(QBrush(QColor(0, 0, 0, 17)))
            painter.drawRect(self.rect())
        # 绘制图标
        painter.drawPixmap(32, 15, self.__iconPixmap.width(),
                           self.__iconPixmap.height(), self.__iconPixmap)
        # 绘制文字
        painter.setPen(QPen(Qt.black))
        painter.setFont(QFont('Microsoft YaHei', 9))
        painter.drawText(
            self.__textRect, Qt.AlignHCenter, self.buttonText)


class TwoStateButton(BasicButton):
    """ 双态按钮 """

    def __init__(self, iconPath_list: list, text_list: list, parent=None, buttonSize: tuple = (84, 70), isState_1=0):
        """ 实例化双态按钮
        Parameters
        ----------
        iconPath_list : 存状态0和状态1对应按钮图标地址的列表\n
        text_list : 与状态0和状态1相对应的按钮文字列表\n
        parent : 父级窗口\n
        buttonSize : 按钮大小元组\n
        isState_0 : 是否处于状态1
        """
        super().__init__(
            iconPath_list[isState_1], text_list[isState_1], parent, buttonSize)
        self.__iconPath_list = iconPath_list
        self.__text_list = text_list
        self.__isState_1 = isState_1
        self.__iconPixmap_list = [
            QPixmap(iconPath) for iconPath in self.__iconPath_list]

    def mouseReleaseEvent(self, e):
        """ 按钮松开时取反状态 """
        super().mouseReleaseEvent(e)
        self.setState(not self.__isState_1)

    def setState(self, isState_1: bool):
        """ 设置按钮状态 """
        self.__isState_1 = isState_1
        self.setText(self.__text_list[self.__isState_1])
        self.setIcon(self.__iconPixmap_list[self.__isState_1])
        self.update()


class CheckAllButton(TwoStateButton):
    """ 全选按钮 """

    def __init__(self, iconPath_list, text_list, parent=None, buttonSize=(84,70), isState_1=0):
        super().__init__(iconPath_list, text_list, parent, buttonSize, isState_1)

    def setCheckedState(self, checkedState: bool):
        """ 设置全选/取消全选状态 """
        self.setState(not checkedState)


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.bt = BasicButton(
            r'resource\\images\\selection_mode_bar\\删除_20_20.png', '删除', self)
        self.setStyleSheet('QWidget{background:rgb(230,230,230)}')
        self.resize(200, 200)
        self.bt.move(41, 77)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
