# coding: utf-8
from pathlib import Path
from PyQt5.QtCore import QStandardPaths

# change DEBUG to False if you want to compile the code to exe
DEBUG = True


YEAR = 2022
AUTHOR = "zhiyiYo"
VERSION = "v1.3.7"
APP_NAME = "Groove"
HELP_URL = "https://groove-music.readthedocs.io"
FEEDBACK_URL = "https://github.com/zhiyiYo/Groove/issues"
RELEASE_URL = "https://github.com/zhiyiYo/Groove/releases/latest"


if DEBUG:
    CONFIG_FOLDER = Path('AppData').absolute()
else:
    CONFIG_FOLDER = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)) / APP_NAME

CONFIG_FILE = CONFIG_FOLDER / "config.json"
