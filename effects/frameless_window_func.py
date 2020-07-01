from ctypes import cdll
from ctypes.wintypes import DWORD, HWND


class FramelessWindowFunc:
    """ 包含无边框窗口各种操作函数的类 """
    dll = cdll.LoadLibrary('dll\\framelessWindowFunc.dll')

    def moveWindow(self, hWnd: HWND):
        """ 移动窗口 """
        self.dll.moveWindow(hWnd)
