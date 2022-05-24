# coding: utf-8
from PyQt5.QtCore import QUrl


def url(path: str):
    if not path.startswith("http"):
        return QUrl.fromLocalFile(path)

    return QUrl(path)