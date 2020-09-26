from PyQt5.QtCore import Qt, QDateTime

dateTime = QDateTime.currentDateTime() #type:QDateTime
print(dateTime.toString(Qt.ISODate))