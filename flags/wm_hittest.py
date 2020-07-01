from enum import Enum

class Flags(Enum):
    """ 包含各宏定义的枚举类 """
    HTCAPTION = 2
    HTLEFT = 10
    HTRIGHT = 11
    HTTOP = 12
    HTTOPLEFT = 13
    HTTOPRIGHT = 14
    HTBOTTOM = 15
    HTBOTTOMLEFT = 16
    HTBOTTOMRIGHT = 17

if __name__ == "__main__":
    print(Flags.HTBOTTOM.value)