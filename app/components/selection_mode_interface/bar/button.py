# coding:utf-8
from PyQt5.QtCore import QEvent, QObject, QRect, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QPushButton


class Button(QPushButton):
    """ 选择模式栏按钮 """

    def __init__(self, iconPath: str, text: str, parent=None, buttonSize: tuple = (85, 70), objectName=None):
        super().__init__(parent)
        self.resize(*buttonSize)
        self.__iconPixmap = QPixmap(iconPath)
        self.buttonText = text
        self.__isEnter = False
        self.installEventFilter(self)
        self.setStyleSheet(
            "QPushButton{font: 15px 'Segoe UI', 'Microsoft YaHei'}")
        self.__adjustText()
        if objectName:
            self.setObjectName(objectName)

    def setText(self, text: str):
        """ 设置按钮文字 """
        self.buttonText = text
        self.__adjustText()
        self.update()

    def setIcon(self, iconPath: str):
        """ 设置按钮图标 """
        self.__iconPixmap = QPixmap(iconPath)
        self.update()

    def __adjustText(self):
        """ 根据字符串宽度调整按钮高度和字符串换行 """
        maxWidth = self.width()-4
        buttonChar_list = list(self.buttonText)

        # 计算宽度
        textWidth = 0
        for index, char in enumerate(self.buttonText):
            if textWidth + self.fontMetrics().width(char) > maxWidth:
                textWidth = 0
                # 插入换行符并调整尺寸
                buttonChar_list.insert(index, '\n')
                self.resize(self.width(), self.height() + 20)
            textWidth += self.fontMetrics().width(char)

        # 更新字符串和字符串所占rect
        self.buttonText = ''.join(buttonChar_list)
        self.__textRect = QRect(0, 40, self.width(), self.height() - 40)

    def eventFilter(self, obj, e: QEvent):
        """ 过滤事件 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.__isEnter = True
                self.update()
                return False
            elif e.type() == QEvent.Leave:
                self.__isEnter = False
                self.update()
                return False
        return super().eventFilter(obj, e)

    def paintEvent(self, e):
        """ 绘制图标和文字 """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        if self.__isEnter:
            # 绘制深色背景和边框
            painter.setPen(QPen(QColor(170, 170, 170)))
            painter.setBrush(QBrush(QColor(0, 0, 0, 17)))
            painter.drawRect(self.rect())

        # 绘制图标
        painter.drawPixmap(32, 15, self.__iconPixmap.width(),
                           self.__iconPixmap.height(), self.__iconPixmap)

        # 绘制文字
        painter.setPen(QPen(Qt.black))
        painter.setFont(self.font())
        painter.drawText(
            self.__textRect, Qt.AlignHCenter, self.buttonText)


class TwoStateButton(Button):
    """ 双态按钮 """

    clicked = pyqtSignal(bool)  # true-->全选

    def __init__(self, iconPaths: list, texts: list, parent=None, buttonSize: tuple = (85, 70), isState_1=0):
        """
        Parameters
        ----------
        iconPaths: list
            存状态0和状态1对应按钮图标地址的列表

        texts: list
            与状态0和状态1相对应的按钮文字列表

        parent:
            父级窗口

        buttonSize: tuple
            按钮大小元组

        isState_0: bool
            是否处于状态1
        """
        super().__init__(
            iconPaths[isState_1], texts[isState_1], parent, buttonSize)
        self.__iconPaths = iconPaths
        self.__texts = texts
        self.__isState_1 = isState_1
        self.__iconPixmap_list = [
            QPixmap(iconPath) for iconPath in self.__iconPaths]

    def mouseReleaseEvent(self, e):
        """ 按钮松开时取反状态 """
        super().mouseReleaseEvent(e)
        self.setState(not self.__isState_1)
        self.clicked.emit(self.__isState_1)

    def setState(self, isState_1: bool):
        """ 设置按钮状态 """
        self.__isState_1 = isState_1
        self.setText(self.__texts[self.__isState_1])
        self.setIcon(self.__iconPixmap_list[self.__isState_1])
        self.update()


class CheckAllButton(TwoStateButton):
    """ 全选按钮 """

    def __init__(self, iconPaths, texts, parent=None, buttonSize=(84, 70), isState_1=0):
        super().__init__(iconPaths, texts, parent, buttonSize, isState_1)
        self.setObjectName('checkAllButton')

    def setCheckedState(self, isChecked: bool):
        """ 设置全选/取消全选状态

        Parameters
        ----------
        isChecked: bool
            按钮图标是否为 `全选` 字样，若为 `False`，为 `取消全选` 字样
        """
        self.setState(not isChecked)


class ButtonFactory(QObject):
    """ 选择模式栏按钮工厂 """

    CANCEL = 0
    PLAY = 1
    NEXT_TO_PLAY = 2
    ADD_TO = 3
    SINGER = 4
    ALBUM = 5
    PROPERTY = 6
    EDIT_INFO = 7
    PIN_TO_START = 8
    RENAME = 9
    MOVE_UP = 10
    MOVE_DOWN = 11
    DELETE = 12
    CHECK_ALL = 13

    def __init__(self) -> None:
        super().__init__()

    def create(self, buttonType: int) -> Button:
        """ 创建一个按钮 """
        if buttonType == self.CANCEL:
            button = Button(
                ":/images/selection_mode_bar/Cancel.png", self.tr("Cancel"), objectName='cancelButton')
        elif buttonType == self.PLAY:
            button = Button(
                ":/images/selection_mode_bar/Play.png", self.tr("Play"), objectName='playButton')
        elif buttonType == self.NEXT_TO_PLAY:
            button = Button(
                ":/images/selection_mode_bar/NextToPlay.png", self.tr("Play next"), objectName='nextToPlayButton')
        elif buttonType == self.ADD_TO:
            button = Button(
                ":/images/selection_mode_bar/Add.png", self.tr("Add to"), objectName='addToButton')
        elif buttonType == self.SINGER:
            button = Button(
                ":/images/selection_mode_bar/Contact.png", self.tr("Show artist"), objectName='singerButton')
        elif buttonType == self.ALBUM:
            button = Button(
                ":/images/selection_mode_bar/ShowAlbum.png", self.tr("Show album"), objectName='albumButton')
        elif buttonType == self.PROPERTY:
            button = Button(
                ":/images/selection_mode_bar/Property.png", self.tr("Properties"), objectName='propertyButton')
        elif buttonType == self.EDIT_INFO:
            button = Button(
                ":/images/selection_mode_bar/Edit.png", self.tr("Edit info"), objectName='editInfoButton')
        elif buttonType == self.PIN_TO_START:
            button = Button(
                ":/images/selection_mode_bar/Pin.png", self.tr('Pin to Start'), objectName='pinToStartButton')
        elif buttonType == self.RENAME:
            button = Button(
                ":/images/selection_mode_bar/Edit.png", self.tr("Rename"), objectName='renameButton')
        elif buttonType == self.MOVE_UP:
            button = Button(
                ":/images/selection_mode_bar/Up.png", self.tr("Move up"), objectName='moveUpButton')
        elif buttonType == self.MOVE_DOWN:
            button = Button(
                ":/images/selection_mode_bar/Down.png", self.tr("Move down"), objectName='moveDownButton')
        elif buttonType == self.DELETE:
            button = Button(
                ":/images/selection_mode_bar/Delete.png", self.tr("Delete"), objectName='deleteButton')
        elif buttonType == self.CHECK_ALL:
            button = CheckAllButton(
                [
                    ":/images/selection_mode_bar/SelectAll.png",
                    ":/images/selection_mode_bar/CancelSelectAll.png",
                ],
                [self.tr("Select all"), self.tr("Deselect all")],
            )
        else:
            raise ValueError(f'`{buttonType}` 非法')

        return button
