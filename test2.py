import sys


from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QListWidgetItem


class Demo(QListWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.resize(1210,800)
        self.item_list=[]
        self.leftSpacing = QWidget(self)
        self.rightSpacing = QWidget(self)
        self.leftSpacing.setStyleSheet('background:white')
        self.rightSpacing.setStyleSheet('background:white')
        self.setViewportMargins(30, 0, 30, 0)
        self.setAlternatingRowColors(True)
        self.createItems()

    def createItems(self):
        for i in range(20):
            item = QListWidgetItem(f'item{i}')
            item.setSizeHint(QSize(1150, 60))
            self.addItem(item)
            self.item_list.append(item)
        self.leftSpacing.raise_()
        with open('resource\\css\\songTabInterfaceSongListWidget.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def resizeEvent(self, e):
        """ 更新item的尺寸 """
        for item in self.item_list:
            item.setSizeHint(QSize(self.width()-60, 60))
        super().resizeEvent(e)
        self.rightSpacing.move(self.width() - 33, 0)
        self.rightSpacing.resize(32,self.height())
        self.leftSpacing.resize(31,self.height())
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
