# coding:utf-8
import os
from copy import deepcopy

from common.image_process_utils import getPicSuffix
from common.os_utils import adjustName
from components.buttons.perspective_button import PerspectivePushButton
from components.widgets.label import ErrorIcon
from components.widgets.line_edit import LineEdit
from components.widgets.perspective_widget import PerspectiveWidget
from components.widgets.scroll_area import ScrollArea
from PyQt5.QtCore import QFile, QRegExp, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import (QBrush, QColor, QLinearGradient, QPainter, QPixmap,
                         QRegExpValidator)
from PyQt5.QtWidgets import (QApplication, QCompleter, QFileDialog, QLabel,
                             QWidget)

from .mask_dialog_base import MaskDialogBase


class AlbumInfoEditDialog(MaskDialogBase):
    """ 专辑信息编辑对话框 """

    saveInfoSig = pyqtSignal(dict, dict, str)
    MAXHEIGHT = 755

    def __init__(self, albumInfo: dict, parent):
        super().__init__(parent)
        self.oldAlbumInfo = deepcopy(albumInfo)
        self.albumInfo = deepcopy(albumInfo)
        self.genre = self.albumInfo["genre"]  # type:str
        self.singer = self.albumInfo["singer"]  # type:str
        self.albumName = self.albumInfo["album"]  # type:str
        self.coverPath = self.albumInfo["coverPath"]  # type:str
        self.songInfo_list = self.albumInfo["songInfo_list"]  # type:list
        self.newAlbumCoverPath = ''
        # 创建小部件
        self.__createWidgets()
        # 初始化
        self.__initWidget()

    def __createWidgets(self):
        """ 创建小部件 """
        self.delayTimer = QTimer(self)
        # 创建滚动区域和抬头
        self.scrollArea = ScrollArea(self.widget)
        self.scrollWidget = QWidget()
        self.editAlbumInfoLabel = QLabel(
            self.tr("Edit Album Info"), self.widget)

        # 上半部分
        self.albumCover = AlbumCoverWindow(
            self.coverPath, (170, 170), self.scrollWidget)
        self.albumNameLineEdit = LineEdit(self.albumName, self.scrollWidget)
        self.albumSongerLineEdit = LineEdit(self.singer, self.scrollWidget)
        self.genreLineEdit = LineEdit(self.genre, self.scrollWidget)
        self.albumNameLabel = QLabel(self.tr("Album title"), self.scrollWidget)
        self.albumSongerLabel = QLabel(
            self.tr("Album artist"), self.scrollWidget)
        self.genreLabel = QLabel(self.tr("Genre"), self.scrollWidget)

        # 下半部分
        self.songInfoWidget_list = []
        for songInfo in self.songInfo_list:
            songInfoWidget = SongInfoWidget(songInfo, self.scrollWidget)
            songInfoWidget.isTrackNumEmptySig.connect(self.__trackNumEmptySlot)
            self.songInfoWidget_list.append(songInfoWidget)
        self.saveButton = PerspectivePushButton(self.tr("Save"), self.widget)
        self.cancelButton = PerspectivePushButton(
            self.tr("Cancel"), self.widget)

    def __initWidget(self):
        """ 初始化小部件 """
        self.widget.setFixedWidth(936)
        self.widget.setMaximumHeight(self.MAXHEIGHT)
        self.scrollArea.setWidget(self.scrollWidget)
        self.songInfoWidgetNum = len(self.songInfoWidget_list)  # type:int
        # 初始化定时器
        self.delayTimer.setInterval(300)
        self.delayTimer.timeout.connect(self.__showFileDialog)
        # 设置滚动区域的大小
        if self.songInfoWidgetNum <= 4:
            self.scrollArea.resize(931, 216 + self.songInfoWidgetNum * 83)
        else:
            self.scrollArea.resize(931, 595)
        # 设置层叠样式
        self.__setQss()
        # 初始化布局
        self.__initLayout()
        # 信号连接到槽
        self.__connectSignalToSlot()
        # 流派补全
        genres = [
            "Pop",
            "Blues",
            "Soundtrack",
            "Japanese Pop & Rock",
            "Rock",
            "J-Pop",
            "RAP/HIP HOP",
            "Classical",
            "Country",
            "R&B",
            "Anime",
            "Dance",
            "Jazz",
            "New Age",
            "Folk",
            "Easy Listening"
        ]
        self.genreCompleter = QCompleter(genres, self.widget)
        self.genreCompleter.setCompletionMode(QCompleter.InlineCompletion)
        self.genreCompleter.setCaseSensitivity(Qt.CaseInsensitive)
        self.genreLineEdit.setCompleter(self.genreCompleter)

    def __initLayout(self):
        """ 初始化布局 """
        self.editAlbumInfoLabel.move(30, 30)
        self.scrollArea.move(2, 62)
        self.albumCover.move(30, 13)
        self.albumNameLabel.move(225, 7)
        self.albumSongerLabel.move(578, 7)
        self.genreLabel.move(225, 77)
        self.albumNameLineEdit.move(225, 36)
        self.albumSongerLineEdit.move(578, 36)
        self.genreLineEdit.move(225, 106)
        for i, songInfoWidget in enumerate(self.songInfoWidget_list):
            songInfoWidget.move(0, songInfoWidget.height() * i + 216)
        self.scrollWidget.resize(931, self.songInfoWidgetNum * 83 + 216)
        self.albumNameLineEdit.resize(327, 40)
        self.albumSongerLineEdit.resize(326, 40)
        self.genreLineEdit.resize(327, 40)

        self.widget.setFixedSize(
            936, self.scrollArea.y() + self.scrollArea.height() + 98)

        self.cancelButton.move(self.widget.width()-self.cancelButton.width()-30,
                               self.widget.height()-16-self.cancelButton.height())
        self.saveButton.move(self.cancelButton.x() -
                             self.saveButton.width()-5, self.cancelButton.y())

    def __setQss(self):
        """ 设置层叠样式表 """
        self.scrollArea.setObjectName("infoEditScrollArea")
        self.editAlbumInfoLabel.setObjectName("editAlbumInfo")

        f = QFile(":/qss/album_info_edit_dialog.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

        self.saveButton.adjustSize()
        self.cancelButton.adjustSize()

    def __trackNumEmptySlot(self, isShowErrorMsg: bool):
        """ 如果曲目为空则禁用保存按钮 """
        self.saveButton.setEnabled(not isShowErrorMsg)
        if not self.sender().bottomErrorLabel.isVisible():
            # 获取曲目为空的小部件的index
            senderIndex = self.songInfoWidget_list.index(self.sender())
            # 调整面板高度
            self.__adjustWidgetPos(senderIndex, isShowErrorMsg)

    def onSaveError(self, index: int):
        """ 保存信息失败槽函数 """
        songInfoWidget = self.songInfoWidget_list[index]
        if not songInfoWidget.bottomErrorLabel.isVisible():
            senderIndex = self.songInfoWidget_list.index(songInfoWidget)
            self.__adjustWidgetPos(senderIndex, True)
        songInfoWidget.setSaveSongInfoErrorMsgHidden(False)

    def onSaveComplete(self):
        """ 保存成功槽函数 """
        self.__saveAlbumCover()
        self.close()

    def __adjustWidgetPos(self, senderIndex, isShowErrorMsg: bool):
        """ 调整小部件位置 """
        # 调整面板高度
        deltaHeight = 54 if isShowErrorMsg else -54
        if self.widget.height() == self.MAXHEIGHT:
            if deltaHeight < 0:
                height = self.scrollWidget.height() + deltaHeight
                if height < 600:
                    self.widget.setFixedSize(936, height + 155)
                    self.scrollArea.resize(931, height)
        elif self.MAXHEIGHT - abs(deltaHeight) < self.widget.height() < self.MAXHEIGHT:
            if deltaHeight > 0:
                self.widget.setFixedSize(936, self.MAXHEIGHT)
                self.scrollArea.resize(931, 600)
            else:
                self.__adjustHeight(deltaHeight)
        elif self.widget.height() <= self.MAXHEIGHT - abs(deltaHeight):
            self.__adjustHeight(deltaHeight)
        self.scrollWidget.resize(931, self.scrollWidget.height() + deltaHeight)
        self.saveButton.move(563, self.widget.height() -
                             16-self.saveButton.height())
        self.cancelButton.move(735, self.widget.height() -
                               16-self.saveButton.height())
        # 调整后面的小部件的位置
        for songInfoWidget in self.songInfoWidget_list[senderIndex + 1:]:
            songInfoWidget.move(0, songInfoWidget.y() + deltaHeight)

    def __adjustHeight(self, deltaHeight):
        """ 调整高度 """
        self.widget.setFixedSize(936, self.widget.height() + deltaHeight)
        self.scrollArea.resize(931, self.scrollArea.height() + deltaHeight)

    def __saveAlbumInfo(self):
        """ 保存专辑信息 """
        # 禁用小部件
        self.__setWidgetEnable(False)

        # 更新标签信息
        self.albumInfo["album"] = self.albumNameLineEdit.text()
        self.albumInfo["singer"] = self.albumSongerLineEdit.text()
        self.albumInfo["genre"] = self.genreLineEdit.text()
        coverName = adjustName(
            self.albumSongerLineEdit.text()+'_'+self.albumNameLineEdit.text())

        for songInfo, songInfoWidget in zip(self.songInfo_list, self.songInfoWidget_list):
            songInfo["album"] = self.albumNameLineEdit.text()
            songInfo["coverName"] = coverName
            songInfo["songName"] = songInfoWidget.songNameLineEdit.text()
            songInfo["singer"] = songInfoWidget.singerLineEdit.text()
            songInfo["genre"] = self.genreLineEdit.text()
            # 根据后缀名选择曲目标签的写入方式
            songInfo["tracknumber"] = songInfoWidget.trackNumLineEdit.text()

        self.saveInfoSig.emit(
            self.oldAlbumInfo, self.albumInfo, self.newAlbumCoverPath)

        # 保存失败时重新启用编辑框
        self.__setWidgetEnable(True)

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.saveButton.clicked.connect(self.__saveAlbumInfo)
        self.cancelButton.clicked.connect(self.close)
        self.albumCover.clicked.connect(self.delayTimer.start)

    def __showFileDialog(self):
        """ 显示专辑图片选取对话框 """
        self.delayTimer.stop()
        path, _ = QFileDialog.getOpenFileName(
            self, self.tr("Open"), "./", self.tr("All files")+"(*.png;*.jpg;*.jpeg;*jpe;*jiff)")
        if path:
            # 复制图片到封面文件夹下
            if os.path.abspath(self.coverPath) == path:
                return

            # 暂存图片地址并刷新图片
            self.newAlbumCoverPath = path
            self.albumCover.setAlbumCover(path)

    def __saveAlbumCover(self):
        """ 保存新专辑封面 """
        if not self.newAlbumCoverPath:
            return
        with open(self.newAlbumCoverPath, "rb") as f:
            picData = f.read()

            # 更换文件夹下的封面图片
            if self.newAlbumCoverPath == os.path.abspath(self.coverPath):
                return

            # 判断文件格式后修改后缀名
            newSuffix = getPicSuffix(picData)

            # 如果封面路径是默认专辑封面，就修改封面路径
            if self.coverPath == ":/images/default_covers/album_200_200.png":
                self.coverPath = "cache/Album_Cover/{0}/{0}{1}".format(
                    self.albumInfo["coverName"], newSuffix)

            with open(self.coverPath, "wb") as f:
                f.write(picData)

            oldName, oldSuffix = os.path.splitext(self.coverPath)
            if newSuffix != oldSuffix:
                os.rename(self.coverPath, oldName + newSuffix)
                self.coverPath = oldName + newSuffix
                self.albumInfo["coverPath"] = self.coverPath

    def __setWidgetEnable(self, isEnable: bool):
        """ 设置编辑框是否启用 """
        self.setEnabled(isEnable)
        # 更新样式
        self.setStyle(QApplication.style())


class SongInfoWidget(QWidget):
    """ 歌曲信息窗口 """

    isTrackNumEmptySig = pyqtSignal(bool)

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(parent)
        self.songInfo = songInfo
        # 创建小部件
        self.trackNumLabel = QLabel(self.tr("Track"), self)
        self.songNameLabel = QLabel(self.tr("Song title"), self)
        self.singerLabel = QLabel(self.tr("Song artist"), self)
        self.trackNumLineEdit = LineEdit(songInfo["tracknumber"], self, False)
        self.songNameLineEdit = LineEdit(songInfo["songName"], self)
        self.singerLineEdit = LineEdit(songInfo["singer"], self)
        self.errorIcon = ErrorIcon(self)
        self.bottomErrorIcon = ErrorIcon(self)
        self.bottomErrorLabel = QLabel(
            self.tr("The track must be a number below 1000"), self)
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedSize(903, 83)
        self.__initLayout()
        # 分配ID和属性
        self.bottomErrorLabel.setObjectName("bottomErrorLabel")
        self.trackNumLineEdit.setProperty("hasClearBt", "false")
        self.trackNumLineEdit.setProperty("hasText", "false")
        self.__setTrackNumEmptyErrorMsgHidden(True)
        self.__checkTrackNum()
        # 给输入框设置过滤器
        rex_trackNum = QRegExp(r"(\d)|([1-9]\d{1,2})")
        validator_tracknum = QRegExpValidator(
            rex_trackNum, self.trackNumLineEdit)
        self.trackNumLineEdit.setValidator(validator_tracknum)
        # 信号连接到槽
        self.trackNumLineEdit.textChanged.connect(self.__checkTrackNum)

    def __initLayout(self):
        """ 初始化布局 """
        self.trackNumLabel.move(30, 0)
        self.songNameLabel.move(135, 0)
        self.singerLabel.move(532, 0)
        self.trackNumLineEdit.move(30, 26)
        self.songNameLineEdit.move(135, 26)
        self.singerLineEdit.move(532, 26)
        self.errorIcon.move(7, 36)
        self.bottomErrorIcon.move(30, 95)
        self.bottomErrorLabel.move(59, 94)
        self.trackNumLineEdit.resize(80, 41)
        self.singerLineEdit.resize(371, 41)
        self.songNameLineEdit.resize(371, 41)

    def __checkTrackNum(self):
        """ 检查曲目是否为空，为空则发出禁用保存按钮信号，并显示错误标签 """
        if (
            self.trackNumLineEdit.text()
            and self.trackNumLineEdit.property("hasText") == "false"
        ):
            self.__setTrackNumEmptyErrorMsgHidden(True)
            self.setFixedSize(903, 83)
            self.isTrackNumEmptySig.emit(False)
            self.trackNumLineEdit.setProperty("hasText", "true")
            self.setStyle(QApplication.style())
        elif not self.trackNumLineEdit.text():
            self.isTrackNumEmptySig.emit(True)
            self.setFixedSize(903, 137)
            self.__setTrackNumEmptyErrorMsgHidden(False)
            self.trackNumLineEdit.setProperty("hasText", "false")
            self.setStyle(QApplication.style())

    def __setTrackNumEmptyErrorMsgHidden(self, isHidden: bool):
        """ 设置曲目为空错误信息是否显示 """
        self.errorIcon.setHidden(isHidden)
        self.bottomErrorIcon.setHidden(isHidden)
        self.bottomErrorLabel.setText(
            self.tr("The track must be a number below 1000"))
        self.bottomErrorLabel.adjustSize()
        self.bottomErrorLabel.setHidden(isHidden)

    def setSaveSongInfoErrorMsgHidden(self, isHidden: bool):
        """ 设置保存歌曲元数据错误信息是否显示 """
        if not isHidden:
            self.setFixedSize(903, 137)
        else:
            self.setFixedSize(903, 83)
        self.errorIcon.setHidden(isHidden)
        self.bottomErrorIcon.setHidden(isHidden)
        self.bottomErrorLabel.setText(
            self.tr("An unknown error was encountered. Please try again later"))
        self.bottomErrorLabel.adjustSize()
        self.bottomErrorLabel.setHidden(isHidden)

    def setLineEditEnable(self, isEnable: bool):
        """ 设置编辑框是否启用 """
        self.songNameLineEdit.setEnabled(isEnable)
        self.singerLineEdit.setEnabled(isEnable)
        self.trackNumLineEdit.setEnabled(isEnable)


class AlbumCoverWindow(PerspectiveWidget):
    """ 显示专辑封面窗口 """

    clicked = pyqtSignal()

    def __init__(self, picPath: str, picSize: tuple, parent=None):
        super().__init__(parent)
        self.__picPath = picPath
        self.__picSize = picSize
        # 实例化小部件
        self.albumCoverLabel = QLabel(self)
        self.albumCoverMask = AlbumCoverMask(self)
        self.editAlbumCoverLabel = QLabel(self)
        # 初始化小部件
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedSize(*self.__picSize)
        self.albumCoverLabel.setFixedSize(*self.__picSize)
        self.setAlbumCover(self.__picPath)
        # 必须将标签的背景设置为透明
        self.editAlbumCoverLabel.setAttribute(Qt.WA_TranslucentBackground)
        self.editAlbumCoverLabel.setPixmap(
            QPixmap(":/images/album_interface/Edit.png"))
        self.editAlbumCoverLabel.move(14, 137)

    def setAlbumCover(self, picPath: str):
        """ 更换专辑封面 """
        self.__picPath = picPath
        self.albumCoverLabel.setPixmap(QPixmap(picPath).scaled(
            self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def mouseReleaseEvent(self, e):
        """ 鼠标松开发送点击信号 """
        super().mouseReleaseEvent(e)
        self.clicked.emit()


class AlbumCoverMask(QWidget):
    """ 专辑封面渐变遮罩 """

    def __init__(self, parent, size: tuple = (170, 170)):
        super().__init__(parent)
        self.resize(*size)

    def paintEvent(self, e):
        """ 绘制遮罩和图标 """
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        # 绘制遮罩
        gradientColor = QLinearGradient(0, self.height(), self.width(), 0)
        gradientColor.setColorAt(0, QColor(0, 0, 0, 128))
        gradientColor.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(gradientColor))
        painter.drawRect(self.rect())
