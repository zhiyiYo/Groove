# coding:utf-8
from typing import List, Union

from common.config import config, Theme
from common.crawler import SongQuality
from common.icon import MenuIconEngine, QIcon, getIconColor, drawSvgIcon
from common.os_utils import getPlaylistNames
from common.signal_bus import signalBus
from common.style_sheet import setStyleSheet
from common.window_effect import WindowEffect
from .list_widget import ListWidget
from PyQt5.QtCore import (QEasingCurve, QEvent, QPropertyAnimation, QPoint, QRect,
                          Qt, pyqtSignal, QRectF, QSize, QTimer)
from PyQt5.QtGui import QColor, QPainter, QPen, QCursor, QPixmap, QRegion, QShowEvent
from PyQt5.QtWidgets import (QAction, QApplication, QMenu, QWidget, QListWidgetItem,
                             QHBoxLayout, QGraphicsDropShadowEffect)


class MenuIconFactory:
    """ Menu icon factory """

    ADD = "Add"
    CUT = "Cut"
    COPY = "Copy"
    LOCK = "Lock"
    VIEW = "View"
    PLAY = "Play"
    NEXT = "Next"
    PAUSE = "Pause"
    MOVIE = "Movie"
    ALBUM = "Album"
    PASTE = "Paste"
    LYRIC = "Lyric"
    CLEAR = "Clear"
    CLOSE = "Close"
    EMBED = "Embed"
    SPEED = "Speed"
    CANCEL = "Cancel"
    UNLOCK = "Unlock"
    RELOAD = "Reload"
    UNVIEW = "Unview"
    LOCATE = "Locate"
    PLAYING = "Playing"
    SPEED_UP = "SpeedUp"
    SIGN_OUT = "SignOut"
    SETTINGS = "Settings"
    PREVIOUS = "Previous"
    PLAYLIST = "Playlist"
    FILE_LINK = "FileLink"
    MUSIC_NOTE = "MusicNote"
    CLEAR_BOLD = "ClearBold"
    SPEED_DOWN = "SpeedDown"
    FULL_SCREEN = "FullScreen"
    FOLDER_LINK = "FolderLink"
    MUSIC_FOLDER = "MusicFolder"
    CHEVRON_RIGHT = "ChevronRight"

    @classmethod
    def path(cls, iconType: str, theme=Theme.AUTO):
        """ get the path of menu icon

        Parameters
        ----------
        iconType: str
            menu icon type

        theme: Theme
            the theme of icon
            * `Theme.Light`: black icon
            * `Theme.DARK`: white icon
            * `Theme.AUTO`: icon color depends on `config.theme`
        """
        if theme == Theme.AUTO:
            c = getIconColor()
        else:
            c = "white" if theme == Theme.DARK else "black"

        return f":/images/menu/{iconType}_{c}.svg"

    @classmethod
    def icon(cls, iconType: str, theme=Theme.AUTO):
        """ create icon

        Parameters
        ----------
        iconType: str
            menu icon type

        theme: Theme
            the theme of icon
            * `Theme.Light`: black icon
            * `Theme.DARK`: white icon
            * `Theme.AUTO`: icon color depends on `config.theme`
        """
        return QIcon(cls.path(iconType, theme))

    @classmethod
    def render(cls, iconType: str, painter: QPainter, rect: Union[QRect, QRectF], theme=Theme.AUTO):
        """ draw svg icon

        Parameters
        ----------
        iconType: str
            menu icon type

        painter: QPainter
            painter

        rect: QRect | QRectF
            the rect to render icon

        theme: Theme
            the theme of icon
        """
        drawSvgIcon(cls.path(iconType, theme), painter, rect)


MIF = MenuIconFactory


class MenuSeparator(QWidget):
    """ Menu separator """

    def __init__(self, parent=None, theme=Theme.AUTO):
        super().__init__(parent=parent)
        self.setFixedHeight(11)
        self.theme = theme

    def paintEvent(self, e):
        painter = QPainter(self)
        theme = config.theme if self.theme == Theme.AUTO else self.theme
        c = 255 if theme == Theme.DARK else 0
        pen = QPen(QColor(c, c, c, 104), 1)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawLine(0, 5, self.width(), 5)


