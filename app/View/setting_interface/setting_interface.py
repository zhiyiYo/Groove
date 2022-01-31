# coding:utf-8
import os
import json

from common.os_utils import checkDirExists
from common.thread.get_meta_data_thread import GetFolderMetaDataThread
from components.buttons.switch_button import SwitchButton
from components.dialog_box.folder_list_dialog import FolderListDialog
from components.widgets.label import ClickableLabel
from components.widgets.scroll_area import ScrollArea
from components.widgets.slider import Slider
from components.widgets.state_tooltip import StateTooltip
from PyQt5.QtCore import QEvent, QFile, Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (QFileDialog, QLabel, QLineEdit, QPushButton,
                             QRadioButton, QWidget, QButtonGroup)

from .config import Config


class SettingInterface(ScrollArea):
    """ 设置界面 """

    crawlFinished = pyqtSignal()
    pageSizeChanged = pyqtSignal(int)
    mvQualityChanged = pyqtSignal(str)
    acrylicEnableChanged = pyqtSignal(bool)
    downloadFolderChanged = pyqtSignal(str)
    minimizeToTrayChanged = pyqtSignal(bool)
    onlinePlayQualityChanged = pyqtSignal(str)
    selectedMusicFoldersChanged = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        # 配置
        self.config = Config()

        # 滚动小部件
        self.scrollwidget = QWidget()

        # 设置标签
        self.settingLabel = QLabel(self.tr("Settings"), self)

        # 选择音乐文件夹
        self.musicInThisPCLabel = QLabel(
            self.tr("Music on this PC"), self.scrollwidget)
        self.selectMusicFolderLabel = ClickableLabel(
            self.tr("Choose where we look for music"), self.scrollwidget)

        # 启动亚克力背景
        self.acrylicLabel = QLabel(
            self.tr("Acrylic Background"), self.scrollwidget)
        self.acrylicHintLabel = QLabel(
            self.tr("Use the acrylic background effect"), self.scrollwidget)
        self.acrylicSwitchButton = SwitchButton(
            self.tr("Off"), self.scrollwidget)

        # 媒体信息
        self.mediaInfoLabel = QLabel(self.tr("Media Info"), self.scrollwidget)
        self.getMetaDataLabel = QLabel(self.tr(
            "Automatically retrieve and update missing album art and metadata"), self.scrollwidget)
        self.getMetaDataSwitchButton = SwitchButton(
            self.tr("Off"), self.scrollwidget)

        # 搜索
        self.searchLabel = QLabel(self.tr('Search'), self.scrollwidget)
        self.pageSizeSlider = Slider(Qt.Horizontal, self.scrollwidget)
        self.pageSizeValueLabel = QLabel(self.scrollwidget)
        self.pageSizeHintLabel = QLabel(
            self.tr('Set the number of online music displayed'), self.scrollwidget)

        # 在线音乐音质
        self.onlinePlayQualityGroup = QButtonGroup(self)
        self.onlinePlayQualityLabel = QLabel(
            self.tr('Online Playing Quality'), self.scrollwidget)
        self.standardQualityButton = QRadioButton(
            self.tr('Standard quality'), self.scrollwidget)
        self.highQualityButton = QRadioButton(
            self.tr('High quality'), self.scrollwidget)
        self.superQualityButton = QRadioButton(
            self.tr('Super quality'), self.scrollwidget)

        # MV 画质
        self.mvQualityGroup = QButtonGroup(self)
        self.mvQualityLabel = QLabel(self.tr('MV Quality'), self.scrollwidget)
        self.fullHDButton = QRadioButton(self.tr('Full HD'), self.scrollwidget)
        self.hDButton = QRadioButton(self.tr('HD'), self.scrollwidget)
        self.sDButton = QRadioButton(self.tr('SD'), self.scrollwidget)
        self.lDButton = QRadioButton(self.tr('LD'), self.scrollwidget)

        # 关闭主界面
        self.closeWindowGroup = QButtonGroup(self)
        self.closeWindowLabel = QLabel(
            self.tr('Close Main Window'), self.scrollwidget)
        self.minimizeToTrayButton = QRadioButton(
            self.tr('Minimize to system tray'), self.scrollwidget)
        self.quitGrooveMusicButton = QRadioButton(
            self.tr('Quit Groove Music'), self.scrollwidget)

        # 下载目录
        self.downloadFolderHintLabel = QLabel('')
        self.downloadFolderButton = QPushButton(
            self.tr("Choose"), self.scrollwidget)
        self.downloadFolderLineEdit = QLineEdit(
            self.config['download-folder'], self.scrollwidget)
        self.downloadFolderLabel = QLabel(
            self.tr("Download Directory"), self.scrollwidget)

        # 应用
        self.appLabel = QLabel(self.tr("App"), self.scrollwidget)
        self.helpLabel = ClickableLabel(self.tr("Help"), self.scrollwidget)
        self.issueLabel = ClickableLabel(
            self.tr("Feedback"), self.scrollwidget)

        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1000, 800)
        self.downloadFolderLineEdit.resize(313, 42)
        self.downloadFolderLineEdit.setReadOnly(True)
        self.downloadFolderLineEdit.setCursorPosition(0)
        self.scrollwidget.resize(self.width(), 1360)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 0)
        self.setWidget(self.scrollwidget)

        # 设置亚克力开关按钮的状态
        enableAcrylic = self.config["enable-acrylic-background"]
        self.acrylicSwitchButton.setChecked(enableAcrylic)
        self.acrylicSwitchButton.setText(
            self.tr('On') if enableAcrylic else self.tr('Off'))

        # 设置鼠标光标
        self.selectMusicFolderLabel.setCursor(Qt.PointingHandCursor)
        self.helpLabel.setCursor(Qt.PointingHandCursor)
        self.issueLabel.setCursor(Qt.PointingHandCursor)

        # 设置播放音质
        self.onlinePlayQualityGroup.addButton(self.standardQualityButton)
        self.onlinePlayQualityGroup.addButton(self.highQualityButton)
        self.onlinePlayQualityGroup.addButton(self.superQualityButton)
        self.standardQualityButton.setProperty('quality', 'Standard quality')
        self.highQualityButton.setProperty('quality', 'High quality')
        self.superQualityButton.setProperty('quality', 'Super quality')
        self.__setCheckedOnlineMusicQualityRadioButton()

        # 设置 MV 画质
        self.mvQualityGroup.addButton(self.fullHDButton)
        self.mvQualityGroup.addButton(self.hDButton)
        self.mvQualityGroup.addButton(self.sDButton)
        self.mvQualityGroup.addButton(self.lDButton)
        self.fullHDButton.setProperty('quality', 'Full HD')
        self.hDButton.setProperty('quality', 'HD')
        self.sDButton.setProperty('quality', 'SD')
        self.lDButton.setProperty('quality', 'LD')
        self.__setCheckedMvQualityRadioButton()

        # 设置关闭主面板
        self.closeWindowGroup.addButton(self.minimizeToTrayButton)
        self.closeWindowGroup.addButton(self.quitGrooveMusicButton)
        self.minimizeToTrayButton.setProperty('minimize-to-tray', True)
        self.quitGrooveMusicButton.setProperty('minimize-to-tray', False)
        self.__setCheckedCloseWindowRadioButton()

        # 设置滑动条
        pageSize = self.config['online-music-page-size']
        self.pageSizeSlider.setRange(1, 30)
        self.pageSizeSlider.setValue(pageSize)
        self.pageSizeValueLabel.setNum(pageSize)

        # 根据是否有选中目录来设置爬虫复选框的启用与否
        self.__updateMetaDataSwitchButtonEnabled()

        # 设置超链接
        self.helpLabel.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://github.com/zhiyiYo/Groove#readme')))
        self.issueLabel.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://github.com/zhiyiYo/Groove/issues')))

        # 安装事件过滤器
        self.downloadFolderLineEdit.installEventFilter(self)

        # 初始化布局和样式
        self.__initLayout()
        self.__setQss()

        # 将信号连接到槽函数
        self.__connectSignalToSlot()

    def __initLayout(self):
        """ 初始化布局 """
        self.settingLabel.move(30, 63)
        # 选择歌曲文件夹
        self.musicInThisPCLabel.move(30, 18)
        self.selectMusicFolderLabel.move(30, 64)
        # 亚克力效果
        self.acrylicLabel.move(30, 125)
        self.acrylicHintLabel.move(30, 168)
        self.acrylicSwitchButton.move(30, 200)
        # 媒体信息
        self.mediaInfoLabel.move(30, 262)
        self.getMetaDataLabel.move(30, 312)
        self.getMetaDataSwitchButton.move(30, 344)
        # 搜索
        self.searchLabel.move(30, 406)
        self.pageSizeHintLabel.move(30, 456)
        self.pageSizeSlider.move(30, 486)
        self.pageSizeValueLabel.move(230, 486)
        # 在线音乐音质
        self.onlinePlayQualityLabel.move(30, 548)
        self.standardQualityButton.move(30, 598)
        self.highQualityButton.move(30, 638)
        self.superQualityButton.move(30, 678)
        # MV 画质
        self.mvQualityLabel.move(30, 740)
        self.fullHDButton.move(30, 790)
        self.hDButton.move(30, 830)
        self.sDButton.move(30, 870)
        self.lDButton.move(30, 910)
        # 关闭主界面
        self.closeWindowLabel.move(30, 972)
        self.minimizeToTrayButton.move(30, 1022)
        self.quitGrooveMusicButton.move(30, 1062)
        # 下载目录
        self.downloadFolderLabel.move(30, 1124)
        self.downloadFolderLineEdit.move(30, 1174)
        self.downloadFolderButton.move(350, 1174)
        # 应用
        self.appLabel.move(self.width() - 400, 18)
        self.helpLabel.move(self.width() - 400, 64)
        self.issueLabel.move(self.width() - 400, 94)

    def __updateMetaDataSwitchButtonEnabled(self):
        """ 根据是否有选中目录来设置爬虫复选框的启用与否 """
        if self.config["selected-folders"]:
            self.getMetaDataSwitchButton.setEnabled(True)
        else:
            self.getMetaDataSwitchButton.setEnabled(False)

    def __onCheckBoxStatedChanged(self):
        """ 复选框状态改变对应的槽函数 """
        if self.getMetaDataSwitchButton.isChecked():
            self.getMetaDataSwitchButton.setText(self.tr("On"))
            self.getMetaDataSwitchButton.setEnabled(False)
            # 开始爬取信息
            self.__crawlMetaData()
        else:
            self.getMetaDataSwitchButton.setEnabled(True)
            self.getMetaDataSwitchButton.setText(self.tr("Off"))

    def __crawlMetaData(self):
        """ 爬取歌曲元数据 """
        # 创建爬虫线程
        crawler = GetFolderMetaDataThread(
            self.config["selected-folders"], self)

        # 创建状态提示条
        stateToolTip = StateTooltip(
            self.tr("Crawling metadata"), self.tr("Current progress: ")+f"{0:>3.0%}", self.window())
        stateToolTip.move(stateToolTip.getSuitablePos())
        stateToolTip.show()

        # 信号连接到槽
        crawler.finished.connect(lambda: stateToolTip.setState(True))
        crawler.finished.connect(self.__onCrawlFinished)
        crawler.crawlSignal.connect(stateToolTip.setContent)
        stateToolTip.closedSignal.connect(crawler.stop)

        crawler.start()

    def __onCrawlFinished(self):
        """ 退出爬虫线程 """
        self.sender().quit()
        self.sender().wait()
        self.sender().deleteLater()
        self.getMetaDataSwitchButton.setEnabled(True)
        self.getMetaDataSwitchButton.setChecked(False)
        self.getMetaDataSwitchButton.setText(self.tr("Off"))
        self.crawlFinished.emit()

    def __setQss(self):
        """ 设置层叠样式 """
        self.appLabel.setObjectName("titleLabel")
        self.downloadFolderLabel.setObjectName("titleLabel")
        self.settingLabel.setObjectName("settingLabel")
        self.mediaInfoLabel.setObjectName("titleLabel")
        self.acrylicLabel.setObjectName("titleLabel")
        self.searchLabel.setObjectName('titleLabel')
        self.mvQualityLabel.setObjectName('titleLabel')
        self.onlinePlayQualityLabel.setObjectName('titleLabel')
        self.closeWindowLabel.setObjectName('titleLabel')
        self.helpLabel.setObjectName("clickableLabel")
        self.issueLabel.setObjectName("clickableLabel")
        self.musicInThisPCLabel.setObjectName("titleLabel")
        self.selectMusicFolderLabel.setObjectName("clickableLabel")
        f = QFile(":/qss/setting_interface.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

    def resizeEvent(self, e):
        self.appLabel.move(self.width() - 400, self.appLabel.y())
        self.helpLabel.move(self.width() - 400, self.helpLabel.y())
        self.issueLabel.move(self.width() - 400, self.issueLabel.y())
        self.scrollwidget.resize(self.width(), self.scrollwidget.height())
        super().resizeEvent(e)

    def eventFilter(self, obj, e: QEvent):
        """ 事件过滤器 """
        if obj is self.downloadFolderLineEdit:
            if e.type() == QEvent.ContextMenu:
                return True
        return super().eventFilter(obj, e)

    def __showSongFolderListDialog(self):
        """ 显示歌曲文件夹选择面板 """
        title = self.tr('Build your collection from your local music files')
        content = self.tr("Right now, we're watching these folders:")
        w = FolderListDialog(
            self.config["selected-folders"], title, content, self.window())

        # 用户选择的歌曲文件夹变化
        w.folderChanged.connect(self.__updateSelectedFolders)
        w.exec_()

    def __updateSelectedFolders(self, selectedFolders: list):
        """ 更新选中的歌曲文件夹列表 """
        if self.config["selected-folders"] == selectedFolders:
            return

        self.config["selected-folders"] = selectedFolders
        self.__updateMetaDataSwitchButtonEnabled()
        self.selectedMusicFoldersChanged.emit(selectedFolders)

    def __setCheckedOnlineMusicQualityRadioButton(self):
        """ 设置选中的在线音乐音质单选按钮 """
        quality = self.config['online-play-quality']
        if quality == 'Standard quality':
            self.standardQualityButton.setChecked(True)
        elif quality == 'High quality':
            self.highQualityButton.setChecked(True)
        else:
            self.superQualityButton.setChecked(True)

    def __setCheckedMvQualityRadioButton(self):
        """ 设置选中的 MV 音质单选按钮 """
        quality = self.config['mv-quality']
        if quality == 'Full HD':
            self.fullHDButton.setChecked(True)
        elif quality == 'HD':
            self.hDButton.setChecked(True)
        elif quality == 'SD':
            self.sDButton.setChecked(True)
        else:
            self.lDButton.setChecked(True)

    def __setCheckedCloseWindowRadioButton(self):
        """ 设置选中的关闭主界面单选按钮 """
        minimize = self.config['minimize-to-tray']
        if minimize:
            self.minimizeToTrayButton.setChecked(True)
        else:
            self.quitGrooveMusicButton.setChecked(True)

    def __onPageSliderValueChanged(self, value: int):
        """ 滑动条数值改变槽函数 """
        self.pageSizeValueLabel.setNum(value)
        self.pageSizeValueLabel.adjustSize()
        self.config['online-music-page-size'] = value
        self.pageSizeChanged.emit(value)

    def __onOnlinePlayQualityChanged(self):
        """ 在线播放音质改变槽函数 """
        quality = self.sender().property('quality')
        if self.config['online-play-quality'] == quality:
            return

        self.config['online-play-quality'] = quality
        self.onlinePlayQualityChanged.emit(quality)

    def __onMvQualityChanged(self):
        """ 在线播放音质改变槽函数 """
        quality = self.sender().property('quality')
        if self.config['mv-quality'] == quality:
            return

        self.config['mv-quality'] = quality
        self.mvQualityChanged.emit(quality)

    def __onMinimizeToTrayChanged(self):
        """ 最小化到托盘改变槽函数 """
        minimize = self.sender().property('minimize-to-tray')
        if self.config['minimize-to-tray'] == minimize:
            return

        self.config['minimize-to-tray'] = minimize
        self.minimizeToTrayChanged.emit(minimize)

    def __onDownloadFolderButtonClicked(self):
        """ 下载文件夹按钮点击槽函数 """
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹", "./")
        if folder and self.config['download-folder'] == folder:
            return

        self.config['download-folder'] = folder
        self.downloadFolderLineEdit.setText(folder)
        self.downloadFolderChanged.emit(folder)

    def __onAcrylicCheckedChanged(self, isChecked: bool):
        """ 是否启用亚克力效果开关按钮状态改变槽函数 """
        self.config["enable-acrylic-background"] = isChecked
        self.acrylicEnableChanged.emit(isChecked)

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.hDButton.clicked.connect(self.__onMvQualityChanged)
        self.sDButton.clicked.connect(self.__onMvQualityChanged)
        self.lDButton.clicked.connect(self.__onMvQualityChanged)
        self.fullHDButton.clicked.connect(self.__onMvQualityChanged)
        self.getMetaDataSwitchButton.checkedChanged.connect(
            self.__onCheckBoxStatedChanged)
        self.selectMusicFolderLabel.clicked.connect(
            self.__showSongFolderListDialog)
        self.pageSizeSlider.valueChanged.connect(
            self.__onPageSliderValueChanged)
        self.standardQualityButton.clicked.connect(
            self.__onOnlinePlayQualityChanged)
        self.highQualityButton.clicked.connect(
            self.__onOnlinePlayQualityChanged)
        self.superQualityButton.clicked.connect(
            self.__onOnlinePlayQualityChanged)
        self.downloadFolderButton.clicked.connect(
            self.__onDownloadFolderButtonClicked)
        self.minimizeToTrayButton.clicked.connect(
            self.__onMinimizeToTrayChanged)
        self.quitGrooveMusicButton.clicked.connect(
            self.__onMinimizeToTrayChanged)
        self.acrylicSwitchButton.checkedChanged.connect(
            self.__onAcrylicCheckedChanged)