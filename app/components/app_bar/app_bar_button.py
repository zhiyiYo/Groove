# coding:utf-8
from common.icon import drawSvgIcon
from PyQt5.QtCore import QEvent, Qt, QObject, QPoint, QRect
from PyQt5.QtGui import QPainter, QHoverEvent, QIcon
from PyQt5.QtWidgets import QApplication, QPushButton


class AppBarButton(QPushButton):

    def __init__(self, iconPath: str, text: str, parent=None, objectName=None):
        super().__init__(text, parent)
        self.iconPath = iconPath
        styleSheet = f"""
            QPushButton {{
                border: none;
                border-radius: 23px;
                spacing: 10px;
                color: white;
                background: transparent;
                font: 16px "Segoe UI", "Microsoft YaHei";
                padding: 13px 24px 13px {54 if text else 6}px;
            }}

            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.2)
            }}

            QPushButton:pressed {{
                background: rgba(255, 255, 255, 0.4)
            }}
        """
        self.setStyleSheet(styleSheet)
        self.setFocusPolicy(Qt.NoFocus)
        self.adjustSize()
        if objectName:
            self.setObjectName(objectName)

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        # draw icon
        rect = QRect(24, (self.height()-20)/2, 20, 20)
        drawSvgIcon(self.iconPath, painter, rect)

    def cancelHoverState(self):
        """ cancel mouse hover state """
        self.setAttribute(Qt.WA_UnderMouse, False)
        e = QHoverEvent(QEvent.HoverLeave, QPoint(self.width()*2, 0), QPoint())
        QApplication.sendEvent(self, e)


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
                ":/images/app_bar/Play.svg", self.tr("Play all"), objectName="playAllButton")
        elif buttonType == self.ADD_TO:
            button = AppBarButton(
                ":/images/app_bar/Add.svg", self.tr("Add to"), objectName="addToButton")
        elif buttonType == self.SINGER:
            button = AppBarButton(
                ":/images/app_bar/Contact.svg", self.tr("Show artist"), objectName="singerButton")
        elif buttonType == self.ONLINE:
            button = AppBarButton(
                ":/images/app_bar/Online.svg", self.tr("View online"), objectName="viewOnlineButton")
        elif buttonType == self.PIN_TO_START:
            button = AppBarButton(
                ":/images/app_bar/Pin.svg", self.tr("Pin to Start"), objectName="pinToStartMenuButton")
        elif buttonType == self.EDIT_INFO:
            button = AppBarButton(
                ":/images/app_bar/Edit.svg", self.tr("Edit info"), objectName="editInfoButton")
        elif buttonType == self.RENAME:
            button = AppBarButton(
                ":/images/app_bar/Edit.svg", self.tr("Rename"), objectName="renameButton")
        elif buttonType == self.DELETE:
            button = AppBarButton(
                ":/images/app_bar/Delete.svg", self.tr("Delete"), objectName="deleteButton")
        elif buttonType == self.ADD_FAVORITE:
            button = AppBarButton(
                ":/images/app_bar/AddFavorite.svg", self.tr("Add songs"), objectName="addButton")
        elif buttonType == self.MORE:
            button = AppBarButton(
                ":/images/app_bar/More.svg", "", objectName="moreActionButton")
        else:
            raise ValueError(f'Button type `{buttonType}` is illegal')

        return button
