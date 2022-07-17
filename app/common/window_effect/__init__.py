import sys

if sys.platform == "win32":
    from .window_effect import WindowsEffect as WindowEffect
elif sys.platform == "darwin":
    from .window_effect import MacWindowEffect as WindowEffect
else:
    from .window_effect import LinuxWindowEffect as WindowEffect

