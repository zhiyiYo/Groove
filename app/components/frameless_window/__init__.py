import sys

from PyQt5.QtWidgets import QDialog


if sys.platform == "win32":
    from .win32 import AcrylicWindow, FramelessWindow
elif sys.platform == "darwin":
    from .mac import FramelessWindow
    AcrylicWindow = FramelessWindow
else:
    from .linux import FramelessWindow
    AcrylicWindow = FramelessWindow


class FramelessDialog(QDialog, FramelessWindow):
    """ Frameless dialog """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.windowEffect.addShadowEffect(self.winId())
