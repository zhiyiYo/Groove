# coding:utf-8
from enum import Enum
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QWidget


class Position(Enum):
    """ Position enumeration """
    LEFT = 0
    RIGHT = 1
    TOP = 2
    BOTTOM = 3
    CENTER = 4
    TOP_LEFT = 5
    TOP_RIGHT = 6
    BOTTOM_LEFT = 7
    BOTTOM_RIGHT = 8


def getPressedPos(widget: QWidget, e: QMouseEvent):
    """ Detect the position of the mouse down

    Parameters
    ----------
    widget: QWidget
        the widget which happens mouse press event

    e: QMouseEvent
        mouse press event

    Returns
    -------
    pressedPos: Position or None
        the position of the mouse click
    """
    pos = None
    w, h = widget.width(), widget.height()
    lx = 0 <= e.x() <= w // 3
    mx = w // 3 < e.x() <= w * 2 // 3
    rx = w * 2 // 3 < e.x() <= w
    ty = 0 <= e.y() <= h // 3
    my = h // 3 < e.y() <= h * 2 // 3
    by = h * 2 // 3 < e.y() <= h

    if lx and ty:
        pos = Position.TOP_LEFT
    elif mx and ty:
        pos = Position.TOP
    elif rx and ty:
        pos = Position.TOP_RIGHT
    elif lx and my:
        pos = Position.LEFT
    elif mx and my:
        pos = Position.CENTER
    elif rx and my:
        pos = Position.RIGHT
    elif lx and by:
        pos = Position.BOTTOM_LEFT
    elif mx and by:
        pos = Position.BOTTOM
    elif rx and by:
        pos = Position.BOTTOM_RIGHT

    return pos
