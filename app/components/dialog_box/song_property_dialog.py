# coding:utf-8
from common.auto_wrap import autoWrap
from components.buttons.perspective_button import PerspectivePushButton
from PyQt5.QtCore import QFile, Qt
from PyQt5.QtWidgets import QLabel

from .mask_dialog_base import MaskDialogBase


class SongPropertyDialog(MaskDialogBase):
    """ 歌曲属性对话框 """

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(parent)
        self.songInfo = songInfo
        # 实例化小部件
        self.createWidgets(songInfo)
        # 初始化小部件的位置
        self.initWidget()
        # 设置层叠样式
        self.setQss()

    def createWidgets(self, songInfo: dict):
        """ 实例化标签 """
        # 标题
        self.yearLabel = QLabel("年", self.widget)
        self.diskLabel = QLabel("光盘", self.widget)
        self.genreLabel = QLabel("类型", self.widget)
        self.durationLabel = QLabel("时长", self.widget)
        self.propertyLabel = QLabel("属性", self.widget)
        self.singerLabel = QLabel("歌曲歌手", self.widget)
        self.songNameLabel = QLabel("歌曲名", self.widget)
        self.trackNumberLabel = QLabel("曲目", self.widget)
        self.songPathLabel = QLabel("文件位置", self.widget)
        self.albumNameLabel = QLabel("专辑标题", self.widget)
        self.albumSongerLabel = QLabel("专辑歌手", self.widget)
        # 内容
        self.disk = QLabel("1", self.widget)
        self.year = QLabel(songInfo.get("year", '未知年份'), self.widget)
        self.genre = QLabel(songInfo.get("genre", '未知流派'), self.widget)
        self.singer = QLabel(songInfo.get("singer", "未知歌手"), self.widget)
        self.albumName = QLabel(songInfo.get("album", '未知专辑'), self.widget)
        self.duration = QLabel(songInfo.get("duration", "0:00"), self.widget)
        self.songName = QLabel(songInfo.get("songName", "未知歌名"), self.widget)
        self.albumSonger = QLabel(songInfo.get("singer", '未知歌手'), self.widget)
        self.trackNumber = QLabel(songInfo.get(
            "tracknumber", '0'), self.widget)
        self.songPath = QLabel(
            songInfo.get("songPath", '').replace("\\", "/"), self.widget)
        # 实例化关闭按钮
        self.closeButton = PerspectivePushButton("关闭", self.widget)
        # 创建小部件列表
        self.label_list_1 = [
            self.albumName,
            self.songName,
            self.songPath,
            self.singer,
            self.albumSonger,
        ]
        self.label_list_2 = [
            self.trackNumberLabel,
            self.trackNumber,
            self.diskLabel,
            self.disk,
            self.albumNameLabel,
            self.albumName,
            self.albumSongerLabel,
            self.albumSonger,
            self.genreLabel,
            self.genre,
            self.durationLabel,
            self.duration,
            self.yearLabel,
            self.year,
            self.songPathLabel,
            self.songPath,
            self.closeButton,
        ]
        self.label_list_3 = [
            self.disk,
            self.year,
            self.genre,
            self.singer,
            self.albumName,
            self.duration,
            self.songName,
            self.albumSonger,
            self.songPath,
            self.trackNumber,
        ]

    def initWidget(self):
        """ 初始化小部件的属性 """
        self.widget.setFixedSize(942, 590)
        # 初始化抬头的位置
        self.genreLabel.move(28, 330)
        self.diskLabel.move(584, 168)
        self.yearLabel.move(652, 330)
        self.singerLabel.move(584, 90)
        self.propertyLabel.move(28, 27)
        self.songNameLabel.move(28, 90)
        self.songPathLabel.move(28, 408)
        self.albumNameLabel.move(28, 252)
        self.durationLabel.move(584, 330)
        self.trackNumberLabel.move(28, 168)
        self.albumSongerLabel.move(584, 252)
        # 初始化内容的位置
        self.genre.move(28, 362)
        self.year.move(652, 362)
        self.disk.move(584, 202)
        self.singer.move(584, 122)
        self.songName.move(28, 122)
        self.songPath.move(28, 442)
        self.albumName.move(28, 282)
        self.duration.move(584, 362)
        self.trackNumber.move(28, 202)
        self.albumSonger.move(584, 282)
        self.closeButton.move(732, 535)
        # 设置按钮的大小
        self.closeButton.setFixedSize(170, 40)
        # 将关闭信号连接到槽函数
        self.closeButton.clicked.connect(self.close)
        # 设置宽度
        for label in self.label_list_1:
            if label in [self.singer, self.albumSonger]:
                label.setFixedWidth(291)
            elif label in [self.albumName, self.songName]:
                label.setFixedWidth(500)
            elif label == self.songPath:
                label.setFixedWidth(847)
        # 调整高度
        self.adjustHeight()
        # 允许鼠标选中
        for label in self.label_list_3:
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)

    def adjustHeight(self):
        """ 如果有换行的发生就调整高度 """
        newSongName, isSongNameWrap = autoWrap(self.songName.text(), 57)
        newSonger, isSongerWrap = autoWrap(self.singer.text(), 33)
        newAlbumName, isAlbumNameWrap = autoWrap(self.albumName.text(), 57)
        newAlbumSonger, isAlbumSongerWrap = autoWrap(
            self.albumSonger.text(), 33)
        newSongPath, isSongPathWrap = autoWrap(self.songPath.text(), 100)
        if isSongNameWrap or isSongerWrap:
            self.songName.setText(newSongName)
            self.singer.setText(newSonger)
            # 后面的所有标签向下平移25px
            for label in self.label_list_2:
                label.move(label.geometry().x(), label.geometry().y() + 25)
            self.widget.setFixedSize(
                self.widget.width(), self.widget.height() + 25)
        if isAlbumNameWrap or isAlbumSongerWrap:
            self.albumName.setText(newAlbumName)
            self.albumSonger.setText(newAlbumSonger)
            # 后面的所有标签向下平移25px
            for label in self.label_list_2[8:]:
                label.move(label.geometry().x(), label.geometry().y() + 25)
            self.widget.setFixedSize(
                self.widget.width(), self.widget.height() + 25)
        if isSongPathWrap:
            self.songPath.setText(newSongPath)
            self.widget.setFixedSize(
                self.widget.width(), self.widget.height() + 25)

    def setQss(self):
        """ 设置层叠样式表 """
        self.year.setObjectName("singer")
        self.singer.setObjectName("singer")
        self.duration.setObjectName("singer")
        self.songPath.setObjectName("songPath")
        self.albumSonger.setObjectName("singer")
        self.propertyLabel.setObjectName("propertyLabel")

        f = QFile(":/qss/song_property_dialog.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()