class SubMenuItemWidget(QWidget):
    """ Sub menu item """

    showMenuSig = pyqtSignal(QListWidgetItem)

    def __init__(self, menu, item, parent=None, theme=Theme.AUTO):
        """
        Parameters
        ----------
        menu: QMenu | RoundMenu
            sub menu

        item: QListWidgetItem
            menu item

        parent: QWidget
            parent widget
        """
        super().__init__(parent)
        self.menu = menu
        self.item = item
        self.theme = theme

    def enterEvent(self, e):
        super().enterEvent(e)
        self.showMenuSig.emit(self.item)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)

        # draw right arrow
        MIF.render(MIF.CHEVRON_RIGHT, painter, QRectF(
            self.width()-13, self.height()/2-12/2, 12, 12), self.theme)


class MenuActionListWidget(ListWidget):
    """ Menu action list widget """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setViewportMargins(0, 8, 0, 8)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTextElideMode(Qt.ElideNone)
        self.setMouseTracking(True)
        self.setIconSize(QSize(19, 19))
        self.setStyleSheet(
            'MenuActionListWidget{font: 18px "Segoe UI", "Microsoft YaHei"}')

    def insertItem(self, row, item):
        """ inserts menu item at the position in the list given by row """
        super().insertItem(row, item)
        self.adjustSize()

    def addItem(self, item):
        """ add menu item at the end """
        super().addItem(item)
        self.adjustSize()

    def takeItem(self, row):
        """ delete item from list """
        item = super().takeItem(row)
        self.adjustSize()
        return item

    def adjustSize(self):
        size = QSize()
        for i in range(self.count()):
            s = self.item(i).sizeHint()
            size.setWidth(max(s.width(), size.width()))
            size.setHeight(size.height() + s.height())

        # adjust the height of viewport
        ss = QApplication.screenAt(QCursor.pos()).availableSize()
        w, h = ss.width() - 100, ss.height() - 100
        vsize = QSize(size)
        vsize.setHeight(min(h-12, vsize.height()))
        vsize.setWidth(min(w-12, vsize.width()))
        self.viewport().adjustSize()

        # adjust the height of list widget
        m = self.viewportMargins()
        size += QSize(m.left()+m.right()+2, m.top()+m.bottom())
        size.setHeight(min(h, size.height()+3))
        size.setWidth(min(w, size.width()))
        self.setFixedSize(size)

    def setItemHeight(self, height):
        """ set the height of item """
        for i in range(self.count()):
            item = self.item(i)
            item.setSizeHint(item.sizeHint().width(), i)

        self.adjustSize()


