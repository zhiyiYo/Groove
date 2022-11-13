# coding:utf-8
from common.config import config
from common.os_utils import isGreaterEqualWin10
from common.signal_bus import signalBus
from common.window_effect import WindowEffect
from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt

from .navigation_widget import NavigationWidget


class NavigationMenu(NavigationWidget):
    """ Navigation menu """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__isShowBottomSpacing = False
        self.__ani = QPropertyAnimation(self, b"geometry")
        self.windowEffect = WindowEffect()
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.resize(60, 800)
        self.setWindowFlags(Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setProperty("useAcrylic", isGreaterEqualWin10())
        color = '2B2B2B99' if config.theme == 'dark' else 'F2F2F299'
        self.windowEffect.setAcrylicEffect(self.winId(), color, False)

        self.myMusicButton.setText(self.tr('My music'))
        self.historyButton.setText(self.tr("Recent plays"))
        self.playingButton.setText(self.tr('Now playing'))
        self.playlistButton.setText(self.tr('Playlists'))
        self.settingButton.setText(self.tr('Settings'))

        # connect signal to slot
        signalBus.switchToPlaylistInterfaceSig.connect(self.aniHide)
        self.myMusicButton.clicked.connect(self.aniHide)
        self.settingButton.clicked.connect(self.aniHide)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.scrollArea.resize(self.width(), self.height() - 232)
        self.settingButton.move(
            0, self.height() - 62 - 10 - self.__isShowBottomSpacing * 115)
        self.searchLineEdit.resize(
            self.width() - 30, self.searchLineEdit.height())

    def aniShow(self):
        """ show menu """
        super().show()
        self.activateWindow()
        self.searchLineEdit.show()
        self.__ani.setStartValue(QRect(self.x(), self.y(), 60, self.height()))
        self.__ani.setEndValue(QRect(self.x(), self.y(), 400, self.height()))
        self.__ani.setEasingCurve(QEasingCurve.InOutQuad)
        self.__ani.setDuration(85)
        self.__ani.start()

    def aniHide(self):
        """ hide menu """
        self.__ani.setStartValue(QRect(self.x(), self.y(), 400, self.height()))
        self.__ani.setEndValue(QRect(self.x(), self.y(), 60, self.height()))
        self.__ani.finished.connect(self.__hideAniFinishedSlot)
        self.__ani.setDuration(85)
        self.searchLineEdit.hide()
        self.__ani.start()

    def __hideAniFinishedSlot(self):
        """ hide animation finished slot """
        super().hide()
        self.resize(60, self.height())
        self.__ani.disconnect()

    def setBottomSpacingVisible(self, isBottomSpacingVisible: bool):
        self.__isShowBottomSpacing = isBottomSpacingVisible

    def _onSearchButtonClicked(self):
        """ search button clicked slot """
        text = self.searchLineEdit.text()
        if text:
            self.aniHide()
            self.currentButton.setSelected(False)
            self.searchSig.emit(text)

    @property
    def isShowBottomSpacing(self):
        return self.__isShowBottomSpacing
