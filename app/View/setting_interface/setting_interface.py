# coding:utf-8
import os
from json import dump, load

from app.common.os_utils import checkDirExists
from app.common.thread.get_meta_data_thread import GetMetaDataThread
from app.components.buttons.switch_button import SwitchButton
from app.components.dialog_box.folder_list_dialog import FolderListDialog
from app.components.label import ClickableLabel
from app.components.scroll_area import ScrollArea
from app.components.slider import Slider
from app.components.state_tooltip import StateTooltip
from PyQt5.QtCore import QEvent, Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (QFileDialog, QLabel, QLineEdit, QPushButton,
                             QRadioButton, QWidget)


class SettingInterface(ScrollArea):
    """ 设置界面 """

    crawlComplete = pyqtSignal()
    pageSizeChanged = pyqtSignal(int)
    downloadFolderChanged = pyqtSignal(str)
    onlinePlayQualityChanged = pyqtSignal(str)
    selectedMusicFoldersChanged = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        # 读入数据
        self.__readConfig()

        # 创建小部件
        self.scrollwidget = QWidget()
        self.settingLabel = QLabel("设置", self)
        self.appLabel = QLabel("应用", self.scrollwidget)
        self.mediaInfoLabel = QLabel("媒体信息", self.scrollwidget)
        self.helpLabel = ClickableLabel("帮助", self.scrollwidget)
        self.issueLabel = ClickableLabel("反馈", self.scrollwidget)
        self.musicInThisPCLabel = QLabel("此PC上的音乐", self.scrollwidget)
        self.getMetaDataSwitchButton = SwitchButton("关", self.scrollwidget)
        self.getMetaDataLabel = QLabel("自动检索并更新缺失的专辑封面和元数据", self.scrollwidget)
        self.onlinePlayQualityLabel = QLabel('在线播放音质', self.scrollwidget)
        self.normalQualityButton = QRadioButton('流畅', self.scrollwidget)
        self.highQualityButton = QRadioButton('高品', self.scrollwidget)
        self.superQualityButton = QRadioButton('超品', self.scrollwidget)
        self.searchLabel = QLabel('搜索', self.scrollwidget)
        self.pageSizeHintLabel = QLabel('显示的在线音乐数量', self.scrollwidget)
        self.pageSizeSlider = Slider(Qt.Horizontal, self.scrollwidget)
        self.pageSizeValueLabel = QLabel(self.scrollwidget)
        self.selectMusicFolderLabel = ClickableLabel(
            "选择查找音乐的位置", self.scrollwidget)
        self.downloadFolderLabel = QLabel("下载目录", self.scrollwidget)
        self.downloadFolderHintLabel = QLabel('')
        self.downloadFolderButton = QPushButton("浏览", self.scrollwidget)
        self.downloadFolderLineEdit = QLineEdit(self.config.get(
            'download-folder', os.path.abspath('app/download').replace('\\', '/')), self.scrollwidget)
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1000, 800)
        self.downloadFolderLineEdit.resize(313, 42)
        self.downloadFolderLineEdit.setReadOnly(True)
        self.downloadFolderLineEdit.setCursorPosition(0)
        self.scrollwidget.resize(self.width(), 850)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 0)
        self.setWidget(self.scrollwidget)

        # 设置鼠标光标
        self.selectMusicFolderLabel.setCursor(Qt.PointingHandCursor)
        self.helpLabel.setCursor(Qt.PointingHandCursor)
        self.issueLabel.setCursor(Qt.PointingHandCursor)

        # 设置播放音质
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
        # 搜索
        self.searchLabel.move(30, 262)
        self.pageSizeHintLabel.move(30, 312)
        self.pageSizeSlider.move(30, 342)
        self.pageSizeValueLabel.move(230, 342)
        # 在线音乐音质
        self.onlinePlayQualityLabel.move(30, 402)
        self.normalQualityButton.move(30, 452)
        self.highQualityButton.move(30, 492)
        self.superQualityButton.move(30, 532)
        # 下载目录
        self.downloadFolderLabel.move(30, 594)
        self.downloadFolderLineEdit.move(30, 644)
        self.downloadFolderButton.move(350, 644)
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
            self.getMetaDataSwitchButton.setText("开")
            self.getMetaDataSwitchButton.setEnabled(False)
            # 开始爬取信息
            self.__crawlMetaData()
        else:
            self.getMetaDataSwitchButton.setEnabled(True)
            self.getMetaDataSwitchButton.setText("关")

    def __crawlMetaData(self):
        """ 爬取歌曲元数据 """
        # 创建爬虫线程
        crawler = GetMetaDataThread(self.config["selected-folders"], self)

        # 创建状态提示条
        stateToolTip = StateTooltip(
            "正在爬取歌曲元数据", f"当前进度：{0:>3.0%}", self.window())
        stateToolTip.move(self.window().width()-stateToolTip.width() - 30, 63)
        stateToolTip.show()

        # 信号连接到槽
        crawler.finished.connect(lambda: stateToolTip.setState(True))
        crawler.finished.connect(self.__onCrawlFinished)
        crawler.crawlSignal.connect(stateToolTip.setContent)

        crawler.start()

    def __onCrawlFinished(self):
        """ 退出爬虫线程 """
        self.sender().quit()
        self.sender().wait()
        self.sender().deleteLater()
        self.getMetaDataSwitchButton.setEnabled(True)
        self.getMetaDataSwitchButton.setChecked(False)
        self.getMetaDataSwitchButton.setText("关")
        self.crawlComplete.emit()

    def __setQss(self):
        """ 设置层叠样式 """
        self.appLabel.setObjectName("titleLabel")
        self.downloadFolderLabel.setObjectName("titleLabel")
        self.settingLabel.setObjectName("settingLabel")
        self.mediaInfoLabel.setObjectName("titleLabel")
        self.searchLabel.setObjectName('titleLabel')
        self.helpLabel.setObjectName("clickableLabel")
        self.issueLabel.setObjectName("clickableLabel")
        self.onlinePlayQualityLabel.setObjectName('titleLabel')
        self.musicInThisPCLabel.setObjectName("titleLabel")
        self.selectMusicFolderLabel.setObjectName("clickableLabel")
        with open("app/resource/css/setting_interface.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

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
        title = '从本地曲库创建个人"收藏"'
        content = '现在我们正在查看这些文件夹:'
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

    @ checkDirExists('app/config')
    def __readConfig(self):
        """ 读入配置文件数据 """
        try:
            with open("app/config/config.json", encoding="utf-8") as f:
                self.config = load(f)  # type:dict
        except:
            self.config = {"selected-folders": []}

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

    @ checkDirExists('app/config')
    def updateConfig(self, config: dict):
        """ 更新并保存配置数据

        Parameters
        ----------
        config : dict
            配置信息字典
        """
        self.config.update(config)
        with open("app/config/config.json", "w", encoding="utf-8") as f:
            dump(self.config, f)

    def __setCheckedRadioButton(self):
        """ 设置选中的单选按钮 """
        quality = self.config.get('online-play-quality', '流畅音质')
        if quality == '流畅音质':
            self.normalQualityButton.setChecked(True)
        elif quality == '高品音质':
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
        quality = self.sender().text() + '音质'
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

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.getMetaDataSwitchButton.checkedChanged.connect(
            self.onCheckBoxStatedChanged)
        self.selectMusicFolderLabel.clicked.connect(
            self.__showSongFolderListDialog)
        self.pageSizeSlider.valueChanged.connect(
            self.__onPageSliderValueChanged)
        self.normalQualityButton.clicked.connect(
            self.__onOnlinePlayQualityChanged)
        self.highQualityButton.clicked.connect(
            self.__onOnlinePlayQualityChanged)
        self.superQualityButton.clicked.connect(
            self.__onOnlinePlayQualityChanged)
        self.downloadFolderButton.clicked.connect(
            self.__onDownloadFolderButtonClicked)
