# coding:utf-8

import json

from app.components.dialog_box.sub_panel_frame import SubPanelFrame
from app.components.buttons.perspective_button import PerspectivePushButton
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QGraphicsDropShadowEffect,
    QLabel,
    QWidget,
)

from .delete_song_folder_panel import DeleteSongFolderPanel
from .folder_card import FolderCard
from .folding_window import FoldingWindow


class SelectSongFolderPanel(SubPanelFrame):
    """ 选择歌曲文件夹面板 """

    def __init__(self, selectedFolders: list, parent=None):
        """
        Parameters
        ----------
        selectedFolders: list
            选中的文件夹

        parent:
            父级窗口
         """
        super().__init__(parent)
        # 实例化子属性面板
        self.subSelectSongFolderPanel = SubSelectSongFolderPanel(selectedFolders, self)
        self.updateSelectedFoldersSig = (
            self.subSelectSongFolderPanel.updateSelectedFoldersSig
        )
        # 初始化
        self.showMask()
        self.setSubWindowPos()

    def setSubWindowPos(self):
        """ 设置子窗口的位置 """
        self.subSelectSongFolderPanel.move(
            int(self.width() / 2 - self.subSelectSongFolderPanel.width() / 2),
            int(self.height() / 2 - self.subSelectSongFolderPanel.height() / 2),
        )


