import sys
from ctypes import c_bool, cdll
from ctypes.wintypes import HWND

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QToolTip

sys.path.append('..')
from Groove.effects.setEffect import setShadowEffect


class ToolTip(QToolTip):
    """ 自定义气泡 """

    def __init__(self):
        super().__init__()

    def setDropShadow(self):
        """ 设置阴影 """
        dll = cdll.LoadLibrary('acrylic_dll\\acrylic.dll')
        # 添加阴影
        self.class_amended = setShadowEffect(
            dll, self.class_amended, self.hWnd)

