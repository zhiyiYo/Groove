# coding:utf-8
import sys
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QWidget

if sys.platform == "win32":
    from .win_utils import WindowsMoveResize as MoveResize
elif sys.platform == "darwin":
    from .mac_utils import MacMoveResize as MoveResize
else:
    from .linux_utils import LinuxMoveResize as MoveResize


def startSystemMove(window: QWidget, globalPos: QPoint):
    """ resize window

    Parameters
    ----------
    window: QWidget
        window

    globalPos: QPoint
        the global point of mouse release event
    """
    MoveResize.startSystemMove(window, globalPos)


def starSystemResize(cls, window, globalPos, edges):
    """ resize window

    Parameters
    ----------
    window: QWidget
        window

    globalPos: QPoint
        the global point of mouse release event

    edges: `Qt.Edges`
        window edges
    """
    MoveResize.starSystemResize(window, globalPos, edges)