class RoundMenu(QWidget):
    """ Round corner menu """

    def __init__(self, title="", parent=None, theme=Theme.AUTO):
        super().__init__(parent=parent)
        self.theme = theme
        self._title = title
        self._icon = QIcon()
        self._actions = []
        self._subMenus = []     # type: List[RoundMenu]
        self.isSubMenu = False
        self.isHideBySystem = True
        self.parentMenu = None  # type: RoundMenu
        self.menuItem = None    # QListWidget
        self.lastHoverItem = None
        self.lastHoverSubMenuItem = None
        self.itemHeight = 39
        self.hBoxLayout = QHBoxLayout(self)
        self.view = MenuActionListWidget(self)
        self.ani = QPropertyAnimation(self, b'pos', self)
        self.__initWidgets()

    def __initWidgets(self):
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint |
                            Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)

        self.setShadowEffect()
        self.hBoxLayout.addWidget(self.view, 1, Qt.AlignCenter)
        self.hBoxLayout.setContentsMargins(12, 8, 12, 20)

        setStyleSheet(self, 'menu', self.theme)
        self.view.itemClicked.connect(self._onItemClicked)
        self.view.itemEntered.connect(self._onItemEntered)
        self.ani.valueChanged.connect(self._onSlideValueChanged)

    def setItemHeight(self, height):
        """ set the height of menu item """
        if height == self.itemHeight:
            return

        self.itemHeight = height
        self.view.setItemHeight(height)

    def setShadowEffect(self, blurRadius=30, offset=(0, 8), color=QColor(0, 0, 0, 30)):
        """ add shadow to dialog """
        self.shadowEffect = QGraphicsDropShadowEffect(self.view)
        self.shadowEffect.setBlurRadius(blurRadius)
        self.shadowEffect.setOffset(*offset)
        self.shadowEffect.setColor(color)
        self.view.setGraphicsEffect(None)
        self.view.setGraphicsEffect(self.shadowEffect)

    def _setParentMenu(self, parent, item: QListWidgetItem):
        self.parentMenu = parent
        self.menuItem = item
        self.isSubMenu = True if parent else False

    def adjustSize(self):
        m = self.layout().contentsMargins()
        w = self.view.width() + m.left() + m.right()
        h = self.view.height() + m.top() + m.bottom()
        self.setFixedSize(w, h)

    def icon(self):
        return self._icon

    def title(self):
        return self._title

    def clear(self):
        """ clear all actions """
        for i in range(len(self._actions)-1, -1, -1):
            self.removeAction(self._actions[i])

    def setIcon(self, icon: QIcon):
        """ set the icon of menu """
        self._icon = icon

    def addAction(self, action: QAction):
        """ add action to menu

        Parameters
        ----------
        action: QAction
            menu action
        """
        item = self._createActionItem(action)
        self.view.addItem(item)
        self.adjustSize()

    def _createActionItem(self, action: QAction, before=None):
        """ create menu action item  """
        if not before:
            self._actions.append(action)
        elif before in self._actions:
            index = self._actions.index(before)
            self._actions.insert(index, action)
        else:
            raise ValueError('`before` is not in the action list')

        item = QListWidgetItem(self._createItemIcon(action), action.text())

        if not self._hasItemIcon():
            w = 35 + self.view.fontMetrics().width(action.text())
        else:
            # add a blank character to increase space between icon and text
            item.setText(" " + item.text())
            w = 75 + self.view.fontMetrics().width(item.text())

        item.setSizeHint(QSize(w, self.itemHeight))
        item.setData(Qt.UserRole, action)
        action.setProperty('item', item)
        action.changed.connect(self._onActionChanged)
        return item

    def _hasItemIcon(self):
        return any(not i.icon().isNull() for i in self._actions+self._subMenus)

    def _createItemIcon(self, w: Union[QAction, QMenu]):
        """ create the icon of menu item """
        hasIcon = self._hasItemIcon()
        icon = QIcon(MenuIconEngine(w.icon()))

        if hasIcon and w.icon().isNull():
            pixmap = QPixmap(self.view.iconSize())
            pixmap.fill(Qt.transparent)
            icon = QIcon(pixmap)
        elif not hasIcon:
            icon = QIcon()

        return icon

    def insertAction(self, before: QAction, action: QAction):
        """ inserts action to menu, before the action before """
        if before not in self._actions:
            return

        beforeItem = before.property('item')
        if not beforeItem:
            return

        index = self.view.row(beforeItem)
        item = self._createActionItem(action, before)
        self.view.insertItem(index, item)
        self.adjustSize()

    def addActions(self, actions: List[QAction]):
        """ add actions to menu

        Parameters
        ----------
        actions: Iterable[QAction]
            menu actions
        """
        for action in actions:
            self.addAction(action)

    def insertActions(self, before: QAction, actions: List[QAction]):
        """ inserts the actions actions to menu, before the action before """
        for action in actions:
            self.insertAction(before, action)

    def removeAction(self, action: QAction):
        """ remove action from menu """
        if action not in self._actions:
            return

        index = self._actions.index(action)
        self._actions.remove(action)
        action.setProperty('item', None)
        item = self.view.takeItem(index)
        item.setData(Qt.UserRole, None)

        # delete widget
        widget = self.view.itemWidget(item)
        if widget:
            widget.deleteLater()

    def setDefaultAction(self, action: QAction):
        """ set the default action """
        if action not in self._actions:
            return

        index = self._actions.index(action)
        self.view.setCurrentRow(index)

    def addMenu(self, menu):
        """ add sub menu

        Parameters
        ----------
        menu: RoundMenu
            sub round menu
        """
        if not isinstance(menu, RoundMenu):
            raise ValueError('`menu` should be an instance of `RoundMenu`.')

        item, w = self._createSubMenuItem(menu)
        self.view.addItem(item)
        self.view.setItemWidget(item, w)
        self.adjustSize()

    def insertMenu(self, before: QAction, menu):
        """ insert menu before action `before` """
        if not isinstance(menu, RoundMenu):
            raise ValueError('`menu` should be an instance of `RoundMenu`.')

        if before not in self._actions:
            raise ValueError('`before` should be in menu action list')

        item, w = self._createSubMenuItem(menu)
        self.view.insertItem(self.view.row(before.property('item')), item)
        self.view.setItemWidget(item, w)
        self.adjustSize()

    def _createSubMenuItem(self, menu):
        """ Create submenu item """
        self._subMenus.append(menu)

        item = QListWidgetItem(self._createItemIcon(menu), menu.title())
        if not self._hasItemIcon():
            w = 60 + self.view.fontMetrics().width(menu.title())
        else:
            # add a blank character to increase space between icon and text
            item.setText(" " + item.text())
            w = 75 + self.view.fontMetrics().width(item.text())

        # add submenu item
        menu._setParentMenu(self, item)
        item.setSizeHint(QSize(w, self.itemHeight))
        item.setData(Qt.UserRole, menu)
        w = SubMenuItemWidget(menu, item, self, self.theme)
        w.showMenuSig.connect(self._showSubMenu)
        w.resize(item.sizeHint())

        return item, w

    def _showSubMenu(self, item):
        """ show sub menu """
        self.lastHoverItem = item
        self.lastHoverSubMenuItem = item
        # delay 400 ms to anti-shake
        QTimer.singleShot(400, self._onShowMenuTimeOut)

    def _onShowMenuTimeOut(self):
        if self.lastHoverSubMenuItem is None or not self.lastHoverItem is self.lastHoverSubMenuItem:
            return

        w = self.view.itemWidget(self.lastHoverSubMenuItem)
        self.lastHoverItem = None
        self.lastHoverSubMenuItem = None
        pos = w.mapToGlobal(QPoint(w.width()+8, -8))
        w.menu.exec(pos)

    def addSeparator(self):
        """ add seperator to menu """
        m = self.view.viewportMargins()
        w = self.view.width()-m.left()-m.right()

        # icon separator
        separator = MenuSeparator(self.view, self.theme)
        separator.resize(w, separator.height())

        # add separator to list widget
        item = QListWidgetItem(self.view)
        item.setFlags(Qt.NoItemFlags)
        item.setSizeHint(QSize(w, separator.height()))
        self.view.addItem(item)
        self.view.setItemWidget(item, separator)
        self.adjustSize()

    def _onItemClicked(self, item):
        action = item.data(Qt.UserRole)
        if action not in self._actions:
            return

        self._hideMenu(False)

        if not self.isSubMenu:
            action.trigger()
            return

        # close parent menu
        self.closeParentMenu()
        action.trigger()

    def closeParentMenu(self):
        menu = self
        while menu.parentMenu:
            menu = menu.parentMenu

        menu.close()

    def _onItemEntered(self, item):
        self.lastHoverItem = item
        if not isinstance(item.data(Qt.UserRole), RoundMenu):
            return

        self._showSubMenu(item)

    def _hideMenu(self, isHideBySystem=False):
        self.isHideBySystem = isHideBySystem
        if self.isSubMenu:
            self.hide()
        else:
            self.close()

        self.view.clearSelection()

    def hideEvent(self, e):
        if self.isHideBySystem and self.isSubMenu:
            self.closeParentMenu()

        self.isHideBySystem = True
        e.accept()

    def menuActions(self):
        return self._actions

    def mousePressEvent(self, e):
        if self.childAt(e.pos()) is not self.view:
            self._hideMenu(True)

    def mouseMoveEvent(self, e):
        if not self.isSubMenu:
            return

        # hide submenu when mouse moves out of submenu item
        pos = e.globalPos()
        view = self.parentMenu.view

        # get the rect of menu item
        margin = view.viewportMargins()
        rect = view.visualItemRect(self.menuItem).translated(
            view.mapToGlobal(QPoint()))
        rect = rect.translated(margin.left(), margin.top()+3)
        if self.parentMenu.geometry().contains(pos) and not rect.contains(pos) and \
                not self.geometry().contains(pos):
            view.clearSelection()
            self._hideMenu(False)

            # update style
            index = view.row(self.menuItem)
            if index > 0:
                view.item(index-1).setFlags(Qt.ItemIsEnabled)
            if index < view.count()-1:
                view.item(index+1).setFlags(Qt.ItemIsEnabled)

    def _onActionChanged(self):
        """ action changed slot """
        action = self.sender()  # type:QAction
        item = action.property('item')  # type:QListWidgetItem
        item.setIcon(self._createItemIcon(action))

        if not self._hasItemIcon():
            item.setText(action.text())
            w = 35 + self.view.fontMetrics().width(action.text())
        else:
            # add a blank character to increase space between icon and text
            item.setText(" " + action.text())
            w = 75 + self.view.fontMetrics().width(item.text())

        item.setSizeHint(QSize(w, self.itemHeight))
        self.view.adjustSize()
        self.adjustSize()

    def _onSlideValueChanged(self, pos):
        m = self.layout().contentsMargins()
        w = self.view.width() + m.left() + m.right() + 150
        h = self.view.height() + m.top() + m.bottom() + 25
        y = self.ani.endValue().y() - pos.y()
        self.setMask(QRegion(0, y, w, h))

    def getPopupPos(self, widget: QWidget):
        """ get suitable popup position

        Parameters
        ----------
        widget: QWidget
            the widget that triggers the pop-up menu
        """
        pos = widget.mapToGlobal(QPoint())
        x = pos.x() + widget.width() + 5
        y = pos.y() + int(widget.height() / 2 - (self.height()-20) / 2)
        return QPoint(x, y)

    def exec(self, pos: QPoint, ani=True):
        """ show menu

        Parameters
        ----------
        pos: QPoint
            pop-up position

        ani: bool
            Whether to show pop-up animation
        """
        if self.isVisible():
            return

        desktop = QApplication.desktop().availableGeometry()
        w, h = self.width() + 5, self.height() + 5
        pos.setX(max(
            10, min(pos.x() - self.layout().contentsMargins().left(), desktop.width() - w)))
        pos.setY(max(10, min(pos.y() - 5, desktop.height() - h)))

        if ani:
            self.ani.setStartValue(pos-QPoint(0, h/2))
            self.ani.setEndValue(pos)
            self.ani.setDuration(250)
            self.ani.setEasingCurve(QEasingCurve.OutQuad)
            self.ani.start()
        else:
            self.move(pos)

        self.show()

        if not self.isSubMenu:
            return

        self.menuItem.setSelected(True)

        # temporarily disable item to change style
        view = self.parentMenu.view
        index = view.row(self.menuItem)
        if index > 0:
            view.item(index-1).setFlags(Qt.NoItemFlags)
        if index < view.count()-1:
            view.item(index+1).setFlags(Qt.NoItemFlags)

    def exec_(self, pos: QPoint, ani=True):
        """ show menu

        Parameters
        ----------
        pos: QPoint
            pop-up position

        ani: bool
            Whether to show pop-up animation
        """
        self.exec(pos, ani)


