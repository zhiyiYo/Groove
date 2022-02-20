# coding:utf-8
from PyQt5.QtGui import QMouseEvent


def getPressedPos(widget, e: QMouseEvent):
    """ Detect the position of the mouse down

    Parameters
    ----------
    widget:
        the widget which happens mouse press event

    e: QMouseEvent
        mouse press event

    Returns
    -------
    pressedPos: str or None
        the position of the mouse down
    """
    pressedPos = None
    width = widget.width()
    height = widget.height()
    leftX = 0 <= e.x() <= int(width / 3)
    midX = int(width / 3) < e.x() <= int(width * 2 / 3)
    rightX = int(width * 2 / 3) < e.x() <= width
    topY = 0 <= e.y() <= int(height / 3)
    midY = int(height / 3) < e.y() <= int(height * 2 / 3)
    bottomY = int(height * 2 / 3) < e.y() <= height

    if leftX and topY:
        pressedPos = 'left-top'
    elif midX and topY:
        pressedPos = 'top'
    elif rightX and topY:
        pressedPos = 'right-top'
    elif leftX and midY:
        pressedPos = 'left'
    elif midX and midY:
        pressedPos = 'center'
    elif rightX and midY:
        pressedPos = 'right'
    elif leftX and bottomY:
        pressedPos = 'left-bottom'
    elif midX and bottomY:
        pressedPos = 'bottom'
    elif rightX and bottomY:
        pressedPos = 'right-bottom'

    return pressedPos
