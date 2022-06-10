# coding:utf-8
from typing import List

import pinyin
from common.style_sheet import setStyleSheet
from PyQt5.QtCore import QFile, Qt, pyqtSignal
from PyQt5.QtWidgets import QGridLayout, QStackedWidget, QWidget

from components.layout.v_box_layout import VBoxLayout
from components.widgets.label import ClickableLabel
from components.widgets.scroll_area import ScrollArea


class LabelNavigationInterface(QWidget):
    """ Label navigation interface """

    labelClicked = pyqtSignal(str)

    def __init__(self, parent=None, label_list: list = None):
        super().__init__(parent)
        self.scrollWidget = QWidget()
        self.scrollArea = ScrollArea(self)
        self.stackWidget = QStackedWidget(self)
        self.vBox = VBoxLayout(self.scrollWidget)
        self.letterNavigationWidget = QWidget(self)
        self.gridLayout = QGridLayout(self.letterNavigationWidget)
        self.__clickableLabels = []  # type:List[ClickableLabel]
        self.__clickableLetterLabels = [
            ClickableLabel(chr(i)) for i in range(65, 91)]  # type:List[ClickableLabel]
        self.__clickableLetterLabels.append(ClickableLabel("..."))

        self.setLabels(label_list)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.resize(800, 800)
        self.vBox.setSpacing(40)
        self.gridLayout.setSpacing(60)
        self.vBox.setAlignment(Qt.AlignLeft)
        self.vBox.setContentsMargins(25, 25, 0, 140)
        self.gridLayout.setContentsMargins(0, 0, 0, 140)
        self.gridLayout.setAlignment(Qt.AlignCenter)
        self.scrollArea.setWidget(self.scrollWidget)
        self.stackWidget.addWidget(self.scrollWidget)
        self.stackWidget.addWidget(self.letterNavigationWidget)

        self.__setQss()

        # add letters to layout
        for i, label in enumerate(self.__clickableLetterLabels):
            row = i // 8
            col = i - row * 8
            label.setFixedHeight(50)
            text = label.text()
            label.clicked.connect(
                lambda text=text: self.labelClicked.emit(text))
            self.gridLayout.addWidget(label, row, col, 1, 1, Qt.AlignCenter)

    def setLabels(self, labels: List[str] = None, layout="grid"):
        """ set labels in layout

        Parameters
        ----------
        labels: List[str]
            labels need to display

        layout: str
            layout of labels, including `grid` and `list`
        """
        self.vBox.removeAllWidget()

        for label in self.__clickableLabels:
            label.deleteLater()

        self.__clickableLabels = []
        self.__labels = labels if labels else []

        if not self.__labels:
            return

        if layout != "grid":
            self.__clickableLabels = [
                ClickableLabel(label) for label in labels]
            self.__connectLabelSigToSlot()

            self.__adjustLabelSize()
            for label in self.__clickableLabels:
                label.setCursor(Qt.PointingHandCursor)
                self.vBox.addWidget(label)
        else:
            letters = set(pinyin.get_initial(i)[0].upper() for i in labels)
            letters = set(i if 65 <= ord(i) <=
                            90 else "..." for i in letters)

            for label in self.__clickableLetterLabels:
                enabled = label.text() in letters
                cursor = Qt.PointingHandCursor if enabled else Qt.ArrowCursor
                label.setCursor(cursor)
                label.setEnabled(enabled)

        self.stackWidget.setCurrentIndex(layout == "grid")

    def __adjustLabelSize(self):
        """ 调整标签尺寸 """
        for label in self.__clickableLabels:
            label.setFixedHeight(50)

        N = len(self.__clickableLabels)
        self.scrollWidget.resize(self.width(), 50*N + 40*(N - 1) + 140 + 25)

    def resizeEvent(self, e):
        self.stackWidget.resize(self.size())
        self.scrollWidget.resize(self.width(), self.scrollWidget.height())

    def __setQss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName("scrollWidget")
        setStyleSheet(self, 'label_navigation_interface')

    def __connectLabelSigToSlot(self):
        """ 标签点击信号的槽函数 """
        for label in self.__clickableLabels:
            text = label.text()
            label.clicked.connect(
                lambda text=text: self.labelClicked.emit(text))

    @property
    def labels(self):
        return self.__labels
