# coding:utf-8
from common.icon import Icon
from components.buttons.three_state_button import ThreeStateButton
from components.widgets.menu import LineEditMenu
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QLineEdit


class SearchLineEdit(QLineEdit):
    """ Search line edit """

    def __init__(self, parent=None):
        super().__init__(parent)

        clearIcons = {
            "normal": ":/images/navigation_interface/clear_normal.png",
            "hover": ":/images/navigation_interface/clear_hover.png",
            "pressed": ":/images/navigation_interface/clear_pressed.png",
        }
        self.__searchIcons = {
            "normal": ":/images/navigation_interface/search_normal_46_45.png",
            "hover": ":/images/navigation_interface/search_hover_46_45.png",
            "pressed": ":/images/navigation_interface/search_pressed_46_45.png",
        }

        self.menu = LineEditMenu(self)
        self.clearButton = ThreeStateButton(clearIcons, self, (46, 45))
        self.searchButton = ThreeStateButton(
            self.__searchIcons, self, (46, 45))

        self.__initWidget()

    def __initWidget(self):
        """ initialize widget """
        self.clearButton.hide()
        self.setAttribute(Qt.WA_StyledBackground)
        self.setPlaceholderText(self.tr("Search"))
        self.textChanged.connect(self.__onTextChanged)
        self.setTextMargins(
            0, 0, self.clearButton.width() + self.searchButton.width(), 0)
        self.resize(370, 45)
        self.clearButton.installEventFilter(self)
        self.searchButton.installEventFilter(self)

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
        if obj == self.clearButton:
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.clear()
                self.clearButton.hide()
                return True
        elif obj == self.searchButton:
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.searchButton.setIcon(Icon(self.__searchIcons["hover"]))
                return False

        return super().eventFilter(obj, e)

    def contextMenuEvent(self, e):
        self.menu.exec_(e.globalPos())
