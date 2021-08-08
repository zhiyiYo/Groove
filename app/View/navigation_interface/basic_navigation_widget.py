# coding:utf-8

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget


class BasicNavigationWidget(QWidget):
    """ 导航部件基类 """

    switchInterfaceSig = pyqtSignal(int)
    selectedButtonChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        # 初始化按钮及其名字列表
        self._selectableButton_list = []
        self._selectableButtonName_list = []
        self.__switchInterfaceButtonIndex_dict = {
            'musicGroupButton': 0,
            'playlistButton': 1,
            'settingButton': 2
        }
        # 初始化当前按钮
        self.currentButton = None
        # 设置样式
        self.__setQss()

    def _connectButtonClickedSigToSlot(self):
        """ 将按钮点击信号连接到槽函数 """
        if len(self._selectableButtonName_list) != len(self._selectableButton_list):
            raise Exception('按钮与其对应的名字列表长度不一致')
        for button, name in zip(self._selectableButton_list, self._selectableButtonName_list):
            button.setProperty('name', name)
            button.clicked.connect(
                lambda checked, name=name: self.__buttonClickedSlot(name))

    def setCurrentIndex(self, index: int):
        """ 设置下标对应的按钮的选中状态 """
        selectedButtonName_list = [
            key for key, value in self.__switchInterfaceButtonIndex_dict.items() if value == index]
        if selectedButtonName_list:
            # 更新按钮的选中状态
            self.__updateButtonSelectedState(selectedButtonName_list[0])

    def setSelectedButton(self, buttonName: str):
        """ 设置当前选中的按钮

        Parameters
        ----------
        buttonName: str
            由 `btn.objectName()` 返回的按钮名字
        """
        self.__updateButtonSelectedState(buttonName)

    def __buttonClickedSlot(self, selectedButtonName: str):
        """ 按钮点击槽函数 """
        if selectedButtonName == 'playingButton':
            return
        self.__updateButtonSelectedState(selectedButtonName)
        # 发送当前按钮的名字
        self.selectedButtonChanged.emit(selectedButtonName)
        # 如果按下的按钮在切换界面的按钮列表中，就发送切换界面的信号
        if selectedButtonName in self.__switchInterfaceButtonIndex_dict.keys():
            self.switchInterfaceSig.emit(
                self.__switchInterfaceButtonIndex_dict[selectedButtonName])

    def __updateButtonSelectedState(self, selectedButtonName: str):
        """ 更新选中的按钮样式 """
        self.currentButton.setSelected(False)
        if selectedButtonName in self._selectableButtonName_list:
            self.currentButton = self._selectableButton_list[self._selectableButtonName_list.index(
                selectedButtonName)]
            self.currentButton.setSelected(True)

    def __setQss(self):
        """ 设置层叠样式 """
        with open(r'app\resource\css\navigation.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())
