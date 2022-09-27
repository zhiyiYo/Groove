# coding:utf-8
from PyQt5.QtCore import Qt, QSize, QObject
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QPushButton


class AppBarButton(QPushButton):

    def __init__(self, iconPath: str, text: str, parent=None, objectName=None):
        super().__init__(parent)
        self.pixmap = QPixmap(iconPath)
        self.__text = text
        styleSheet = """
        QPushButton {
            border: none;
            border-radius: 23px;
            spacing: 10px;
            color: white;
            background: transparent;
            font: 16px "Segoe UI", "Microsoft YaHei";
            padding: 13px 24px 13px 24px;
        }

        QPushButton:hover {
            background: rgba(255, 255, 255, 0.2)
        }

        QPushButton:pressed {
            background: rgba(255, 255, 255, 0.5)
        }
        """
        self.setStyleSheet(styleSheet)
        self.setFocusPolicy(Qt.NoFocus)
        self.adjustSize()
        if objectName:
            self.setObjectName(objectName)

    def sizeHint(self):
        spacing = 12*(self.__text != '')
        w = self.pixmap.width() + spacing + self.fontMetrics().width(self.__text) + 46
        size = QSize(w, 46)
        return size

    def text(self):
        return self.__text

    def paintEvent(self, e):
        """ paint icon """
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        y = (self.height()-self.pixmap.height())//2
        painter.drawPixmap(24, y, self.pixmap)
        painter.setPen(Qt.white)
        painter.setFont(self.font())
        painter.drawText(54, 29, self.__text)


class AppBarButtonFactory(QObject):
    """ Selection mode button factory """

    PLAY = 0
    ADD_TO = 1
    SINGER = 2
    ONLINE = 3
    PIN_TO_START = 4
    EDIT_INFO = 5
    RENAME = 6
    DELETE = 7
    ADD_FAVORITE = 8
    MORE = 9

    def create(self, buttonType: int) -> AppBarButton:
        """ create a button """
        if buttonType == self.PLAY:
            button = AppBarButton(
                ":/images/album_interface/Play.png", self.tr("Play all"), objectName="playAllButton")
        elif buttonType == self.ADD_TO:
            button = AppBarButton(
                ":/images/album_interface/Add.png", self.tr("Add to"), objectName="addToButton")
        elif buttonType == self.SINGER:
            button = AppBarButton(
                ":/images/album_interface/Contact.png", self.tr("Show artist"), objectName="singerButton")
        elif buttonType == self.ONLINE:
            button = AppBarButton(
                ":/images/album_interface/Online.png", self.tr("View online"), objectName="viewOnlineButton")
        elif buttonType == self.PIN_TO_START:
            button = AppBarButton(
                ":/images/album_interface/Pin.png", self.tr("Pin to Start"), objectName="pinToStartMenuButton")
        elif buttonType == self.EDIT_INFO:
            button = AppBarButton(
                ":/images/album_interface/Edit.png", self.tr("Edit info"), objectName="editInfoButton")
        elif buttonType == self.RENAME:
            button = AppBarButton(
                ":/images/album_interface/Edit.png", self.tr("Rename"), objectName="renameButton")
        elif buttonType == self.DELETE:
            button = AppBarButton(
                ":/images/album_interface/Delete.png", self.tr("Delete"), objectName="deleteButton")
        elif buttonType == self.ADD_FAVORITE:
            button = AppBarButton(
                ":/images/album_interface/AddFavorite.png", self.tr("Add songs"), objectName="addButton")
        elif buttonType == self.MORE:
            button = AppBarButton(
                ":/images/album_interface/More.png", "", objectName="moreActionButton")
        else:
            raise ValueError(f'Button type `{buttonType}` is illegal')

        return button