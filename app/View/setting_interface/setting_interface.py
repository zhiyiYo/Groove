# coding:utf-8
import sys
from typing import List

from common.config import ConfigItem, config, HELP_URL, FEEDBACK_URL
from common.signal_bus import signalBus
from common.style_sheet import setStyleSheet
from common.os_utils import isGreaterEqualWin10
from common.thread.get_meta_data_thread import GetFolderMetaDataThread
from components.buttons.switch_button import SwitchButton
from components.dialog_box.folder_list_dialog import FolderListDialog
from components.widgets.color_picker import ColorPicker
from components.widgets.label import ClickableLabel
from components.widgets.scroll_area import ScrollArea
from components.widgets.slider import Slider
from components.widgets.tooltip import StateTooltip, ToastTooltip
from PyQt5.QtCore import QEvent, Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QColor, QDesktopServices
from PyQt5.QtWidgets import (QButtonGroup, QCheckBox, QFileDialog, QFontDialog,
                             QLabel, QLineEdit, QPushButton, QRadioButton,
                             QVBoxLayout, QWidget)


class SettingInterface(ScrollArea):
    """ Setting interface """

    crawlFinished = pyqtSignal()
    checkUpdateSig = pyqtSignal()
    acrylicEnableChanged = pyqtSignal(bool)
    downloadFolderChanged = pyqtSignal(str)
    minimizeToTrayChanged = pyqtSignal(bool)
    selectedMusicFoldersChanged = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scrollwidget = QWidget()

        # setting label
        self.settingLabel = QLabel(self.tr("Settings"), self)

        # select music folders
        self.musicInThisPCLabel = QLabel(
            self.tr("Music on this PC"), self.scrollwidget)
        self.selectMusicFolderLabel = ClickableLabel(
            self.tr("Choose where we look for music"), self.scrollwidget)

        # acrylic background
        self.acrylicGroup = SwitchButtonGroup(
            self.tr("Acrylic Background"),
            self.tr("Use the acrylic background effect"),
            config.enableAcrylicBackground,
            self.scrollwidget
        )

        # media info
        self.mediaInfoGroup = SwitchButtonGroup(
            self.tr("Media Info"),
            self.tr(
                "Automatically retrieve and update missing album art and metadata"),
            parent=self.scrollwidget
        )

        # search
        self.searchLabel = QLabel(self.tr('Search'), self.scrollwidget)
        self.pageSizeSlider = Slider(Qt.Horizontal, self.scrollwidget)
        self.pageSizeValueLabel = QLabel(self.scrollwidget)
        self.pageSizeHintLabel = QLabel(
            self.tr('Set the number of online music displayed'), self.scrollwidget)

        # online music quality
        self.onlinePlayQualityGroup = RadioButtonGroup(
            property=config.onlineSongQuality,
            texts=[
                self.tr('Standard quality'), self.tr('High quality'),
                self.tr('Super quality'), self.tr('Lossless quality')
            ],
            title=self.tr('Online Playing Quality'),
            parent=self.scrollwidget
        )

        # MV quality
        self.mvQualityGroup = RadioButtonGroup(
            property=config.onlineMvQuality,
            texts=[
                self.tr('Full HD'), self.tr('HD'),
                self.tr('SD'), self.tr('LD')
            ],
            title=self.tr('MV Quality'),
            parent=self.scrollwidget
        )

        # close main window
        self.closeWindowGroup = RadioButtonGroup(
            property=config.minimizeToTray,
            texts=[
                self.tr('Minimize to system tray'),
                self.tr('Quit Groove Music')
            ],
            title=self.tr('Close Main Window'),
            parent=self.scrollwidget
        )

        # theme mode
        self.modeGroup = RadioButtonGroup(
            property=config.themeMode,
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            title=self.tr('Mode'),
            parent=self.scrollwidget
        )

        # desktop lyric
        self.desktopLyricLabel = QLabel(
            self.tr("Desktop Lyric"), self.scrollwidget)
        self.lyricStyleLabel = QLabel(self.tr("Style"), self.scrollwidget)
        self.lyricFontLabel = QLabel(self.tr("Font"), self.scrollwidget)
        self.lyricFontColorLabel = QLabel(
            self.tr("Font color"), self.scrollwidget)
        self.lyricHighlightLabel = QLabel(
            self.tr("Highlight color"), self.scrollwidget)
        self.lyricStrokeColorLabel = QLabel(
            self.tr("Stroke color"), self.scrollwidget)
        self.lyricStrokeSizeLabel = QLabel(
            self.tr("Stroke size"), self.scrollwidget)
        self.lyricFontColorPicker = ColorPicker(
            config.get(config.deskLyricFontColor), self.scrollwidget)
        self.lyricHighlightColorPicker = ColorPicker(
            config.get(config.deskLyricHighlightColor), self.scrollwidget)
        self.lyricStrokeColorPicker = ColorPicker(
            config.get(config.deskLyricStrokeColor), self.scrollwidget)
        self.lyricAlignGroup = RadioButtonGroup(
            property=config.deskLyricAlignment,
            texts=[
                self.tr('Center aligned'), self.tr('Left aligned'),
                self.tr('Right aligned')
            ],
            title=self.tr('Alignment'),
            titleType="subTitle",
            parent=self.scrollwidget
        )
        self.lyricStrokeSizeSlider = Slider(Qt.Horizontal, self.scrollwidget)
        self.lyricStrokeSizeValueLabel = QLabel(self.scrollwidget)
        self.lyricFontButton = QPushButton(
            self.tr("Choose font"), self.scrollwidget)

        # embedded lyrics
        self.embedLyricLabel = QLabel(
            self.tr("Embedded Lyrics"), self.scrollwidget)
        self.preferEmbedCheckBox = QCheckBox(
            self.tr("Prefer embedded lyrics"), self.scrollwidget)
        self.embedWhenSaveCheckBox = QCheckBox(
            self.tr("Embed lyrics when saving song information"), self.scrollwidget)

        # media info
        self.softwareUpdateGroup = SwitchButtonGroup(
            self.tr("Software update"),
            self.tr("Check for updates when the application starts"),
            config.checkUpdateAtStartUp,
            self.scrollwidget
        )

        # download folder
        self.downloadFolderHintLabel = QLabel('')
        self.downloadFolderButton = QPushButton(
            self.tr("Choose"), self.scrollwidget)
        self.downloadFolderLineEdit = QLineEdit(
            config.get(config.downloadFolder), self.scrollwidget)
        self.downloadFolderLabel = QLabel(
            self.tr("Download Directory"), self.scrollwidget)

        # application
        self.appLabel = QLabel(self.tr("App"), self.scrollwidget)
        self.helpLabel = ClickableLabel(self.tr("Help"), self.scrollwidget)
        self.issueLabel = ClickableLabel(
            self.tr("Feedback"), self.scrollwidget)
        self.checkUpdateLabel = ClickableLabel(
            self.tr("Check update"), self.scrollwidget)

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.resize(1000, 800)
        self.downloadFolderLineEdit.resize(313, 42)
        self.downloadFolderLineEdit.setReadOnly(True)
        self.downloadFolderLineEdit.setCursorPosition(0)
        self.scrollwidget.resize(self.width(), 2460)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 0)
        self.setWidget(self.scrollwidget)

        # set the checked state of acrylic switch button
        self.acrylicGroup.switchButton.setEnabled(isGreaterEqualWin10())

        # set cursor
        self.selectMusicFolderLabel.setCursor(Qt.PointingHandCursor)
        self.helpLabel.setCursor(Qt.PointingHandCursor)
        self.issueLabel.setCursor(Qt.PointingHandCursor)
        self.checkUpdateLabel.setCursor(Qt.PointingHandCursor)

        # set slider
        pageSize = config.onlinePageSize
        self.pageSizeSlider.setRange(*pageSize.range)
        self.pageSizeSlider.setValue(pageSize.value)
        self.pageSizeSlider.setSingleStep(1)
        self.pageSizeValueLabel.setNum(pageSize.value)

        # set desktop lyric
        strokeSize = config.deskLyricStrokeSize
        self.lyricStrokeSizeSlider.setRange(*strokeSize.range)
        self.lyricStrokeSizeSlider.setSingleStep(1)
        self.lyricStrokeSizeSlider.setValue(strokeSize.value)
        self.lyricStrokeSizeValueLabel.setNum(strokeSize.value)

        # set embedded lyrics
        self.preferEmbedCheckBox.setChecked(config.preferEmbedLyric.value)
        self.embedWhenSaveCheckBox.setChecked(config.embedLyricWhenSave.value)

        self.__updateMetaDataSwitchButtonEnabled()

        # set hyper link
        self.helpLabel.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(HELP_URL)))
        self.issueLabel.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(FEEDBACK_URL)))

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
        self.acrylicGroup.move(30, 125)

        # media info
        self.mediaInfoGroup.move(30, 262)

        # search
        self.searchLabel.move(30, 406)
        self.pageSizeHintLabel.move(30, 456)
        self.pageSizeSlider.move(30, 486)
        self.pageSizeValueLabel.move(230, 486)

        # online music quality
        self.onlinePlayQualityGroup.move(30, 548)

        # MV quality
        self.mvQualityGroup.move(30, 780)

        # close main window
        self.closeWindowGroup.move(30, 1012)

        # theme mode
        self.modeGroup.move(30, 1164)

        # desktop lyric
        self.desktopLyricLabel.move(30, 1354)
        self.lyricStyleLabel.move(30, 1404)
        self.lyricFontLabel.move(30, 1454)
        self.lyricFontButton.move(230, 1454)
        self.lyricFontColorLabel.move(30, 1504)
        self.lyricFontColorPicker.move(230, 1504)
        self.lyricHighlightLabel.move(30, 1554)
        self.lyricHighlightColorPicker.move(230, 1554)
        self.lyricStrokeColorLabel.move(30, 1604),
        self.lyricStrokeColorPicker.move(230, 1604)
        self.lyricStrokeSizeLabel.move(30, 1654)
        self.lyricStrokeSizeSlider.move(30, 1684)
        self.lyricStrokeSizeValueLabel.move(230, 1684)
        self.lyricAlignGroup.move(30, 1724)

        # embedded lyrics
        self.embedLyricLabel.move(30, 1917)
        self.preferEmbedCheckBox.move(30, 1967)
        self.embedWhenSaveCheckBox.move(30, 2007)

        # software update
        self.softwareUpdateGroup.move(30, 2069)

        # download folder
        self.downloadFolderLabel.move(30, 2206)
        self.downloadFolderLineEdit.move(30, 2266)
        self.downloadFolderButton.move(350, 2266)

        # application
        self.appLabel.move(self.width() - 400, 18)
        self.helpLabel.move(self.width() - 400, 64)
        self.issueLabel.move(self.width() - 400, 94)
        self.checkUpdateLabel.move(self.width() - 400, 124)

    def __updateMetaDataSwitchButtonEnabled(self):
        """ set the enabled state of meta data switch button """
        self.mediaInfoGroup.switchButton.setEnabled(
            bool(config.get(config.musicFolders)))

    def __onGetMetaDataSwitchButtonCheckedChanged(self):
        """ get meta data switch button checked changed slot """
        if self.mediaInfoGroup.isChecked():
            self.mediaInfoGroup.switchButton.setEnabled(False)
            self.__crawlMetaData()
        else:
            self.mediaInfoGroup.switchButton.setEnabled(True)

    def __crawlMetaData(self):
        """ crawl song meta data """
        crawler = GetFolderMetaDataThread(
            config.get(config.musicFolders), self)

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
        self.mediaInfoGroup.switchButton.setEnabled(True)
        self.mediaInfoGroup.setChecked(False)
        self.crawlFinished.emit()

    def __setQss(self):
        """ set style sheet """
        self.appLabel.setObjectName("titleLabel")
        self.downloadFolderLabel.setObjectName("titleLabel")
        self.settingLabel.setObjectName("settingLabel")
        self.searchLabel.setObjectName('titleLabel')
        self.helpLabel.setObjectName("clickableLabel")
        self.issueLabel.setObjectName("clickableLabel")
        self.checkUpdateLabel.setObjectName("clickableLabel")
        self.musicInThisPCLabel.setObjectName("titleLabel")
        self.selectMusicFolderLabel.setObjectName("clickableLabel")
        self.desktopLyricLabel.setObjectName("titleLabel")
        self.lyricStyleLabel.setObjectName("subTitleLabel")
        self.embedLyricLabel.setObjectName("titleLabel")
        setStyleSheet(self, 'setting_interface')

    def resizeEvent(self, e):
        self.appLabel.move(self.width() - 400, self.appLabel.y())
        self.helpLabel.move(self.width() - 400, self.helpLabel.y())
        self.issueLabel.move(self.width() - 400, self.issueLabel.y())
        self.checkUpdateLabel.move(
            self.width() - 400, self.checkUpdateLabel.y())
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
            config.get(config.musicFolders), title, content, self.window())

        w.folderChanged.connect(self.__updateSelectedFolders)
        w.exec_()

    def __updateSelectedFolders(self, folders: list):
        """ update selected folders """
        if config.get(config.musicFolders) == folders:
            return

        config.set(config.musicFolders, folders)
        self.__updateMetaDataSwitchButtonEnabled()
        self.selectedMusicFoldersChanged.emit(folders)

    def __onPageSliderValueChanged(self, value: int):
        """ page slider value changed slot """
        self.pageSizeValueLabel.setNum(value)
        self.pageSizeValueLabel.adjustSize()
        config.set(config.onlinePageSize, value)

    def __onMinimizeToTrayChanged(self, button: QRadioButton, key: str):
        """ minimize to tray changed slot """
        self.minimizeToTrayChanged.emit(button.property(key))

    def __onThemeModeChanged(self, button: QRadioButton, key: str):
        """ theme mode changed slot """
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
        if not folder or config.get(config.downloadFolder) == folder:
            return

        config.set(config.downloadFolder, folder)
        self.downloadFolderLineEdit.setText(folder)
        self.downloadFolderChanged.emit(folder)

    def __onLyricFontButtonClicked(self):
        """ desktop lyric font button clicked slot """
        font, isOk = QFontDialog.getFont(
            config.lyricFont, self.window(), self.tr("Select Font"))
        if isOk:
            config.lyricFont = font
            signalBus.lyricFontChanged.emit(font)

    def __onLyricAlignmentChanged(self, button: QRadioButton, key: str):
        """ desktop lyric alignment changed slot """
        signalBus.lyricAlignmentChanged.emit(button.property(key))

    def __onLyricFontColorChanged(self, color: QColor):
        """ desktop lyric font color changed slot """
        config.set(config.deskLyricFontColor, list(color.getRgb())[:3])
        signalBus.lyricFontColorChanged.emit(color)

    def __onLyricHighlightColorChanged(self, color: QColor):
        """ desktop lyric highlight color changed slot """
        config.set(config.deskLyricHighlightColor, list(color.getRgb())[:3])
        signalBus.lyricHighlightColorChanged.emit(color)

    def __onLyricStrokeColorChanged(self, color: QColor):
        """ desktop lyric stroke color changed slot """
        config.set(config.deskLyricStrokeColor, list(color.getRgb())[:3])
        signalBus.lyricStrokeColorChanged.emit(color)

    def __onLyricStrokeSizeChanged(self, size: int):
        """ desktop lyric stroke size changed slot """
        config.set(config.deskLyricStrokeSize, size)
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
        self.preferEmbedCheckBox.stateChanged.connect(
            lambda: config.set(config.preferEmbedLyric, self.preferEmbedCheckBox.isChecked()))
        self.embedWhenSaveCheckBox.stateChanged.connect(
            lambda: config.set(config.embedLyricWhenSave, self.embedWhenSaveCheckBox.isChecked()))
        self.modeGroup.buttonClicked.connect(self.__onThemeModeChanged)
        self.mediaInfoGroup.checkedChanged.connect(
            self.__onGetMetaDataSwitchButtonCheckedChanged)
        self.selectMusicFolderLabel.clicked.connect(
            self.__showSongFolderListDialog)
        self.pageSizeSlider.valueChanged.connect(
            self.__onPageSliderValueChanged)
        self.downloadFolderButton.clicked.connect(
            self.__onDownloadFolderButtonClicked)
        self.closeWindowGroup.buttonClicked.connect(
            self.__onMinimizeToTrayChanged)
        self.acrylicGroup.checkedChanged.connect(
            self.acrylicEnableChanged)
        self.checkUpdateLabel.clicked.connect(self.checkUpdateSig)


