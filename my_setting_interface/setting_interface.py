import sys
from json import load,dump

from PyQt5.QtCore import Qt,pyqtSignal
from PyQt5.QtWidgets import (QApplication, QCheckBox, QLabel, QRadioButton,
                             QWidget,QScrollArea,QHBoxLayout)
sys.path.append('..')
from Groove.my_widget.my_label import ClickableLabel
from Groove.my_widget.my_scroll_bar import ScrollBar
from Groove.my_setting_interface.select_song_folder_panel import SelectSongFolderPanel
from Groove.my_setting_interface.get_meta_data_thread import GetMetaDataThread
from Groove.my_setting_interface.state_tool_tip import StateToolTip
from Groove.get_info.get_song_info import SongInfo



class SettingInterface(QWidget):
    """ 设置界面 """
    # 创建一个爬虫完成工作的信号
    crawlComplete = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # 读入数据
        self.readConfig()
        # 创建小部件
        self.createWidgets()
        # 初始化界面
        self.initWidget()
        self.initLayout()
        self.setQss()
        
    def createWidgets(self):
        """ 创建小部件 """
        # 实例化滚动区域
        self.all_h_layout = QHBoxLayout(self)
        self.scrollArea = QScrollArea(self)
        self.widget = QWidget()
        # 实例化标签
        self.appLabel = QLabel('应用', self.widget)
        self.playLabel = QLabel('播放', self.widget)
        self.settingLabel = QLabel('设置', self.widget)
        self.colorModeLabel = QLabel('模式', self.widget)
        self.mediaInfoLabel = QLabel('媒体信息', self.widget)
        self.loginLabel = ClickableLabel('登录', self.widget)
        self.getMetaDataCheckBox = QCheckBox('关', self.widget)
        self.darkColorButton = QRadioButton('深色', self.widget)
        self.lightColorButton = QRadioButton('浅色', self.widget)
        self.equalizerLabel = ClickableLabel('均衡器', self.widget)
        self.musicInThisPCLabel = QLabel('此PC上的音乐', self.widget)
        self.selectFolderLabel = ClickableLabel('选择查找音乐的位置', self.widget)
        self.getMetaDataLabel = QLabel('自动检索并更新缺失的专辑封面和元数据', self.widget)    
        
    def initWidget(self):
        """ 初始化小部件 """
        self.resize(1000, 800)
        self.widget.resize(self.width(), 800)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 将信号连接到槽函数
        self.getMetaDataCheckBox.stateChanged.connect(self.checkBoxStatedChangedEvent)
        self.selectFolderLabel.clicked.connect(self.showSelectSongFolderPanel)
        self.lightColorButton.clicked.connect(self.colorModeChangeEvent)
        self.darkColorButton.clicked.connect(self.colorModeChangeEvent)
        # 设置鼠标光标
        self.selectFolderLabel.setCursor(Qt.PointingHandCursor)
        self.equalizerLabel.setCursor(Qt.PointingHandCursor)
        self.loginLabel.setCursor(Qt.PointingHandCursor)
        # 分配ID
        self.appLabel.setObjectName('titleLabel')
        self.playLabel.setObjectName('titleLabel')
        self.colorModeLabel.setObjectName('titleLabel')
        self.settingLabel.setObjectName('settingLabel')
        self.mediaInfoLabel.setObjectName('titleLabel')
        self.loginLabel.setObjectName('clickableLabel')
        self.musicInThisPCLabel.setObjectName('titleLabel')
        self.equalizerLabel.setObjectName('clickableLabel')
        self.selectFolderLabel.setObjectName('clickableLabel')
        # 设置选中的主题颜色
        if self.config['color-mode'] == 'light-color':
            self.lightColorButton.setChecked(True)
        else:
            self.darkColorButton.setChecked(True)
        
    def initLayout(self):
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
        self.getMetaDataCheckBox.move(30, 423)
        self.appLabel.move(self.width() - 400, 140)
        self.loginLabel.move(self.width() - 400, 188)
        self.scrollArea.setWidget(self.widget)
        self.all_h_layout.addWidget(self.scrollArea)
        self.all_h_layout.setContentsMargins(0, 0, 0, 0)

    def checkBoxStatedChangedEvent(self):
        """ 复选框状态改变对应的槽函数 """
        if self.getMetaDataCheckBox.isChecked():
            self.getMetaDataCheckBox.setText('开')
            self.getMetaDataCheckBox.setEnabled((False))
            # 创建一个爬虫线程
            self.createCrawlThread()
        else:
            self.getMetaDataCheckBox.setEnabled(True)
            self.getMetaDataCheckBox.setText('关')

    def createCrawlThread(self):
        """ 创建一个爬虫线程 """
        self.getMetaDataThread = GetMetaDataThread(
            self.config['selected-folders'])
        self.stateToolTip = StateToolTip(
            '正在爬取专辑信息', '正在启动浏览器...', self.getMetaDataThread, self.window())
        self.getMetaDataThread.crawlSignal.connect(self.updateStateToolTip)
        self.getMetaDataThread.finished.connect(
            self.getMetaDataThread.deleteLater)
        self.stateToolTip.show()
        self.getMetaDataThread.start()

    def updateStateToolTip(self, crawlState):
        """ 根据爬取进度更新进度提示框 """
        if crawlState == '酷狗爬取完成':
            self.stateToolTip.setTitle('正在爬取流派信息')
        elif crawlState == '全部完成':
            self.stateToolTip.setState(True)
            # 摧毁线程
            self.getMetaDataThread.requestInterruption()
            self.getMetaDataThread.wait()
            # 更新json文件
            self.__updateSongInfo()
        elif crawlState == '强制退出':
            self.__updateSongInfo()
        else:
            self.stateToolTip.setContent(crawlState)

    def __updateSongInfo(self):
        """ 更新歌曲信息 """
        self.getMetaDataCheckBox.setCheckState(Qt.Unchecked)
        songInfo = SongInfo(self.config['selected-folders'])
        songInfo.updateInfo()
        # 发送爬取完成的信号
        self.crawlComplete.emit()

    def colorModeChangeEvent(self):
        """ 主题颜色改变时更新Json文件 """
        if self.sender() == self.lightColorButton:
            self.config['color-mode'] = 'light-color'
        else:
            self.config['color-mode'] = 'dark-color'
        self.writeConfig()

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\settingInterface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def resizeEvent(self,e):
        self.appLabel.move(self.width() - 400, 140)
        self.loginLabel.move(self.width() - 400, 188)
        self.widget.resize(self.width(),self.widget.height())
        super().resizeEvent(e)

    def showSelectSongFolderPanel(self):
        """ 显示歌曲文件夹选择面板 """
        selectSongFolderPanel = SelectSongFolderPanel(self.window())
        # 如果歌曲文件夹选择面板更新了json文件那么自己也得更新
        selectSongFolderPanel.updateConfigSignal.connect(self.readConfig)
        selectSongFolderPanel.exec_()

    def readConfig(self):
        """ 读入配置文件数据 """
        with open('Data\\config.json', encoding='utf-8') as f:
            self.config = load(f)

    def writeConfig(self):
        """ 读入配置文件数据 """
        # 重置下标
        self.config['current-index'] = 0
        self.config['pre-index'] = 1
        with open('Data\\config.json','w', encoding='utf-8') as f:
            dump(self.config, f)

    def closeEvent(self, e):
        """ 关闭窗口之前更新json文件 """
        self.writeConfig()
        e.accept()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = SettingInterface()
    demo.show()
    sys.exit(app.exec_())
