# coding:utf-8
from common.style_sheet import setStyleSheet
from PyQt5.QtCore import QFile, pyqtSignal
from PyQt5.QtWidgets import QWidget


class NavigationWidgetBase(QWidget):
    """ Navigation widget base """

    selectedButtonChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._selectableButtons = []
        self._selectableButtonNames = []
        self.playlistNameButtons = []
        self.__buttonIndexes = {
            'myMusicButton': 0,
            'historyButton': 1,
            'playlistButton': 2,
            'settingButton': 3
        }
        self.currentButton = None

        setStyleSheet(self, 'navigation')

    def _connectButtonClickedSigToSlot(self):
        """ _connect button clicked signal to slot """
        if len(self._selectableButtonNames) != len(self._selectableButtons):
            raise Exception(
                'The button list does not match the length of its corresponding name list.')

        for button, name in zip(self._selectableButtons, self._selectableButtonNames):
            if button.property('name'):
                continue
            button.setProperty('name', name)
            button.clicked.connect(
                lambda checked, name=name: self.__onButtonClicked(name))

    def setCurrentIndex(self, index: int):
        """ set selected button """
        names = [k for k, v in self.__buttonIndexes.items() if v == index]
        if names:
            self.__updateButtonSelectedState(names[0])

    def setSelectedButton(self, buttonName: str):
        """ set selected button

        Parameters
        ----------
        buttonName: str
            button name, defined by `btn.property('name')`
        """
        self.__updateButtonSelectedState(buttonName)

    def __onButtonClicked(self, buttonName: str):
        """ button clicked slot """
        if buttonName == 'playingButton':
            return

        self.__updateButtonSelectedState(buttonName)
        self.selectedButtonChanged.emit(buttonName)

    def __updateButtonSelectedState(self, buttonName: str):
        """ update selected state of all buttons """
        self.currentButton.setSelected(False)
        if buttonName in self._selectableButtonNames:
            index = self._selectableButtonNames.index(buttonName)
            self.currentButton = self._selectableButtons[index]
            self.currentButton.setSelected(True)