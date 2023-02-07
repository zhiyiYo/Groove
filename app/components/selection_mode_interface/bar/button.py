# coding:utf-8
from common.icon import getIconColor, drawSvgIcon
from common.config import config, Theme
from PyQt5.QtCore import QEvent, QObject, QRect, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QPushButton


class Button(QPushButton):
    """ Button of selection mode bar """

    def __init__(self, iconPath: str, text: str, parent=None, buttonSize: tuple = (85, 70), objectName=None):
        super().__init__(text, parent)
        self.isEnter = False
        self.iconPath = iconPath

        self.resize(*buttonSize)
        self.setStyleSheet("QPushButton{font: 15px 'Segoe UI', 'Microsoft YaHei'}")
        self.setText(text)

        self.installEventFilter(self)
        if objectName:
            self.setObjectName(objectName)

    def setText(self, text: str):
        """ set the text of button """
        maxWidth = self.width()-4
        chars = list(text)

        # calculate text width
        w = 0
        for index, char in enumerate(text):
            if w + self.fontMetrics().width(char) > maxWidth:
                w = 0
                chars.insert(index, '\n')
                self.resize(self.width(), self.height() + 20)

            w += self.fontMetrics().width(char)

        super().setText(''.join(chars))
        self.update()

    def setIcon(self, iconPath: str):
        """ set the icon of button """
        self.iconPath = iconPath
        self.update()

    def eventFilter(self, obj, e: QEvent):
        if obj is self:
            if e.type() == QEvent.Enter:
                self.isEnter = True
                self.update()
            elif e.type() == QEvent.Leave:
                self.isEnter = False
                self.update()

        return super().eventFilter(obj, e)

    def paintEvent(self, e):
        """ paint button """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)

        isDark = config.theme == Theme.DARK
        if self.isEnter:
            # draw background and border
            bc = 85 if isDark else 170
            painter.setPen(QColor(bc, bc, bc))
            painter.setBrush(QColor(0, 0, 0, 17))
            painter.drawRect(self.rect())

        # draw icon
        drawSvgIcon(self.iconPath, painter, QRect(32, 15, 20, 20))

        # draw text
        painter.setPen(Qt.white if isDark else Qt.black)
        painter.setFont(self.font())
        rect = QRect(0, 40, self.width(), self.height() - 40)
        painter.drawText(rect, Qt.AlignHCenter, self.text())


class TwoStateButton(Button):
    """ Two state button """

    clicked = pyqtSignal(bool)  # true --> select all

    def __init__(self, iconPaths: list, texts: list, parent=None, buttonSize: tuple = (85, 70), isState_1=0):
        """
        Parameters
        ----------
        iconPaths: list
            icon path list contains state0 and state1 icon

        texts: list
            texts list contains state0 and state1 text

        parent:
            parent window

        buttonSize: tuple
            button size

        isState_0: bool
            whether button in state0
        """
        super().__init__(
            iconPaths[isState_1], texts[isState_1], parent, buttonSize)
        self.iconPaths = iconPaths
        self.texts = texts
        self.isState_1 = isState_1

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.setState(not self.isState_1)
        self.clicked.emit(self.isState_1)

    def setState(self, isState_1: bool):
        """ set button state """
        self.isState_1 = isState_1
        self.setText(self.texts[self.isState_1])
        self.setIcon(self.iconPaths[self.isState_1])
        self.update()


class CheckAllButton(TwoStateButton):
    """ Check all button """

    def __init__(self, iconPaths, texts, parent=None, buttonSize=(84, 70), isState_1=0):
        super().__init__(iconPaths, texts, parent, buttonSize, isState_1)
        self.setObjectName('checkAllButton')

    def setCheckedState(self, isChecked: bool):
        """ set check all/deselect all state

        Parameters
        ----------
        isChecked: bool
            whether the button icon is `select all`, icon will be `deselect all` if `isChecked` is `False`
        """
        self.setState(not isChecked)


class SelectionModeBarButtonFactory(QObject):
    """ Selection mode button factory """

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
    DOWNLOAD = 14

    def create(self, buttonType: int) -> Button:
        """ create a button """
        c = getIconColor()
        folder = ":/images/selection_mode_bar"
        if buttonType == self.CANCEL:
            button = Button(
                f"{folder}/Cancel_{c}.svg", self.tr("Cancel"), objectName='cancelButton')
        elif buttonType == self.PLAY:
            button = Button(
                f"{folder}/Play_{c}.svg", self.tr("Play"), objectName='playButton')
        elif buttonType == self.NEXT_TO_PLAY:
            button = Button(
                f"{folder}/NextToPlay_{c}.svg", self.tr("Play next"), objectName='nextToPlayButton')
        elif buttonType == self.ADD_TO:
            button = Button(
                f"{folder}/Add_{c}.svg", self.tr("Add to"), objectName='addToButton')
        elif buttonType == self.SINGER:
            button = Button(
                f"{folder}/Contact_{c}.svg", self.tr("Show artist"), objectName='singerButton')
        elif buttonType == self.ALBUM:
            button = Button(
                f"{folder}/ShowAlbum_{c}.svg", self.tr("Show album"), objectName='albumButton')
        elif buttonType == self.PROPERTY:
            button = Button(
                f"{folder}/Property_{c}.svg", self.tr("Properties"), objectName='propertyButton')
        elif buttonType == self.EDIT_INFO:
            button = Button(
                f"{folder}/Edit_{c}.svg", self.tr("Edit info"), objectName='editInfoButton')
        elif buttonType == self.PIN_TO_START:
            button = Button(
                f"{folder}/Pin_{c}.svg", self.tr('Pin to Start'), objectName='pinToStartButton')
        elif buttonType == self.RENAME:
            button = Button(
                f"{folder}/Edit_{c}.svg", self.tr("Rename"), objectName='renameButton')
        elif buttonType == self.MOVE_UP:
            button = Button(
                f"{folder}/Up_{c}.svg", self.tr("Move up"), objectName='moveUpButton')
        elif buttonType == self.MOVE_DOWN:
            button = Button(
                f"{folder}/Down_{c}.svg", self.tr("Move down"), objectName='moveDownButton')
        elif buttonType == self.DELETE:
            button = Button(
                f"{folder}/Delete_{c}.svg", self.tr("Delete"), objectName='deleteButton')
        elif buttonType == self.DOWNLOAD:
            button = Button(
                f"{folder}/Download_{c}.svg", self.tr("Download"), objectName='downloadButton')
        elif buttonType == self.CHECK_ALL:
            button = CheckAllButton(
                [
                    f"{folder}/SelectAll_{c}.svg",
                    f"{folder}/CancelSelectAll_{c}.svg",
                ],
                [self.tr("Select all"), self.tr("Deselect all")],
            )
        else:
            raise ValueError(f'Button type `{buttonType}` is illegal')

        return button
