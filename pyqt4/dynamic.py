import sys
from PyQt4 import QtGui, QtCore

class myWidget(QtGui.QWidget):
    def __init__(self):
        super(myWidget, self).__init__()

        self.setLayout(QtGui.QVBoxLayout())
        self.childLabel = QtGui.QLabel("foo", self)
        self.childButton = QtGui.QPushButton("Do the switch", self)
        self.layout().addWidget(self.childLabel)
        self.layout().addWidget(self.childButton)

        QtCore.QObject.connect(self.childButton, QtCore.SIGNAL("clicked()"), self.doTheSwitch)

    def doTheSwitch(self):
        self.layout().removeWidget(self.childLabel)
        self.childLabel = QtGui.QLabel("Added a new one instead.", self)
        self.layout().addWidget(self.childLabel)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    someWidget = myWidget()
    someWidget.show()
    sys.exit(app.exec_())

