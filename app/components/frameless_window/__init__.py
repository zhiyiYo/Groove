import sys


if sys.platform == "win32":
    from .win32 import AcrylicWindow, FramelessWindow
elif sys.platform == "darwin":
    from .mac import FramelessWindow
    AcrylicWindow = FramelessWindow
else:
    from .linux import FramelessWindow
    AcrylicWindow = FramelessWindow
