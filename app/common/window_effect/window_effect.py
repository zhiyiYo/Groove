# coding:utf-8
import sys

from common.os_utils import getWindowsVersion

if sys.platform == "win32":
    from ctypes import POINTER, WinDLL, byref, c_bool, c_int, pointer, sizeof
    from ctypes.wintypes import DWORD, LONG, LPCVOID

    from win32 import win32gui
    from win32.lib import win32con

    from .c_structures import (ACCENT_POLICY, ACCENT_STATE,
                               DWMNCRENDERINGPOLICY, DWMWINDOWATTRIBUTE,
                               MARGINS, WINDOWCOMPOSITIONATTRIB,
                               WINDOWCOMPOSITIONATTRIBDATA)


class WindowEffectBase:
    """ Window effect base class """

    def __init__(self, window=None):
        self.window = window

    def setAcrylicEffect(self, hWnd, gradientColor="F2F2F230", isEnableShadow=True, animationId=0):
        """ set acrylic effect for window

        Parameter
        ----------
        hWnd: int or `sip.voidptr`
            window handle

        gradientColor: str
            hexadecimal acrylic mixed color, corresponding to RGBA components

        isEnableShadow: bool
            whether to enable window shadow

        animationId: int
            turn on blur animation or not
        """
        pass

    def setAeroEffect(self, hWnd):
        """ add the aero effect to the window

        Parameter
        ----------
        hWnd: int or `sip.voidptr`
            Window handle
        """
        pass

    def setTransparentEffect(self, hWnd):
        """ set transparent effect for window """
        pass

    def removeBackgroundEffect(self, hWnd):
        """ Remove background effect """
        pass

    def addShadowEffect(self, hWnd):
        """ add DWM shadow to window

        Parameter
        ----------
        hWnd: int or `sip.voidptr`
            Window handle
        """
        pass

    def addMenuShadowEffect(self, hWnd):
        """ add DWM shadow to menu

        Parameter
        ----------
        hWnd: int or `sip.voidptr`
            Window handle
        """
        pass

    @staticmethod
    def addWindowAnimation(hWnd):
        """ Enables the maximize and minimize animation of the window

        Parameters
        ----------
        hWnd : int or `sip.voidptr`
            Window handle
        """
        pass

    @staticmethod
    def setWindowStayOnTop(hWnd, isStayOnTop: bool):
        """ set whether the window is topped

        Parameters
        ----------
        hWnd : int or `sip.voidptr`
            Window handle
        """
        pass


class WindowsEffect(WindowEffectBase):
    """ Window effect of Windows system """

    def __init__(self, window=None):
        super().__init__(window)
        # call API
        self.user32 = WinDLL("user32")
        self.dwmapi = WinDLL("dwmapi")
        self.SetWindowCompositionAttribute = self.user32.SetWindowCompositionAttribute
        self.DwmExtendFrameIntoClientArea = self.dwmapi.DwmExtendFrameIntoClientArea
        self.DwmSetWindowAttribute = self.dwmapi.DwmSetWindowAttribute
        self.SetWindowCompositionAttribute.restype = c_bool
        self.DwmExtendFrameIntoClientArea.restype = LONG
        self.DwmSetWindowAttribute.restype = LONG
        self.SetWindowCompositionAttribute.argtypes = [
            c_int,
            POINTER(WINDOWCOMPOSITIONATTRIBDATA),
        ]
        self.DwmSetWindowAttribute.argtypes = [c_int, DWORD, LPCVOID, DWORD]
        self.DwmExtendFrameIntoClientArea.argtypes = [c_int, POINTER(MARGINS)]

        # initialize structure
        self.accentPolicy = ACCENT_POLICY()
        self.winCompAttrData = WINDOWCOMPOSITIONATTRIBDATA()
        self.winCompAttrData.Attribute = WINDOWCOMPOSITIONATTRIB.WCA_ACCENT_POLICY.value
        self.winCompAttrData.SizeOfData = sizeof(self.accentPolicy)
        self.winCompAttrData.Data = pointer(self.accentPolicy)

    def setAcrylicEffect(self, hWnd, gradientColor: str = "F2F2F230", isEnableShadow: bool = True, animationId: int = 0):
        if getWindowsVersion() < 10:
            return

        # Acrylic mixed color
        gradientColor = (
            gradientColor[6:]
            + gradientColor[4:6]
            + gradientColor[2:4]
            + gradientColor[:2]
        )
        gradientColor = DWORD(int(gradientColor, base=16))
        # blur animation
        animationId = DWORD(animationId)
        # window shadow
        accentFlags = DWORD(0x20 | 0x40 | 0x80 |
                            0x100) if isEnableShadow else DWORD(0)
        self.accentPolicy.AccentState = ACCENT_STATE.ACCENT_ENABLE_ACRYLICBLURBEHIND.value
        self.accentPolicy.GradientColor = gradientColor
        self.accentPolicy.AccentFlags = accentFlags
        self.accentPolicy.AnimationId = animationId
        # enable acrylic effect
        self.SetWindowCompositionAttribute(
            int(hWnd), pointer(self.winCompAttrData))

    def setAeroEffect(self, hWnd):
        self.accentPolicy.AccentState = ACCENT_STATE.ACCENT_ENABLE_BLURBEHIND.value
        self.SetWindowCompositionAttribute(
            int(hWnd), pointer(self.winCompAttrData))

    def setTransparentEffect(self, hWnd):
        self.accentPolicy.AccentState = ACCENT_STATE.ACCENT_ENABLE_TRANSPARENTGRADIENT.value
        self.SetWindowCompositionAttribute(
            int(hWnd), pointer(self.winCompAttrData))

    def removeBackgroundEffect(self, hWnd):
        self.accentPolicy.AccentState = ACCENT_STATE.ACCENT_DISABLED.value
        self.SetWindowCompositionAttribute(
            int(hWnd), pointer(self.winCompAttrData))

    def addShadowEffect(self, hWnd):
        hWnd = int(hWnd)
        margins = MARGINS(-1, -1, -1, -1)
        self.DwmExtendFrameIntoClientArea(hWnd, byref(margins))

    def addMenuShadowEffect(self, hWnd):
        hWnd = int(hWnd)
        self.DwmSetWindowAttribute(
            hWnd,
            DWMWINDOWATTRIBUTE.DWMWA_NCRENDERING_POLICY.value,
            byref(c_int(DWMNCRENDERINGPOLICY.DWMNCRP_ENABLED.value)),
            4,
        )
        margins = MARGINS(-1, -1, -1, -1)
        self.DwmExtendFrameIntoClientArea(hWnd, byref(margins))

    @staticmethod
    def addWindowAnimation(hWnd):
        style = win32gui.GetWindowLong(hWnd, win32con.GWL_STYLE)
        win32gui.SetWindowLong(
            int(hWnd),
            win32con.GWL_STYLE,
            style
            | win32con.WS_MAXIMIZEBOX
            | win32con.WS_MINIMIZEBOX
            | win32con.WS_CAPTION
            | win32con.CS_DBLCLKS
            | win32con.WS_THICKFRAME,
        )

    @staticmethod
    def setWindowStayOnTop(hWnd, isStayOnTop: bool):
        flag = win32con.HWND_TOPMOST if isStayOnTop else win32con.HWND_NOTOPMOST
        win32gui.SetWindowPos(int(hWnd), flag, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE |
                              win32con.SWP_NOSIZE |
                              win32con.SWP_NOACTIVATE)


class MacWindowEffect(WindowEffectBase):
    """ Window effect of macOS """


class LinuxWindowEffect(WindowEffectBase):
    """ Window effect of Linux system """
