import sys

from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtGui import QContextMenuEvent, QIcon, QMouseEvent, QResizeEvent
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QPushButton, QWidget

sys.path.append('..')
from Groove.card_widget.songcard_sub_unit import SongNameCard, YearTconDurationCard
from Groove.my_widget.my_label import ClickableLabel

class SongCard(QWidget):
    """ 定义一个歌曲卡类 """

    def __init__(self, songName, songer, album, tcon, year, duration):
        super().__init__()

        # 实例化小部件
        self.song_name_card = SongNameCard(songName)
        self.songerLabel = ClickableLabel(songer, self)
        self.albumLabel = ClickableLabel(album, self)
        self.yearTconDuration = YearTconDurationCard(year, tcon, duration)

        # 实例化布局
        self.all_h_layout = QHBoxLayout()
        self.right_h_layout = QHBoxLayout()

        # 初始化小部件
        self.initWidget()

        # 初始化布局
        self.initLayout()
        self.setQss()

    def initLayout(self):
        """ 初始化布局 """

        # 设置右侧的布局
        self.right_h_layout.addWidget(self.songerLabel, 0, Qt.AlignLeft)
        self.right_h_layout.addSpacing(13)
        self.right_h_layout.addWidget(self.albumLabel, 0, Qt.AlignLeft)
        self.right_h_layout.addWidget(self.yearTconDuration)

        # 设置全局布局
        self.all_h_layout.addWidget(self.song_name_card)
        self.all_h_layout.addLayout(self.right_h_layout)
        self.all_h_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.all_h_layout)

        self.resizetimes = 0

    def initWidget(self):
        """ 初始化小部件 """

        self.songerLabel.setFixedWidth(190)
        self.albumLabel.setFixedWidth(190)

        # 设置鼠标的光标
        self.songerLabel.setCursor(Qt.PointingHandCursor)
        self.albumLabel.setCursor(Qt.PointingHandCursor)

        # 分配ID
        self.songerLabel.setObjectName('songerLabel')
        self.albumLabel.setObjectName('albumLabel')
        self.setObjectName('songCard')

        # 安装事件过滤器
        self.installEventFilter(self)

    def setQss(self):
        """ 设置初始层叠样式 """
        with open('resource\\css\\songCard.qss', 'r', encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)

    def setClickableLabelState(self,labelState='unClicked'):
        """ 设置歌手和专辑这两个可点击标签state属性的状态 """
        self.songerLabel.setProperty('state', labelState)
        self.albumLabel.setProperty('state', labelState)

    def eventFilter(self, obj, event):
        """ 当鼠标点击歌曲卡时将文本换成白色 """
        if obj == self:
            if event.type() == QEvent.Enter and not self.song_name_card.contextMenuSelecting:
                if not self.song_name_card.clicked:
                    self.song_name_card.setWidgetState('enter and unClicked')
                    self.yearTconDuration.setWidgetState()
                    self.setClickableLabelState()
                    self.song_name_card.playButton.show()
                    self.song_name_card.addToButton.show()
                    self.song_name_card.maskButton.show()  
                    self.setStyle(QApplication.style())
            elif event.type() == QEvent.Leave:
                if not self.song_name_card.clicked:
                    self.song_name_card.setWidgetState()
                    self.yearTconDuration.setWidgetState()
                    self.setClickableLabelState()
                    self.song_name_card.playButton.hide()
                    self.song_name_card.addToButton.hide()
                    self.song_name_card.maskButton.hide()
                    # 更新样式
                    self.setStyle(QApplication.style())
            elif event.type() == QEvent.MouseButtonPress:
                self.song_name_card.clicked = True
                self.song_name_card.setWidgetState('clicked', 'clicked')
                self.yearTconDuration.setWidgetState('clicked')
                self.setClickableLabelState('clicked')
                self.song_name_card.addToButton.setIcon(
                    QIcon('resource\\images\\white_add_to_bt.png'))
                self.song_name_card.playButton.setIcon(
                    QIcon('resource\\images\\white_play_bt.png'))
                # 更新样式
                self.setStyle(QApplication.style())

        return False

    def resizeEvent(self, e: QResizeEvent):
        """ 窗口大小改变时就改变专辑和歌手名标签的长度 """
        # 初始化时会改变大小
        self.resizetimes += 1

        if self.resizetimes == 2:
            self.originalWidth = self.width()
        if self.resizetimes > 2:
            deltaWidth = self.width() - self.originalWidth
            self.originalWidth = self.width()
            # 分配多出来的宽度
            self.albumLabel.setFixedWidth(
                int(self.albumLabel.width() + 0.7*deltaWidth))
            self.songerLabel.setFixedWidth(
                int(self.songerLabel.width() + 0.2*deltaWidth))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = SongCard('猫じゃらし', 'RADWIMPS', '泠鸢yousa、鹿乃、花丸晴琉、神楽七奈、物述有栖、白上吹雪、夏色祭',
                    'ロック', '2020', '4:02')
    demo.show()
    sys.exit(app.exec_())
