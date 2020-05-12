self.scrollBar.valueChanged.connect(
            lambda: self.myMusicWindows.songTag.songCardListWidget.
            verticalScrollBar().setValue(self.scrollBar.value()))

        self.myMusicWindows.songTag.songCardListWidget.verticalScrollBar().valueChanged.connect(
            lambda: self.scrollBar.setValue(self.myMusicWindows.
            songTag.songCardListWidget.verticalScrollBar().value()))