# coding:utf-8
import sys
from ctypes import POINTER, cast

from PyQt5.QtCore import QCoreApplication, QEvent, Qt
from PyQt5.QtGui import QCloseEvent, QCursor, QMouseEvent
from PyQt5.QtWidgets import QApplication, QWidget

if sys.platform == "win32":
    from ctypes.wintypes import MSG

    from common.window_effect.c_structures import MINMAXINFO, NCCALCSIZE_PARAMS
    from PyQt5.QtWinExtras import QtWin
    from win32 import win32api, win32gui
    from win32.lib import win32con
else:
    from common.linux_utils import LinuxMoveResize

from common.os_utils import getWindowsVersion
from common.window_effect import WindowEffect

from ..title_bar import TitleBar


class FramelessWindowBase(QWidget):
    """ Frameless window """

    BORDER_WIDTH = 5

    def __init__(self, parent=None):
        super().__init__(parent)
        self.windowEffect = WindowEffect()

    def _isWindowMaximized(self, hWnd):
        """ Determine whether the window is maximized """
        return self.isMaximized()


class WindowsFramelessWindow(FramelessWindowBase):
    """ Frameless window """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__monitorInfo = None

        # remove window border
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

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
            if self._isWindowMaximized(msg.hWnd):
                self.__monitorNCCALCSIZE(msg)
            return True, 0
        elif msg.message == win32con.WM_GETMINMAXINFO:
            if self._isWindowMaximized(msg.hWnd):
                window_rect = win32gui.GetWindowRect(msg.hWnd)
                if not window_rect:
                    return False, 0

                # get the monitor handle
                monitor = win32api.MonitorFromRect(window_rect)
                if not monitor:
                    return False, 0

                # get the monitor information
                __monitorInfo = win32api.GetMonitorInfo(monitor)
                monitor_rect = __monitorInfo['Monitor']
                work_area = __monitorInfo['Work']

                # convert lParam to MINMAXINFO pointer
                info = cast(msg.lParam, POINTER(MINMAXINFO)).contents

                # adjust the size of window
                info.ptMaxSize.x = work_area[2] - work_area[0]
                info.ptMaxSize.y = work_area[3] - work_area[1]
                info.ptMaxTrackSize.x = info.ptMaxSize.x
                info.ptMaxTrackSize.y = info.ptMaxSize.y

                # modify the upper left coordinate
                info.ptMaxPosition.x = abs(window_rect[0] - monitor_rect[0])
                info.ptMaxPosition.y = abs(window_rect[1] - monitor_rect[1])
                return True, 1

        return QWidget.nativeEvent(self, eventType, message)

    def _isWindowMaximized(self, hWnd) -> bool:
        """ Determine whether the window is maximized """
        windowPlacement = win32gui.GetWindowPlacement(hWnd)
        if not windowPlacement:
            return False

        return windowPlacement[1] == win32con.SW_MAXIMIZE

    def __monitorNCCALCSIZE(self, msg):
        """ Adjust the size of window """
        monitor = win32api.MonitorFromWindow(msg.hWnd)

        # If the display information is not saved, return directly
        if monitor is None and not self.__monitorInfo:
            return
        elif monitor is not None:
            self.__monitorInfo = win32api.GetMonitorInfo(monitor)

        # adjust the size of window
        params = cast(msg.lParam, POINTER(NCCALCSIZE_PARAMS)).contents
        params.rgrc[0].left = self.__monitorInfo['Work'][0]
        params.rgrc[0].top = self.__monitorInfo['Work'][1]
        params.rgrc[0].right = self.__monitorInfo['Work'][2]
        params.rgrc[0].bottom = self.__monitorInfo['Work'][3]

    def __onScreenChanged(self):
        hWnd = int(self.windowHandle().winId())
        win32gui.SetWindowPos(hWnd, None, 0, 0, 0, 0, win32con.SWP_NOMOVE |
                              win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED)


class AcrylicWindow(WindowsFramelessWindow):
    """ A frameless window with acrylic effect """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.__closeByKey = False

        QtWin.enableBlurBehindWindow(self)
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.WindowMinMaxButtonsHint)
        self.windowEffect.addWindowAnimation(self.winId())

        version = getWindowsVersion()
        if version == 7:
            self.windowEffect.addShadowEffect(self.winId())
            self.windowEffect.setAeroEffect(self.winId())
        else:
            self.windowEffect.setAcrylicEffect(self.winId())
            if version == 11:
                self.windowEffect.addShadowEffect(self.winId())

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


class UnixFramelessWindow(FramelessWindowBase):
    """ Frameless window for Unix system """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        QCoreApplication.instance().installEventFilter(self)

    def eventFilter(self, obj, event):
        et = event.type()
        if et != QEvent.MouseButtonPress and et != QEvent.MouseMove:
            return False

        edges = Qt.Edges()
        pos = QMouseEvent(event).globalPos() - self.pos()
        if pos.x() < self.BORDER_WIDTH:
            edges |= Qt.LeftEdge
        if pos.x() >= self.width()-self.BORDER_WIDTH:
            edges |= Qt.RightEdge
        if pos.y() < self.BORDER_WIDTH:
            edges |= Qt.TopEdge
        if pos.y() >= self.height()-self.BORDER_WIDTH:
            edges |= Qt.BottomEdge

        # change cursor
        if et == QEvent.MouseMove and self.windowState() == Qt.WindowNoState:
            if edges in (Qt.LeftEdge | Qt.TopEdge, Qt.RightEdge | Qt.BottomEdge):
                self.setCursor(Qt.SizeFDiagCursor)
            elif edges in (Qt.RightEdge | Qt.TopEdge, Qt.LeftEdge | Qt.BottomEdge):
                self.setCursor(Qt.SizeBDiagCursor)
            elif edges in (Qt.TopEdge, Qt.BottomEdge):
                self.setCursor(Qt.SizeVerCursor)
            elif edges in (Qt.LeftEdge, Qt.RightEdge):
                self.setCursor(Qt.SizeHorCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

        elif (obj is self or isinstance(obj, TitleBar)) and et == QEvent.MouseButtonPress and edges:
            LinuxMoveResize.starSystemResize(self, event.globalPos(), edges)

        return super().eventFilter(obj, event)
