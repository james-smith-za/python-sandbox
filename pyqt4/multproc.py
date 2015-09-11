import sys
from PyQt4 import QtGui, QtCore
import multiprocessing
import time

def processFunc():
    print "In the process now."
    for i in range(10):
        print i
        time.sleep(1)
    print "Exiting the process now."

class guiWin(QtGui.QWidget):
    def __init__(self):
        super(guiWin, self).__init__()
        self.initUI()

    def initUI(self):
        self.okButton = QtGui.QPushButton('OK')
        cancelButton = QtGui.QPushButton('Cancel')

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.okButton)
        hbox.addWidget(cancelButton)

        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        #QWidgets take layouts, QMainWindows take setcentralwidget. I've figured this out better in my RoachMonitor app, so look there for reference.
        self.setLayout(vbox)

        exitAction = QtGui.QAction(QtGui.QIcon(), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        self.myProcess = multiprocessing.Process(target=processFunc, name='processFunc')

        QtCore.QObject.connect(self.okButton, QtCore.SIGNAL("clicked()"), self.executeProcess)

        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('Window Title')
        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def executeProcess(self):
        self.myProcess.start()
        self.myProcess.join()
        # for some reason, a process can't be started twice, even if it's already joined. So we assign a new one, and it works again.
        self.myProcess = multiprocessing.Process(target=processFunc, name='processFunc')


def main():
    app = QtGui.QApplication(sys.argv)
    win = guiWin()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


