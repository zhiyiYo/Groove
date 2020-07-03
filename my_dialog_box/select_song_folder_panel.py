import sys
import json

from PyQt5.QtCore import Qt,QTimer
from PyQt5.QtGui import QPen, QPainter, QBrush, QColor,QPixmap
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QWidget,QGraphicsDropShadowEffect,QFileDialog
sys.path.append('..')
from Groove.my_widget.folding_window import FoldingWindow


class SelectSongFolderPanel(QDialog):
    """ 选择歌曲文件夹面板 """

    def __init__(self, parent=None):
        super().__init__(parent)

        # 实例化子属性面板
        self.subSelectSongFolderPanel = SubSelectSongFolderPanel(self)
        # 初始化
        self.initWidget()
        self.initLayout()

    def initWidget(self):
        """ 初始化小部件 """
        self.resize(self.subSelectSongFolderPanel.size())
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        # deleteLater才能真正释放内存
        self.subSelectSongFolderPanel.completeButton.clicked.connect(self.deleteLater)
        if self.parent():
            parent_rect = self.parent().geometry()
            self.setGeometry(parent_rect.x(), parent_rect.y(),
                             parent_rect.width(), parent_rect.height())
            self.createWindowMask()

    def initLayout(self):
        """ 初始化布局 """
        self.subSelectSongFolderPanel.move(int(self.width() / 2 - self.subSelectSongFolderPanel.width() / 2),
                                   int(self.height() / 2 - self.subSelectSongFolderPanel.height() / 2))

    def createWindowMask(self):
        """ 创建白色透明遮罩 """
        self.windowMask = QWidget(self)
        self.windowMask.setStyleSheet('background:rgba(255,255,255,177)')
        self.windowMask.resize(self.size())
        self.windowMask.lower()



class SubSelectSongFolderPanel(QWidget):
    """ 子选择歌曲文件夹面板 """
    def __init__(self, parent=None):
        super().__init__(parent)
        # 读入配置文件
        self.readConfig()
        # 创建小部件
        self.createWidgets()
        # 初始化
        self.initWidget()
        self.initLayout()
        self.setQss()

    def createWidgets(self):
        """ 创建小部件 """
        self.titleLabel = QLabel('从本地曲库创建个人"收藏"', self)
        if self.__config['selected-folders']:
            self.subTitleLabel = QLabel('现在我们正在这些文件夹', self)
        self.completeButton = QPushButton('完成', self)
        self.addFolderCard = AddFolderCard(self)
        
    def initWidget(self):
        """ 初始化小部件 """
        self.setFixedWidth(440)
        self.setMinimumHeight(324)
        self.setAttribute(Qt.WA_StyledBackground)
        # 添加阴影
        self.setShadowEffect()
        # 分配ID
        self.setObjectName('father')
        self.titleLabel.setObjectName('titleLabel')

    def initLayout(self):
        """ 初始化布局 """
        self.titleLabel.move(31, 31)
        self.addFolderCard.move(36,116)
        self.completeButton.move(221, self.height() - 71)

    def setShadowEffect(self):
        """ 添加阴影 """
        self.shadowEffect = QGraphicsDropShadowEffect(self)
        self.shadowEffect.setBlurRadius(60)
        self.shadowEffect.setOffset(0, 5)
        self.setGraphicsEffect(self.shadowEffect)
        
    def readConfig(self):
        """ 从json文件读入配置 """
        with open('Data\\config.json', encoding='utf-8') as f:
            self.__config = json.load(f)

    def paintEvent(self,e):
        """ 绘制边框 """
        pen = QPen(QColor(204, 204, 204))
        painter = QPainter(self)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

    def setQss(self):
        """ 设置层叠样式 """ 
        with open(r'resource\css\selectSongFolderPanel.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())
        

class AddFolderCard(FoldingWindow):
    """ 点击选择文件夹 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.showFileDialog)
        self.image = QPixmap('resource\\images\\setting_interface\\黑色加号.png')
        
    def mouseReleaseEvent(self, e):
        """ 鼠标松开之后选择文件夹 """
        super().mouseReleaseEvent(e)
        self.timer.start()

    def showFileDialog(self):
        """ 定时器溢出时显示文件对话框 """
        self.timer.stop()
        fileDialog = QFileDialog(self)
        fileDialog.move(self.window().x() + 10, self.window().y())
        path = fileDialog.getExistingDirectory(
            self, '选择文件夹', './')
        if path:
            pass

    def paintEvent(self, e):
        """ 绘制背景 """
        super().paintEvent(e)
        painter = QPainter(self)
        painter.drawPixmap(int(self.width() / 2 - self.image.width() / 2),
                            int(self.height() / 2 - self.image.height() / 2),
                            self.image.width(), self.image.height(),self.image)


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1280, 800)
        self.label = QLabel(self)
        self.label.setPixmap(QPixmap(r"D:\hzz\图片\硝子\硝子 (3).jpg").scaled(
            1280, 800, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.bt = QPushButton('点击打开歌曲文件夹选择面板', self)
        self.bt.move(480, 355)
        self.bt.clicked.connect(self.showPanel)

    def showPanel(self):
        # 读取信息
        panel = SelectSongFolderPanel(self)
        panel.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
