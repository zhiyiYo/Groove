import sys
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication
from PyQt5.QtCore import QSize


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setMinimumSize(QSize(400, 400))

        color = QPushButton('color', self)
        color.clicked.connect(self.color)
        color.resize(100, 115)
        color.move(0, 100)

        buttons = ['button1', 'button2', 'button3']
        self.pybutton = {}

        qss = """
        QPushButton{
            max-width: 75px;
            text-align:center;
            padding-left: 20px; 
            max-height: 60px; 
            font-size: 20px;
        }
        QPushButton[color = "0"]{
            background-color: green;
        }
        QPushButton[color = "1"]{
            background-color: red;
        }
        """

        for i, text in enumerate(buttons):
            btn = QPushButton(text, self)
            btn.setObjectName('btn{}'.format(i))
            btn.setGeometry(300-i*100, 100, 100, 100)
            btn.setStyleSheet(qss)
            self.pybutton[str(i)] = btn

    def color(self):
        for i, btn in self.pybutton.items():
            if btn.objectName() == 'btn1':
                btn.setProperty("color", "0")
            else:
                btn.setProperty("color", "1")
            btn.style().polish(btn)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
