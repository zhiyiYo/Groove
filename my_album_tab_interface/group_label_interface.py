# coding:utf-8

from my_widget.my_label import ClickableLabel
from my_widget.my_scrollArea import ScrollArea
from my_widget.my_v_box_layout import VBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget


class GroupLabelInterface(QWidget):
    """ 分组标签导航界面 """
    scrollToGroupSig = pyqtSignal(str)

    def __init__(self, parent=None, label_list: list = None):
        super().__init__(parent)
        self.scrollWidget = QWidget()
        self.scrollArea = ScrollArea(self)
        self.vBox = VBoxLayout(self.scrollWidget)
        # 初始化界面
        self.setLabels(label_list)
        self.__initWidget()

    def __initWidget(self):
        """ 初始化界面 """
        self.resize(800, 800)
        self.vBox.setSpacing(40)
        self.vBox.setAlignment(Qt.AlignLeft)
        self.scrollWidget.setLayout(self.vBox)
        self.vBox.setContentsMargins(25, 25, 0, 140)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollWidget.setObjectName('scrollWidget')
        # 设置层叠样式
        self.__setQss()
        # 调整标签尺寸
        self.__adjustLabelSize()

    def setLabels(self, label_list: list = None):
        """ 设置导航标签 """
        self.vBox.removeAllWidget()
        self.__label_list = label_list if label_list else []
        self.__clickableLabel_list = [ClickableLabel(
            label, self.scrollWidget) for label in self.__label_list]
        self.__connectLabelSigToSlot()
        if not self.__label_list:
            return
        # 将新的标签添加到布局中
        self.__adjustLabelSize()
        for label in self.__clickableLabel_list:
            self.vBox.addWidget(label)

    def __adjustLabelSize(self):
        """ 调整标签尺寸 """
        for label in self.__clickableLabel_list:
            label.setFixedHeight(50)
            
    def resizeEvent(self, e):
        """ 调整部件尺寸 """
        self.scrollArea.resize(self.size())
        self.scrollWidget.resize(self.width(), self.scrollWidget.height())
        self.scrollArea.verticalScrollBar().move(-1, 40)
        self.scrollArea.verticalScrollBar().resize(
            self.scrollArea.verticalScrollBar().width(), self.height() - 156)

    def __setQss(self):
        """ 设置层叠样式 """
        with open(r'resource\css\groupLabelInterface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __connectLabelSigToSlot(self):
        """ 标签点击信号的槽函数 """
        for label in self.__clickableLabel_list:
            text = label.text()
            label.clicked.connect(
                lambda text=text: self.scrollToGroupSig.emit(text))
