# coding:utf-8
from components.buttons.three_state_button import ThreeStateButton
from components.widgets.label import ErrorIcon
from components.widgets.menu import LineEditMenu
from PyQt5.QtCore import QEvent, Qt, QRegExp
from PyQt5.QtGui import QContextMenuEvent, QRegExpValidator
from PyQt5.QtWidgets import QApplication, QLineEdit


class LineEdit(QLineEdit):
    """ 包含清空按钮的单行输入框 """

    def __init__(self, string=None, parent=None, needClearBtn: bool = True):
        super().__init__(string, parent)
        self.needClearBtn = needClearBtn
        self.clickedTime = 0
        iconPaths = {
            "normal": ":/images/line_edit/close_normal.png",
            "hover": ":/images/line_edit/close_hover.png",
            "pressed": ":/images/line_edit/clear_pressed.png",
        }
        self.clearButton = ThreeStateButton(iconPaths, self)
        self.menu = LineEditMenu(self)
        self.initWidget()

    def initWidget(self):
        """ initialize widgets """
        self.resize(500, 40)
        self.clearButton.hide()
        self.setCursorPosition(0)
        self.textChanged.connect(self.onTextChanged)
        self.clearButton.move(self.width() - self.clearButton.width(), 0)

        if self.needClearBtn:
            self.setTextMargins(0, 0, self.clearButton.width(), 0)

        self.clearButton.installEventFilter(self)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self.clickedTime == 0:
                self.selectAll()
            else:
                super().mousePressEvent(e)

            self.setFocus()

            if self.text() and self.needClearBtn:
                self.clearButton.show()

        self.clickedTime += 1

    def contextMenuEvent(self, e: QContextMenuEvent):
        self.menu.exec_(e.globalPos())

    def focusOutEvent(self, e):
        super().focusOutEvent(e)
        self.clickedTime = 0
        self.clearButton.hide()

    def onTextChanged(self):
        """ text changed slot """
        if self.text() and not self.clearButton.isVisible() and self.needClearBtn and self.hasFocus():
            self.clearButton.show()

    def resizeEvent(self, e):
        self.clearButton.move(self.width() - self.clearButton.width(), 0)

    def eventFilter(self, obj, e):
        if obj == self.clearButton:
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.clear()
                self.clearButton.hide()
                return True

        return super().eventFilter(obj, e)


class VLineEdit(LineEdit):
    """ Line edit with a validator """

    def __init__(self, regex: str, errorMessage: str, text=None, parent=None):
        super().__init__(text, parent, True)
        self.errorMessage = errorMessage
        self.setValidator(QRegExpValidator(QRegExp(regex), self))
        self.errorIcon = ErrorIcon(parent)
        self.errorIcon.hide()

    def validate(self) -> bool:
        """ validate the text """
        state = self.validator().validate(self.text(), 0)[0]
        illegal = state != QRegExpValidator.Acceptable

        # set the visibility error icon
        x = self.pos().x()-25
        y = self.pos().y()+self.height()//2-self.errorIcon.height()//2
        self.errorIcon.move(x, y)
        self.errorIcon.setVisible(illegal)

        # update style sheet
        self.setProperty('error', illegal)
        self.setStyle(QApplication.style())

        return not illegal
