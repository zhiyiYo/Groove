import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton,QLabel
from my_title_bar import TitleBar


class Demo(QWidget):

    def __init__(self):
        super().__init__()
        self.resize(500, 500)
        self.lb = QLabel(self)
        self.lb.setText('123456789')
        self.lb.setText('123456789'*10)

            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo=Demo()
    demo.show()
    sys.exit(app.exec_())


 def __adjustLabelWidth(self):
        """ 调整标签宽度 """
        for label in self.__label_list:
            width=self.__getLabelWidth(label)
            label.resize(width,label.height())
        
    def __getLabelWidth(self,label,pointSize=9):
        """ 计算歌名的长度 """
        fontMetrics = QFontMetrics(QFont('Microsoft YaHei', pointSize))
        labelWidth= sum([fontMetrics.width(i) for i in label.text()])
        return labelWidth
