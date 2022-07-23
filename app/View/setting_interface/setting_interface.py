# coding:utf-8
import sys
from typing import List

from common.config import config
from common.signal_bus import signalBus
from common.style_sheet import setStyleSheet
from common.thread.get_meta_data_thread import GetFolderMetaDataThread
from components.buttons.switch_button import SwitchButton
from components.dialog_box.folder_list_dialog import FolderListDialog
from components.widgets.label import ClickableLabel
from components.widgets.scroll_area import ScrollArea
from components.widgets.slider import Slider
from components.widgets.tooltip import StateTooltip, ToastTooltip
from components.widgets.color_picker import ColorPicker
from PyQt5.QtCore import QEvent, Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QDesktopServices, QColor
from PyQt5.QtWidgets import (QButtonGroup, QFileDialog, QLabel, QLineEdit,
                             QPushButton, QRadioButton, QWidget, QFontDialog)


class SettingInterface(ScrollArea):
    """ Setting interface """

    crawlFinished = pyqtSignal()
    acrylicEnableChanged = pyqtSignal(bool)
    downloadFolderChanged = pyqtSignal(str)
    minimizeToTrayChanged = pyqtSignal(bool)
    selectedMusicFoldersChanged = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = config

        self.scrollwidget = QWidget()

        # setting label
        self.settingLabel = QLabel(self.tr("Settings"), self)

        # select music folders
        self.musicInThisPCLabel = QLabel(
            self.tr("Music on this PC"), self.scrollwidget)
        self.selectMusicFolderLabel = ClickableLabel(
            self.tr("Choose where we look for music"), self.scrollwidget)

        # acrylic background
        self.acrylicLabel = QLabel(
            self.tr("Acrylic Background"), self.scrollwidget)
        self.acrylicHintLabel = QLabel(
            self.tr("Use the acrylic background effect"), self.scrollwidget)
        self.acrylicSwitchButton = SwitchButton(
            self.tr("Off"), self.scrollwidget)

        # media info
        self.mediaInfoLabel = QLabel(self.tr("Media Info"), self.scrollwidget)
        self.getMetaDataLabel = QLabel(self.tr(
            "Automatically retrieve and update missing album art and metadata"), self.scrollwidget)
        self.getMetaDataSwitchButton = SwitchButton(
            self.tr("Off"), self.scrollwidget)

        # search
        self.searchLabel = QLabel(self.tr('Search'), self.scrollwidget)
        self.pageSizeSlider = Slider(Qt.Horizontal, self.scrollwidget)
        self.pageSizeValueLabel = QLabel(self.scrollwidget)
        self.pageSizeHintLabel = QLabel(
            self.tr('Set the number of online music displayed'), self.scrollwidget)

        # online music quality
        self.onlinePlayQualityGroup = QButtonGroup(self)
        self.onlinePlayQualityLabel = QLabel(
            self.tr('Online Playing Quality'), self.scrollwidget)
        self.standardQualityButton = QRadioButton(
            self.tr('Standard quality'), self.scrollwidget)
        self.highQualityButton = QRadioButton(
            self.tr('High quality'), self.scrollwidget)
        self.superQualityButton = QRadioButton(
            self.tr('Super quality'), self.scrollwidget)

        # MV quality
        self.mvQualityGroup = QButtonGroup(self)
        self.mvQualityLabel = QLabel(self.tr('MV Quality'), self.scrollwidget)
        self.fullHDButton = QRadioButton(self.tr('Full HD'), self.scrollwidget)
        self.hDButton = QRadioButton(self.tr('HD'), self.scrollwidget)
        self.sDButton = QRadioButton(self.tr('SD'), self.scrollwidget)
        self.lDButton = QRadioButton(self.tr('LD'), self.scrollwidget)

        # close main window
        self.closeWindowGroup = QButtonGroup(self)
        self.closeWindowLabel = QLabel(
            self.tr('Close Main Window'), self.scrollwidget)
        self.minimizeToTrayButton = QRadioButton(
            self.tr('Minimize to system tray'), self.scrollwidget)
        self.quitGrooveMusicButton = QRadioButton(
            self.tr('Quit Groove Music'), self.scrollwidget)

        # theme mode
        self.modeGroup = QButtonGroup(self)
        self.modeLabel = QLabel(self.tr('Mode'), self.scrollwidget)
        self.lightModeButton = QRadioButton(
            self.tr('Light'), self.scrollwidget)
        self.darkModeButton = QRadioButton(self.tr('Dark'), self.scrollwidget)
        self.autoModeButton = QRadioButton(
            self.tr('Use system setting'), self.scrollwidget)

        # desktop lyric
        self.desktopLyricLabel = QLabel(
            self.tr("Desktop Lyric"), self.scrollwidget)
        self.lyricStyleLabel = QLabel(self.tr("Style"), self.scrollwidget)
        self.lyricFontLabel = QLabel(self.tr("Font"), self.scrollwidget)
        self.lyricAlignLabel = QLabel(
            self.tr("Alignment"), self.scrollwidget)
        self.lyricFontColorLabel = QLabel(
            self.tr("Font color"), self.scrollwidget)
        self.lyricHighlightLabel = QLabel(
            self.tr("Highlight color"), self.scrollwidget)
        self.lyricStrokeColorLabel = QLabel(
            self.tr("Stroke color"), self.scrollwidget)
        self.lyricStrokeSizeLabel = QLabel(
            self.tr("Stroke size"), self.scrollwidget)
        self.lyricFontColorPicker = ColorPicker(
            config["lyric.font-color"], self.scrollwidget)
        self.lyricHighlightColorPicker = ColorPicker(
            config["lyric.highlight-color"], self.scrollwidget)
        self.lyricStrokeColorPicker = ColorPicker(
            config["lyric.stroke-color"], self.scrollwidget)
        self.lyricAlignGroup = QButtonGroup(self)
        self.lyricCenterAlignButton = QRadioButton(
            self.tr("Center aligned"), self.scrollwidget)
        self.lyricLeftAlignButton = QRadioButton(
            self.tr("Left aligned"), self.scrollwidget)
        self.lyricRightAlignButton = QRadioButton(
            self.tr("Right aligned"), self.scrollwidget)
        self.lyricStrokeSizeSlider = Slider(Qt.Horizontal, self.scrollwidget)
        self.lyricStrokeSizeValueLabel = QLabel(self.scrollwidget)
        self.lyricFontButton = QPushButton(
            self.tr("Choose font"), self.scrollwidget)

        # download folder
        self.downloadFolderHintLabel = QLabel('')
        self.downloadFolderButton = QPushButton(
            self.tr("Choose"), self.scrollwidget)
        self.downloadFolderLineEdit = QLineEdit(
            self.config['download-folder'], self.scrollwidget)
        self.downloadFolderLabel = QLabel(
            self.tr("Download Directory"), self.scrollwidget)

        # application
        self.appLabel = QLabel(self.tr("App"), self.scrollwidget)
        self.helpLabel = ClickableLabel(self.tr("Help"), self.scrollwidget)
        self.issueLabel = ClickableLabel(
            self.tr("Feedback"), self.scrollwidget)

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.resize(1000, 800)
        self.downloadFolderLineEdit.resize(313, 42)
        self.downloadFolderLineEdit.setReadOnly(True)
        self.downloadFolderLineEdit.setCursorPosition(0)
        self.scrollwidget.resize(self.width(), 2100)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 0)
        self.setWidget(self.scrollwidget)

        # set the checked state of acrylic switch button
        enableAcrylic = self.config["enable-acrylic-background"]
        self.acrylicSwitchButton.setChecked(enableAcrylic)
        self.acrylicSwitchButton.setText(
            self.tr('On') if enableAcrylic else self.tr('Off'))
        self.acrylicSwitchButton.setEnabled(sys.platform == "win32")

        # set cursor
        self.selectMusicFolderLabel.setCursor(Qt.PointingHandCursor)
        self.helpLabel.setCursor(Qt.PointingHandCursor)
        self.issueLabel.setCursor(Qt.PointingHandCursor)

        # set online play quality
        self.onlinePlayQualityGroup.addButton(self.standardQualityButton)
        self.onlinePlayQualityGroup.addButton(self.highQualityButton)
        self.onlinePlayQualityGroup.addButton(self.superQualityButton)
        self.standardQualityButton.setProperty('quality', 'Standard quality')
        self.highQualityButton.setProperty('quality', 'High quality')
        self.superQualityButton.setProperty('quality', 'Super quality')
        self.__setCheckedRadioButton(
            "quality", config["online-play-quality"], self.onlinePlayQualityGroup.buttons())

        # set MV quality
        self.mvQualityGroup.addButton(self.fullHDButton)
        self.mvQualityGroup.addButton(self.hDButton)
        self.mvQualityGroup.addButton(self.sDButton)
        self.mvQualityGroup.addButton(self.lDButton)
        self.fullHDButton.setProperty('quality', 'Full HD')
        self.hDButton.setProperty('quality', 'HD')
        self.sDButton.setProperty('quality', 'SD')
        self.lDButton.setProperty('quality', 'LD')
        self.__setCheckedRadioButton(
            "quality", config["mv-quality"], self.mvQualityGroup.buttons())

        # set the action when closing main window
        self.closeWindowGroup.addButton(self.minimizeToTrayButton)
        self.closeWindowGroup.addButton(self.quitGrooveMusicButton)
        self.minimizeToTrayButton.setProperty('minimize-to-tray', True)
        self.quitGrooveMusicButton.setProperty('minimize-to-tray', False)
        self.__setCheckedRadioButton(
            "minimize-to-tray", config["minimize-to-tray"], self.closeWindowGroup.buttons())

        # set theme mode
        self.modeGroup.addButton(self.lightModeButton)
        self.modeGroup.addButton(self.darkModeButton)
        self.modeGroup.addButton(self.autoModeButton)
        self.lightModeButton.setProperty('mode', "Light")
        self.darkModeButton.setProperty('mode', "Dark")
        self.autoModeButton.setProperty('mode', "Auto")
        self.__setCheckedRadioButton(
            "mode", config["mode"], self.modeGroup.buttons())

        # set slider
        pageSize = self.config['online-music-page-size']
        self.pageSizeSlider.setRange(1, 30)
        self.pageSizeSlider.setValue(pageSize)
        self.pageSizeSlider.setSingleStep(1)
        self.pageSizeValueLabel.setNum(pageSize)

        # set desktop lyric
        self.lyricStrokeSizeSlider.setRange(0, 10)
        self.lyricStrokeSizeSlider.setSingleStep(1)
        self.lyricStrokeSizeSlider.setValue(config["lyric.stroke-size"])
        self.lyricStrokeSizeValueLabel.setNum(config["lyric.stroke-size"])
        self.lyricAlignGroup.addButton(self.lyricCenterAlignButton)
        self.lyricAlignGroup.addButton(self.lyricLeftAlignButton)
        self.lyricAlignGroup.addButton(self.lyricRightAlignButton)
        self.lyricCenterAlignButton.setProperty("align", "Center")
        self.lyricLeftAlignButton.setProperty("align", "Left")
        self.lyricRightAlignButton.setProperty("align", "Right")
        self.__setCheckedRadioButton(
            "align", config["lyric.alignment"], self.lyricAlignGroup.buttons())

        self.__updateMetaDataSwitchButtonEnabled()

        # set hyper link
        self.helpLabel.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://github.com/zhiyiYo/Groove#readme')))
        self.issueLabel.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://github.com/zhiyiYo/Groove/issues')))

        self.downloadFolderLineEdit.installEventFilter(self)

        self.__initLayout()
        self.__setQss()
        self.__connectSignalToSlot()

    def __initLayout(self):
        """ initialize layout """
        self.settingLabel.move(30, 63)
        # select music folders
        self.musicInThisPCLabel.move(30, 18)
        self.selectMusicFolderLabel.move(30, 64)

        # acrylic background
        self.acrylicLabel.move(30, 125)
        self.acrylicHintLabel.move(30, 168)
        self.acrylicSwitchButton.move(30, 200)

        # media info
        self.mediaInfoLabel.move(30, 262)
        self.getMetaDataLabel.move(30, 312)
        self.getMetaDataSwitchButton.move(30, 344)

        # search
        self.searchLabel.move(30, 406)
        self.pageSizeHintLabel.move(30, 456)
        self.pageSizeSlider.move(30, 486)
        self.pageSizeValueLabel.move(230, 486)

        # online music quality
        self.onlinePlayQualityLabel.move(30, 548)
        self.standardQualityButton.move(30, 598)
        self.highQualityButton.move(30, 638)
        self.superQualityButton.move(30, 678)

        # MV quality
        self.mvQualityLabel.move(30, 740)
        self.fullHDButton.move(30, 790)
        self.hDButton.move(30, 830)
        self.sDButton.move(30, 870)
        self.lDButton.move(30, 910)

        # close main window
        self.closeWindowLabel.move(30, 972)
        self.minimizeToTrayButton.move(30, 1022)
        self.quitGrooveMusicButton.move(30, 1062)

        # theme mode
        self.modeLabel.move(30, 1124)
        self.lightModeButton.move(30, 1174)
        self.darkModeButton.move(30, 1214)
        self.autoModeButton.move(30, 1254)

        # desktop lyric
        self.desktopLyricLabel.move(30, 1314)
        self.lyricStyleLabel.move(30, 1364)
        self.lyricFontLabel.move(30, 1414)
        self.lyricFontButton.move(230, 1414)
        self.lyricFontColorLabel.move(30, 1464)
        self.lyricFontColorPicker.move(230, 1464)
        self.lyricHighlightLabel.move(30, 1514)
        self.lyricHighlightColorPicker.move(230, 1514)
        self.lyricStrokeColorLabel.move(30, 1564),
        self.lyricStrokeColorPicker.move(230, 1564)
        self.lyricStrokeSizeLabel.move(30, 1614)
        self.lyricStrokeSizeSlider.move(30, 1644)
        self.lyricStrokeSizeValueLabel.move(230, 1644)
        self.lyricAlignLabel.move(30, 1684)
        self.lyricCenterAlignButton.move(30, 1729)
        self.lyricLeftAlignButton.move(30, 1769)
        self.lyricRightAlignButton.move(30, 1809)

        # download folder
        self.downloadFolderLabel.move(30, 1869)
        self.downloadFolderLineEdit.move(30, 1929)
        self.downloadFolderButton.move(350, 1929)

        # application
        self.appLabel.move(self.width() - 400, 18)
        self.helpLabel.move(self.width() - 400, 64)
        self.issueLabel.move(self.width() - 400, 94)

    def __updateMetaDataSwitchButtonEnabled(self):
        """ set the enabled state of meta data switch button """
        if self.config["selected-folders"]:
            self.getMetaDataSwitchButton.setEnabled(True)
        else:
            self.getMetaDataSwitchButton.setEnabled(False)

    def __onGetMetaDataSwitchButtonCheckedChanged(self):
        """ get meta data switch button checked changed slot """
        if self.getMetaDataSwitchButton.isChecked():
            self.getMetaDataSwitchButton.setText(self.tr("On"))
            self.getMetaDataSwitchButton.setEnabled(False)
            self.__crawlMetaData()
        else:
            self.getMetaDataSwitchButton.setEnabled(True)
            self.getMetaDataSwitchButton.setText(self.tr("Off"))

    def __crawlMetaData(self):
        """ crawl song meta data """
        crawler = GetFolderMetaDataThread(
            self.config["selected-folders"], self)

        stateToolTip = StateTooltip(
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
        self.getMetaDataSwitchButton.setEnabled(True)
        self.getMetaDataSwitchButton.setChecked(False)
        self.getMetaDataSwitchButton.setText(self.tr("Off"))
        self.crawlFinished.emit()

    def __setQss(self):
        """ set style sheet """
        self.appLabel.setObjectName("titleLabel")
        self.downloadFolderLabel.setObjectName("titleLabel")
        self.settingLabel.setObjectName("settingLabel")
        self.mediaInfoLabel.setObjectName("titleLabel")
        self.acrylicLabel.setObjectName("titleLabel")
        self.searchLabel.setObjectName('titleLabel')
        self.mvQualityLabel.setObjectName('titleLabel')
        self.onlinePlayQualityLabel.setObjectName('titleLabel')
        self.closeWindowLabel.setObjectName('titleLabel')
        self.helpLabel.setObjectName("clickableLabel")
        self.issueLabel.setObjectName("clickableLabel")
        self.modeLabel.setObjectName("titleLabel")
        self.musicInThisPCLabel.setObjectName("titleLabel")
        self.selectMusicFolderLabel.setObjectName("clickableLabel")
        self.desktopLyricLabel.setObjectName("titleLabel")
        self.lyricAlignLabel.setObjectName("subTitleLabel")
        self.lyricStyleLabel.setObjectName("subTitleLabel")
        setStyleSheet(self, 'setting_interface')

    def resizeEvent(self, e):
        self.appLabel.move(self.width() - 400, self.appLabel.y())
        self.helpLabel.move(self.width() - 400, self.helpLabel.y())
        self.issueLabel.move(self.width() - 400, self.issueLabel.y())
        self.scrollwidget.resize(self.width(), self.scrollwidget.height())
        super().resizeEvent(e)

    def eventFilter(self, obj, e: QEvent):
        if obj is self.downloadFolderLineEdit:
            if e.type() == QEvent.ContextMenu:
                return True
        return super().eventFilter(obj, e)

    def __showSongFolderListDialog(self):
        """ show song folder list dialog box """
        title = self.tr('Build your collection from your local music files')
        content = self.tr("Right now, we're watching these folders:")
        w = FolderListDialog(
            self.config["selected-folders"], title, content, self.window())

        w.folderChanged.connect(self.__updateSelectedFolders)
        w.exec_()

    def __updateSelectedFolders(self, selectedFolders: list):
        """ update selected folders """
        if self.config["selected-folders"] == selectedFolders:
            return

        self.config["selected-folders"] = selectedFolders
        self.__updateMetaDataSwitchButtonEnabled()
        self.selectedMusicFoldersChanged.emit(selectedFolders)

    def __setCheckedRadioButton(self, property: str, value, buttons: List[QRadioButton]):
        """ set checked radio button """
        for button in buttons:
            button.setChecked(button.property(property) == value)

    def __onPageSliderValueChanged(self, value: int):
        """ page slider value changed slot """
        self.pageSizeValueLabel.setNum(value)
        self.pageSizeValueLabel.adjustSize()
        self.config['online-music-page-size'] = value

    def __onOnlinePlayQualityChanged(self, button: QRadioButton):
        """ online play quality changed slot """
        self.config['online-play-quality'] = button.property('quality')

    def __onMvQualityChanged(self, button: QRadioButton):
        """ MV quality changed slot """
        self.config['mv-quality'] = button.property('quality')

    def __onMinimizeToTrayChanged(self, button: QRadioButton):
        """ minimize to tray changed slot """
        minimize = button.property('minimize-to-tray')
        if self.config['minimize-to-tray'] == minimize:
            return

        self.config['minimize-to-tray'] = minimize
        self.minimizeToTrayChanged.emit(minimize)

    def __onThemeModeChanged(self, button: QRadioButton):
        """ theme mode changed slot """
        self.config["mode"] = button.property("mode")
        w = ToastTooltip(
            self.tr('Change mode successful'),
            self.tr('Configuration takes effect after restart'),
            'info',
            self.window()
        )
        w.show()

    def __onDownloadFolderButtonClicked(self):
        """ download folder button clicked slot """
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), "./")
        if not folder or self.config['download-folder'] == folder:
            return

        self.config['download-folder'] = folder
        self.downloadFolderLineEdit.setText(folder)
        self.downloadFolderChanged.emit(folder)

    def __onAcrylicCheckedChanged(self, isChecked: bool):
        """ acrylic switch button checked changed slot """
        self.config["enable-acrylic-background"] = isChecked
        self.acrylicEnableChanged.emit(isChecked)

    def __onLyricFontButtonClicked(self):
        """ desktop lyric font button clicked slot """
        font, isOk = QFontDialog.getFont(
            config.lyricFont, self.window(), self.tr("Select Font"))
        if isOk:
            config.lyricFont = font
            signalBus.lyricFontChanged.emit(font)

    def __onLyricAlignmentChanged(self, button: QRadioButton):
        """ desktop lyric alignment changed slot """
        config["lyric.alignment"] = button.property("align")
        signalBus.lyricAlignmentChanged.emit(button.property("align"))

    def __onLyricFontColorChanged(self, color: QColor):
        """ desktop lyric font color changed slot """
        config["lyric.font-color"] = [color.red(), color.green(), color.blue()]
        signalBus.lyricFontColorChanged.emit(color)

    def __onLyricHighlightColorChanged(self, color: QColor):
        """ desktop lyric highlight color changed slot """
        config["lyric.highlight-color"] = [color.red(), color.green(),
                                           color.blue()]
        signalBus.lyricHighlightColorChanged.emit(color)

    def __onLyricStrokeColorChanged(self, color: QColor):
        """ desktop lyric stroke color changed slot """
        config["lyric.stroke-color"] = [color.red(), color.green(),
                                        color.blue()]
        signalBus.lyricStrokeColorChanged.emit(color)

    def __onLyricStrokeSizeChanged(self, size: int):
        """ desktop lyric stroke size changed slot """
        config["lyric.stroke-size"] = size
        self.lyricStrokeSizeValueLabel.setNum(size)
        self.lyricStrokeSizeValueLabel.adjustSize()
        signalBus.lyricStrokeSizeChanged.emit(size)

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.lyricFontButton.clicked.connect(self.__onLyricFontButtonClicked)
        self.lyricFontColorPicker.colorChanged.connect(
            self.__onLyricFontColorChanged)
        self.lyricHighlightColorPicker.colorChanged.connect(
            self.__onLyricHighlightColorChanged)
        self.lyricStrokeColorPicker.colorChanged.connect(
            self.__onLyricStrokeColorChanged)
        self.lyricStrokeSizeSlider.valueChanged.connect(
            self.__onLyricStrokeSizeChanged)
        self.lyricAlignGroup.buttonClicked.connect(
            self.__onLyricAlignmentChanged)
        self.mvQualityGroup.buttonClicked.connect(self.__onMvQualityChanged)
        self.modeGroup.buttonClicked.connect(self.__onThemeModeChanged)
        self.getMetaDataSwitchButton.checkedChanged.connect(
            self.__onGetMetaDataSwitchButtonCheckedChanged)
        self.selectMusicFolderLabel.clicked.connect(
            self.__showSongFolderListDialog)
        self.pageSizeSlider.valueChanged.connect(
            self.__onPageSliderValueChanged)
        self.downloadFolderButton.clicked.connect(
            self.__onDownloadFolderButtonClicked)
        self.onlinePlayQualityGroup.buttonClicked.connect(
            self.__onOnlinePlayQualityChanged)
        self.closeWindowGroup.buttonClicked.connect(
            self.__onMinimizeToTrayChanged)
        self.acrylicSwitchButton.checkedChanged.connect(
            self.__onAcrylicCheckedChanged)