class SubSelectSongFolderPanel(QWidget):
    """ 子选择歌曲文件夹面板 """

    updateSelectedFoldersSig = pyqtSignal(list)  # 发送更新了的歌曲文件夹列表

    def __init__(self, selectedFolders: list, parent):
        super().__init__(parent)
        # 读入配置文件
        # self.readConfig()
        self.selectedFolders = selectedFolders.copy()
        # 创建小部件
        self.__createWidgets()
        # 初始化
        self.__initWidget()
        self.__initLayout()

    def __createWidgets(self):
        """ 创建小部件 """
        self.addFolderTimer = QTimer(self)
        self.deleteFolderTimer = QTimer(self)
        self.addFolderCard = AddFolderCard(self)
        self.completeButton = PerspectivePushButton("完成", self)
        self.titleLabel = QLabel('从本地曲库创建个人"收藏"', self)
        self.folderCard_list = []
        if self.selectedFolders:
            self.subTitleLabel = QLabel("现在我们正在查看这些文件夹", self)
            for folderPath in self.selectedFolders:
                folderCard = FolderCard(folderPath, self)
                # 在显示删除文件卡对话框前加个延时
                folderCard.clicked.connect(self.startDeleteFolderTimer)
                self.folderCard_list.append(folderCard)

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedWidth(440)
        self.setFixedHeight(324 + 100 * len(self.folderCard_list))
        self.setAttribute(Qt.WA_StyledBackground)
        # 添加阴影
        self.setShadowEffect()
        # 初始化定时器
        self.addFolderTimer.setInterval(500)
        self.deleteFolderTimer.setInterval(600)
        self.addFolderTimer.timeout.connect(self.showFileDialog)
        self.deleteFolderTimer.timeout.connect(self.showDeleteFolderCardPanel)
        # 将信号连接到槽函数
        self.addFolderCard.clicked.connect(self.addFolderTimer.start)
        self.completeButton.clicked.connect(self.updateSelectedFolders)
        # 分配ID
        self.setObjectName("father")
        self.titleLabel.setObjectName("titleLabel")
        if hasattr(self, "subTitleLabel"):
            self.subTitleLabel.setObjectName("subTitleLabel")
        self.__setQss()

    def __initLayout(self):
        """ 初始化布局 """
        self.titleLabel.move(31, 31)
        self.addFolderCard.move(36, 120)
        self.completeButton.move(223, self.height() - 71)
        if hasattr(self, "subTitleLabel"):
            self.subTitleLabel.move(31, 79)
            for index, folderCard in enumerate(self.folderCard_list):
                folderCard.move(36, 220 + index * 100)

    def startDeleteFolderTimer(self):
        """ 打卡定时器并记录发送者 """
        self.__clickedFolder = self.sender()
        self.deleteFolderTimer.start()

    def showFileDialog(self):
        """ 定时器溢出时显示文件对话框 """
        self.addFolderTimer.stop()
        path = QFileDialog.getExistingDirectory(self, "选择文件夹", "./")
        if path and path not in self.selectedFolders:
            # 将斜杠替换为反斜杠
            path = path.replace("/", "\\")
            # 将选择的文件夹路径插入列表
            self.selectedFolders.append(path)
            # 创建文件路径卡
            self.setFixedHeight(self.height() + 100)
            self.parent().setSubWindowPos()
            newFolderCard = FolderCard(path, self)
            newFolderCard.move(36, self.height() - 206)
            self.folderCard_list.append(newFolderCard)
            newFolderCard.clicked.connect(self.startDeleteFolderTimer)

    def showDeleteFolderCardPanel(self):
        """ 显示删除文件夹对话框 """
        self.deleteFolderTimer.stop()
        self.deleteSongFolderPanel = DeleteSongFolderPanel(
            self.__clickedFolder.folderName, self.window()
        )
        self.deleteSongFolderPanel.deleteButton.clicked.connect(self.deleteSongFolder)
        self.deleteSongFolderPanel.exec_()

    def deleteSongFolder(self):
        """ 删除选中的文件卡 """
        sender = self.__clickedFolder
        sender.deleteLater()
        # 获取下标
        index = self.folderCard_list.index(sender)
        self.selectedFolders.remove(sender.folderPath)
        self.folderCard_list.remove(sender)
        self.deleteSongFolderPanel.deleteLater()
        # 将下面的卡片上移
        for folderCard in self.folderCard_list[index:]:
            folderCard.move(folderCard.x(), folderCard.y() - 100)
        # 更新高度
        self.setFixedHeight(self.height() - 100)
        self.parent().setSubWindowPos()

    def setShadowEffect(self):
        """ 添加阴影 """
        self.shadowEffect = QGraphicsDropShadowEffect(self)
        self.shadowEffect.setBlurRadius(60)
        self.shadowEffect.setOffset(0, 5)
        self.setGraphicsEffect(self.shadowEffect)

    def readConfig(self):
        """ 从json文件读入配置 """
        try:
            with open("app\\config\\config.json", encoding="utf-8") as f:
                self.__config = json.load(f)  # type:dict
        except:
            self.__config = {"selected-folders": []}
        if "selected-folders" not in self.__config.keys():
            self.__config["selected-folders"] = []

    def paintEvent(self, e):
        """ 绘制边框 """
        pen = QPen(QColor(172, 172, 172))
        pen.setWidth(2)
        painter = QPainter(self)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

    def __setQss(self):
        """ 设置层叠样式 """
        with open(r"app\resource\css\selectSongFolderPanel.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def updateSelectedFolders(self):
        """ 更新主界面中选中的歌曲文件夹列表 """
        QApplication.processEvents()
        # 保存设置后禁用窗口
        self.setEnabled(False)
        self.updateSelectedFoldersSig.emit(self.selectedFolders)
        self.parent().deleteLater()

    def resizeEvent(self, e):
        """ 改变高度时移动按钮 """
        self.completeButton.move(223, self.height() - 71)


class AddFolderCard(FoldingWindow):
    """ 点击选择文件夹 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = QPixmap("app\\resource\\images\\setting_interface\\黑色加号.png")

    def paintEvent(self, e):
        """ 绘制背景 """
        super().paintEvent(e)
        painter = QPainter(self)
        if not self.pressedPos:
            painter.drawPixmap(
                int(self.width() / 2 - self.image.width() / 2),
                int(self.height() / 2 - self.image.height() / 2),
                self.image.width(),
                self.image.height(),
                self.image,
            )
        elif self.pressedPos in ["top", "bottom"]:
            painter.drawPixmap(
                int(self.width() / 2 - (self.image.width() - 2) / 2),
                int(self.height() / 2 - (self.image.height() - 4) / 2),
                self.image.width() - 2,
                self.image.height() - 4,
                self.image,
            )
        elif self.pressedPos in ["left", "right"]:
            painter.drawPixmap(
                int(self.width() / 2 - (self.image.width() - 4) / 2),
                int(self.height() / 2 - (self.image.height() - 2) / 2),
                self.image.width() - 4,
                self.image.height() - 2,
                self.image,
            )
        else:
            painter.drawPixmap(
                int(self.width() / 2 - (self.image.width() - 4) / 2),
                int(self.height() / 2 - (self.image.height() - 4) / 2),
                self.image.width() - 4,
                self.image.height() - 4,
                self.image,
            )

