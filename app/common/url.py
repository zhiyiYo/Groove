# coding: utf-8
from typing import List

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices


class FakeUrl(QUrl):
    """ Fake url """

    server_name = "base"
    category = ""
    _fake_urls = []  # type:List[FakeUrl]

    def __init__(self, id: str):
        """
        Parameters
        ----------
        id: str
            the id of url
        """
        self.id = id
        super().__init__(f"http://{self.server_name}/{self.category}/{id}")

    @classmethod
    def getId(cls, url: str):
        """ get the id of fake url, return `""` if the `url` isn't fake """
        if not url.startswith(f"http://{cls.server_name}/{cls.category}/"):
            return ""

        return url.split("/")[-1]

    @classmethod
    def register(cls, fake_url):
        """ register song information reader

        Parameters
        ----------
        fake_url:
            fake url class
        """
        if fake_url not in cls._fake_urls:
            cls._fake_urls.append(fake_url)

        return fake_url

    @classmethod
    def isFake(cls, url: str):
        """ whether a url is a fake url """
        for fake_url in cls._fake_urls:
            if url.startswith(f"http://{fake_url.server_name}/{fake_url.category}/"):
                return True

        return False


def url(path: str):
    if not path.startswith("http"):
        return QUrl.fromLocalFile(path)

    if FakeUrl.isFake(path):
        return QUrl("http")

    return QUrl(path)


def openUrl(url: str):
    """ open url """
    QDesktopServices.openUrl(QUrl(url))