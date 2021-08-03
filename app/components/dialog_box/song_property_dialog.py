# coding:utf-8
from .mask_dialog_base import MaskDialogBase
from app.common.auto_wrap import autoWrap
from app.components.buttons.perspective_button import PerspectivePushButton
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel


class SongPropertyDialog(MaskDialogBase):
    """ 歌曲属性对话框 """

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(parent)
        self.songInfo = songInfo
        # 实例化小部件
        self.createWidgets()
        # 初始化小部件的位置
        self.initWidget()
        # 设置层叠样式
        self.setQss()

    def createWidgets(self):
        """ 实例化标签 """
        # 标题
        self.yearLabel = QLabel("年", self.widget)
        self.diskLabel = QLabel("光盘", self.widget)
        self.tconLabel = QLabel("类型", self.widget)
        self.durationLabel = QLabel("时长", self.widget)
        self.propertyLabel = QLabel("属性", self.widget)
        self.songerLabel = QLabel("歌曲歌手", self.widget)
        self.songNameLabel = QLabel("歌曲名", self.widget)
        self.trackNumberLabel = QLabel("曲目", self.widget)
        self.songPathLabel = QLabel("文件位置", self.widget)
        self.albumNameLabel = QLabel("专辑标题", self.widget)
        self.albumSongerLabel = QLabel("专辑歌手", self.widget)
        # 内容
        self.disk = QLabel("1", self.widget)
        self.year = QLabel(self.songInfo["year"], self.widget)
        self.tcon = QLabel(self.songInfo["tcon"], self.widget)
        self.songer = QLabel(self.songInfo["songer"], self.widget)
        self.albumName = QLabel(self.songInfo["album"], self.widget)
        self.duration = QLabel(self.songInfo["duration"], self.widget)
        self.songName = QLabel(self.songInfo["songName"], self.widget)
        self.albumSonger = QLabel(self.songInfo["songer"], self.widget)
        self.songPath = QLabel(self.songInfo["songPath"], self.widget)
        self.trackNumber = QLabel(self.songInfo["tracknumber"], self.widget)
        # 实例化关闭按钮
        self.closeButton = PerspectivePushButton("关闭", self.widget)
        # 创建小部件列表
        self.label_list_1 = [
            self.albumName,
            self.songName,
            self.songPath,
            self.songer,
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
            self.tconLabel,
            self.tcon,
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
            self.tcon,
            self.songer,
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
        self.tconLabel.move(28, 330)
        self.diskLabel.move(584, 168)
        self.yearLabel.move(652, 330)
        self.songerLabel.move(584, 90)
        self.propertyLabel.move(28, 27)
        self.songNameLabel.move(28, 90)
        self.songPathLabel.move(28, 408)
        self.albumNameLabel.move(28, 252)
        self.durationLabel.move(584, 330)
        self.trackNumberLabel.move(28, 168)
        self.albumSongerLabel.move(584, 252)
        # 初始化内容的位置
        self.tcon.move(28, 362)
        self.year.move(652, 362)
        self.disk.move(584, 202)
        self.songer.move(584, 122)
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
            if label in [self.songer, self.albumSonger]:
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
        newSonger, isSongerWrap = autoWrap(self.songer.text(), 33)
        newAlbumName, isAlbumNameWrap = autoWrap(self.albumName.text(), 57)
        newAlbumSonger, isAlbumSongerWrap = autoWrap(
            self.albumSonger.text(), 33)
        newSongPath, isSongPathWrap = autoWrap(self.songPath.text(), 100)
        if isSongNameWrap or isSongerWrap:
            self.songName.setText(newSongName)
            self.songer.setText(newSonger)
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
        self.year.setObjectName("songer")
        self.songer.setObjectName("songer")
        self.duration.setObjectName("songer")
        self.songPath.setObjectName("songPath")
        self.albumSonger.setObjectName("songer")
        self.propertyLabel.setObjectName("propertyLabel")
        with open("app/resource/css/song_property_dialog.qss",  encoding="utf-8") as f:
            self.setStyleSheet(f.read())
