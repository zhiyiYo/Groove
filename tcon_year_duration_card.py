import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QLabel,
                             QWidget)


class TconYearDurationCard(QWidget):
    """ 定义一个包含年份、流派、时长的类 """

    def __init__(self, tcon, year, duration):
        super().__init__()

        self.setFixedWidth(400)
        # 实例化三个标签
        self.tconLabel = QLabel(tcon, self)
        self.yearLabel = QLabel(year, self)
        self.durationLabel = QLabel(duration, self)

        # 实例化布局
        self.h_layout = QHBoxLayout(self)

        # 初始化布局
        self.initLayout()

    def initLayout(self):
        """ 初始化布局 """
        self.h_layout.addWidget(self.yearLabel, 0, Qt.AlignLeft)
        self.h_layout.addSpacing(5)        
        self.h_layout.addWidget(self.tconLabel, 0, Qt.AlignLeft)     
        self.h_layout.addStretch(1)
        self.h_layout.addWidget(self.durationLabel, 0, Qt.AlignRight)

        self.setLayout(self.h_layout)

    def initWidget(self):
        """ 初始化小部件 """

        # 分配ID
        self.tconLabel.setObjectName('tconLabel')
        self.yearLabel.setObjectName('yearLabel')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = TconYearDurationCard('ロック', '2020', '4:02')
    demo.show()
    sys.exit(app.exec_())
