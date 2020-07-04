from PyQt5.QtGui import QMouseEvent

def getPressedPos(widget, e:QMouseEvent):
    """ 检测鼠标并返回按下的方位 """
    if 0 <= e.x() <= int(widget.width() / 3) and 0 <= e.y() <= int(widget.height() / 3):
        pressedPos = 'left-top'
    elif int(widget.width() / 3) < e.x() <= int(widget.width() * 2 / 3) and 0 <= e.y() <= int(widget.height() / 3):
        pressedPos = 'top'
    elif int(widget.width() * 2 / 3) < e.x() <= widget.width() and 0 <= e.y() <= int(widget.height() / 3):
        pressedPos = 'right-top'
    elif 0 <= e.x() <= int(widget.width() / 3) and int(widget.height() / 3) < e.y() <= int(widget.height() * 2 / 3):
        pressedPos = 'left'
    elif int(widget.width() / 3) < e.x() <= int(widget.width()*2 / 3) and int(widget.height() / 3) < e.y() <= int(widget.height() * 2 / 3):
        pressedPos = 'center'
    elif int(widget.width()*2 / 3) < e.x() <= widget.width() and int(widget.height() / 3) < e.y() <= int(widget.height() * 2 / 3):
        pressedPos = 'right'
    elif 0 <= e.x() <= int(widget.width() / 3) and int(widget.height()*2 / 3) < e.y() <= widget.height():
        pressedPos = 'left-bottom'
    elif int(widget.width() / 3) < e.x() <= int(widget.width()*2 / 3) and int(widget.height()*2 / 3) < e.y() <= widget.height():
        pressedPos = 'bottom'
    elif int(widget.width() * 2 / 3) < e.x() <= widget.width() and int(widget.height() * 2 / 3) < e.y() <= widget.height():
        pressedPos = 'right-bottom'
    return pressedPos
