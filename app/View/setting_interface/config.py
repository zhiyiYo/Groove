# coding:utf-8
import json
import os
from pathlib import Path


class Config:
    """ 配置类 """

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
            'download-folder': str(Path('download').absolute()).replace("\\", '/')
        }
        self.__readConfig()

    def __readConfig(self):
        """ 读入配置文件数据 """
        try:
            with open("config/config.json", encoding="utf-8") as f:
                self.__config.update(json.load(f))
        except:
            pass

        for folder in self.__config["selected-folders"].copy():
            if not os.path.exists(folder):
                self.__config["selected-folders"].remove(folder)

        os.makedirs(self.__config['download-folder'], exist_ok=True)

    def __setitem__(self, key, value):
        if key not in self.__config:
            raise KeyError(f'配置项 `{key}` 非法')

        if self.__config[key] != value:
            self.save()

        self.__config[key] = value

    def __getitem__(self, key):
        return self.__config[key]

    def update(self, config: dict):
        """ 更新配置 """
        for k, v in config.items():
            self[k] = v

    def save(self):
        """ 保存配置 """
        self.folder.mkdir(parents=True, exist_ok=True)
        with open("config/config.json", "w", encoding="utf-8") as f:
            json.dump(self.__config, f)
