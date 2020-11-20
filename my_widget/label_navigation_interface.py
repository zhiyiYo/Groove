# coding:utf-8

from typing import List

from my_widget.my_label import ClickableLabel
from my_widget.my_scrollArea import ScrollArea
from my_widget.my_v_box_layout import VBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QStackedWidget, QGridLayout
import pinyin


class LabelNavigationInterface(QWidget):
    """ 标签导航界面 """

    labelClicked = pyqtSignal(str)

    def __init__(self, parent=None, label_list: list = None):
        super().__init__(parent)
        self.scrollWidget = QWidget()
        self.scrollArea = ScrollArea(self)
        self.stackWidget = QStackedWidget(self)
        self.vBox = VBoxLayout(self.scrollWidget)
        self.letterNavigationWidget = QWidget(self)
        self.gridLayout = QGridLayout(self.letterNavigationWidget)
        self.__clickableLabel_list = []  # type:List[ClickableLabel]
        self.__clickableLetterLabel_list = [
            ClickableLabel(chr(i)) for i in range(65, 91)]  # type:List[ClickableLabel]
        self.__clickableLetterLabel_list.append(ClickableLabel('...'))
        # 初始化界面
        self.setLabels(label_list)
        self.__initWidget()

    def __initWidget(self):
        """ 初始化界面 """
        self.resize(800, 800)
        self.vBox.setSpacing(40)
        self.gridLayout.setSpacing(60)
        self.vBox.setAlignment(Qt.AlignLeft)
        self.vBox.setContentsMargins(25, 25, 0, 140)
        self.gridLayout.setContentsMargins(0, 0, 0, 140)
        self.gridLayout.setAlignment(Qt.AlignCenter)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollWidget.setObjectName('scrollWidget')
        self.stackWidget.addWidget(self.scrollWidget)
        self.stackWidget.addWidget(self.letterNavigationWidget)
        # 设置层叠样式
        self.__setQss()
        # 调整字母标签尺寸并将字母添加到网格布局中
        for i, label in enumerate(self.__clickableLetterLabel_list):
            row = i // 8
            col = i - row * 8
            label.setFixedHeight(50)
            text = label.text()
            label.clicked.connect(
                lambda text=text: self.labelClicked.emit(text))
            self.gridLayout.addWidget(label, row, col, 1, 1, Qt.AlignCenter)

    def setLabels(self, label_list: List[str] = None, layout='letterGridLayout'):
        """ 设置导航标签

        Parameters
        ----------
        label_list : List[str]
            需要显示的标签列表

        layout : str
            显示的标签的布局，有字母网格布局`letterGridLayout`和列表布局`listLayout`两种
        """
        self.vBox.removeAllWidget()
        # 删除旧标签
        for label in self.__clickableLabel_list:
            label.deleteLater()
        self.__clickableLabel_list = []
        self.__label_list = label_list if label_list else []

        if self.__label_list:
            # 不使用棋盘布局直接显示所有标签
            if layout != 'letterGridLayout':
                self.__clickableLabel_list = [
                    ClickableLabel(label) for label in label_list]
                self.__connectLabelSigToSlot()
                # 将新的标签添加到布局中
                self.__adjustLabelSize()
                for label in self.__clickableLabel_list:
                    self.vBox.addWidget(label)
            else:
                # 生成首字母集合
                _ = set(pinyin.get_initial(i)[0].upper() for i in label_list)
                letter_set = set(i if 65 <= ord(i) <= 90 else '...' for i in _)
                # 启用在字母结合中的标签
                for label in self.__clickableLetterLabel_list:
                    label.setEnabled(label.text() in letter_set)
            # 切换布局
            self.stackWidget.setCurrentIndex(layout == 'letterGridLayout')

    def __adjustLabelSize(self):
        """ 调整标签尺寸 """
        for label in self.__clickableLabel_list:
            label.setFixedHeight(50)
        labelNum = len(self.__clickableLabel_list)
        self.scrollWidget.resize(
            self.width(), 50 * labelNum + 40 * (labelNum - 1) + 140 + 25)

    def resizeEvent(self, e):
        """ 调整部件尺寸 """
        self.stackWidget.resize(self.size())
        self.scrollWidget.resize(self.width(), self.scrollWidget.height())
        self.scrollArea.verticalScrollBar().move(-1, 40)
        self.scrollArea.verticalScrollBar().resize(
            self.scrollArea.verticalScrollBar().width(), self.height() - 156)

    def __setQss(self):
        """ 设置层叠样式 """
        with open(r'resource\css\labelNavigationInterface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __connectLabelSigToSlot(self):
        """ 标签点击信号的槽函数 """
        for label in self.__clickableLabel_list:
            text = label.text()
            label.clicked.connect(
                lambda text=text: self.labelClicked.emit(text))

    @property
    def label_list(self):
        return self.__label_list