class AeroMenu(QMenu):
    """ Aero menu """

    def __init__(self, string="", parent=None):
        super().__init__(string, parent)
        self.windowEffect = WindowEffect()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground | Qt.WA_StyledBackground)
        self.setObjectName("AeroMenu")
        setStyleSheet(self, 'menu')

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            self.setMenuEffect()
        return QMenu.event(self, e)

    def setMenuEffect(self):
        """ set menu effect """
        self.windowEffect.setAeroEffect(self.winId())
        self.windowEffect.addMenuShadowEffect(self.winId())


class DWMMenu(QMenu):
    """ A menu with DWM shadow """

    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.windowEffect = WindowEffect()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_StyledBackground)
        setStyleSheet(self, 'menu')

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            self.windowEffect.addMenuShadowEffect(self.winId())
        return QMenu.event(self, e)

    def getPopupPos(self, widget: QWidget):
        """ get suitable popup position

        Parameters
        ----------
        widget: QWidget
            the widget that triggers the pop-up menu
        """
        pos = widget.mapToGlobal(QPoint())
        x = pos.x() + widget.width() + 5
        y = pos.y() + int(widget.height() / 2 - (13 + 38 * len(self.actions())) / 2)
        return QPoint(x, y)


class AddToMenu(RoundMenu):
    """ Add to menu """

    addSongsToPlaylistSig = pyqtSignal(str)

    def __init__(self, title="Add to", parent=None, theme=Theme.AUTO):
        super().__init__(title, parent, theme)

        self.playingAct = QAction(
            MIF.icon(MIF.PLAYING, theme), self.tr("Now playing"), self)
        self.newPlaylistAct = QAction(
            MIF.icon(MIF.ADD, theme), self.tr("New playlist"), self)

        # create actions according to playlists
        names = getPlaylistNames()
        self.playlistNameActs = [
            QAction(MIF.icon(MIF.ALBUM, theme), i, self) for i in names]

        self.addAction(self.playingAct)
        self.addSeparator()
        self.addActions([self.newPlaylistAct] + self.playlistNameActs)

        # connect the signal of playlist to slot
        for name, act in zip(names, self.playlistNameActs):
            act.triggered.connect(
                lambda c, n=name: self.addSongsToPlaylistSig.emit(n))


