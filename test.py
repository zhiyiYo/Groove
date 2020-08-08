import ctypes
import sys
from ctypes.wintypes import HWND, MSG, POINT

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWinExtras import QtWin
from win32 import win32api, win32gui
from win32.lib import win32con

from effects.window_effect import WindowEffect
from my_main_window.c_structures import MINMAXINFO
from my_main_window.monitor_functions import (adjust_maximized_client_rect,
                                              isMaximized)
from my_title_bar import TitleBar


class Window(QWidget):
    BORDER_WIDTH = 5

    def __init__(self, parent=None):
        super().__init__(parent)

        self.monitor_rect = QApplication.desktop().availableGeometry()
        self.titleBar = TitleBar(self)
        self.windowEffect = WindowEffect()
        self.hWnd = HWND(int(self.winId()))
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(800, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.windowEffect.setWindowAnimation(int(self.winId()))
        self.windowEffect.setAcrylicEffect(self.hWnd)
        if QtWin.isCompositionEnabled():
            QtWin.extendFrameIntoClientArea(self,0,0,0,0)

    def nativeEvent(self, eventType, message):
        msg = MSG.from_address(message.__int__())
        if msg.message == win32con.WM_NCHITTEST:
            xPos = win32api.LOWORD(msg.lParam) - self.frameGeometry().x()
            yPos = win32api.HIWORD(msg.lParam) - self.frameGeometry().y()
            w, h = self.width(), self.height()
            lx = xPos < self.BORDER_WIDTH
            rx = xPos + 9 > w - self.BORDER_WIDTH
            ty = yPos < self.BORDER_WIDTH
            by = yPos > h - self.BORDER_WIDTH
            if (lx and ty):
                return True, win32con.HTTOPLEFT
            elif (rx and by):
                return True, win32con.HTBOTTOMRIGHT
            elif (rx and ty):
                return True, win32con.HTTOPRIGHT
            elif (lx and by):
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
            if isMaximized(msg.hWnd):
                self.windowEffect.adjustMaximizedClientRect(
                    HWND(msg.hWnd), msg.lParam)
            return True, 0
        if msg.message == win32con.WM_GETMINMAXINFO:
            if isMaximized(msg.hWnd):
                window_rect = win32gui.GetWindowRect(msg.hWnd)
                if not window_rect:
                    return False, 0
                # 获取显示器句柄
                monitor = win32api.MonitorFromRect(window_rect)
                if not monitor:
                    return False, 0
                # 获取显示器信息
                monitor_info = win32api.GetMonitorInfo(monitor)
                monitor_rect = monitor_info['Monitor']
                work_area = monitor_info['Work']
                # 将lParam转换为MINMAXINFO指针
                info = cast(
                    msg.lParam, POINTER(MINMAXINFO)).contents
                # 调整位置
                info.ptMaxSize.x = work_area[2] - work_area[0]
                info.ptMaxSize.y = work_area[3] - work_area[1]
                info.ptMaxTrackSize.x = info.ptMaxSize.x
                info.ptMaxTrackSize.y = info.ptMaxSize.y
                # 修改放置点的x,y坐标
                info.ptMaxPosition.x = abs(
                    window_rect[0] - monitor_rect[0])
                info.ptMaxPosition.y = abs(
                    window_rect[1] - monitor_rect[1])
                return True, 1
        return QWidget.nativeEvent(self, eventType, message)

    def resizeEvent(self, e):
        """ 改变标题栏大小 """
        #self.titleBar.resize(self.width(), 40)
        super().resizeEvent(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())
