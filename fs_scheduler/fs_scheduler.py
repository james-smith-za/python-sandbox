from PyQt4 import QtCore, QtGui
import sys

import MainWindow


class FSSchedulerMainWindow(QtGui.QMainWindow, MainWindow.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.telescopeParamsFilename = None
        self.sourceCatalogFilename = None

        self.qt_btnOpenTelescopeParams.clicked.connect(self.openTelescopeParams)
        self.qt_btnOpenSourceCatalog.clicked.connect(self.openSourceCatalog)

    def openTelescopeParams(self):
        self.telescopeParamsFilename = QtGui.QFileDialog.getOpenFileName(parent=self,
                                                                         caption="Select telescope parameter file...")
        self.qt_txtedTelescopeParams.setText("%s"%(self.telescopeParamsFilename))

    def openSourceCatalog(self):
        self.sourceCatalogFilename = QtGui.QFileDialog.getOpenFileName(parent=self,
                                                                       caption="Select source catalog file...")
        # At this point, this link may be helpful: http://thomas-cokelaer.info/blog/2012/10/pyqt4-example-of-tablewidget-usage/


def main():
    app = QtGui.QApplication(sys.argv)
    form = FSSchedulerMainWindow()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()