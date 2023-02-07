# coding:utf-8
from common.icon import getIconColor
from components.buttons.three_state_button import ThreeStateButton
from components.widgets.menu import LineEditMenu
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QLineEdit


class ToolButton(ThreeStateButton):

    CLEAR = "Close"
    SEARCH = "SearchFlipped"

    def __init__(self, iconType: str, iconSize=(20, 20), parent=None):
        c = getIconColor()
        folder = ":/images/navigation_interface"
        iconPaths = {
            "normal": f"{folder}/{iconType}_{c}.svg",
            "hover": f"{folder}/{iconType}_green_{c}.svg",
            "pressed": f"{folder}/{iconType}_white.svg",
        }
        super().__init__(iconPaths, parent, (46, 45), iconSize)



class SearchLineEdit(QLineEdit):
    """ Search line edit """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.menu = LineEditMenu(self)
        self.clearButton = ToolButton(ToolButton.CLEAR, (16, 16), self)
        self.searchButton = ToolButton(ToolButton.SEARCH, parent=self)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widget """
        self.setAttribute(Qt.WA_StyledBackground)
        self.setPlaceholderText(self.tr("Search"))
        self.setTextMargins(
            0, 0, self.clearButton.width() + self.searchButton.width(), 0)
        self.resize(370, 45)

        self.clearButton.hide()
        self.clearButton.installEventFilter(self)

        self.textChanged.connect(self.__onTextChanged)

    def __onTextChanged(self, text):
        """ text changed slot """
        self.clearButton.setVisible(bool(text))

    def resizeEvent(self, e):
        self.searchButton.move(self.width() - self.searchButton.width() - 8, 0)
        self.clearButton.move(self.searchButton.x() -
                              self.clearButton.width(), 0)

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return

        super().mousePressEvent(e)
        if self.text():
            self.clearButton.show()

    def keyPressEvent(self, e: QKeyEvent):
        super().keyPressEvent(e)
        if e.key() in [Qt.Key_Enter, Qt.Key_Return]:
            self.searchButton.click()

    def focusOutEvent(self, e):
        super().focusOutEvent(e)
        self.clearButton.hide()

    def eventFilter(self, obj, e):
        if obj is self.clearButton:
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.clear()
                self.clearButton.hide()

        return super().eventFilter(obj, e)

    def contextMenuEvent(self, e):
        self.menu.exec_(e.globalPos())