class DownloadMenu(RoundMenu):
    """ Download online music menu """

    downloadSig = pyqtSignal(SongQuality)

    def __init__(self, title="Download", parent=None, theme=Theme.AUTO):
        super().__init__(title=title, parent=parent, theme=theme)
        self.standardQualityAct = QAction(self.tr('Standard'), self)
        self.highQualityAct = QAction(self.tr('HQ'), self)
        self.superQualityAct = QAction(self.tr('SQ'), self)
        self.addActions(
            [self.standardQualityAct, self.highQualityAct, self.superQualityAct])
        self.standardQualityAct.triggered.connect(
            lambda: self.downloadSig.emit(SongQuality.STANDARD))
        self.highQualityAct.triggered.connect(
            lambda: self.downloadSig.emit(SongQuality.HIGH))
        self.superQualityAct.triggered.connect(
            lambda: self.downloadSig.emit(SongQuality.SUPER))


class LineEditMenu(RoundMenu):
    """ Line edit menu """

    def __init__(self, parent):
        super().__init__("", parent)

    def createActions(self):
        self.cutAct = QAction(
            MIF.icon(MIF.CUT),
            self.tr("Cut"),
            self,
            shortcut="Ctrl+X",
            triggered=self.parent().cut,
        )
        self.copyAct = QAction(
            MIF.icon(MIF.COPY),
            self.tr("Copy"),
            self,
            shortcut="Ctrl+C",
            triggered=self.parent().copy,
        )
        self.pasteAct = QAction(
            MIF.icon(MIF.PASTE),
            self.tr("Paste"),
            self,
            shortcut="Ctrl+V",
            triggered=self.parent().paste,
        )
        self.cancelAct = QAction(
            MIF.icon(MIF.CANCEL),
            self.tr("Cancel"),
            self,
            shortcut="Ctrl+Z",
            triggered=self.parent().undo,
        )
        self.selectAllAct = QAction(
            self.tr("Select all"), self, shortcut="Ctrl+A", triggered=self.parent().selectAll)
        self.action_list = [self.cutAct, self.copyAct,
                            self.pasteAct, self.cancelAct, self.selectAllAct]

    def exec_(self, pos):
        self.clear()
        self.createActions()

        if QApplication.clipboard().mimeData().hasText():
            if self.parent().text():
                if self.parent().selectedText():
                    self.addActions(self.action_list)
                else:
                    self.addActions(self.action_list[2:])
            else:
                self.addAction(self.pasteAct)
        else:
            if self.parent().text():
                if self.parent().selectedText():
                    self.addActions(
                        self.action_list[:2] + self.action_list[3:])
                else:
                    self.addActions(self.action_list[3:])
            else:
                return

        super().exec(pos)


