class PlayButton(BasicCircleButton):
    """ 播放按钮 """

    def __init__(self, parent=None):
        self.iconPath_list = [
            r'resource\images\playing_play_bar\play_47_47.png',
            r'resource\images\playing_play_bar\pause_47_47.png']
        super().__init__(self.iconPath_list[1], parent)
        # 设置暂停标志位
        self.__isPaused = True
        # 创建pixmap列表
        self.pixmap_list = [QPixmap(iconPath)
                            for iconPath in self.iconPath_list]
        self._pixPos_list = [(0, 0), (2, 2)]

    def mouseReleaseEvent(self, e):
        """ 鼠标松开时更换图标 """
        self.__isPaused = not self.__isPaused
        self.iconPixmap = self.pixmap_list[self.__isPaused]
        self.update()

    def setPlay(self, isPlay: bool):
        """ 设置按钮状态 """
        self.__isPaused = not isPlay
        self.iconPixmap = self.pixmap_list[self.__isPaused]
        self.update()
