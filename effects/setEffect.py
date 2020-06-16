from ctypes import c_bool
from ctypes.wintypes import DWORD


def setAcrylicEffect(dll, hWnd, gradientColor):
    """ 开启亚克力效果 """

    # 设置阴影
    # accentFlags=DWORD(0x20|0x40|0x80|0x100)
    accentFlags = DWORD(0)
    # 设置和亚克力效果相叠加的背景颜色
    gradientColor = DWORD(gradientColor)
    animationId = DWORD(0)
    dll.setBlur(
        hWnd, accentFlags, gradientColor, animationId)


def setShadowEffect(dll,class_amended, hWnd):
    """ 添加阴影 """
    class_amended = c_bool(dll.setShadow(class_amended, hWnd))
    return class_amended