class RadioButtonGroup(QWidget):
    """ Radio button group """

    buttonClicked = pyqtSignal(QRadioButton, str)

    def __init__(self, property: ConfigItem, texts: List[str], title: str, titleType="title", parent=None):
        """
        Parameters
        ----------
        property: ConfigItem
            config item

        texts: List[str]
            the texts of radio buttons

        title: str
            the title of button group

        titleType: str
            the type of title, including `title` and `subTitle`

        parent:
            parent window
        """
        super().__init__(parent=parent)
        setStyleSheet(self, "setting_interface")
        self.vBox = QVBoxLayout(self)
        self.vBox.setContentsMargins(0, 0, 0, 0)
        self.vBox.setSpacing(0)
        self.vBox.setAlignment(Qt.AlignTop)

        self.configItem = property
        self.propertyName = self.configItem.name
        self.titleLabel = QLabel(title, self, objectName=titleType+"Label")
        self.buttonGroup = QButtonGroup(self)
        self.buttons = []

        self.vBox.addWidget(self.titleLabel, 0, Qt.AlignTop)
        self.vBox.addSpacing(13)
        for value, text in zip(property.options, texts):
            button = QRadioButton(text, self)
            button.setProperty(property.name, value)
            self.vBox.addWidget(button, 0, Qt.AlignTop)
            self.vBox.addSpacing(14)
            self.buttonGroup.addButton(button)
            self.buttons.append(button)

        self.adjustSize()
        self.setSelected(config.get(property))
        self.buttonGroup.buttonClicked.connect(self.__onButtonClicked)

    def __onButtonClicked(self, button: QRadioButton):
        """ button clicked slot """
        value = button.property(self.propertyName)
        config.set(self.configItem, value)
        for btn in self.buttons:
            btn.setChecked(btn.property(self.propertyName) == value)

        self.buttonClicked.emit(button, self.propertyName)

    def setSelected(self, value):
        """ select button according to the value """
        for button in self.buttons:
            button.setChecked(button.property(self.propertyName) == value)


