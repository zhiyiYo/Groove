# coding:utf-8

from ctypes import sizeof, byref, cast, POINTER
from ctypes.wintypes import HWND, RECT

from win32.lib import win32con
from win32.win32api import GetMonitorInfo, GetWindowLong, MonitorFromWindow, MonitorFromRect
from win32.win32gui import GetWindowPlacement, ReleaseCapture, GetWindowRect, GetClientRect

from .c_structures import WINDOWPLACEMENT, MONITORINFO


def isMaximized(hWnd: int) -> bool:
    """ 判断窗口是否最大化 """
    # 返回指定窗口的显示状态以及被恢复的、最大化的和最小化的窗口位置，返回值为元组
    windowPlacement = GetWindowPlacement(hWnd)
    if not windowPlacement:
        return False
    return windowPlacement[1] == win32con.SW_MAXIMIZE


def adjust_maximized_client_rect(hWnd: int):
    """ 最大化时调整客户区大小 """
    if not isMaximized(hWnd):
        return
    # 返回显示监视器的句柄
    monitor = MonitorFromWindow(hWnd, win32con.MONITOR_DEFAULTTONULL)
    if not monitor:
        return
    # 获取显示监视器信息，返回值为字典
    monitor_info = GetMonitorInfo(monitor)
    print('monitor info',monitor_info)
    if not monitor_info:
        return
    # 返回显示监视器的工作区域矩形
    rect = monitor_info['Work']
    return rect
