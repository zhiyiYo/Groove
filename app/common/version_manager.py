# coding: utf-8
import re
import requests

from PyQt5.QtCore import QVersionNumber

from .config import VERSION
from .exception_handler import exceptionHandler


class VersionManager:
    """ Version manager """

    def __init__(self):
        self.currentVersion = VERSION
        self.lastestVersion = VERSION
        self.versionPattern = re.compile(r'v(\d+)\.(\d+)\.(\d+)')

    @exceptionHandler('version', VERSION)
    def getLatestVersion(self):
        """ get latest version """
        url = "https://api.github.com/repos/zhiyiYo/Groove/releases/latest"
        response = requests.get(url, timeout=2)
        response.raise_for_status()

        # parse version
        version = response.json()['tag_name']  # type:str
        match = self.versionPattern.search(version)
        if not match:
            return VERSION

        self.lastestVersion = version
        return version

    def hasNewVersion(self):
        """ check whether there is a new version """
        version = QVersionNumber.fromString(self.getLatestVersion()[1:])[0]
        currentVersion = QVersionNumber.fromString(self.currentVersion[1:])[0]
        return version > currentVersion