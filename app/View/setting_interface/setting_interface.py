# coding:utf-8
import os
from json import dump, load

from common.os_utils import checkDirExists
from common.thread.get_meta_data_thread import GetMetaDataThread
from components.buttons.switch_button import SwitchButton
from components.dialog_box.folder_list_dialog import FolderListDialog
from components.label import ClickableLabel
from components.scroll_area import ScrollArea
from components.slider import Slider
from components.state_tooltip import StateTooltip
from PyQt5.QtCore import QEvent, QFile, Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (QFileDialog, QLabel, QLineEdit, QPushButton,
                             QRadioButton, QWidget)


class SettingInterface(ScrollArea):
    """ 设置界面 """

    crawlComplete = pyqtSignal()
    pageSizeChanged = pyqtSignal(int)
    acrylicEnableChanged = pyqtSignal(bool)
    downloadFolderChanged = pyqtSignal(str)
    onlinePlayQualityChanged = pyqtSignal(str)
    selectedMusicFoldersChanged = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        # 读入数据
        self.__readConfig()

        # 滚动小部件
        self.scrollwidget = QWidget()

        # 设置
        self.settingLabel = QLabel(self.tr("Settings"), self)

        # 选择音乐文件夹
        self.musicInThisPCLabel = QLabel(
            self.tr("Music on this PC"), self.scrollwidget)
        self.selectMusicFolderLabel = ClickableLabel(
            self.tr("Choose where we look for music"), self.scrollwidget)

        # 媒体信息
        self.mediaInfoLabel = QLabel(self.tr("Media Info"), self.scrollwidget)
        self.getMetaDataLabel = QLabel(self.tr(
            "Automatically retrieve and update missing album art and metadata"), self.scrollwidget)
        self.getMetaDataSwitchButton = SwitchButton(
            self.tr("Off"), self.scrollwidget)

        # 启动亚克力背景
        self.acrylicLabel = QLabel(
            self.tr("Acrylic Background"), self.scrollwidget)
        self.acrylicHintLabel = QLabel(
            self.tr("Use the acrylic background effect"), self.scrollwidget)
        self.acrylicSwitchButton = SwitchButton(
            self.tr("Off"), self.scrollwidget)

        # 搜索
        self.searchLabel = QLabel(self.tr('Search'), self.scrollwidget)
        self.pageSizeSlider = Slider(Qt.Horizontal, self.scrollwidget)
        self.pageSizeValueLabel = QLabel(self.scrollwidget)
        self.pageSizeHintLabel = QLabel(
            self.tr('Set the number of online music displayed'), self.scrollwidget)

        # 在线音乐音质
        self.onlinePlayQualityLabel = QLabel(
            self.tr('Online Playing Quality'), self.scrollwidget)
        self.standardQualityButton = QRadioButton(
            self.tr('Standard quality'), self.scrollwidget)
        self.highQualityButton = QRadioButton(
            self.tr('High quality'), self.scrollwidget)
        self.superQualityButton = QRadioButton(
            self.tr('Super quality'), self.scrollwidget)

        # 下载目录
        self.downloadFolderHintLabel = QLabel('')
        self.downloadFolderButton = QPushButton(
            self.tr("Choose"), self.scrollwidget)
        self.downloadFolderLineEdit = QLineEdit(self.config.get(
            'download-folder', os.path.abspath('download').replace('\\', '/')), self.scrollwidget)
        self.downloadFolderLabel = QLabel(
            self.tr("Download directory"), self.scrollwidget)

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
        self.scrollwidget.resize(self.width(), 1000)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 0)
        self.setWidget(self.scrollwidget)

        # 设置鼠标光标
        self.selectMusicFolderLabel.setCursor(Qt.PointingHandCursor)
        self.helpLabel.setCursor(Qt.PointingHandCursor)
        self.issueLabel.setCursor(Qt.PointingHandCursor)

        # 设置亚克力开关按钮的状态
        self.acrylicSwitchButton.setChecked(
            self.config.get("enable-acrylic-background", False))

        # 设置播放音质
        self.standardQualityButton.setProperty('quality', 'Standard quality')
        self.highQualityButton.setProperty('quality', 'High quality')
        self.superQualityButton.setProperty('quality', 'Super quality')
        self.__setCheckedRadioButton()

        # 设置滑动条
        pageSize = self.config.get('online-music-page-size', 10)
        self.pageSizeSlider.setRange(1, 50)
        self.pageSizeSlider.setValue(pageSize)
        self.pageSizeValueLabel.setNum(pageSize)

        # 根据是否有选中目录来设置爬虫复选框的启用与否
        self.__updateSwitchButtonEnabled()

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
        # 媒体信息
        self.mediaInfoLabel.move(30, 125)
        self.getMetaDataLabel.move(30, 168)
        self.getMetaDataSwitchButton.move(30, 200)
        # 亚克力效果
        self.acrylicLabel.move(30, 262)
        self.acrylicHintLabel.move(30, 312)
        self.acrylicSwitchButton.move(30, 344)
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
        # 下载目录
        self.downloadFolderLabel.move(30, 740)
        self.downloadFolderLineEdit.move(30, 790)
        self.downloadFolderButton.move(350, 790)
        # 应用
        self.appLabel.move(self.width() - 400, 18)
        self.helpLabel.move(self.width() - 400, 64)
        self.issueLabel.move(self.width() - 400, 94)

    def __updateSwitchButtonEnabled(self):
        """ 根据是否有选中目录来设置爬虫复选框的启用与否 """
        if self.config.get("selected-folders"):
            self.getMetaDataSwitchButton.setEnabled(True)
        else:
            self.getMetaDataSwitchButton.setEnabled(False)

    def onCheckBoxStatedChanged(self):
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
        crawler = GetMetaDataThread(self.config["selected-folders"], self)

        # 创建状态提示条
        stateToolTip = StateTooltip(
            self.tr("Crawling metadata"), self.tr("Current progress: ")+f"{0:>3.0%}", self.window())
        stateToolTip.move(self.window().width()-stateToolTip.width() - 30, 63)
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
        self.crawlComplete.emit()

    def __setQss(self):
        """ 设置层叠样式 """
        self.appLabel.setObjectName("titleLabel")
        self.downloadFolderLabel.setObjectName("titleLabel")
        self.settingLabel.setObjectName("settingLabel")
        self.mediaInfoLabel.setObjectName("titleLabel")
        self.acrylicLabel.setObjectName("titleLabel")
        self.searchLabel.setObjectName('titleLabel')
        self.helpLabel.setObjectName("clickableLabel")
        self.issueLabel.setObjectName("clickableLabel")
        self.onlinePlayQualityLabel.setObjectName('titleLabel')
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
        # 如果歌曲文件夹选择面板更新了json文件那么自己也得更新
        w.folderChanged.connect(self.__updateSelectedFolders)
        w.exec_()

    def __updateSelectedFolders(self, selectedFolders: list):
        """ 更新选中的歌曲文件夹列表 """
        if self.config["selected-folders"] == selectedFolders:
            return
        self.config["selected-folders"] = selectedFolders
        self.__updateSwitchButtonEnabled()
        # 更新配置文件
        self.updateConfig({"selected-folders": selectedFolders})
        # 发送更新歌曲文件夹列表的信号
        self.selectedMusicFoldersChanged.emit(selectedFolders)

    @ checkDirExists('config')
    def __readConfig(self):
        """ 读入配置文件数据 """
        try:
            with open("config/config.json", encoding="utf-8") as f:
                self.config = load(f)  # type:dict
        except:
            self.config = {
                "selected-folders": [],
                "online-play-quality": "Standard quality",
                "online-music-page-size": 20,
                "enable-acrylic-background": False,
                "volume": 30,
                "playBar-color": [34, 92, 127],
                'download-folder': 'download'
            }

        # 检查文件夹是否存在，不存在则从配置中移除
        for folder in self.config["selected-folders"].copy():
            if not os.path.exists(folder):
                self.config["selected-folders"].remove(folder)

        # 根据是否有选中目录来设置爬虫复选框的启用与否
        if hasattr(self, "getMetaDataSwitchButton"):
            self.__updateSwitchButtonEnabled()

    def getConfig(self, configName: str, default=None):
        """ 获取配置

        Parameters
        ----------
        configName : str
            配置名称

        default : Any
            配置的默认值
        """
        return self.config.get(configName, default)

    @ checkDirExists('config')
    def updateConfig(self, config: dict):
        """ 更新并保存配置数据

        Parameters
        ----------
        config : dict
            配置信息字典
        """
        self.config.update(config)
        with open("config/config.json", "w", encoding="utf-8") as f:
            dump(self.config, f)

    def __setCheckedRadioButton(self):
        """ 设置选中的单选按钮 """
        quality = self.config.get('online-play-quality', 'Standard quality')
        if quality == 'Standard quality':
            self.standardQualityButton.setChecked(True)
        elif quality == 'High quality':
            self.highQualityButton.setChecked(True)
        else:
            self.superQualityButton.setChecked(True)

    def __onPageSliderValueChanged(self, value: int):
        """ 滑动条数值改变槽函数 """
        self.pageSizeValueLabel.setNum(value)
        self.pageSizeValueLabel.adjustSize()
        self.config['online-music-page-size'] = value
        self.pageSizeChanged.emit(value)
        self.updateConfig(self.config)

    def __onOnlinePlayQualityChanged(self):
        """ 在线播放音质改变槽函数 """
        quality = self.sender().property('quality')
        if self.config.get('online-play-quality', '') == quality:
            return
        self.config['online-play-quality'] = quality
        self.onlinePlayQualityChanged.emit(quality)
        self.updateConfig(self.config)

    def __onDownloadFolderButtonClicked(self):
        """ 下载文件夹按钮点击槽函数 """
        path = QFileDialog.getExistingDirectory(self, "选择文件夹", "./")
        if path and self.config.get('download-folder', '') != path:
            self.config['download-folder'] = path
            self.downloadFolderLineEdit.setText(path)
            self.downloadFolderChanged.emit(path)
            self.updateConfig(self.config)

    def __onAcrylicCheckedChanged(self, isChecked: bool):
        """ 是否启用亚克力效果开关按钮状态改变槽函数 """
        self.config["enable-acrylic-background"] = isChecked
        self.acrylicEnableChanged.emit(isChecked)

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.getMetaDataSwitchButton.checkedChanged.connect(
            self.onCheckBoxStatedChanged)
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
        self.acrylicSwitchButton.checkedChanged.connect(
            self.__onAcrylicCheckedChanged)
