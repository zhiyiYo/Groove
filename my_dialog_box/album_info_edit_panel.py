# coding:utf-8

import os

from mutagen import File, MutagenError
from PyQt5.QtCore import QEvent, QPoint, QRegExp, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import (QBrush, QColor, QMouseEvent, QMovie, QPainter, QPen,
                         QPixmap, QRegExpValidator, QLinearGradient)
from PyQt5.QtWidgets import (
    QApplication, QFileDialog, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect, QLabel, QLineEdit, QScrollArea, QWidget)

from my_functions.adjust_album_name import adjustAlbumName
from my_functions.get_pic_suffix import getPicSuffix
from my_functions.modify_songInfo import modifySongInfo
from my_functions.write_album_cover import writeAlbumCover
from my_widget.my_label import ErrorIcon
from my_widget.my_lineEdit import LineEdit
from my_widget.my_scrollArea import ScrollArea
from my_widget.perspective_button import PerspectivePushButton
from my_widget.perspective_widget import PerspectiveWidget

from .sub_panel_frame import SubPanelFrame


class AlbumInfoEditPanel(SubPanelFrame):
    """ 专辑信息编辑面板 """
    saveInfoSig = pyqtSignal(dict)

    def __init__(self, albumInfo: dict, parent=None):
        super().__init__(parent)
        self.albumInfo = albumInfo
        # 实例化子属性面板
        self.subAlbumInfoEditPanel = SubAlbumInfoEditPanel(albumInfo, self)
        # 初始化
        self.initWidget()
        self.initLayout()
        self.__setQss()

    def initWidget(self):
        """ 初始化小部件 """
        self.showMask()
        self.subAlbumInfoEditPanel.saveInfoSig.connect(self.saveInfoSig)
        self.subAlbumInfoEditPanel.adjustHeightSig.connect(self.initLayout)

    def initLayout(self):
        """ 初始化布局 """
        self.subAlbumInfoEditPanel.move(int(self.width() / 2 - self.subAlbumInfoEditPanel.width() / 2),
                                        int(self.height() / 2 - self.subAlbumInfoEditPanel.height() / 2))

    def __setQss(self):
        """ 设置层叠样式表 """
        with open(r'resource\css\infoEditPanel.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


class SubAlbumInfoEditPanel(QWidget):
    """ 专辑信息编辑面板主界面 """
    saveInfoSig = pyqtSignal(dict)
    adjustHeightSig = pyqtSignal()
    MAXHEIGHT = 755

    def __init__(self, albumInfo: dict, parent):
        super().__init__(parent)
        self.albumInfo = albumInfo
        self.tcon = self.albumInfo['tcon']        # type:str
        self.songer = self.albumInfo['songer']    # type:str
        self.albumName = self.albumInfo['album']  # type:str
        self.cover_path = self.albumInfo['cover_path']  # type:str
        self.songInfo_list = self.albumInfo['songInfo_list']  # type:list
        self.saveErrorHappened = False
        self.newAlbumCoverPath = None
        # 创建小部件
        self.__createWidgets()
        # 初始化
        self.__initWidget()

    def __createWidgets(self):
        """ 创建小部件 """
        self.delayTimer = QTimer(self)
        # 创建滚动区域和抬头
        self.scrollArea = ScrollArea(self)
        self.scrollWidget = QWidget()
        self.editAlbumInfoLabel = QLabel('编辑专辑信息', self)
        # 上半部分
        self.albumCover = AlbumCoverWindow(
            self.cover_path, (170, 170), self.scrollWidget)
        self.albumNameLineEdit = LineEdit(self.albumName, self.scrollWidget)
        self.albumSongerLineEdit = LineEdit(self.songer, self.scrollWidget)
        self.tconLineEdit = LineEdit(self.tcon, self.scrollWidget)
        self.albumNameLabel = QLabel('专辑标题', self.scrollWidget)
        self.albumSongerLabel = QLabel('专辑歌手', self.scrollWidget)
        self.tconLabel = QLabel('类型', self.scrollWidget)
        # 下半部分
        self.songInfoWidget_list = []
        for songInfo in self.songInfo_list:
            songInfoWidget = SongInfoWidget(songInfo, self.scrollWidget)
            songInfoWidget.isTrackNumEmptySig.connect(self.__trackNumEmptySlot)
            self.songInfoWidget_list.append(songInfoWidget)
        self.saveButton = PerspectivePushButton('保存', self)
        self.cancelButton = PerspectivePushButton('取消', self)
        # 创建gif
        # self.loadingLabel = QLabel(self)
        # self.movie = QMovie(
        #    'resource\\images\\loading_gif\\loading.gif', parent=self)

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedWidth(936)
        self.setMaximumHeight(self.MAXHEIGHT)
        self.setAttribute(Qt.WA_StyledBackground)
        # self.loadingLabel.setAttribute(Qt.WA_TranslucentBackground)
        # self.loadingLabel.setMovie(self.movie)
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
        # 初始化布局
        self.__initLayout()
        # 信号连接到槽
        self.__connectSignalToSlot()
        # 分配ID
        self.scrollArea.setObjectName('infoEditScrollArea')
        self.editAlbumInfoLabel.setObjectName('editAlbumInfo')
        # 设置阴影和层叠样式
        self.__setShadowEffect()
        self.__setQss()

    def __initLayout(self):
        """ 初始化布局 """
        self.editAlbumInfoLabel.move(30, 30)
        self.scrollArea.move(2, 62)
        self.albumCover.move(30, 13)
        self.albumNameLabel.move(225, 7)
        self.albumSongerLabel.move(578, 7)
        self.tconLabel.move(225, 77)
        self.albumNameLineEdit.move(225, 36)
        self.albumSongerLineEdit.move(578, 36)
        self.tconLineEdit.move(225, 106)
        for i, songInfoWidget in enumerate(self.songInfoWidget_list):
            songInfoWidget.move(0, songInfoWidget.height() * i + 216)
        self.scrollWidget.resize(931, self.songInfoWidgetNum * 83 + 216)
        self.albumNameLineEdit.resize(327, 40)
        self.albumSongerLineEdit.resize(326, 40)
        self.tconLineEdit.resize(327, 40)
        self.saveButton.resize(168, 40)
        self.cancelButton.resize(168, 40)
        self.resize(936, self.scrollArea.y() + self.scrollArea.height() + 98)
        self.saveButton.move(563, self.height() - 16 -
                             self.saveButton.height())
        self.cancelButton.move(735, self.height() -
                               16 - self.saveButton.height())

    def __setShadowEffect(self):
        """ 添加阴影 """
        self.shadowEffect = QGraphicsDropShadowEffect(self)
        self.shadowEffect.setBlurRadius(50)
        self.shadowEffect.setOffset(0, 5)
        self.setGraphicsEffect(self.shadowEffect)

    def __setQss(self):
        """ 设置层叠样式表 """
        with open(r'resource\css\infoEditPanel.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def paintEvent(self, event):
        """ 绘制背景和阴影 """
        # 创建画笔
        painter = QPainter(self)
        # 绘制边框
        pen = QPen(QColor(0, 153, 188))
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width()-1, self.height()-1)

    def __trackNumEmptySlot(self, isShowErrorMsg: bool):
        """ 如果曲目为空则禁用保存按钮 """
        self.saveButton.setEnabled(not isShowErrorMsg)
        if not self.sender().bottomErrorLabel.isVisible():
            # 获取曲目为空的小部件的index
            senderIndex = self.songInfoWidget_list.index(self.sender())
            # 调整面板高度
            self.__adjustWidgetPos(senderIndex, isShowErrorMsg)

    def __saveErrorSlot(self, songInfoWidget):
        """ 保存歌曲失败 """
        self.saveErrorHappened = True
        if not songInfoWidget.bottomErrorLabel.isVisible():
            senderIndex = self.songInfoWidget_list.index(songInfoWidget)
            self.__adjustWidgetPos(senderIndex, True)

    def __adjustWidgetPos(self, senderIndex, isShowErrorMsg: bool):
        """ 调整小部件位置 """
        # 调整面板高度
        deltaHeight = 54 if isShowErrorMsg else - 54
        if self.height() == self.MAXHEIGHT:
            if deltaHeight < 0:
                height = self.scrollWidget.height() + deltaHeight
                if height < 600:
                    self.resize(936, height + 155)
                    self.adjustHeightSig.emit()
                    self.scrollArea.resize(931, height)
        elif self.MAXHEIGHT - abs(deltaHeight) < self.height() < self.MAXHEIGHT:
            if deltaHeight > 0:
                self.resize(936, self.MAXHEIGHT)
                self.adjustHeightSig.emit()
                self.scrollArea.resize(931, 600)
            else:
                self.__adjustHeight(deltaHeight)
        elif self.height() <= self.MAXHEIGHT - abs(deltaHeight):
            self.__adjustHeight(deltaHeight)
        self.scrollWidget.resize(
            931, self.scrollWidget.height() + deltaHeight)
        self.saveButton.move(563, self.height()-16 -
                             self.saveButton.height())
        self.cancelButton.move(
            735, self.height() - 16 - self.saveButton.height())
        # 调整后面的小部件的位置
        for songInfoWidget in self.songInfoWidget_list[senderIndex + 1:]:
            songInfoWidget.move(0, songInfoWidget.y() + deltaHeight)

    def __adjustHeight(self, deltaHeight):
        """ 调整高度 """
        self.resize(936, self.height() + deltaHeight)
        self.adjustHeightSig.emit()
        self.scrollArea.resize(931, self.scrollArea.height() + deltaHeight)

    def saveAlbumInfo(self):
        """ 保存专辑信息 """
        # 禁用小部件
        # self.__setWidgetEnable(False)
        # 显示动图
        # self.__showLoadingGif()
        # 更新标签信息
        self.albumInfo['album'] = self.albumNameLineEdit.text()
        self.albumInfo['songer'] = self.albumSongerLineEdit.text()
        self.albumInfo['tcon'] = self.tconLineEdit.text()
        for songInfo, songInfoWidget in zip(self.songInfo_list, self.songInfoWidget_list):
            album_list = adjustAlbumName(self.albumNameLineEdit.text())
            songInfo['album'] = album_list[0]
            songInfo['modifiedAlbum'] = album_list[-1]
            songInfo['songName'] = songInfoWidget.songNameLineEdit.text()
            songInfo['songer'] = songInfoWidget.songerLineEdit.text()
            songInfo['tcon'] = self.tconLineEdit.text()
            # 根据后缀名选择曲目标签的写入方式
            songInfo['tracknumber'] = songInfoWidget.trackNumLineEdit.text()
            # 实例化标签卡
            id_card = File(songInfo['songPath'])
            modifySongInfo(id_card, songInfo)
            try:
                id_card.save()
            except MutagenError:
                self.__saveErrorSlot(songInfoWidget)
                songInfoWidget.setSaveSongInfoErrorMsgHidden(False)
                break
        if not self.saveErrorHappened:
            self.saveAlbumCover()
            self.saveInfoSig.emit(self.albumInfo)
            self.parent().deleteLater()
        self.saveErrorHappened = False
        # 保存失败时重新启用编辑框
        # self.__setWidgetEnable(True)
        # self.loadingLabel.hide()
        # self.movie.stop()

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.saveButton.clicked.connect(self.saveAlbumInfo)
        self.cancelButton.clicked.connect(self.parent().deleteLater)
        self.albumCover.clicked.connect(self.delayTimer.start)
        """ self.saveAlbumInfoThread.saveErrorSig.connect(
            lambda index:self.__saveErrorSlot(self.songInfoWidget_list[index])) """

    def __showFileDialog(self):
        """ 显示专辑图片选取对话框 """
        self.delayTimer.stop()
        path, filterType = QFileDialog.getOpenFileName(
            self, '打开', './', '所有文件(*.png;*.jpg;*.jpeg;*jpe;*jiff)')
        if path:
            # 复制图片到封面文件夹下
            if os.path.abspath(self.cover_path) == path:
                return
            # 暂存图片地址并刷新图片
            self.newAlbumCoverPath = path
            self.albumCover.setAlbumCover(path)

    def saveAlbumCover(self):
        """ 保存新专辑封面 """
        if not self.newAlbumCoverPath:
            return
        with open(self.newAlbumCoverPath, 'rb') as f:
            picData = f.read()
            # 给专辑中的所有文件写入同一张封面
            for songInfo in self.songInfo_list:
                writeAlbumCover(songInfo['songPath'], self.newAlbumCoverPath)
            # 更换文件夹下的封面图片
            if self.newAlbumCoverPath == os.path.abspath(self.cover_path):
                return
            # 判断文件格式后修改后缀名
            newSuffix = getPicSuffix(picData)
            # 如果封面路径是默认专辑封面，就修改封面路径
            if self.cover_path == 'resource\\images\\未知专辑封面_200_200.png':
                self.cover_path = 'resource\\Album_Cover\\{0}\\{0}{1}'.format(
                    self.albumInfo['modifiedAlbum'], newSuffix)
            with open(self.cover_path, 'wb') as f:
                f.write(picData)
            oldName, oldSuffix = os.path.splitext(self.cover_path)
            if newSuffix != oldSuffix:
                os.rename(self.cover_path, oldName + newSuffix)
                self.cover_path = oldName + newSuffix
                self.albumInfo['cover_path'] = self.cover_path

    def __setWidgetEnable(self, isEnable: bool):
        """ 设置编辑框是否启用 """
        self.setEnabled(isEnable)
        """ self.albumCover.setEnabled(isEnable)
        self.saveButton.setEnabled(isEnable)
        self.tconLineEdit.setEnabled(isEnable)
        self.albumNameLineEdit.setEnabled(isEnable)
        self.albumSongerLineEdit.setEnabled(isEnable)
        for songInfoWidget in self.songInfoWidget_list:
            songInfoWidget.setLineEditEnable(isEnable) """
        # 更新样式
        self.setStyle(QApplication.style())

    def __showLoadingGif(self):
        """ 显示正在加载动画 """
        self.loadingLabel.resize(77, 77)
        self.loadingLabel.move(int(self.width() / 2 - self.loadingLabel.width() / 2),
                               int(self.height() / 2 - self.loadingLabel.height() / 2))
        self.loadingLabel.raise_()
        self.loadingLabel.show()
        self.movie.start()


class SongInfoWidget(QWidget):
    """ 歌曲信息窗口 """
    isTrackNumEmptySig = pyqtSignal(bool)

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(parent)
        self.songInfo = songInfo
        # 创建小部件
        self.trackNumLabel = QLabel('曲目', self)
        self.songNameLabel = QLabel('歌名', self)
        self.songerLabel = QLabel('歌手', self)
        self.trackNumLineEdit = LineEdit(songInfo['tracknumber'], self, False)
        self.songNameLineEdit = LineEdit(songInfo['songName'], self)
        self.songerLineEdit = LineEdit(songInfo['songer'], self)
        self.errorIcon = ErrorIcon(self)
        self.bottomErrorIcon = ErrorIcon(self)
        self.bottomErrorLabel = QLabel('曲目必须是1000以下的数字', self)
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(903, 83)
        self.__initLayout()
        # 分配ID和属性
        self.bottomErrorLabel.setObjectName('bottomErrorLabel')
        self.trackNumLineEdit.setProperty('hasClearBt', 'false')
        self.trackNumLineEdit.setProperty('hasText', 'false')
        self.__setTrackNumEmptyErrorMsgHidden(True)
        self.__checkTrackNum()
        # 给输入框设置过滤器
        rex_trackNum = QRegExp(r'(\d)|([1-9]\d{1,2})')
        validator_tracknum = QRegExpValidator(
            rex_trackNum, self.trackNumLineEdit)
        self.trackNumLineEdit.setValidator(validator_tracknum)
        # 信号连接到槽
        self.trackNumLineEdit.textChanged.connect(self.__checkTrackNum)

    def __initLayout(self):
        """ 初始化布局 """
        self.trackNumLabel.move(30, 0)
        self.songNameLabel.move(135, 0)
        self.songerLabel.move(532, 0)
        self.trackNumLineEdit.move(30, 26)
        self.songNameLineEdit.move(135, 26)
        self.songerLineEdit.move(532, 26)
        self.errorIcon.move(7, 36)
        self.bottomErrorIcon.move(30, 95)
        self.bottomErrorLabel.move(59, 94)
        self.trackNumLineEdit.resize(80, 41)
        self.songerLineEdit.resize(371, 41)
        self.songNameLineEdit.resize(371, 41)

    def __checkTrackNum(self):
        """ 检查曲目是否为空，为空则发出禁用保存按钮信号，并显示错误标签 """
        if self.trackNumLineEdit.text() and self.trackNumLineEdit.property('hasText') == 'false':
            self.__setTrackNumEmptyErrorMsgHidden(True)
            self.resize(903, 83)
            self.isTrackNumEmptySig.emit(False)
            self.trackNumLineEdit.setProperty('hasText', 'true')
            self.setStyle(QApplication.style())
        elif not self.trackNumLineEdit.text():
            self.isTrackNumEmptySig.emit(True)
            self.resize(903, 137)
            self.__setTrackNumEmptyErrorMsgHidden(False)
            self.trackNumLineEdit.setProperty('hasText', 'false')
            self.setStyle(QApplication.style())

    def __setTrackNumEmptyErrorMsgHidden(self, isHidden: bool):
        """ 设置曲目为空错误信息是否显示 """
        self.errorIcon.setHidden(isHidden)
        self.bottomErrorIcon.setHidden(isHidden)
        self.bottomErrorLabel.setText('曲目必须是1000以下的数字')
        self.bottomErrorLabel.adjustSize()
        self.bottomErrorLabel.setHidden(isHidden)

    def setSaveSongInfoErrorMsgHidden(self, isHidden: bool):
        """ 设置保存歌曲元数据错误信息是否显示 """
        if not isHidden:
            self.resize(903, 137)
        else:
            self.resize(903, 83)
        self.errorIcon.setHidden(isHidden)
        self.bottomErrorIcon.setHidden(isHidden)
        self.bottomErrorLabel.setText('遇到未知错误，请稍后再试')
        self.bottomErrorLabel.adjustSize()
        self.bottomErrorLabel.setHidden(isHidden)

    def setLineEditEnable(self, isEnable: bool):
        """ 设置编辑框是否启用 """
        self.songNameLineEdit.setEnabled(isEnable)
        self.songerLineEdit.setEnabled(isEnable)
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
            QPixmap('resource\\images\\album_interface\\编辑信息.png'))
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
