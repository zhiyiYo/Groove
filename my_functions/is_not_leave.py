def isNotLeave(widget) -> bool:
    """ 判断leaveEvent是否发生在小部件所占据的区域 """
    if not widget.isWindow():
        globalPos = widget.parent().mapToGlobal(widget.pos())
    else:
        globalPos = widget.pos()
    globalX = globalPos.x()
    globalY = globalPos.y()
    # 判断事件发生的位置发生在自己所占的rect内
    condX = (globalX <= widget.cursor().pos().x()
             <= globalX + widget.width())
    condY = (globalY <= widget.cursor().pos().y()
             <= globalY + widget.height())
    return (condX and condY)
    
