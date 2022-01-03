# coding:utf-8
import os

from components.buttons.perspective_button import PerspectivePushButton
from components.widgets.scroll_area import ScrollArea
from PyQt5.QtCore import QFile, Qt, pyqtSignal
from PyQt5.QtGui import (QBrush, QColor, QFont, QFontMetrics, QMouseEvent,
                         QPainter, QPen, QPixmap)
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
                             QVBoxLayout, QWidget, QScrollBar)

from .dialog import Dialog
from .mask_dialog_base import MaskDialogBase


class FolderListDialog(MaskDialogBase):
    """ 文件夹列表对话框 """

    folderChanged = pyqtSignal(list)

    def __init__(self, folderPaths: list, title: str, content: str, parent):
        super().__init__(parent=parent)
        self.title = title
        self.content = content
        self.__original_paths = folderPaths
        self.folderPaths = folderPaths.copy()

        self.vBoxLayout = QVBoxLayout(self.widget)
        self.titleLabel = QLabel(title, self.widget)
        self.contentLabel = QLabel(content, self.widget)
        self.scrollArea = ScrollArea(self.widget)
        self.scrollWidget = QWidget(self.scrollArea)
        self.completeButton = PerspectivePushButton(
            self.tr('Done'), self.widget)
        self.addFolderCard = AddFolderCard(self.scrollWidget)
        self.folderCards = [FolderCard(i, self.scrollWidget)
                            for i in folderPaths]
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.__setQss()

        w = max(self.titleLabel.width()+60, self.contentLabel.width()+60, 440)
        self.widget.setFixedWidth(w)
        self.scrollArea.resize(368, 90)
        self.scrollWidget.resize(365, 90)
        self.scrollArea.setFixedWidth(368)
        self.scrollWidget.setFixedWidth(365)
        self.scrollArea.setMaximumHeight(500)
        self.scrollArea.setViewportMargins(0, 0, 0, 0)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.__initLayout()

        # 信号连接到槽
        self.addFolderCard.clicked.connect(self.__showFileDialog)
        self.completeButton.clicked.connect(self.__onButtonClicked)
        for card in self.folderCards:
            card.clicked.connect(self.__showDeleteFolderCardDialog)

    def __initLayout(self):
        """ 初始化布局 """
        self.vBoxLayout.setContentsMargins(30, 30, 30, 30)
        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SetFixedSize)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.setSpacing(0)

        # 标签
        layout_1 = QVBoxLayout()
        layout_1.setContentsMargins(0, 0, 0, 0)
        layout_1.setSpacing(7)
        layout_1.addWidget(self.titleLabel, 0, Qt.AlignTop)
        layout_1.addWidget(self.contentLabel, 0, Qt.AlignTop)
        self.vBoxLayout.addLayout(layout_1, 0)
        self.vBoxLayout.addSpacing(15)

        # 卡片
        layout_2 = QHBoxLayout()
        layout_2.setAlignment(Qt.AlignCenter)
        layout_2.setContentsMargins(5, 0, 5, 0)
        layout_2.addWidget(self.scrollArea, 0, Qt.AlignCenter)
        self.vBoxLayout.addLayout(layout_2, 1)
        self.vBoxLayout.addSpacing(30)

        self.scrollLayout = QVBoxLayout(self.scrollWidget)
        self.scrollLayout.setAlignment(Qt.AlignTop)
        self.scrollLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollLayout.setSpacing(10)
        self.scrollLayout.addWidget(self.addFolderCard, 0, Qt.AlignTop)
        for card in self.folderCards:
            self.scrollLayout.addWidget(card, 0, Qt.AlignTop)

        # 按钮
        layout_3 = QHBoxLayout()
        layout_3.setContentsMargins(0, 0, 0, 0)
        layout_3.addStretch(1)
        layout_3.addWidget(self.completeButton)
        self.vBoxLayout.addLayout(layout_3, 0)

        self.__adjustWidgetSize()

    def __showFileDialog(self):
        """ 显示文件对话框 """
        path = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), "./")

        if not path or path in self.folderPaths:
            return

        # 创建文件路径卡
        card = FolderCard(path, self.scrollWidget)
        self.scrollLayout.addWidget(card, 0, Qt.AlignTop)
        card.clicked.connect(self.__showDeleteFolderCardDialog)
        card.show()

        self.folderPaths.append(path)
        self.folderCards.append(card)

        self.__adjustWidgetSize()

    def __showDeleteFolderCardDialog(self):
        """ 显示删除文件夹卡片对话框 """
        sender = self.sender()
        title = self.tr('Are you sure you want to delete the folder?')
        content = self.tr("If you delete the ") + f'"{sender.folderName}"' + \
            self.tr(" folder and remove it from the list, the folder will no "
                    "longer appear in the list, but will not be deleted.")
        dialog = Dialog(title, content, self.window())
        dialog.yesSignal.connect(lambda: self.__deleteFolderCard(sender))
        dialog.exec_()

    def __deleteFolderCard(self, folderCard):
        """ 删除选中的文件卡 """
        self.scrollLayout.removeWidget(folderCard)
        index = self.folderCards.index(folderCard)
        self.folderCards.pop(index)
        self.folderPaths.pop(index)
        folderCard.deleteLater()

        # 更新高度
        self.__adjustWidgetSize()

    def __setQss(self):
        """ 设置层叠样式 """
        self.titleLabel.setObjectName('titleLabel')
        self.contentLabel.setObjectName('contentLabel')
        self.completeButton.setObjectName('completeButton')
        self.scrollWidget.setObjectName('scrollWidget')

        f = QFile(":/qss/folder_list_dialog.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

        self.setStyle(QApplication.style())
        self.titleLabel.adjustSize()
        self.contentLabel.adjustSize()
        self.completeButton.adjustSize()

    def __onButtonClicked(self):
        """ 完成按钮点击槽函数 """
        if sorted(self.__original_paths) != sorted(self.folderPaths):
            self.setEnabled(False)
            QApplication.processEvents()
            self.folderChanged.emit(self.folderPaths)

        self.close()

    def __adjustWidgetSize(self):
        N = len(self.folderCards)
        h = 90*(N+1) + 10*N
        self.scrollArea.setFixedHeight(min(h, 500))
        self.scrollWidget.setFixedHeight(h)


class ClickableWindow(QWidget):
    """ 可点击窗口 """

    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(365, 90)
        self._isPressed = None
        self._isEnter = False

    def enterEvent(self, e):
        """ 鼠标进入界面就置位进入标志位 """
        self._isEnter = True
        self.update()

    def leaveEvent(self, e):
        """ 鼠标离开就清零置位标志位 """
        self._isEnter = False
        self.update()

    def mouseReleaseEvent(self, e):
        """ 鼠标松开时更新界面 """
        self._isPressed = False
        self.update()
        if e.button() == Qt.LeftButton:
            self.clicked.emit()

    def mousePressEvent(self, e: QMouseEvent):
        self._isPressed = True
        self.update()

    def paintEvent(self, e):
        """ 绘制背景 """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        brush = QBrush(QColor(204, 204, 204))
        painter.setPen(Qt.NoPen)
        if not self._isEnter:
            painter.setBrush(brush)
            painter.drawRoundedRect(self.rect(), 5, 5)
        else:
            painter.setPen(QPen(QColor(204, 204, 204), 2))
            painter.drawRect(1, 1, self.width() - 2, self.height() - 2)
            painter.setPen(Qt.NoPen)
            if not self._isPressed:
                brush.setColor(QColor(230, 230, 230))
                painter.setBrush(brush)
                painter.drawRect(2, 2, self.width() - 4, self.height() - 4)
            else:
                brush.setColor(QColor(153, 153, 153))
                painter.setBrush(brush)
                painter.drawRoundedRect(
                    6, 1, self.width() - 12, self.height() - 2, 3, 3)


class FolderCard(ClickableWindow):
    """ 文件夹卡片 """

    def __init__(self, folderPath: str, parent=None):
        super().__init__(parent)
        self.folderPath = folderPath
        self.folderName = os.path.basename(folderPath)
        self.__closeIcon = QPixmap(":/images/setting_interface/Close.png")

    def paintEvent(self, e):
        """ 绘制背景 """
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        # 绘制文字和图标
        if self._isPressed:
            self.__drawText(painter, 15, 10, 15, 9)
            painter.drawPixmap(
                self.width() - 33, 23, self.__closeIcon.width(), self.__closeIcon.height(), self.__closeIcon)
        else:
            self.__drawText(painter, 12, 11, 12, 10)
            painter.drawPixmap(
                self.width() - 30, 25, self.__closeIcon.width(), self.__closeIcon.height(), self.__closeIcon)

    def __drawText(self, painter, x1, fontSize1, x2, fontSize2):
        """ 绘制文字 """
        # 绘制文件夹名字
        font = QFont("Microsoft YaHei", fontSize1, 75)
        painter.setFont(font)
        name = QFontMetrics(font).elidedText(
            self.folderName, Qt.ElideRight, self.width()-60)
        painter.drawText(x1, 37, name)

        # 绘制路径
        font = QFont("Microsoft YaHei", fontSize2)
        painter.setFont(font)
        path = QFontMetrics(font).elidedText(
            self.folderPath, Qt.ElideRight, self.width()-30)
        painter.drawText(x2, 46, self.width() - 20, 23, Qt.AlignLeft, path)


class AddFolderCard(ClickableWindow):
    """ 添加文件夹卡 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__iconPix = QPixmap(":/images/setting_interface/Add.png")

    def paintEvent(self, e):
        """ 绘制背景 """
        super().paintEvent(e)
        painter = QPainter(self)
        if not self._isPressed:
            painter.drawPixmap(
                int(self.width() / 2 - self.__iconPix.width() / 2),
                int(self.height() / 2 - self.__iconPix.height() / 2),
                self.__iconPix.width(),
                self.__iconPix.height(),
                self.__iconPix,
            )
        else:
            painter.drawPixmap(
                int(self.width() / 2 - (self.__iconPix.width() - 4) / 2),
                int(self.height() / 2 - (self.__iconPix.height() - 4) / 2),
                self.__iconPix.width() - 4,
                self.__iconPix.height() - 4,
                self.__iconPix,
            )
