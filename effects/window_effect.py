# coding:utf-8

from ctypes import c_bool, cdll
from ctypes.wintypes import DWORD, HWND, LPARAM

from win32 import win32gui
from win32.lib import win32con


class WindowEffect():
    """ 调用windowEffect.dll来设置窗口外观 """
    dll = cdll.LoadLibrary('dll\\windowEffect.dll')

    @classmethod
    def setAcrylicEffect(cls, hWnd, gradientColor: str = 'FF000066', isEnableShadow: bool = False, animationId: int = 0):
        """ 给窗口开启Win10的亚克力效果

        Parameters
        ----------
        hWnd : `sip.voidptr`
            由 `QObject.winId()` 返回的窗口句柄

        gradientColor : str
            十六进制亚克力混合色，对应rgba四个分量

        isEnableShadow : bool
            控制是否启用窗口阴影

        animationId : int
            控制磨砂动画
        """
        hWnd = HWND(int(hWnd))
        # 设置阴影
        accentFlags = DWORD(0x20 | 0x40 | 0x80 |
                            0x100) if isEnableShadow else DWORD(0)
        # 设置和亚克力效果相叠加的背景颜色
        gradientColor = gradientColor[6:] + gradientColor[4:6] + \
            gradientColor[2:4] + gradientColor[:2]
        gradientColor = DWORD(int(gradientColor, base=16))
        # 设置窗口动画
        animationId = DWORD(animationId)
        cls.dll.setAcrylicEffect(hWnd, accentFlags, gradientColor,
                                 animationId)

    @classmethod
    def setAeroEffect(cls, hWnd):
        """ 开启Aero效果

        Parameters
        ----------
        hWnd : `sip.voidptr`
            由 `QObject.winId()` 返回的窗口句柄
        """
        cls.dll.setAeroEffect(HWND(int(hWnd)))

    @classmethod
    def setShadowEffect(cls, hWnd,  class_amended: bool = False, newShadow=True):
        """ 去除窗口自带阴影并决定是否添加新阴影

        Parameters
        ----------
        hWnd : `sip.voidptr`
            由 `QObject.winId()` 返回的窗口句柄

        class_amended : bool
            False 时去除原来窗口的阴影

        newShadow : bool
            去除 Qt 原生阴影后是否添加环绕阴影
        """
        class_amended = c_bool(
            cls.dll.setShadowEffect(c_bool(class_amended), HWND(int(hWnd)), c_bool(newShadow)))
        return class_amended

    @classmethod
    def addShadowEffect(cls, hWnd, isShadowEnable: bool = True):
        """ 直接添加新阴影

        Parameters
        ----------
        hWnd : `sip.voidptr`
            由 `QObject.winId()` 返回的窗口句柄

        isShadowEnable : bool
            是否启用阴影
        """
        cls.dll.addShadowEffect(c_bool(isShadowEnable), HWND(int(hWnd)),)

    @classmethod
    def setWindowFrame(cls, hWnd, left: int, top, right, bottom):
        """ 设置客户区的边框大小

        Parameters
        ----------
        hWnd : `sip.voidptr`
            由 `QObject.winId()` 返回的窗口句柄

        left, top, right, bottom : int
            边框宽度
        """
        cls.dll.setWindowFrame(HWND(int(hWnd)), left, top, right, bottom)

    @classmethod
    def setWindowAnimation(cls, hWnd):
        """ 打开窗口动画效果

        Parameters
        ----------
        hWnd : Union[int, `sip.voidptr`]
            由 `QObject.winId()` 返回的窗口句柄或者转成 `int` 的窗口句柄
        """
        style = win32gui.GetWindowLong(hWnd, win32con.GWL_STYLE)
        win32gui.SetWindowLong(
            hWnd, win32con.GWL_STYLE, style | win32con.WS_MAXIMIZEBOX
                                            | win32con.WS_CAPTION
                                            | win32con.CS_DBLCLKS
                                            | win32con.WS_THICKFRAME)

    @classmethod
    def adjustMaximizedClientRect(cls, hWnd: HWND, lParam: int):
        """ 窗口最大化时调整大小

        Parameters
        ----------
        hWnd : HWND
            窗口句柄

        lParam : int
        """
        cls.dll.adjustMaximizedClientRect(hWnd, LPARAM(lParam))

    @classmethod
    def moveWindow(cls, hWnd):
        """ 移动窗口

        Parameters
        ----------
        hWnd : Union[int, `sip.voidptr`]
            由 `QObject.winId()` 返回的窗口句柄或者转成 `int` 的窗口句柄
        """
        cls.dll.moveWindow(HWND(int(hWnd)))

    @classmethod
    def setWindowStayOnTop(cls, hWnd, isStayOnTop: bool):
        """ 设置窗口是否置顶

        Parameters
        ----------
        hWnd : Union[int, `sip.voidptr`]
            由 `QObject.winId()` 返回的窗口句柄或者转成 `int` 的窗口句柄
        """
        flag = win32con.HWND_TOPMOST if isStayOnTop else win32con.HWND_NOTOPMOST
        win32gui.SetWindowPos(hWnd, flag, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE |
                              win32con.SWP_NOSIZE |
                              win32con.SWP_NOACTIVATE)
