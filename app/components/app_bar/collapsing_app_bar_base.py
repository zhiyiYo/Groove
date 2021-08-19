# coding:utf-8
from typing import List

from app.common.image_process_utils import DominantColor
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QColor, QPainter, QFont, QFontMetrics, QResizeEvent
from PyQt5.QtWidgets import QWidget, QLabel

from .app_bar_button import AppBarButton


class CollapsingAppBarBase(QWidget):

    def __init__(self, title: str, content: str, coverPath: str, buttons: List[AppBarButton],
                 needWhiteBar=False, parent=None):
        """
        Parameters
        ----------
        title: str
            标题

        content: str
            内容

        coverPath: str
            封面路径

        buttons: List[AppBarButtons]
            工具栏按钮列表，不包括"更多操作"按钮

        needWhiteBar: bool
            是否需要在封面上绘制白条

        parent:
            父级窗口
        """
        super().__init__(parent=parent)
        self.title = title
        self.content = content
        self.coverPath = coverPath
        self.needWhiteBar = needWhiteBar
        self.coverLabel = QLabel(self)
        self.contentLabel = QLabel(content, self)
        self.titleLabel = QLabel(title, self)
        self.dominantColorGetter = DominantColor()
        self.titleFontSize = 43
        self.contentFontSize = 16
        self.__buttons = buttons.copy()         # type:List[AppBarButton]
        self.__nButtons = len(self.__buttons)
        self.hiddenButtonNum = 0
        self.moreActionsButton = AppBarButton(
            "app/resource/images/album_interface/More.png", "", self)
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        for button in self.__buttons:
            button.setParent(self)
        self.moreActionsButton.hide()
        self.setMinimumHeight(155)
        self.setMaximumHeight(385)
        self.setBackgroundColor()
        self.coverLabel.setPixmap(QPixmap(self.coverPath).scaled(
            275, 275, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        self.coverLabel.setScaledContents(True)
        self.setObjectName("CollapsingAppBar")
        self.moreActionsButton.clicked.connect(self.onMoreActionsButtonClicked)
        self.resize(1300, 385)

    def setBackgroundColor(self):
        """ 设置背景颜色 """
        bgColor = self.dominantColorGetter.getDominantColor(self.coverPath)
        self.setStyleSheet("#CollapsingAppBar{background:#"+bgColor+"}")

    def resizeEvent(self, e: QResizeEvent):
        """ 改变部件位置和大小 """
        h = self.height()
        needWhiteBar = self.needWhiteBar

        # 调整封面大小和位置
        coverWidth = 275 - \
            int((385-h)/230*192) if needWhiteBar else 295-int((385-h)/230*206)
        self.coverLabel.resize(coverWidth, coverWidth)
        y = 65-int((385-h)/230*17) if needWhiteBar else 45-int((385-h)/230*4)
        self.coverLabel.move(45, y)

        # 调整标签大小和位置
        self.titleFontSize = int(40/43*(43-(385-h)/230*12))
        self.contentFontSize = int(16-(385-h)/147*3)
        self.__adjustText()
        self.titleLabel.setStyleSheet(self.__getLabelStyleSheet(
            'Microsoft YaHei Light', self.titleFontSize))
        self.contentLabel.setStyleSheet(
            self.__getLabelStyleSheet('Microsoft YaHei', self.contentFontSize))
        self.titleLabel.adjustSize()
        self.contentLabel.adjustSize()
        x = 45 + coverWidth + 44
        y1 = int(71/81*(71-(385-h)/230*25)) if needWhiteBar else y
        y2 = int(132-(385-h)/147*15) if needWhiteBar else y+56
        self.titleLabel.move(x, y1)
        self.contentLabel.move(x, y2)
        self.contentLabel.setVisible(h >= 238)

        # 调整按钮位置
        x = 45 + coverWidth + 22
        y = 288 - int((385-h)/230*206) if needWhiteBar else 308 - \
            int((385-h)/230*220)
        for button in self.__buttons:
            button.move(x, y)
            x += button.width()+10

        # 隐藏一部分按钮
        index = self.__getLastVisibleButtonIndex()
        self.hiddenButtonNum = self.__nButtons-(index+1)
        self.moreActionsButton.setVisible(index + 1 < self.__nButtons)
        for i, button in enumerate(self.__buttons):
            button.setHidden(i > index)

        # 先移动一次按钮
        self.moreActionsButton.move(
            self.__buttons[index].geometry().right()+10, y)

        # 根据按钮的位置和此时的宽度决定是否再次隐藏按钮
        if self.moreActionsButton.isVisible() and self.width() < self.moreActionsButton.geometry().right()+10:
            self.hiddenButtonNum += 1
            self.__buttons[index].hide()
            self.moreActionsButton.move(
                self.__buttons[index-1].geometry().right()+10, y)

    def paintEvent(self, e):
        """ 封面白条 """
        super().paintEvent(e)
        if not self.needWhiteBar:
            return
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setRenderHint(QPainter.Antialiasing)
        h = self.height()
        y = self.coverLabel.y()
        x = self.coverLabel.x()
        w1 = 255 - int((385-h)/230*178)
        w2 = 235 - int((385-h)/230*164)
        h_ = (self.coverLabel.width()-w1)//2
        # 绘制第一个白条
        painter.setBrush(QColor(255, 255, 255, 255*0.4))
        painter.drawRect(x+h_, y-h_, w1, h_)
        # 绘制第二个白条
        painter.setBrush(QColor(255, 255, 255, 255*0.2))
        painter.drawRect(x+2*h_, y-2*h_, w2, h_)

    @staticmethod
    def __getLabelStyleSheet(fontFamily: str, fontSize: int, fontWeight=400):
        """ 获取标签样式表

        Parameters
        ----------
        fontFamily: str
            字体家族

        fontSize: int
            以 pt 为单位的字体大小

        fontWeight: int or str
            字体粗细
        """
        styleSheet = f"""
            color: white;
            margin: 0;
            padding: 0;
            font-family: '{fontFamily}';
            font-size: {fontSize}px;
            font-weight: {fontWeight};
        """
        return styleSheet

    def __adjustText(self):
        """ 调整过长的文本 """
        maxWidth = self.width()-40-self.coverLabel.rect().right()-45
        # 调节标题
        fontMetrics = QFontMetrics(
            QFont('Microsoft YaHei', round(self.titleFontSize*27/43)))
        title = fontMetrics.elidedText(self.title, Qt.ElideRight, maxWidth)
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()
        # 调解内容
        fontMetrics = QFontMetrics(
            QFont('Microsoft YaHei', round(self.contentFontSize*27/43)))
        content = fontMetrics.elidedText(self.content, Qt.ElideRight, maxWidth)
        self.contentLabel.setText(content)
        self.contentLabel.adjustSize()

    def __getLastVisibleButtonIndex(self):
        """ 获取最后一个可见的按钮下标 """
        for i, button in enumerate(self.__buttons):
            if button.geometry().right() + 10 > self.width():
                return i-1
        return i

    def onMoreActionsButtonClicked(self):
        """ 更多操作按钮点击槽函数，需要被子类重载 """
        raise NotImplementedError("此方法需要被重载")

    def updateWindow(self, title: str, content: str, coverPath: str):
        """ 更新窗口 """
        self.title = title
        self.content = content
        self.coverPath = coverPath
        self.coverLabel.setPixmap(QPixmap(self.coverPath))
        self.setBackgroundColor()
        self.__adjustText()
        self.update()

    @property
    def buttons(self):
        return self.__buttons
