# coding: utf-8
from pathlib import Path
from .logger import Logger
from .signal_bus import signalBus


def writeAudio(func):
    """ decorator for writing data to playing song """

    def wrapper(*args, **kwargs):
        try:
            signalBus.writePlayingSongStarted.emit()
            func(*args, **kwargs)
            return True
        except Exception as e:
            Logger("meta_data_writer").error(e)
            return False
        finally:
            signalBus.writePlayingSongFinished.emit()

    return wrapper


def isValidLocalAudio(file: str):
    return not file.startswith('http') and Path(file).exists()
