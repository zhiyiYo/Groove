# coding:utf-8

from app.my_functions.auto_wrap import autoWrap
from app.my_widget.perspective_button import PerspectivePushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QLabel, QWidget

from .sub_panel_frame import SubPanelFrame


class PropertyPanel(SubPanelFrame):
    """ 父属性面板 """

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(parent)
        # 实例化子属性面板
        self.subPropertyPanel = SubPropertyPanel(songInfo, self)
        # 初始化
        self.initWidget()
        self.initLayout()

    def initWidget(self):
        """ 初始化小部件 """
        # deleteLater才能真正释放内存
        self.subPropertyPanel.closeButton.clicked.connect(self.deleteLater)
        self.showMask()

    def initLayout(self):
        """ 初始化布局 """
        self.subPropertyPanel.move(
            int(self.width() / 2 - self.subPropertyPanel.width() / 2),
            int(self.height() / 2 - self.subPropertyPanel.height() / 2),
        )


class SubPropertyPanel(QWidget):
    """ 子属性面板 """

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(parent)

        self.songInfo = songInfo
        self.pen = QPen(QColor(0, 153, 188))

        # 实例化小部件
        self.createWidgets()
        # 初始化小部件的位置
        self.initWidget()
        self.setShadowEffect()
        # 设置层叠样式
        self.setQss()

    def createWidgets(self):
        """ 实例化标签 """
        # 标题
        self.yearLabel = QLabel("年", self)
        self.diskLabel = QLabel("光盘", self)
        self.tconLabel = QLabel("类型", self)
        self.durationLabel = QLabel("时长", self)
        self.propertyLabel = QLabel("属性", self)
        self.songerLabel = QLabel("歌曲歌手", self)
        self.songNameLabel = QLabel("歌曲名", self)
        self.trackNumberLabel = QLabel("曲目", self)
        self.songPathLabel = QLabel("文件位置", self)
        self.albumNameLabel = QLabel("专辑标题", self)
        self.albumSongerLabel = QLabel("专辑歌手", self)
        # 内容
        self.disk = QLabel("1", self)
        self.year = QLabel(self.songInfo["year"], self)
        self.tcon = QLabel(self.songInfo["tcon"], self)
        self.songer = QLabel(self.songInfo["songer"], self)
        self.albumName = QLabel(self.songInfo["album"], self)
        self.duration = QLabel(self.songInfo["duration"], self)
        self.songName = QLabel(self.songInfo["songName"], self)
        self.albumSonger = QLabel(self.songInfo["songer"], self)
        self.songPath = QLabel(self.songInfo["songPath"], self)
        self.trackNumber = QLabel(self.songInfo["tracknumber"], self)
        # 实例化关闭按钮
        self.closeButton = PerspectivePushButton("关闭", self)
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
        self.resize(942, 590)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground)
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
        if not self.parent():
            self.closeButton.clicked.connect(self.deleteLater)
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
        # 分配ID
        self.year.setObjectName("songer")
        self.songer.setObjectName("songer")
        self.duration.setObjectName("songer")
        self.songPath.setObjectName("songPath")
        self.albumSonger.setObjectName("songer")
        self.propertyLabel.setObjectName("propertyLabel")

    def adjustHeight(self):
        """ 如果有换行的发生就调整高度 """
        newSongName, isSongNameWrap = autoWrap(self.songName.text(), 57)
        newSonger, isSongerWrap = autoWrap(self.songer.text(), 33)
        newAlbumName, isAlbumNameWrap = autoWrap(self.albumName.text(), 57)
        newAlbumSonger, isAlbumSongerWrap = autoWrap(self.albumSonger.text(), 33)
        newSongPath, isSongPathWrap = autoWrap(self.songPath.text(), 100)
        if isSongNameWrap or isSongerWrap:
            self.songName.setText(newSongName)
            self.songer.setText(newSonger)
            # 后面的所有标签向下平移25px
            for label in self.label_list_2:
                label.move(label.geometry().x(), label.geometry().y() + 25)
            self.resize(self.width(), self.height() + 25)
        if isAlbumNameWrap or isAlbumSongerWrap:
            self.albumName.setText(newAlbumName)
            self.albumSonger.setText(newAlbumSonger)
            # 后面的所有标签向下平移25px
            for label in self.label_list_2[8:]:
                label.move(label.geometry().x(), label.geometry().y() + 25)
            self.resize(self.width(), self.height() + 25)
        if isSongPathWrap:
            self.songPath.setText(newSongPath)
            self.resize(self.width(), self.height() + 25)

    def setQss(self):
        """ 设置层叠样式表 """
        with open("app\\resource\\css\\propertyPanel.qss", "r", encoding="utf-8") as f:
            qss = f.read()
            self.setStyleSheet(qss)

    def paintEvent(self, event):
        """ 绘制边框 """
        painter = QPainter(self)
        # 绘制边框
        painter.setPen(self.pen)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

    def setShadowEffect(self):
        """ 添加阴影效果 """
        self.shadowEffect = QGraphicsDropShadowEffect(self)
        self.shadowEffect.setBlurRadius(50)
        self.shadowEffect.setOffset(0, 5)
        self.setGraphicsEffect(self.shadowEffect)
