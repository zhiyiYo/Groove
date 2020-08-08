# coding:utf-8

from ctypes import POINTER, cast, Structure
from ctypes.wintypes import POINT, UINT, DWORD, RECT


class MINMAXINFO(Structure):
    _fields_ = [
        ("ptReserved",      POINT),
        ("ptMaxSize",       POINT),
        ("ptMaxPosition",   POINT),
        ("ptMinTrackSize",  POINT),
        ("ptMaxTrackSize",  POINT),
    ]


class WINDOWPLACEMENT(Structure):
    _fields_ = [
        ("length",           UINT),
        ("flags",            UINT),
        ("showCmd",          UINT),
        ("ptMinPosition",    POINT),
        ("ptMaxPosition",    POINT),
        ("rcNormalPosition", RECT),
        ("rcDevice",         RECT)
    ]


class MONITORINFO(Structure):
    _fields_ = [
        ("cbSize",    DWORD),
        ("rcMonitor", RECT),
        ("rcWork",    RECT),
        ("dwFlags",   DWORD),
    ]

