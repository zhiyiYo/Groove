# coding:utf-8
from typing import List
from pathlib import Path

from common.config import ConfigItem, config
from common.icon import drawSvgIcon
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QStandardPaths
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import (QPushButton, QFileDialog, QWidget, QLabel,
                             QHBoxLayout, QToolButton)

from components.dialog_box.dialog import Dialog
from .expand_setting_card import ExpandSettingCard
from .setting_card import SettingIconFactory as SIF


class ToolButton(QToolButton):
    """ Tool button """

    def __init__(self, iconPath: str, size: tuple, iconSize: tuple, parent=None):
        super().__init__(parent=parent)
        self.isPressed = False
        self.iconPath = iconPath
        self._iconSize = iconSize
        self.setFixedSize(*size)

    def mousePressEvent(self, e):
        self.isPressed = True
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.isPressed = False
        super().mouseReleaseEvent(e)

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setOpacity(0.63 if self.isPressed else 1)
        w, h = self._iconSize
        drawSvgIcon(self.iconPath, painter, QRectF(
            (self.width()-w)//2, (self.height()-h)//2, w, h))


class PushButton(QPushButton):
    """ Push button """

    def __init__(self, iconPath: str, text: str, parent=None):
        super().__init__(parent=parent)
        self.isPressed = False
        self.iconPath = iconPath
        self.setText(text)

    def mousePressEvent(self, e):
        self.isPressed = True
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.isPressed = False
        super().mouseReleaseEvent(e)

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setOpacity(0.63 if self.isPressed else 1)
        drawSvgIcon(self.iconPath, painter, QRectF(15, 10, 20, 20))


class FolderItem(QWidget):
    """ Folder item """

    removed = pyqtSignal(QWidget)

    def __init__(self, folder: str, parent=None):
        super().__init__(parent=parent)
        self.folder = folder
        self.hBoxLayout = QHBoxLayout(self)
        self.folderLabel = QLabel(folder, self)
        self.removeButton = ToolButton(SIF.path(SIF.CLOSE), (48, 36), (15, 15), self)

        self.setFixedHeight(66)
        self.hBoxLayout.setContentsMargins(60, 0, 75, 0)
        self.hBoxLayout.addWidget(self.folderLabel, 0, Qt.AlignLeft)
        self.hBoxLayout.addSpacing(20)
        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.removeButton, 0, Qt.AlignRight)
        self.hBoxLayout.setAlignment(Qt.AlignVCenter)

        self.removeButton.clicked.connect(
            lambda: self.removed.emit(self))


class FolderListSettingCard(ExpandSettingCard):
    """ Folder list setting card """

    folderChanged = pyqtSignal(list)

    def __init__(self, configItem: ConfigItem, title: str, content: str = None, parent=None):
        """
        Parameters
        ----------
        configItem: RangeConfigItem
            configuration item operated by the card

        title: str
            the title of card

        content: str
            the content of card

        parent: QWidget
            parent widget
        """
        super().__init__(SIF.path(SIF.MUSIC_FOLDER), title, content, parent)
        self.configItem = configItem
        self.addFolderButton = PushButton(
            SIF.path(SIF.FOLDER_ADD), self.tr('Add folder'), self)

        self.folders = config.get(configItem).copy()   # type:List[str]
        self.__initWidget()

    def __initWidget(self):
        self.addWidget(self.addFolderButton)

        # initialize layout
        self.viewLayout.setSpacing(0)
        self.viewLayout.setAlignment(Qt.AlignTop)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        for folder in self.folders:
            self.__addFolderItem(folder)

        self.addFolderButton.clicked.connect(self.__showFolderDialog)

    def __showFolderDialog(self):
        """ show folder dialog """
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), QStandardPaths.writableLocation(QStandardPaths.MusicLocation))

        if not folder or folder in self.folders:
            return

        self.__addFolderItem(folder)
        self.folders.append(folder)
        config.set(self.configItem, self.folders)
        self.folderChanged.emit(self.folders)

    def __addFolderItem(self, folder: str):
        """ add folder item """
        item = FolderItem(folder, self.view)
        item.removed.connect(self.__removeFolderItem)
        self.viewLayout.addWidget(item)
        self._adjustViewSize()

    def __removeFolderItem(self, item: FolderItem):
        """ remove folder item """
        name = Path(item.folder).name
        title = self.tr('Are you sure you want to delete the folder?')
        content = self.tr("If you delete the ") + f'"{name}"' + \
            self.tr(" folder and remove it from the list, the folder will no "
                    "longer appear in the list, but will not be deleted.")
        w = Dialog(title, content, self.window())
        if not w.exec_():
            return

        if item.folder not in self.folders:
            return

        self.folders.remove(item.folder)
        self.viewLayout.deleteWidget(item)
        self._adjustViewSize()

        self.folderChanged.emit(self.folders)
        config.set(self.configItem, self.folders)