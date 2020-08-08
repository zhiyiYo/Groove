from enum import Enum


class WindowMessage(Enum):
    """ Windows窗口消息类型枚举类 """
    WM_GETMINMAXINFO = 0x0024
    WM_NCCALCSIZE = 0x0083
    WM_NCHITTEST = 0x0084
    
