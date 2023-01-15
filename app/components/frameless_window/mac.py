# coding:utf-8
import Cocoa
import objc
from common.window_effect import WindowEffect
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QWidget

from ..title_bar import TitleBar


class FramelessWindow(QWidget):
    """ Frameless window for Linux system """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.windowEffect = WindowEffect(self)
        self._isResizeEnabled = True

        view = objc.objc_object(c_void_p=self.winId().__int__())
        self.__nsWindow = view.window()

        # hide system title bar
        self.__hideSystemTitleBar()

        self.resize(500, 500)

    def setResizeEnabled(self, isEnabled: bool):
        """ set whether resizing is enabled """
        self._isResizeEnabled = isEnabled

    def paintEvent(self, e):
        super().paintEvent(e)
        self.__nsWindow.setTitlebarAppearsTransparent_(True)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.WindowStateChange:
            self.__hideSystemTitleBar()

    def __hideSystemTitleBar(self):
        # extend view to title bar region
        self.__nsWindow.setStyleMask_(
            self.__nsWindow.styleMask() | Cocoa.NSFullSizeContentViewWindowMask)
        self.__nsWindow.setTitlebarAppearsTransparent_(True)

        # disable the moving behavior of system
        self.__nsWindow.setMovableByWindowBackground_(False)
        self.__nsWindow.setMovable_(False)

        # hide title bar buttons and title
        self.__nsWindow.setShowsToolbarButton_(False)
        self.__nsWindow.setTitleVisibility_(Cocoa.NSWindowTitleHidden)
        self.__nsWindow.standardWindowButton_(
            Cocoa.NSWindowCloseButton).setHidden_(True)
        self.__nsWindow.standardWindowButton_(
            Cocoa.NSWindowZoomButton).setHidden_(True)
        self.__nsWindow.standardWindowButton_(
            Cocoa.NSWindowMiniaturizeButton).setHidden_(True)