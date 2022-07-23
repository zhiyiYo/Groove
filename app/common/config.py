# coding:utf-8
import json
import os
import sys
from pathlib import Path

import darkdetect
from PyQt5.QtGui import QFont, QGuiApplication

from .singleton import Singleton


class Config(Singleton):
    """ Config of app """

    folder = Path('config')

    def __init__(self):
        self.__config = {
            "selected-folders": [],
            "mv-quality": "Full HD",
            "online-play-quality": "Standard quality",
            "online-music-page-size": 20,
            "enable-acrylic-background": False,
            "minimize-to-tray": True,
            "volume": 30,
            "playBar-color": [34, 92, 127],
            "download-folder": str(Path('download').absolute()).replace("\\", '/'),
            "recent-plays-number": 300,
            "mode": "Light",
            "lyric.font-color": [255, 255, 255],
            "lyric.highlight-color": [0, 153, 188],
            "lyric.font-size": 50,
            "lyric.stroke-size": 5,
            "lyric.stroke-color": [0, 0, 0],
            "lyric.font-family": "Microsoft YaHei",
            "lyric.alignment": "Center"
        }
        self.__theme = "Light"
        self.__readConfig()

    def __readConfig(self):
        """ read config """
        try:
            with open("config/config.json", encoding="utf-8") as f:
                self.__config.update(json.load(f))
        except:
            pass

        for folder in self.__config["selected-folders"].copy():
            if not os.path.exists(folder):
                self.__config["selected-folders"].remove(folder)

        if not os.path.exists(self.__config['download-folder']):
            self.__config['download-folder'] = str(
                Path('download').absolute()).replace("\\", '/')

        os.makedirs(self.__config['download-folder'], exist_ok=True)

        if sys.platform != "win32":
            self["enable-acrylic-background"] = False

        if self["mode"] == "Auto":
            self.__theme = darkdetect.theme() or "Light"
        else:
            self.__theme = self["mode"]

    def __setitem__(self, key, value):
        if key not in self.__config:
            raise KeyError(f'Config `{key}` is illegal')

        if self.__config[key] == value:
            return

        self.__config[key] = value
        self.save()

    def __getitem__(self, key):
        return self.__config[key]

    def update(self, config: dict):
        """ update config """
        for k, v in config.items():
            self[k] = v

    def save(self):
        """ save config """
        self.folder.mkdir(parents=True, exist_ok=True)
        with open(self.folder/"config.json", "w", encoding="utf-8") as f:
            json.dump(self.__config, f, ensure_ascii=False, indent=4)

    @property
    def theme(self):
        """ get theme mode, can be `light` or `dark` """
        return self.__theme.lower()

    @property
    def lyricFont(self):
        """ get the desktop lyric font """
        font = QFont(self["lyric.font-family"])
        font.setPixelSize(self["lyric.font-size"])
        return font

    @lyricFont.setter
    def lyricFont(self, font: QFont):
        dpi = QGuiApplication.primaryScreen().logicalDotsPerInch()
        self["lyric.font-family"] = font.family()
        self["lyric.font-size"] = max(15, int(font.pointSize()*dpi/72))


config = Config()
