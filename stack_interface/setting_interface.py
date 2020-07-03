import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QCheckBox, QLabel, QRadioButton,
                             QWidget,QScrollArea,QHBoxLayout)
sys.path.append('..')
from Groove.my_widget.my_label import ClickableLabel
from Groove.my_widget.my_scroll_bar import ScrollBar


class SettingInterface(QWidget):
    """ 设置界面 """
    def __init__(self, parent=None):
        super().__init__(parent)
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
        self.modeLabel = QLabel('模式', self.widget)
        self.playLabel = QLabel('播放', self.widget)
        self.settingLabel = QLabel('设置', self.widget)
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
        # 设置鼠标光标
        self.selectFolderLabel.setCursor(Qt.PointingHandCursor)
        self.equalizerLabel.setCursor(Qt.PointingHandCursor)
        self.loginLabel.setCursor(Qt.PointingHandCursor)
        # 分配ID
        self.appLabel.setObjectName('titleLabel')
        self.playLabel.setObjectName('titleLabel')
        self.modeLabel.setObjectName('titleLabel')
        self.settingLabel.setObjectName('settingLabel')
        self.mediaInfoLabel.setObjectName('titleLabel')
        self.musicInThisPCLabel.setObjectName('titleLabel')
        self.loginLabel.setObjectName('clickableLabel')
        self.equalizerLabel.setObjectName('clickableLabel')
        self.selectFolderLabel.setObjectName('clickableLabel')
        
    def initLayout(self):
        """ 初始化布局 """
        self.playLabel.move(30, 247)
        self.modeLabel.move(30, 483)
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
        else:
            self.getMetaDataCheckBox.setText('关')
        
    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\settingInterface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def resizeEvent(self,e):
        self.appLabel.move(self.width() - 400, 140)
        self.loginLabel.move(self.width() - 400, 188)
        self.widget.resize(self.width(),self.widget.height())
        super().resizeEvent(e)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = SettingInterface()
    demo.show()
    sys.exit(app.exec_())
