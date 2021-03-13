# coding:utf-8

from ctypes import POINTER, Structure, c_int
from ctypes.wintypes import POINT, UINT, RECT, HWND


class MINMAXINFO(Structure):
    _fields_ = [
        ("ptReserved",      POINT),
        ("ptMaxSize",       POINT),
        ("ptMaxPosition",   POINT),
        ("ptMinTrackSize",  POINT),
        ("ptMaxTrackSize",  POINT),
    ]


class PWINDOWPOS(Structure):
    _fields_ = [
        ('hWnd',            HWND),
        ('hwndInsertAfter', HWND),
        ('x',               c_int),
        ('y',               c_int),
        ('cx',              c_int),
        ('cy',              c_int),
        ('flags',           UINT)
    ]


class NCCALCSIZE_PARAMS(Structure):
    _fields_ = [
        ('rgrc', RECT*3),
        ('lppos', POINTER(PWINDOWPOS))
    ]
