# coding:utf-8
from ctypes import cast
from ctypes.wintypes import LPRECT, MSG

from common.os_utils import getWindowsVersion
from common.utils import win_utils
from common.utils.win_utils import Taskbar
from common.window_effect import WindowEffect
from common.window_effect.c_structures import LPNCCALCSIZE_PARAMS
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent, QCursor
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWinExtras import QtWin

from win32 import win32gui
from win32.lib import win32con


class FramelessWindow(QWidget):
    """ Frameless window """

    BORDER_WIDTH = 5

    def __init__(self, parent=None):
        super().__init__(parent)
        self.windowEffect = WindowEffect()

        # remove window border
        if getWindowsVersion() > 7:
            self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        else:
            self.setWindowFlags(Qt.WindowMinMaxButtonsHint | Qt.FramelessWindowHint)

        # add DWM shadow and window animation
        self.windowEffect.addWindowAnimation(self.winId())
        # self.windowEffect.addShadowEffect(self.winId())

        # handle multi screen with different dpi
        self.windowHandle().screenChanged.connect(self.__onScreenChanged)

        self.resize(500, 500)

    def nativeEvent(self, eventType, message):
        """ handle the Windows message """
        msg = MSG.from_address(message.__int__())
        if msg.message == win32con.WM_NCHITTEST:
            pos = QCursor.pos()
            xPos = pos.x() - self.x()
            yPos = pos.y() - self.y()
            w, h = self.width(), self.height()
            lx = xPos < self.BORDER_WIDTH
            rx = xPos > w - self.BORDER_WIDTH
            ty = yPos < self.BORDER_WIDTH
            by = yPos > h - self.BORDER_WIDTH
            if lx and ty:
                return True, win32con.HTTOPLEFT
            elif rx and by:
                return True, win32con.HTBOTTOMRIGHT
            elif rx and ty:
                return True, win32con.HTTOPRIGHT
            elif lx and by:
                return True, win32con.HTBOTTOMLEFT
            elif ty:
                return True, win32con.HTTOP
            elif by:
                return True, win32con.HTBOTTOM
            elif lx:
                return True, win32con.HTLEFT
            elif rx:
                return True, win32con.HTRIGHT
        elif msg.message == win32con.WM_NCCALCSIZE:
            if msg.wParam:
                rect = cast(msg.lParam, LPNCCALCSIZE_PARAMS).contents.rgrc[0]
            else:
                rect = cast(msg.lParam, LPRECT).contents

            isMax = win_utils.isMaximized(msg.hWnd)
            isFull = win_utils.isFullScreen(msg.hWnd)

            # adjust the size of client rect
            if isMax and not isFull:
                thickness = win_utils.getResizeBorderThickness(msg.hWnd)
                rect.top += thickness
                rect.left += thickness
                rect.right -= thickness
                rect.bottom -= thickness

            # handle the situation that an auto-hide taskbar is enabled
            if (isMax or isFull) and Taskbar.isAutoHide():
                position = Taskbar.getPosition(msg.hWnd)
                if position == Taskbar.LEFT:
                    rect.top += Taskbar.AUTO_HIDE_THICKNESS
                elif position == Taskbar.BOTTOM:
                    rect.bottom -= Taskbar.AUTO_HIDE_THICKNESS
                elif position == Taskbar.LEFT:
                    rect.left += Taskbar.AUTO_HIDE_THICKNESS
                elif position == Taskbar.RIGHT:
                    rect.right -= Taskbar.AUTO_HIDE_THICKNESS

            result = 0 if not msg.wParam else win32con.WVR_REDRAW
            return True, result

        return QWidget.nativeEvent(self, eventType, message)

    def __onScreenChanged(self):
        hWnd = int(self.windowHandle().winId())
        win32gui.SetWindowPos(hWnd, None, 0, 0, 0, 0, win32con.SWP_NOMOVE |
                              win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED)


class AcrylicWindow(FramelessWindow):
    """ A frameless window with acrylic effect """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.__closeByKey = False

        QtWin.enableBlurBehindWindow(self)

        # remove border and add acrylic effect
        version = getWindowsVersion()
        if version == 7:
            self.setWindowFlags(Qt.WindowMinMaxButtonsHint | Qt.FramelessWindowHint)
            self.windowEffect.addShadowEffect(self.winId())
            self.windowEffect.setAeroEffect(self.winId())
        else:
            self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
            self.windowEffect.setAcrylicEffect(self.winId())
            if version == 11:
                self.windowEffect.addShadowEffect(self.winId())

        self.windowEffect.addWindowAnimation(self.winId())
        self.setStyleSheet("background:transparent")

    def nativeEvent(self, eventType, message):
        """ Handle the Windows message """
        msg = MSG.from_address(message.__int__())
        if msg.message == win32con.WM_SYSKEYDOWN:
            if msg.wParam == win32con.VK_F4:
                self.__closeByKey = True
                QApplication.sendEvent(self, QCloseEvent())
                return False, 0

        return super().nativeEvent(eventType, message)

    def closeEvent(self, e):
        quitOnClose = QApplication.quitOnLastWindowClosed()
        if not self.__closeByKey or quitOnClose:
            self.__closeByKey = False
            return super().closeEvent(e)

        self.__closeByKey = False
        self.hide()
