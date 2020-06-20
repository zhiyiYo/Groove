import sys

from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtGui import QBitmap, QBrush, QColor, QPainter, QPen, QPixmap,QIcon,QContextMenuEvent
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget,QAction

sys.path.append('..')

from Groove.my_widget.my_button import SongerAddToButton, SongerPlayButton
from Groove.my_widget.my_menu import Menu

class SongerCard(QWidget):
    """ 定义一个包含歌手头像和名字的类 """

    def __init__(self, songer_pic_path, songer_name):
        super().__init__()

        # 实例化歌手名标签和背景
        self.backgroundLabel = QLabel(self)
        self.songerNameLabel = SongerName(songer_name, self)

        # 实例化歌手头像
        self.songerHeadPortrait = SongerHeadPortrait(songer_pic_path, self)

        # 初始化小部件
        self.initWidget()

        # 设置层叠样式
        self.setQss()

    def initWidget(self):
        """ 初始化小部件 """
        self.resize(222, 268)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # 设置小部件的绝对位置
        self.songerHeadPortrait.move(10, 9)
        self.songerNameLabel.move(1, 212)

        # 初始化背景图片
        self.backgroundLabel.setPixmap(
            QPixmap('resource\\images\\歌手头像无阴影.png'))

        # 设置监听
        self.installEventFilter(self)

    def eventFilter(self, obj, e):
        """ 鼠标进入窗口时显示阴影和按钮，否则不显示 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.backgroundLabel.setPixmap(
                    QPixmap('resource\\images\\歌手头像阴影.png'))
                self.songerHeadPortrait.addToButton.show()
                self.songerHeadPortrait.playButton.show()
            elif e.type() == QEvent.Leave:
                self.backgroundLabel.setPixmap(
                    QPixmap('resource\\images\\歌手头像无阴影.png'))
                self.songerHeadPortrait.addToButton.setHidden(True)
                self.songerHeadPortrait.playButton.setHidden(True)

        return False

    def contextMenuEvent(self, event: QContextMenuEvent):
        """ 显示右击菜单 """
        menu = Menu(parent=self)
        addToMenu = Menu('添加到', self)
        playAct = QAction('播放', self)
        chooseAct = QAction('选择', self)
        playingAct = QAction(QIcon('resource\\images\\正在播放.png'), '正在播放', self)
        newPlayList = QAction(
            QIcon('resource\\images\\黑色加号.png'), '新的播放列表', self)
        nextToPlayAct = QAction('下一首播放', self)
        pinToStartMenuAct = QAction('固定到"开始"菜单', self)
        # 设置ID
        addToMenu.setObjectName('addToMenu')
        # 将动作添加到菜单中
        addToMenu.addAction(playingAct)
        addToMenu.addSeparator()
        addToMenu.addAction(newPlayList)
        menu.addActions([playAct, nextToPlayAct])
        menu.addMenu(addToMenu)
        menu.addAction(pinToStartMenuAct)
        menu.addSeparator()
        menu.addAction(chooseAct)
        menu.exec_(event.globalPos())

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\songerCard.qss', 'r', encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)


class SongerHeadPortrait(QWidget):

    def __init__(self, songer_pic_path, parent=None):
        super().__init__(parent)

        self.resize(200, 200)

        # 隐藏边框并将背景设置为透明
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 实例化播放按钮和添加到按钮
        self.playButton = SongerPlayButton(self)
        self.addToButton = SongerAddToButton(self)

        # 设置背景图片
        self.circle_image = QPixmap(songer_pic_path).scaled(
            self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # 初始化小部件
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        self.playButton.move(int(0.5 * self.width() - 36 - 0.5 * self.playButton.width()),
                             int(0.5*self.height() - 0.5*self.playButton.height()+1))

        self.addToButton.move(int(0.5*self.width()+36-0.5*self.playButton.width()),
                              int(0.5*self.height() - 0.5*self.playButton.height()+1))

        # 隐藏按钮
        #self.addToButton.getBackgroundPic()
        self.playButton.setHidden(True)
        self.addToButton.setHidden(True)


    def paintEvent(self, e):
        super(SongerHeadPortrait, self).paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)  # 设置抗锯齿

        #设置描边画笔
        pen = QPen(QColor(253,253,253))
        pen.setWidth(1)
        painter.setPen(pen)
                                   		
        #设置画刷的内容为歌手图
        brush = QBrush(self.circle_image)
        painter.setBrush(brush)								

        #在指定区域画圆
        painter.drawEllipse(0, 0, self.width(), self.height())


class SongerName(QWidget):
    """ 歌手名标签 """

    def __init__(self, songer_name, parent=None):
        super().__init__(parent)

        self.setFixedWidth(220)

        # 实例化歌手名标签
        self.songerNameLabel = QLabel(songer_name, self)
        # 实例化布局
        self.v_layout = QVBoxLayout()

        # 初始化布局

        self.v_layout.addWidget(self.songerNameLabel, 0, Qt.AlignHCenter)
        self.setLayout(self.v_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    songCard = SongerCard(
        'resource\\Songer Photos\\LINKIN PARK\\LINKIN PARK.jpg', 'Backstreet Boys')
    songCard.show()
    sys.exit(app.exec_())
