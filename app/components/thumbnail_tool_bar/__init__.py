import sys


class UnixThumbnailToolBar:

    def __init__(self, parent=None):
        pass

    def setWindow(self, window):
        pass

    def setButtonsEnabled(self, isEnbled: bool):
        """ set button enabled """
        pass

    def setPlay(self, isPlay: bool):
        """ set play state """
        pass


if sys.platform == "win32":
    from .thumbnail_tool_bar import WindowsThumbnailToolBar as ThumbnailToolBar
else:
    ThumbnailToolBar = UnixThumbnailToolBar
