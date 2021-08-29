# coding:utf-8
from PyQt5.QtCore import QFile, pyqtSignal
from PyQt5.QtWidgets import QWidget


class NavigationWidgetBase(QWidget):
    """ 导航部件基类 """

    selectedButtonChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        # 初始化按钮及其名字列表
        self._selectableButtons = []
        self._selectableButtonNames = []
        self.playlistNameButtons = []
        self.__switchInterfaceButtonIndex_dict = {
            'myMusicButton': 0,
            'playlistButton': 1,
            'settingButton': 2
        }
        # 初始化当前按钮
        self.currentButton = None
        # 设置样式
        self.__setQss()

    def _connectButtonClickedSigToSlot(self):
        """ 将按钮点击信号连接到槽函数 """
        if len(self._selectableButtonNames) != len(self._selectableButtons):
            raise Exception('按钮与其对应的名字列表长度不一致')

        for button, name in zip(self._selectableButtons, self._selectableButtonNames):
            if button.property('name'):
                continue
            button.setProperty('name', name)
            button.clicked.connect(
                lambda checked, name=name: self.__onButtonClicked(name))

    def setCurrentIndex(self, index: int):
        """ 设置下标对应的按钮的选中状态 """
        selectedButtonName_list = [
            key for key, value in self.__switchInterfaceButtonIndex_dict.items() if value == index]
        # 更新按钮的选中状态
        if selectedButtonName_list:
            self.__updateButtonSelectedState(selectedButtonName_list[0])

    def setSelectedButton(self, buttonName: str):
        """ 设置当前选中的按钮

        Parameters
        ----------
        buttonName: str
            由 `btn.property('name')` 返回的按钮名字
        """
        self.__updateButtonSelectedState(buttonName)

    def __onButtonClicked(self, selectedButtonName: str):
        """ 按钮点击槽函数 """
        if selectedButtonName == 'playingButton':
            return
        self.__updateButtonSelectedState(selectedButtonName)

        # 发送当前按钮的名字，要求导航界面同步按钮选中状态
        self.selectedButtonChanged.emit(selectedButtonName)

    def __updateButtonSelectedState(self, selectedButtonName: str):
        """ 更新选中的按钮样式 """
        self.currentButton.setSelected(False)
        if selectedButtonName in self._selectableButtonNames:
            index = self._selectableButtonNames.index(selectedButtonName)
            self.currentButton = self._selectableButtons[index]
            self.currentButton.setSelected(True)

    def __setQss(self):
        """ 设置层叠样式 """
        f = QFile(":/qss/navigation.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()
