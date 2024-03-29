# coding:utf-8
from typing import List
from common.config import OptionsConfigItem, config
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QButtonGroup, QLabel, QRadioButton


from .expand_setting_card import ExpandSettingCard


class OptionsSettingCard(ExpandSettingCard):
    """ setting card with a group of options """

    optionChanged = pyqtSignal(OptionsConfigItem)

    def __init__(self, configItem: OptionsConfigItem, iconPath: str, title: str, content: str = None,
                 texts: List[str] = None, parent=None):
        """
        Parameters
        ----------
        configItem: OptionsConfigItem
            options config item

        iconPath: str
            icon path

        title: str
            the title of setting card

        content: str
            the content of setting card

        texts: List[str]
            the texts of radio buttons

        parent: QWidget
            parent window
        """
        super().__init__(iconPath, title, content, parent)
        self.texts = texts or []
        self.configItem = configItem
        self.configName = configItem.name
        self.choiceLabel = QLabel(self)
        self.buttonGroup = QButtonGroup(self)

        self.addWidget(self.choiceLabel)

        # create buttons
        self.viewLayout.setSpacing(24)
        self.viewLayout.setContentsMargins(60, 22, 0, 22)
        for text, option in zip(texts, configItem.options):
            button = QRadioButton(text, self.view)
            self.buttonGroup.addButton(button)
            self.viewLayout.addWidget(button)
            button.setProperty(self.configName, option)

        self._adjustViewSize()
        self.setSelected(config.get(self.configItem))
        self.buttonGroup.buttonClicked.connect(self.__onButtonClicked)

    def __onButtonClicked(self, button: QRadioButton):
        """ button clicked slot """
        if button.text() == self.choiceLabel.text():
            return

        value = button.property(self.configName)
        config.set(self.configItem, value)

        self.choiceLabel.setText(button.text())
        self.choiceLabel.adjustSize()
        self.optionChanged.emit(self.configItem)

    def setSelected(self, value):
        """ select button according to the value """
        for button in self.viewLayout.widgets:
            isChecked = button.property(self.configName) == value
            button.setChecked(isChecked)
            if isChecked:
                self.choiceLabel.setText(button.text())
                self.choiceLabel.adjustSize()
