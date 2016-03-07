import sys
from PyQt4 import QtGui

class guiWin(QtGui.QMainWindow):
    def __init__(self):
        super(guiWin, self).__init__()
        self.initUI()

    def initUI(self):
        okButton = QtGui.QPushButton('OK')
        cancelButton = QtGui.QPushButton('Cancel')

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(okButton)
        hbox.addWidget(cancelButton)

        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)


        self.statusBar().showMessage('Status Bar')

        exitAction = QtGui.QAction(QtGui.QIcon(), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAction)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(exitAction)


        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('Window Title')
        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


def main():
    app = QtGui.QApplication(sys.argv)
    win = guiWin()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


