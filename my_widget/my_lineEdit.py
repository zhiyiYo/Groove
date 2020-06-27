import sys
from PyQt5.QtCore import QEvent, QSize, Qt
from PyQt5.QtGui import QContextMenuEvent, QFont, QIcon
from PyQt5.QtWidgets import QAction, QHBoxLayout, QLineEdit, QToolButton,QApplication   

sys.path.append('..')
from Groove.my_widget.my_menu import Menu,LineEditMenu
from Groove.my_widget.my_button import LineEditButton
from Groove.my_functions.is_not_leave import isNotLeave


class LineEdit(QLineEdit):
    """ 定义一个被点击就全选文字的单行输入框 """

    def __init__(self, string=None, parent=None):
        super().__init__(string, parent)

        # 设置提示条
        self.customToolTip = None
        iconPath_dict = {
            'normal': r'resource\images\lineEdit\clearInfo_cross_normal.png',
            'hover': r'resource\images\lineEdit\clearInfo_cross_hover.png',
            'selected': r'resource\images\lineEdit\clearInfo_cross_selected.png'}

        # 实例化一个用于清空内容的按钮
        self.clearButton = LineEditButton(iconPath_dict, self)
        # 实例化右击菜单
        self.menu = LineEditMenu(self)

        # 实例化布局
        self.h_layout = QHBoxLayout()
        self.initWidget()


    def initWidget(self):
        """ 初始化小部件 """
        self.resize(500,40)
        self.clearButton.hide()
        self.textChanged.connect(self.textChangedEvent)
        self.clearButton.move(self.width() - self.clearButton.width(), 0)
        self.setTextMargins(0, 0, self.clearButton.width(), 0)
        # 安装事件过滤器
        self.clearButton.installEventFilter(self)

    def mousePressEvent(self, e):
        if e.button()==Qt.LeftButton:
            # 如果已经全选了再次点击就取消全选
            if self.selectedText()==self.text():
                self.setSelection(len(self.text()), len(self.text()))
            else:
                self.selectAll() 
            self.setFocus()
            # 如果输入框中有文本，就设置为只读并显示清空按钮
            if self.text():
                self.clearButton.show()


    def contextMenuEvent(self, e: QContextMenuEvent):
        """ 设置右击菜单 """
        self.menu.exec_(e.globalPos())

    def focusOutEvent(self, e):
        """ 当焦点移到别的输入框时隐藏按钮 """
        # 调用父类的函数，消除焦点
        super().focusOutEvent(e)
        self.clearButton.hide()

    def enterEvent(self, e):
        """ 鼠标进入时显示提示条 """
        if self.customToolTip:
            self.customToolTip.setText(self.customToolTipText)
            self.customToolTip.move(e.globalX() - int(self.customToolTip.width() / 2),
                                    e.globalY() - 140 - self.customToolTip.isWordWrap * 30)
            self.customToolTip.show()

    def leaveEvent(self, e):
        """ 判断鼠标是否离开标签 """
        if self.parent() and self.customToolTip:
            notLeave = isNotLeave(self)
            if notLeave:
                return
            self.customToolTip.hide()

    def setCustomToolTip(self, toolTip, text: str):
        """ 设置提示条和提示条内容 """
        self.customToolTip = toolTip
        self.customToolTipText = text

    def textChangedEvent(self):
        """ 如果输入框中文本改变且此时清空按钮不可见，就显示清空按钮 """
        if self.text() and not self.clearButton.isVisible():
            self.clearButton.show()

    def resizeEvent(self, e):
        """ 改变大小时需要移动按钮的位置 """
        self.clearButton.move(self.width() - self.clearButton.width(), 0)
        
    def eventFilter(self, obj, e):
        """ 清空按钮按下时清空内容并隐藏按钮 """
        if obj == self.clearButton:
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.clear()
                self.clearButton.hide()
                return True
        return super().eventFilter(obj,e)

class SearchLineEdit(QLineEdit):
    """ 单行搜索框 """
    def __init__(self, parent=None):
        super().__init__(parent)

        # 按钮图标位置
        clear_iconPath_dict = {
            'normal': r'resource\images\searchLineEdit\搜索框清空按钮_normal_45_45.png',
            'hover': r'resource\images\searchLineEdit\搜索框清空按钮_hover_45_45.png',
            'selected': r'resource\images\searchLineEdit\搜索框清空按钮_selected_45_45.png'}
        self.__search_iconPath_dict = {
            'normal': r'resource\images\searchLineEdit\搜索框搜索按钮_normal_46_45.png',
            'hover': r'resource\images\searchLineEdit\搜索框搜索按钮_hover_46_45.png',
            'selected': r'resource\images\searchLineEdit\搜索框搜索按钮_selected_46_45.png'}
        # 实例化按钮
        self.clearButton = LineEditButton(clear_iconPath_dict, self, (46, 45))
        self.searchButton = LineEditButton(self.__search_iconPath_dict, self, (46, 45))
        # 实例化右击菜单
        self.menu = LineEditMenu(self)
        # 初始化界面
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        self.resize(300,45)
        self.clearButton.hide()
        # 设置提示文字
        self.setPlaceholderText('搜索')
        self.textChanged.connect(self.textChangedEvent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        # 调整按钮位置
        self.adjustButtonPos()
        # 安装监听
        self.clearButton.installEventFilter(self)
        self.searchButton.installEventFilter(self)

    def textChangedEvent(self):
        """ 编辑框的文本改变时选择是否显示清空按钮 """
        if self.text():
            self.clearButton.show()
        else:
            self.clearButton.hide()

    def adjustButtonPos(self):
        """ 调整按钮的位置 """
        # 需要补上margin的位置
        self.searchButton.move(self.width() - self.searchButton.width()-8-16, 8)
        self.clearButton.move(self.searchButton.x() - self.clearButton.width(), 8)
        
    def resizeEvent(self, e):
        """ 调整大小的同时改变按钮位置 """
        self.adjustButtonPos()

    def mousePressEvent(self, e):
        if e.button()==Qt.LeftButton:
            # 如果已经全选了再次点击就取消全选
            if self.selectedText() == self.text():
                self.setSelection(len(self.text()), len(self.text()))
            else:
                self.selectAll()
            self.setFocus()
            # 如果输入框中有文本，就设置为只读并显示清空按钮
            if self.text():
                self.clearButton.show()

    def eventFilter(self, obj, e):
        """ 过滤事件 """
        if obj == self.clearButton:
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.clear()
                self.clearButton.hide()
                return True
        elif obj == self.searchButton:
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.searchButton.setIcon(QIcon(self.__search_iconPath_dict['hover']))
                """ 搜索槽函数有待补充 """
                pass
                return True
        return super().eventFilter(obj, e)

    def contextMenuEvent(self, e: QContextMenuEvent):
        """ 设置右击菜单 """
        self.menu.exec_(e.globalPos())
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = LineEdit()
    demo.show()
    sys.exit(app.exec_())