class SwitchButtonGroup(QWidget):
    """ Switch button group """

    checkedChanged = pyqtSignal(bool)

    def __init__(self, title: str, content: str, property: ConfigItem = None, parent=None):
        """
        Parameters
        ----------
        title: str
            the title of switch button group

        content: str
            the content of switch button group

        property: ConfigItem
            config item

        parent:
            parent window
        """
        super().__init__(parent=parent)
        setStyleSheet(self, "setting_interface")
        self.configItem = property
        self.vBox = QVBoxLayout(self)
        self.titleLabel = QLabel(title, self, objectName="titleLabel")
        self.contentLabel = QLabel(content, self)
        self.switchButton = SwitchButton(self.tr("Off"), self)

        if self.configItem:
            self.setChecked(config.get(property))

        self.vBox.setSpacing(5)
        self.vBox.setContentsMargins(0, 0, 0, 0)
        self.vBox.addWidget(self.titleLabel, 0, Qt.AlignTop)
        self.vBox.addWidget(self.contentLabel, 0, Qt.AlignTop)
        self.vBox.addSpacing(2)
        self.vBox.addWidget(self.switchButton, 0, Qt.AlignTop)
        self.vBox.setAlignment(Qt.AlignTop)
        self.switchButton.checkedChanged.connect(self.__onCheckedChanged)
        self.adjustSize()

    def __onCheckedChanged(self, isChecked: bool):
        """ switch button checked state changed slot """
        self.setChecked(isChecked)
        self.checkedChanged.emit(isChecked)

    def setChecked(self, isChecked: bool):
        """ set switch button checked state """
        if self.configItem:
            config.set(self.configItem, isChecked)

        self.switchButton.setChecked(isChecked)
        self.switchButton.setText(
            self.tr('On') if isChecked else self.tr('Off'))

    def isChecked(self):
        return self.switchButton.isChecked()
