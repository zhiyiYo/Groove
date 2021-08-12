# coding:utf-8
import os
from json import dump, load

from app.components.buttons.switch_button import SwitchButton
from app.components.dialog_box.folder_list_dialog import FolderListDialog
from app.components.label import ClickableLabel
from app.components.state_tooltip import StateTooltip
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QRadioButton, QScrollArea,
                             QWidget)

from .get_meta_data_thread import GetMetaDataThread


class SettingInterface(QWidget):
    """ 设置界面 """

    crawlComplete = pyqtSignal()
    selectedFoldersChanged = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        # 读入数据
        self.__readConfig()
        # 创建小部件
        self.__createWidgets()
        # 初始化界面
        self.__initWidget()

    def __createWidgets(self):
        """ 创建小部件 """
        # 实例化滚动区域
        self.all_h_layout = QHBoxLayout(self)
        self.scrollArea = QScrollArea(self)
        self.widget = QWidget()
        # 实例化标签
        self.appLabel = QLabel("应用", self.widget)
        self.playLabel = QLabel("播放", self.widget)
        self.settingLabel = QLabel("设置", self.widget)
        self.colorModeLabel = QLabel("模式", self.widget)
        self.mediaInfoLabel = QLabel("媒体信息", self.widget)
        self.loginLabel = ClickableLabel("登录", self.widget)
        self.darkColorButton = QRadioButton("深色", self.widget)
        self.lightColorButton = QRadioButton("浅色", self.widget)
        self.equalizerLabel = ClickableLabel("均衡器", self.widget)
        self.musicInThisPCLabel = QLabel("此PC上的音乐", self.widget)
        self.getMetaDataSwitchButton = SwitchButton("关", self.widget)
        self.selectFolderLabel = ClickableLabel("选择查找音乐的位置", self.widget)
        self.getMetaDataLabel = QLabel("自动检索并更新缺失的专辑封面和元数据", self.widget)

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1000, 800)
        self.widget.resize(self.width(), 800)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 将信号连接到槽函数
        self.getMetaDataSwitchButton.checkedChanged.connect(
            self.checkBoxStatedChangedSlot)
        self.selectFolderLabel.clicked.connect(
            self.__showSongFolderListDialog)
        self.lightColorButton.clicked.connect(self.__colorModeChangeSlot)
        self.darkColorButton.clicked.connect(self.__colorModeChangeSlot)
        # 设置鼠标光标
        self.selectFolderLabel.setCursor(Qt.PointingHandCursor)
        self.equalizerLabel.setCursor(Qt.PointingHandCursor)
        self.loginLabel.setCursor(Qt.PointingHandCursor)
        # 根据是否有选中目录来设置爬虫复选框的启用与否
        self.__updateSwitchButtonEnabled()
        # 设置选中的主题颜色
        if self.config.get("color-mode", "light-color") == "light-color":
            self.lightColorButton.setChecked(True)
        else:
            self.darkColorButton.setChecked(True)
        # 初始化布局和样式
        self.__initLayout()
        self.__setQss()

    def __initLayout(self):
        """ 初始化布局 """
        self.playLabel.move(30, 247)
        self.colorModeLabel.move(30, 483)
        self.settingLabel.move(30, 63)
        self.equalizerLabel.move(30, 292)
        self.mediaInfoLabel.move(30, 350)
        self.darkColorButton.move(30, 572)
        self.getMetaDataLabel.move(30, 392)
        self.lightColorButton.move(30, 533)
        self.selectFolderLabel.move(30, 188)
        self.musicInThisPCLabel.move(30, 140)
        self.getMetaDataSwitchButton.move(30, 423)
        self.appLabel.move(self.width() - 400, 140)
        self.loginLabel.move(self.width() - 400, 188)
        self.scrollArea.setWidget(self.widget)
        self.all_h_layout.addWidget(self.scrollArea)
        self.all_h_layout.setContentsMargins(0, 0, 0, 0)

    def __updateSwitchButtonEnabled(self):
        """ 根据是否有选中目录来设置爬虫复选框的启用与否 """
        if self.config.get("selected-folders"):
            self.getMetaDataSwitchButton.setEnabled(True)
        else:
            self.getMetaDataSwitchButton.setEnabled(False)

    def checkBoxStatedChangedSlot(self):
        """ 复选框状态改变对应的槽函数 """
        if self.getMetaDataSwitchButton.isChecked():
            self.getMetaDataSwitchButton.setText("开")
            self.getMetaDataSwitchButton.setEnabled(False)
            # 创建一个爬虫线程
            self.__createCrawlThread()
        else:
            self.getMetaDataSwitchButton.setEnabled(True)
            self.getMetaDataSwitchButton.setText("关")

    def __createCrawlThread(self):
        """ 创建一个爬虫线程 """
        self.getMetaDataThread = GetMetaDataThread(
            self.config["selected-folders"])
        self.stateToolTip = StateTooltip(
            "正在爬取专辑信息", "正在启动浏览器...", self.window())
        # 信号连接到槽
        self.getMetaDataThread.crawlSignal.connect(self.__updateStateToolTip)
        # 启用线程
        self.stateToolTip.move(self.window().width() -
                               self.stateToolTip.width() - 30, 63)
        self.stateToolTip.show()
        self.getMetaDataThread.start()

    def __updateStateToolTip(self, crawlState: str):
        """ 根据爬取进度更新进度提示框 """
        if crawlState == "酷狗爬取完成":
            self.stateToolTip.setTitle("正在爬取流派信息")
        elif crawlState == "全部完成":
            self.stateToolTip.setState(True)
            # 摧毁线程
            self.__stopCrawlThread()
        else:
            self.stateToolTip.setContent(crawlState)

    def __stopCrawlThread(self):
        """ 退出爬虫线程 """
        self.getMetaDataThread.stop()
        self.getMetaDataThread.quit()
        self.getMetaDataThread.wait()
        self.getMetaDataThread.deleteLater()
        self.getMetaDataSwitchButton.setEnabled(True)
        self.__updateSongInfo()

    def __updateSongInfo(self):
        """ 更新歌曲信息 """
        self.getMetaDataSwitchButton.setChecked(False)
        # 发送爬取完成的信号
        self.crawlComplete.emit()

    def __colorModeChangeSlot(self):
        """ 主题颜色改变时更新Json文件 """
        if self.sender() == self.lightColorButton:
            self.config["color-mode"] = "light-color"
        else:
            self.config["color-mode"] = "dark-color"
        # self.updateConfig(self.config)

    def __setQss(self):
        """ 设置层叠样式 """
        self.appLabel.setObjectName("titleLabel")
        self.playLabel.setObjectName("titleLabel")
        self.colorModeLabel.setObjectName("titleLabel")
        self.settingLabel.setObjectName("settingLabel")
        self.mediaInfoLabel.setObjectName("titleLabel")
        self.loginLabel.setObjectName("clickableLabel")
        self.musicInThisPCLabel.setObjectName("titleLabel")
        self.equalizerLabel.setObjectName("clickableLabel")
        self.selectFolderLabel.setObjectName("clickableLabel")
        with open("app/resource/css/setting_interface.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def resizeEvent(self, e):
        self.appLabel.move(self.width() - 400, 140)
        self.loginLabel.move(self.width() - 400, 188)
        self.widget.resize(self.width(), self.widget.height())
        super().resizeEvent(e)

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
        self.selectedFoldersChanged.emit(selectedFolders)

    def __readConfig(self):
        """ 读入配置文件数据 """
        self.__checkConfigDir()
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

    def updateConfig(self, config: dict):
        """ 更新并保存配置数据

        Parameters
        ----------
        config : dict
            配置信息字典
        """
        self.__checkConfigDir()
        self.config.update(config)
        with open("app/config/config.json", "w", encoding="utf-8") as f:
            dump(self.config, f)

    @staticmethod
    def __checkConfigDir():
        """ 检查配置文件夹是否存在，不存在则创建 """
        os.makedirs('app/config', exist_ok=True)
