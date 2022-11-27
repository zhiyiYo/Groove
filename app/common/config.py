# coding:utf-8
import json
import sys
from enum import Enum
from pathlib import Path
from typing import Iterable, List, Union

import darkdetect
from PyQt5.QtGui import QFont, QGuiApplication
from PyQt5.QtMultimedia import QMediaPlaylist

from .crawler import MvQuality, SongQuality
from .exception_handler import exceptionHandler
from .singleton import Singleton
from .signal_bus import signalBus


class ConfigValidator:
    """ Config validator """

    def validate(self, value) -> bool:
        """ Verify whether the value is legal """
        return True

    def correct(self, value):
        """ correct illegal value """
        return value


class RangeValidator(ConfigValidator):
    """ Range validator """

    def __init__(self, min, max):
        self.min = min
        self.max = max
        self.range = (min, max)

    def validate(self, value) -> bool:
        return self.min <= value <= self.max

    def correct(self, value):
        return min(max(self.min, value), self.max)


class OptionsValidator(ConfigValidator):
    """ Options validator """

    def __init__(self, options: Union[Iterable, Enum]) -> None:
        if not options:
            raise ValueError("The `options` can't be empty.")

        if isinstance(options, Enum):
            options = options._member_map_.values()

        self.options = list(options)

    def validate(self, value) -> bool:
        return value in self.options

    def correct(self, value):
        return value if self.validate(value) else self.options[0]


class BoolValidator(OptionsValidator):
    """ Boolean validator """

    def __init__(self):
        super().__init__([True, False])


class FolderValidator(ConfigValidator):
    """ Folder validator """

    def validate(self, value: str) -> bool:
        return Path(value).exists()

    def correct(self, value: str):
        path = Path(value)
        path.mkdir(exist_ok=True, parents=True)
        return str(path.absolute()).replace("\\", "/")


class FolderListValidator(ConfigValidator):
    """ Folder list validator """

    def validate(self, value: List[str]) -> bool:
        return all(Path(i).exists() for i in value)

    def correct(self, value: List[str]):
        folders = []
        for folder in value:
            path = Path(folder)
            if path.exists():
                folders.append(str(path.absolute()).replace("\\", "/"))

        return folders


class ColorValidator(ConfigValidator):
    """ RGB color validator """

    def __init__(self, default: List[int]):
        self.default = default

    def validate(self, value: List[int]) -> bool:
        if not isinstance(value, list) or len(value) != 3:
            return False

        return all(0 <= i <= 255 for i in value)

    def correct(self, value: List[int]):
        return value if self.validate(value) else self.default


class ConfigSerializer:
    """ Config serializer """

    def serialize(self, value):
        """ serialize config value """
        return value

    def deserialize(self, value):
        """ deserialize config from config file's value """
        return value


class EnumSerializer(ConfigSerializer):
    """ enumeration class serializer """

    def __init__(self, enumClass):
        self.enumClass = enumClass

    def serialize(self, value: Enum):
        return value.value

    def deserialize(self, value):
        return self.enumClass(value)


class PlaybackModeSerializer(ConfigSerializer):
    """ Playback mode class serializer """

    def serialize(self, value: QMediaPlaylist.PlaybackMode):
        return int(value)

    def deserialize(self, value):
        return QMediaPlaylist.PlaybackMode(value)


class ConfigItem:
    """ Config item """

    def __init__(self, group: str, name: str, default, validator: ConfigValidator = None,
                 serializer: ConfigSerializer = None, restart=False):
        """
        Parameters
        ----------
        group: str
            config group name

        name: str
            config item name, can be empty

        default:
            default value

        options: list
            options value

        serializer: ConfigSerializer
            config serializer

        restart: bool
            whether to restart the application after updating the configuration item
        """
        self.group = group
        self.name = name
        self.validator = validator or ConfigValidator()
        self.serializer = serializer or ConfigSerializer()
        self.__value = default
        self.value = default
        self.restart = restart

    @property
    def value(self):
        """ get the value of config item """
        return self.__value

    @value.setter
    def value(self, v):
        self.__value = self.validator.correct(v)

    @property
    def options(self):
        """ get optional values, only available for item with `OptionsValidator` """
        if isinstance(self.validator, OptionsValidator):
            return self.validator.options

        return []

    @property
    def range(self):
        """ get the available range of config """
        if isinstance(self.validator, RangeValidator):
            return self.validator.range

        return (self.value, self.value)

    @property
    def key(self):
        """ get the config key separated by `.` """
        return self.group+"."+self.name if self.name else self.group

    def serialize(self):
        return self.serializer.serialize(self.value)

    def deserializeFrom(self, value):
        self.value = self.serializer.deserialize(value)


