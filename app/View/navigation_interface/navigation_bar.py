# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout

from .navigation_widget_base import NavigationWidgetBase
from .navigation_button import CreatePlaylistButton, ToolButton


class NavigationBar(NavigationWidgetBase):
    """ Navigation bar """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__createButtons()
        self.v_layout = QVBoxLayout()
        self.__initWidget()

    def __createButtons(self):
        """create buttons """
        self.showMenuButton = ToolButton(
            ':/images/navigation_interface/GlobalNavButton.png', parent=self)
        self.searchButton = ToolButton(
            ':/images/navigation_interface/Search.png', (60, 62), self)
        self.myMusicButton = ToolButton(
            ':/images/navigation_interface/MusicInCollection.png', (60, 62), self)
        self.historyButton = ToolButton(
            ':/images/navigation_interface/Recent.png', (60, 62), self)
        self.playingButton = ToolButton(
            ':/images/navigation_interface/Playing.png', (60, 62), self)
        self.playlistButton = ToolButton(
            ':/images/navigation_interface/Playlist.png', parent=self)
        self.createPlaylistButton = CreatePlaylistButton(self)
        self.settingButton = ToolButton(
            ':/images/navigation_interface/Settings.png', parent=self)

        # selected button
        self.currentButton = self.myMusicButton

        self.button_list = [
            self.showMenuButton, self.searchButton, self.myMusicButton,
            self.historyButton, self.playingButton, self.playlistButton,
            self.createPlaylistButton, self.settingButton
        ]

        self._selectableButtons = self.button_list[2:6] + [
            self.settingButton]

        self._selectableButtonNames = [
            'myMusicButton', 'historyButton', 'playingButton',
            'playlistButton', 'settingButton'
        ]

    def __initWidget(self):
        """ initialize widgets """
        self.setFixedWidth(60)
        self.setSelectedButton(self.myMusicButton.property('name'))
        self._connectButtonClickedSigToSlot()
        self.__initLayout()
        self.showMenuButton.setToolTip(self.tr('Maximize navigation pane'))
        self.myMusicButton.setToolTip(self.tr('My music'))
        self.historyButton.setToolTip(self.tr('Recently played'))
        self.playingButton.setToolTip(self.tr('Now playing'))
        self.playlistButton.setToolTip(self.tr('Playlist'))
        self.settingButton.setToolTip(self.tr('Settings'))
        self.searchButton.setToolTip(self.tr('Search'))

    def __initLayout(self):
        """ initialize layout """
        self.v_layout.addSpacing(40)
        self.v_layout.setSpacing(0)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        for button in self.button_list[:-1]:
            self.v_layout.addWidget(button)

        self.v_layout.addWidget(self.settingButton, 0, Qt.AlignBottom)

        self.v_layout.addSpacing(127)
        self.setLayout(self.v_layout)
