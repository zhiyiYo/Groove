# coding:utf-8

from PyQt5.QtCore import Qt,QEvent
from PyQt5.QtWidgets import QApplication, QLabel

from my_song_tab_interface.song_card_sub_unit import SongNameCard


class TrackNumSongNameCard(SongNameCard):
    """ 带曲目序号的歌曲卡 """

    def __init__(self, songName,trackNum, parent=None):
        super().__init__(songName, parent)
        # 创建曲目序号标签
        self.trackNumLabel = QLabel(self)
        self.setTrackNum(trackNum)
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化 """
        self.__adjustTrackNumLabelPos()
        self.trackNumLabel.setFixedWidth(25)
        self.trackNumLabel.setObjectName('songNameLabel')
        self.setCheckBoxBtLabelsState('notSelected-notPlay')
        # 安装事件过滤器
        self.checkBox.installEventFilter(self)

    def setCheckBoxBtLabelsState(self, state: str):
        """ 设置复选框、按钮和标签的状态并更新样式,有notSelected-notPlay、notSelected-play、selected这3种状态 """
        super().setCheckBoxBtLabelState(state)
        self.trackNumLabel.setProperty('state', state)
    
    def setCardInfo(self, songName, trackNum:str):
        """ 设置卡片的信息 """
        super().setSongName(songName)
        self.setTrackNum(trackNum)
        self.__adjustTrackNumLabelPos()

    def setTrackNum(self, trackNum:str):
        """ 设置曲目序号 """
        self.trackNum = trackNum
        # 如果是M4a需要转化一下
        if not trackNum[0].isnumeric():
            self.trackNum = str(eval(trackNum)[0])
        self.trackNumLabel.setText(self.trackNum + '.')
        if self.trackNum == '0':
            self.trackNumLabel.setText('')

    def setWidgetsHidden(self, isHidden: bool):
        """ 显示/隐藏小部件 """
        self.trackNumLabel.setHidden(not isHidden)
        super().setWidgetHidden(isHidden)

    def __adjustTrackNumLabelPos(self):
        """ 调整曲目序号标签位置 """
        if len(self.trackNum) >= 2:
            self.trackNumLabel.move(19, 18)
        else:
            self.trackNumLabel.move(28, 18)

    def setPlay(self, isPlay):
        """ 设置播放状态 """
        super().setPlay(isPlay)
        self.trackNumLabel.setHidden(isPlay)

    def eventFilter(self, obj, e: QEvent):
        """ 过滤事件 """
        if obj == self.checkBox:
            if e.type() == QEvent.Show:
                self.trackNumLabel.hide()
                return False
            elif e.type() == QEvent.Hide:
                self.trackNumLabel.show()
                return False
        return super().eventFilter(obj,e)
        