class Config(Singleton):
    """ Config of app """

    folder = Path('config')
    file = folder/"config.json"

    # folders
    musicFolders = ConfigItem(
        "Folders", "LocalMusic", [], FolderListValidator())
    downloadFolder = ConfigItem(
        "Folders", "Download", "download", FolderValidator())

    # online
    onlineSongQuality = ConfigItem(
        "Online", "SongQuality", SongQuality.STANDARD, OptionsValidator(SongQuality), EnumSerializer(SongQuality))
    onlinePageSize = ConfigItem(
        "Online", "PageSize", 30, RangeValidator(0, 30))
    onlineMvQuality = ConfigItem(
        "Online", "MvQuality", MvQuality.FULL_HD, OptionsValidator(MvQuality), EnumSerializer(MvQuality))

    # main window
    enableAcrylicBackground = ConfigItem(
        "MainWindow", "EnableAcrylicBackground", False, BoolValidator())
    minimizeToTray = ConfigItem(
        "MainWindow", "MinimizeToTray", True, BoolValidator())
    playBarColor = ConfigItem(
        "MainWindow", "PlayBarColor", [34, 92, 127], ColorValidator([34, 92, 127]))
    themeMode = ConfigItem(
        "MainWindow", "ThemeMode", "Light", OptionsValidator(["Light", "Dark", "Auto"]), restart=True)
    recentPlaysNumber = ConfigItem(
        "MainWindow", "RecentPlayNumbers", 300, RangeValidator(10, 300))
    dpiScale = ConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)

    # media player
    randomPlay = ConfigItem("Player", "RandomPlay", False, BoolValidator())
    playerVolume = ConfigItem("Player", "Volume", 30, RangeValidator(0, 100))
    playerMuted = ConfigItem("Player", "Muted", False, BoolValidator())
    playerPosition = ConfigItem(
        "Player", "Position", 0, RangeValidator(0, float("inf")))
    playerSpeed = ConfigItem(
        "Player", "Speed", 1, RangeValidator(0.1, float("inf")))
    loopMode = ConfigItem(
        "Player", "LoopMode", QMediaPlaylist.Sequential,
        OptionsValidator([QMediaPlaylist.Sequential, QMediaPlaylist.Loop, QMediaPlaylist.CurrentItemInLoop]),
        PlaybackModeSerializer()
    )

    # desktop lyric
    deskLyricFontColor = ConfigItem(
        "DesktopLyric", "FontColor", [255, 255, 255], ColorValidator([255, 255, 255]))
    deskLyricHighlightColor = ConfigItem(
        "DesktopLyric", "HighlightColor", [0, 153, 188], ColorValidator([0, 153, 188]))
    deskLyricFontSize = ConfigItem(
        "DesktopLyric", "FontSize", 50, RangeValidator(15, 50))
    deskLyricStrokeSize = ConfigItem(
        "DesktopLyric", "StrokeSize", 5, RangeValidator(0, 10))
    deskLyricStrokeColor = ConfigItem(
        "DesktopLyric", "StrokeColor", [0, 0, 0], ColorValidator([0, 0, 0]))
    deskLyricFontFamily = ConfigItem(
        "DesktopLyric", "FontFamily", "Microsoft YaHei")
    deskLyricAlignment = ConfigItem(
        "DesktopLyric", "Alignment", "Center", OptionsValidator(["Center", "Left", "Right"]))

    # embedded lyrics
    preferEmbedLyric = ConfigItem(
        "EmbeddedLyric", "PreferEmbedded", True, BoolValidator())
    embedLyricWhenSave = ConfigItem(
        "EmbeddedLyric", "EmbedWhenSave", False, BoolValidator())    # embed lyric when saving song info

    # software update
    checkUpdateAtStartUp = ConfigItem(
        "Update", "CheckUpdateAtStartUp", True, BoolValidator())

    def __init__(self):
        self.__theme = "Light"
        self.load()

    @classmethod
    def get(cls, item: ConfigItem):
        return item.value

    @classmethod
    def set(cls, item: ConfigItem, value):
        if item.value == value:
            return

        item.value = value
        cls.save()

        if item.restart:
            signalBus.appRestartSig.emit()

    @classmethod
    def toDict(cls, serialize=True):
        """ convert config items to `dict` """
        items = {}
        for name in dir(cls):
            item = getattr(cls, name)
            if not isinstance(item, ConfigItem):
                continue

            value = item.serialize() if serialize else item.value
            if not items.get(item.group):
                if not item.name:
                    items[item.group] = value
                else:
                    items[item.group] = {}

            if item.name:
                items[item.group][item.name] = value

        return items

    @classmethod
    def save(cls):
        cls.folder.mkdir(parents=True, exist_ok=True)
        with open(cls.file, "w", encoding="utf-8") as f:
            json.dump(cls.toDict(), f, ensure_ascii=False, indent=4)

    @exceptionHandler("config")
    def load(self):
        """ load config """
        try:
            with open(self.file, encoding="utf-8") as f:
                cfg = json.load(f)
        except:
            cfg = {}

        # map config items'key to item
        items = {}
        for name in dir(Config):
            item = getattr(Config, name)
            if isinstance(item, ConfigItem):
                items[item.key] = item

        # update the value of config item
        for k, v in cfg.items():
            if not isinstance(v, dict) and items.get(k) is not None:
                items[k].deserializeFrom(v)
            elif isinstance(v, dict):
                for key, value in v.items():
                    key = k + "." + key
                    if items.get(key) is not None:
                        items[key].deserializeFrom(value)

        if sys.platform != "win32":
            self.enableAcrylicBackground.value = False

        if self.get(self.themeMode) == "Auto":
            self.__theme = darkdetect.theme() or "Light"
        else:
            self.__theme = self.get(self.themeMode)

    @property
    def theme(self):
        """ get theme mode, can be `light` or `dark` """
        return self.__theme.lower()

    @property
    def lyricFont(self):
        """ get the desktop lyric font """
        font = QFont(self.deskLyricFontFamily.value)
        font.setPixelSize(self.deskLyricFontSize.value)
        return font

    @lyricFont.setter
    def lyricFont(self, font: QFont):
        dpi = QGuiApplication.primaryScreen().logicalDotsPerInch()
        self.deskLyricFontFamily.value = font.family()
        self.deskLyricFontSize.value = max(15, int(font.pointSize()*dpi/72))
        self.save()


config = Config()

VERSION = "v1.2.3"
HELP_URL = "https://github.com/zhiyiYo/Groove#readme"
FEEDBACK_URL = "https://github.com/zhiyiYo/Groove/issues"
RELEASE_URL = "https://github.com/zhiyiYo/Groove/releases/latest"
