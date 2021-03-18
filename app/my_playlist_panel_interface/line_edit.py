# coding:utf-8

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLineEdit, QLabel

from app.my_widget.my_button import ThreeStateButton
from app.my_widget.my_menu import LineEditMenu


class LineEdit(QLineEdit):
    """ 编辑框 """

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        iconPath_dict = {
            "normal": r"app\resource\images\createPlaylistPanel\清空按钮_normal_50_50.png",
            "hover": r"app\resource\images\createPlaylistPanel\清空按钮_hover_50_50.png",
            "pressed": r"app\resource\images\createPlaylistPanel\清空按钮_pressed_50_50.png",
        }

        # 创建小部件
        self.clearButton = ThreeStateButton(iconPath_dict, self, (50, 50))
        self.pencilPic = QLabel(self)
        self.menu = LineEditMenu(self)
        # 初始化
        self.initWidget()
        self.setQss()

    def initWidget(self):
        """ 初始化小部件 """
        self.setFixedSize(484, 70)
        self.adjustButtonPos()
        self.textChanged.connect(self.textChangedEvent)
        self.setObjectName("createPlaylistPanelLineEdit")
        # 初始化按钮
        self.clearButton.hide()
        self.clearButton.installEventFilter(self)
        self.pencilPic.setPixmap(
            QPixmap(r"app\resource\images\createPlaylistPanel\pencil_50_50.png")
        )
        # 设置文字的外间距，防止文字和文本重叠
        self.setTextMargins(
            0, 0, self.clearButton.width() + self.pencilPic.pixmap().width() + 1, 0
        )

    def textChangedEvent(self):
        """ 编辑框的文本改变时选择是否显示清空按钮 """
        if self.text():
            self.clearButton.show()
        else:
            self.clearButton.hide()

    def enterEvent(self, e):
        """ 鼠标进入更新样式 """
        if self.property("noText") == "true":
            self.pencilPic.setPixmap(
                QPixmap(
                    r"app\resource\images\createPlaylistPanel\pencil_noFocus_hover_50_50.png"
                )
            )

    def leaveEvent(self, e):
        """ 鼠标离开更新样式 """
        if self.property("noText") == "true":
            self.pencilPic.setPixmap(
                QPixmap(
                    r"app\resource\images\createPlaylistPanel\pencil_noFocus_50_50.png"
                )
            )

    def focusOutEvent(self, e):
        """ 当焦点移到别的输入框时隐藏按钮 """
        super().focusOutEvent(e)
        if not self.text():
            self.setProperty("noText", "true")
            self.setStyle(QApplication.style())
            self.setText("       命名此播放列表")
        self.clearButton.hide()
        self.pencilPic.setPixmap(
            QPixmap(r"app\resource\images\createPlaylistPanel\pencil_noFocus_50_50.png")
        )

    def focusInEvent(self, e):
        """ 焦点进入时更换样式并取消提示文字 """
        super().focusInEvent(e)
        # 必须有判断的一步，不然每次右击菜单执行完都会触发focusInEvent()导致菜单功能混乱
        if self.property("noText") == "true":
            self.clear()
        self.setProperty("noText", "false")
        self.setStyle(QApplication.style())
        self.pencilPic.setPixmap(
            QPixmap(r"app\resource\images\createPlaylistPanel\pencil_50_50.png")
        )

    def mousePressEvent(self, e):
        """ 鼠标点击事件 """
        if e.button() == Qt.LeftButton:
            # 需要调用父类的鼠标点击事件，不然无法部分选中
            super().mousePressEvent(e)
            # 如果输入框中有文本，就设置为只读并显示清空按钮
            if self.text():
                self.clearButton.show()

    def contextMenuEvent(self, e):
        """ 设置右击菜单 """
        self.menu.exec_(e.globalPos())

    def resizeEvent(self, e):
        """ 调整大小的同时改变按钮位置 """
        self.adjustButtonPos()

    def eventFilter(self, obj, e):
        """ 过滤事件 """
        if obj == self.clearButton:
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.clear()
                self.clearButton.hide()
                return True
        return super().eventFilter(obj, e)

    def adjustButtonPos(self):
        """ 调整按钮的位置 """
        self.clearButton.move(self.width() - 101, 10)
        self.pencilPic.move(self.width() - 51, 10)

    def setQss(self):
        """ 设置层叠样式 """
        with open("app\\resource\\css\\lineEdit.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