class PlayBarMoreActionsMenu(RoundMenu):
    """ Play bar more actions menu """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.savePlayListAct = QAction(
            MIF.icon(MIF.ADD), self.tr("Save as a playlist"), self)
        self.clearPlayListAct = QAction(
            MIF.icon(MIF.CLEAR), self.tr('Clear now playing'), self)
        self.showPlayListAct = QAction(
            MIF.icon(MIF.PLAYLIST), self.tr("Show now playing list"), self)
        self.fullScreenAct = QAction(
            MIF.icon(MIF.FULL_SCREEN), self.tr("Go full screen"), self)
        self.addActions([self.showPlayListAct, self.fullScreenAct])
        self.addMenu(PlaySpeedMenu(self.tr("Playback speed"), self))
        self.addActions([self.savePlayListAct, self.clearPlayListAct])


class PlayingInterfaceMoreActionsMenu(RoundMenu):
    """ Playing interface more actions menu """

    lyricVisibleChanged = pyqtSignal(bool)

    def __init__(self, parent=None, isLyricVisible=True):
        super().__init__(parent=parent)
        self.isLyricVisible = isLyricVisible

        # play speed submenu
        self.addMenu(PlaySpeedMenu(self.tr("Playback speed"), self))

        self.savePlaylistAct = QAction(
            MIF.icon(MIF.ADD), self.tr("Save as a playlist"), self)
        self.clearPlaylistAct = QAction(
            MIF.icon(MIF.CLEAR), self.tr('Clear now playing'), self)
        self.locateAct = QAction(
            MIF.icon(MIF.LOCATE), self.tr('Locate current song'), self)
        self.reloadLyricAct = QAction(MIF.icon(
            MIF.RELOAD), self.tr("Reload lyric"), self)
        self.revealLyricInFolderAct = QAction(
            MIF.icon(MIF.FOLDER_LINK), self.tr("Reveal in explorer"), self)
        self.loadLyricFromFileAct = QAction(MIF.icon(
            MIF.FILE_LINK), self.tr("Use external lyric file"), self)
        self.embedLyricAct = QAction(MIF.icon(
            MIF.EMBED), self.tr("Embed lyrics to audio file"), self)
        self.movieAct = QAction(
            MIF.icon(MIF.MOVIE), self.tr('Watch MV'), self)
        self.addActions([
            self.savePlaylistAct,
            self.clearPlaylistAct,
            self.locateAct,
            self.movieAct
        ])

        if self.isLyricVisible:
            self.showLyricAct = QAction(
                MIF.icon(MIF.UNVIEW), self.tr('Hide lyric'), self)
        else:
            self.showLyricAct = QAction(
                MIF.icon(MIF.VIEW), self.tr('Show lyric'), self)

        # lyric submenu
        self.lyricMenu = RoundMenu(self.tr("Lyric"), self)
        self.lyricMenu.setIcon(MIF.icon(MIF.LYRIC))
        self.lyricMenu.addActions([
            self.showLyricAct, self.reloadLyricAct,
            self.loadLyricFromFileAct, self.revealLyricInFolderAct,
            self.embedLyricAct
        ])
        self.addMenu(self.lyricMenu)

        self.showLyricAct.triggered.connect(self.__onLyricActionTrigger)

    def __onLyricActionTrigger(self):
        """ lyric action triggered slot """
        if self.isLyricVisible:
            self.showLyricAct.setText(self.tr("Show lyric"))
            self.showLyricAct.setIcon(MIF.icon(MIF.VIEW))
        else:
            self.showLyricAct.setText(self.tr("Hide lyric"))
            self.showLyricAct.setIcon(MIF.icon(MIF.UNVIEW))

        self.lyricVisibleChanged.emit(not self.isLyricVisible)


class PlaySpeedMenu(RoundMenu):
    """ Play speed menu """

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setIcon(MIF.icon(MIF.SPEED))

        self.speedUpAct = QAction(MIF.icon(
            MIF.SPEED_UP), self.tr("Faster"), self)
        self.speedDownAct = QAction(MIF.icon(
            MIF.SPEED_DOWN), self.tr("Slower"), self)
        self.speedResetAct = QAction(MIF.icon(
            MIF.SPEED), self.tr("Normal"), self)
        self.addActions([
            self.speedUpAct, self.speedDownAct, self.speedResetAct])

        self.speedUpAct.triggered.connect(signalBus.playSpeedUpSig)
        self.speedDownAct.triggered.connect(signalBus.playSpeedDownSig)
        self.speedResetAct.triggered.connect(signalBus.playSpeedResetSig)


class AddFromMenu(RoundMenu):
    """ Add from menu """

    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.fromFileAct = QAction(MIF.icon(
            MIF.MUSIC_NOTE), self.tr("From music files"), self)
        self.fromFolderAct = QAction(MIF.icon(
            MIF.MUSIC_FOLDER), self.tr("From music folder"), self)
        self.addActions([self.fromFileAct, self.fromFolderAct])
