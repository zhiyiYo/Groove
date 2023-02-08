# coding:utf-8
from common.config import config, HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR
from common.url import openUrl
from common.signal_bus import signalBus
from common.style_sheet import setStyleSheet
from common.thread.crawl_meta_data_thread import CrawlFolderMetaDataThread
from components.layout.expand_layout import ExpandLayout
from components.widgets.scroll_area import SmoothScrollArea
from components.widgets.tool_tip import ToastToolTip, StateToolTip
from components.settings import (SettingCardGroup, SwitchSettingCard, FolderListSettingCard,
                                 OptionsSettingCard, RangeSettingCard, PushSettingCard,
                                 ColorSettingCard, HyperlinkCard, PrimaryPushSettingCard)
from components.settings import SettingIconFactory as SIF
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QFontDialog, QFileDialog


class SettingInterface(SmoothScrollArea):
    """ Setting interface """

    checkUpdateSig = pyqtSignal()
    crawlMetaDataFinished = pyqtSignal()
    musicFoldersChanged = pyqtSignal(list)
    acrylicEnableChanged = pyqtSignal(bool)
    downloadFolderChanged = pyqtSignal(str)
    minimizeToTrayChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.settingLabel = QLabel(self.tr("Settings"), self)

        # music folders
        self.musicInThisPCGroup = SettingCardGroup(
            self.tr("Music on this PC"), self.scrollWidget)
        self.musicFolderCard = FolderListSettingCard(
            config.musicFolders,
            self.tr("Local music library"),
            parent=self.musicInThisPCGroup
        )
        self.downloadFolderCard = PushSettingCard(
            self.tr('Choose folder'),
            SIF.path(SIF.DOWNLOAD),
            self.tr("Download Directory"),
            config.get(config.downloadFolder),
            self.musicInThisPCGroup
        )

        # personalization
        self.personalGroup = SettingCardGroup(
            self.tr('Personalization'), self.scrollWidget)
        self.enableAcrylicCard = SwitchSettingCard(
            SIF.path(SIF.TRANSPARENT),
            self.tr("Use Acrylic effect"),
            self.tr(
                "Acrylic effect has better visual experience, but it may cause the window to become stuck"),
            configItem=config.enableAcrylicBackground,
            parent=self.personalGroup
        )
        self.themeCard = OptionsSettingCard(
            config.themeMode,
            SIF.path(SIF.BRUSH),
            self.tr('Application theme'),
            self.tr('Choose a color theme to personalize Groove Music'),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self.personalGroup
        )
        self.zoomCard = OptionsSettingCard(
            config.dpiScale,
            SIF.path(SIF.ZOOM),
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("Use system setting")
            ],
            parent=self.personalGroup
        )
        self.languageCard=OptionsSettingCard(
            config.language,
            SIF.path(SIF.LANGUAGE),
            self.tr('Language'),
            self.tr('Set your preferred language for UI'),
            texts=['简体中文', '繁體中文', 'English', self.tr('Use system setting')],
            parent=self.personalGroup
        )

        # media info
        self.mediaInfoGroup = SettingCardGroup(
            self.tr('Media Info'), self.scrollWidget)
        self.crawlMetadataCard = SwitchSettingCard(
            SIF.path(SIF.WEB),
            self.tr(
                "Automatically retrieve and update missing album art and metadata"),
            parent=self.mediaInfoGroup
        )

        # online music
        self.onlineMusicGroup = SettingCardGroup(
            self.tr('Online Music'), self.scrollWidget)
        self.onlinePageSizeCard = RangeSettingCard(
            config.onlinePageSize,
            SIF.path(SIF.SEARCH),
            self.tr("Number of online music displayed on each page"),
            parent=self.onlineMusicGroup
        )
        self.onlineMusicQualityCard = OptionsSettingCard(
            config.onlineSongQuality,
            SIF.path(SIF.MUSIC),
            self.tr('Online music quality'),
            texts=[
                self.tr('Standard quality'), self.tr('High quality'),
                self.tr('Super quality'), self.tr('Lossless quality')
            ],
            parent=self.onlineMusicGroup
        )
        self.onlineMvQualityCard = OptionsSettingCard(
            config.onlineMvQuality,
            SIF.path(SIF.VIDEO),
            self.tr('Online MV quality'),
            texts=[
                self.tr('Full HD'), self.tr('HD'),
                self.tr('SD'), self.tr('LD')
            ],
            parent=self.onlineMusicGroup
        )

        # playing interface
        self.playingInterfaceGroup = SettingCardGroup(
            self.tr('Playing Interface'), self.scrollWidget)
        self.albumBlurRadiusCard = RangeSettingCard(
            config.albumBlurRadius,
            SIF.path(SIF.ALBUM),
            self.tr('Background blur radius'),
            self.tr('The greater the radius, the more blurred the image'),
            parent=self.playingInterfaceGroup
        )
        self.lyricFontCard = PushSettingCard(
            self.tr('Choose font'),
            SIF.path(SIF.FONT),
            self.tr('Lyric font'),
            self.tr(
                'The lyrics being played will be larger than the lyrics not being played'),
            parent=self.playingInterfaceGroup
        )

        # desktop lyric
        self.deskLyricGroup = SettingCardGroup(
            self.tr('Desktop Lyric'), self.scrollWidget)
        self.deskLyricFontCard = PushSettingCard(
            self.tr('Choose font'),
            SIF.path(SIF.FONT),
            self.tr('Font'),
            parent=self.deskLyricGroup
        )
        self.deskLyricBackgroundColorCard = ColorSettingCard(
            config.deskLyricFontColor,
            SIF.path(SIF.PAINT_BUCKET),
            self.tr('Background color'),
            parent=self.deskLyricGroup
        )
        self.deskLyricHighlightColorCard = ColorSettingCard(
            config.deskLyricHighlightColor,
            SIF.path(SIF.PALETTE),
            self.tr('Foreground color'),
            parent=self.deskLyricGroup
        )
        self.deskLyricStrokeColorCard = ColorSettingCard(
            config.deskLyricStrokeColor,
            SIF.path(SIF.PENCIL_INK),
            self.tr('Stroke color'),
            parent=self.deskLyricGroup
        )
        self.deskLyricStrokeSizeCard = RangeSettingCard(
            config.deskLyricStrokeSize,
            SIF.path(SIF.FLUORESCENT_PEN),
            self.tr('Stroke size'),
            parent=self.deskLyricGroup
        )
        self.deskLyricAlignmentCard = OptionsSettingCard(
            config.deskLyricAlignment,
            SIF.path(SIF.ALIGNMENT),
            self.tr('Alignment'),
            texts=[
                self.tr('Center aligned'), self.tr('Left aligned'),
                self.tr('Right aligned')
            ],
            parent=self.deskLyricGroup
        )

        # embedded lyric
        self.embedLyricGroup = SettingCardGroup(
            self.tr('Embedded Lyrics'), self.scrollWidget)
        self.preferEmbedLyricCard = SwitchSettingCard(
            SIF.path(SIF.FILE_SEARCH),
            self.tr('Prefer embedded lyrics'),
            self.tr(
                'Embedded lyrics will be used preferentially instead of online lyrics'),
            config.preferEmbedLyric,
            self.embedLyricGroup
        )
        self.embedLyricWhenSaveCard = SwitchSettingCard(
            SIF.path(SIF.EMBED),
            self.tr('Embed lyrics when saving song information'),
            configItem=config.embedLyricWhenSave,
            parent=self.embedLyricGroup
        )

        # main panel
        self.mainPanelGroup = SettingCardGroup(
            self.tr('Main Panel'), self.scrollWidget)
        self.minimizeToTrayCard = SwitchSettingCard(
            SIF.path(SIF.MINIMIZE),
            self.tr('Minimize to tray after closing'),
            self.tr('Groove Music will continue to run in the background'),
            configItem=config.minimizeToTray,
            parent=self.mainPanelGroup
        )

        # update software
        self.updateSoftwareGroup = SettingCardGroup(
            self.tr("Software update"), self.scrollWidget)
        self.updateOnStartUpCard = SwitchSettingCard(
            SIF.path(SIF.UPDATE),
            self.tr('Check for updates when the application starts'),
            self.tr(
                'The new version will be more stable and have more features'),
            configItem=config.checkUpdateAtStartUp,
            parent=self.updateSoftwareGroup
        )

        # application
        self.aboutGroup = SettingCardGroup(self.tr('About'), self.scrollWidget)
        self.helpCard = HyperlinkCard(
            HELP_URL,
            self.tr('Open help page'),
            SIF.path(SIF.HELP),
            self.tr('Help'),
            self.tr('Discover new features and learn useful tips about Groove Music'),
            self.aboutGroup
        )
        self.feedbackCard = PrimaryPushSettingCard(
            self.tr('Provide feedback'),
            SIF.path(SIF.FEEDBACK),
            self.tr('Provide feedback'),
            self.tr('Help us improve Groove Music by providing feedback'),
            self.aboutGroup
        )
        self.aboutCard = PrimaryPushSettingCard(
            self.tr('Check update'),
            SIF.path(SIF.INFO),
            self.tr('About Groove Music'),
            '© ' + self.tr('Copyright') + f" {YEAR}, {AUTHOR}. " +
            self.tr('Version') + f" {VERSION[1:]}",
            self.aboutGroup
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 133)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        setStyleSheet(self, 'setting_interface')

        # initialize layout
        self.__initLayout()
        self.__updateMetaDataCardEnabled()

        self.__connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(30, 63)

        # add cards to group
        self.musicInThisPCGroup.addSettingCard(self.musicFolderCard)
        self.musicInThisPCGroup.addSettingCard(self.downloadFolderCard)

        self.personalGroup.addSettingCard(self.enableAcrylicCard)
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.mediaInfoGroup.addSettingCard(self.crawlMetadataCard)

        self.onlineMusicGroup.addSettingCard(self.onlinePageSizeCard)
        self.onlineMusicGroup.addSettingCard(self.onlineMusicQualityCard)
        self.onlineMusicGroup.addSettingCard(self.onlineMvQualityCard)

        self.playingInterfaceGroup.addSettingCard(self.albumBlurRadiusCard)
        self.playingInterfaceGroup.addSettingCard(self.lyricFontCard)

        self.deskLyricGroup.addSettingCard(self.deskLyricFontCard)
        self.deskLyricGroup.addSettingCard(self.deskLyricBackgroundColorCard)
        self.deskLyricGroup.addSettingCard(self.deskLyricHighlightColorCard)
        self.deskLyricGroup.addSettingCard(self.deskLyricStrokeColorCard)
        self.deskLyricGroup.addSettingCard(self.deskLyricStrokeSizeCard)
        self.deskLyricGroup.addSettingCard(self.deskLyricAlignmentCard)

        self.embedLyricGroup.addSettingCard(self.preferEmbedLyricCard)
        self.embedLyricGroup.addSettingCard(self.embedLyricWhenSaveCard)

        self.updateSoftwareGroup.addSettingCard(self.updateOnStartUpCard)

        self.mainPanelGroup.addSettingCard(self.minimizeToTrayCard)

        self.aboutGroup.addSettingCard(self.helpCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(32, 5, 32, 30)
        self.expandLayout.addWidget(self.musicInThisPCGroup)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.mediaInfoGroup)
        self.expandLayout.addWidget(self.onlineMusicGroup)
        self.expandLayout.addWidget(self.playingInterfaceGroup)
        self.expandLayout.addWidget(self.deskLyricGroup)
        self.expandLayout.addWidget(self.embedLyricGroup)
        self.expandLayout.addWidget(self.mainPanelGroup)
        self.expandLayout.addWidget(self.updateSoftwareGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __updateMetaDataCardEnabled(self):
        """ set the enabled state of meta data switch button """
        self.crawlMetadataCard.switchButton.setEnabled(
            bool(config.get(config.musicFolders)))

    def __showRestartTooltip(self):
        """ show restart tooltip """
        w = ToastToolTip(
            self.tr('Configuration updated successfully'),
            self.tr('Configuration takes effect after restart'),
            'info',
            self.window()
        )
        w.show()

    def __onLyricFontCardClicked(self):
        """ playing interface lyric font button clicked slot """
        font, isOk = QFontDialog.getFont(
            config.lyricFont, self.window(), self.tr("Choose Font"))
        if isOk:
            config.lyricFont = font
            signalBus.lyricFontChanged.emit(font)

    def __onDeskLyricFontCardClicked(self):
        """ desktop lyric font button clicked slot """
        font, isOk = QFontDialog.getFont(
            config.desktopLyricFont, self.window(), self.tr("Choose Font"))
        if isOk:
            config.desktopLyricFont = font

    def __onMusicFoldersChanged(self, folders: list):
        """ music folders changed slot """
        self.__updateMetaDataCardEnabled()
        self.musicFoldersChanged.emit(folders)

    def __onDownloadFolderCardClicked(self):
        """ download folder card clicked slot """
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), "./")
        if not folder or config.get(config.downloadFolder) == folder:
            return

        config.set(config.downloadFolder, folder)
        self.downloadFolderCard.setContent(folder)

    def __onMetaDataCardCheckedChanged(self):
        """ crawl metadata card checked state changed slot """
        if self.crawlMetadataCard.isChecked():
            self.crawlMetadataCard.switchButton.setEnabled(False)
            self.__crawlMetaData()
        else:
            self.crawlMetadataCard.switchButton.setEnabled(True)

    def __crawlMetaData(self):
        """ crawl song meta data """
        crawler = CrawlFolderMetaDataThread(
            config.get(config.musicFolders), self)

        stateToolTip = StateToolTip(
            self.tr("Crawling metadata"), self.tr("Current progress: ")+f"{0:>3.0%}", self.window())
        stateToolTip.show()

        # connect signal to slot
        crawler.finished.connect(lambda: stateToolTip.setState(True))
        crawler.finished.connect(self.__onCrawlFinished)
        crawler.crawlSignal.connect(stateToolTip.setContent)
        stateToolTip.closedSignal.connect(crawler.stop)

        crawler.start()

    def __onCrawlFinished(self):
        """ crawl finished slot """
        self.sender().quit()
        self.sender().wait()
        self.sender().deleteLater()
        self.crawlMetadataCard.switchButton.setEnabled(True)
        self.crawlMetadataCard.setChecked(False)
        self.crawlMetaDataFinished.emit()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        signalBus.appRestartSig.connect(self.__showRestartTooltip)

        # music in the pc
        self.musicFolderCard.folderChanged.connect(
            self.__onMusicFoldersChanged)
        self.downloadFolderCard.clicked.connect(
            self.__onDownloadFolderCardClicked)

        # personalization
        self.enableAcrylicCard.checkedChanged.connect(
            self.acrylicEnableChanged)

        # media info
        self.crawlMetadataCard.checkedChanged.connect(
            self.__onMetaDataCardCheckedChanged)

        # playing interface
        self.lyricFontCard.clicked.connect(self.__onLyricFontCardClicked)
        self.albumBlurRadiusCard.valueChanged.connect(
            signalBus.albumBlurRadiusChanged)

        # desktop lyric
        self.deskLyricFontCard.clicked.connect(
            self.__onDeskLyricFontCardClicked)
        self.deskLyricBackgroundColorCard.colorChanged.connect(
            lambda i: signalBus.desktopLyricStyleChanged.emit())
        self.deskLyricHighlightColorCard.colorChanged.connect(
            lambda i: signalBus.desktopLyricStyleChanged.emit())
        self.deskLyricStrokeColorCard.colorChanged.connect(
            lambda i: signalBus.desktopLyricStyleChanged.emit())
        self.deskLyricStrokeSizeCard.valueChanged.connect(
            lambda i: signalBus.desktopLyricStyleChanged.emit())
        self.deskLyricAlignmentCard.optionChanged.connect(
            lambda i: signalBus.desktopLyricStyleChanged.emit())

        # main panel
        self.minimizeToTrayCard.checkedChanged.connect(
            self.minimizeToTrayChanged)

        # about
        self.feedbackCard.clicked.connect(lambda: openUrl(FEEDBACK_URL))
        self.aboutCard.clicked.connect(self.checkUpdateSig)
