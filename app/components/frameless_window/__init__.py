import sys

from .frameless_window import (AcrylicWindow, UnixFramelessWindow,
                               WindowsFramelessWindow)

if sys.platform == "win32":
    FramelessWindow = WindowsFramelessWindow
else:
    FramelessWindow = UnixFramelessWindow
    AcrylicWindow = UnixFramelessWindow
