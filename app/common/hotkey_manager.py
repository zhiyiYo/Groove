# coding:utf-8
from PyQt5.QtCore import QAbstractEventDispatcher, QAbstractNativeEventFilter
from pyqtkeybind import keybinder

from .singleton import Singleton


class WinEventFilter(QAbstractNativeEventFilter):

    def nativeEventFilter(self, eventType, message):
        ret = keybinder.handler(eventType, message)
        return ret, 0


class HotkeyManager(Singleton):
    """ Global hotkey manager """

    windows = {}

    def __init__(self):
        keybinder.init()
        self.eventFilter = WinEventFilter()
        self.dispatcher = QAbstractEventDispatcher.instance()
        self.dispatcher.installNativeEventFilter(self.eventFilter)

    def register(self, winId, hotkey, callback):
        """ register hotkey """
        if winId not in self.windows:
            self.windows[winId] = {}

        if not keybinder.register_hotkey(winId, hotkey, callback):
            return False

        self.windows[winId][hotkey] = callback
        return True

    def unregister(self, winId, hotkey):
        """ register hotkey """
        if winId not in self.windows or hotkey not in self.windows[winId]:
            return

        if not keybinder.unregister_hotkey(winId, hotkey):
            return False

        self.windows[winId].pop(hotkey)
        return True

    def clear(self, winId):
        """ clear hotkeys of window """
        if winId not in self.windows:
            return

        for hotkey in self.windows[winId]:
            keybinder.unregister_hotkey(winId, hotkey)

        self.windows.pop(winId)