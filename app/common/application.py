# coding:utf-8
import sys
import traceback
from typing import List

from PyQt5.QtCore import QIODevice, QSharedMemory, pyqtSignal
from PyQt5.QtNetwork import QLocalServer, QLocalSocket
from PyQt5.QtWidgets import QApplication

from .logger import Logger
from .signal_bus import signalBus


class SingletonApplication(QApplication):
    """ Singleton application """

    messageSig = pyqtSignal(object)
    logger = Logger("application")

    def __init__(self, argv: List[str], key: str):
        super().__init__(argv)
        self.key = key
        self.timeout = 1000
        self.server = QLocalServer(self)

        # cleanup (only needed for unix)
        QSharedMemory(key).attach()
        self.memory = QSharedMemory(self)
        self.memory.setKey(key)

        if self.memory.attach():
            self.isRunning = True
            self.sendMessage(argv[1] if len(argv) > 1 else 'show')
            self.logger.info(
                "Another Groove Music is already running, you should kill it first to launch a new one.")
            sys.exit(1)

        self.isRunning = False
        if not self.memory.create(1):
            self.logger.error(self.memory.errorString())
            raise RuntimeError(self.memory.errorString())

        self.server.newConnection.connect(self.__onNewConnection)
        self.server.listen(key)

    def __onNewConnection(self):
        socket = self.server.nextPendingConnection()
        if socket.waitForReadyRead(self.timeout):
            signalBus.appMessageSig.emit(
                socket.readAll().data().decode('utf-8'))
            socket.disconnectFromServer()

    def sendMessage(self, message: str):
        """ send message to another application """
        if not self.isRunning:
            return

        # connect to another application
        socket = QLocalSocket(self)
        socket.connectToServer(self.key, QIODevice.WriteOnly)
        if not socket.waitForConnected(self.timeout):
            self.logger.error(socket.errorString())
            return

        # send message
        socket.write(message.encode("utf-8"))
        if not socket.waitForBytesWritten(self.timeout):
            self.logger.error(socket.errorString())
            return

        socket.disconnectFromServer()


def exception_hook(exception: BaseException, value, tb):
    """ exception callback function """
    SingletonApplication.logger.error("Unhandled exception", (exception, value, tb))
    message = '\n'.join([''.join(traceback.format_tb(tb)),
                        '{0}: {1}'.format(exception.__name__, value)])
    signalBus.appErrorSig.emit(message)


sys.excepthook = exception_hook
