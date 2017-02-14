# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created: Sat Feb 11 10:02:38 2017
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1045, 860)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.qt_tblSourceCatalog = QtGui.QTableView(self.centralwidget)
        self.qt_tblSourceCatalog.setGeometry(QtCore.QRect(10, 160, 371, 621))
        self.qt_tblSourceCatalog.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.qt_tblSourceCatalog.setObjectName(_fromUtf8("qt_tblSourceCatalog"))
        self.qt_txtedTelescopeParams = QtGui.QTextEdit(self.centralwidget)
        self.qt_txtedTelescopeParams.setGeometry(QtCore.QRect(10, 40, 371, 81))
        self.qt_txtedTelescopeParams.setReadOnly(True)
        self.qt_txtedTelescopeParams.setObjectName(_fromUtf8("qt_txtedTelescopeParams"))
        self.qt_lstObsSchedule = QtGui.QListWidget(self.centralwidget)
        self.qt_lstObsSchedule.setGeometry(QtCore.QRect(400, 270, 631, 511))
        self.qt_lstObsSchedule.setObjectName(_fromUtf8("qt_lstObsSchedule"))
        self.qt_calStartDate = QtGui.QCalendarWidget(self.centralwidget)
        self.qt_calStartDate.setGeometry(QtCore.QRect(770, 40, 264, 165))
        self.qt_calStartDate.setObjectName(_fromUtf8("qt_calStartDate"))
        self.qt_lblObservationSchedule = QtGui.QLabel(self.centralwidget)
        self.qt_lblObservationSchedule.setGeometry(QtCore.QRect(410, 240, 151, 31))
        self.qt_lblObservationSchedule.setObjectName(_fromUtf8("qt_lblObservationSchedule"))
        self.qt_btnGenerateSchedule = QtGui.QPushButton(self.centralwidget)
        self.qt_btnGenerateSchedule.setGeometry(QtCore.QRect(850, 790, 181, 51))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.qt_btnGenerateSchedule.setFont(font)
        self.qt_btnGenerateSchedule.setObjectName(_fromUtf8("qt_btnGenerateSchedule"))
        self.qt_lblStartDate = QtGui.QLabel(self.centralwidget)
        self.qt_lblStartDate.setGeometry(QtCore.QRect(770, 10, 151, 31))
        self.qt_lblStartDate.setObjectName(_fromUtf8("qt_lblStartDate"))
        self.qt_txtReservedForPlot = QtGui.QTextEdit(self.centralwidget)
        self.qt_txtReservedForPlot.setEnabled(False)
        self.qt_txtReservedForPlot.setGeometry(QtCore.QRect(410, 30, 321, 201))
        self.qt_txtReservedForPlot.setReadOnly(True)
        self.qt_txtReservedForPlot.setObjectName(_fromUtf8("qt_txtReservedForPlot"))
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setGeometry(QtCore.QRect(480, 800, 351, 25))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.qt_lblOutputFilename = QtGui.QLabel(self.splitter)
        self.qt_lblOutputFilename.setObjectName(_fromUtf8("qt_lblOutputFilename"))
        self.qt_lineOutputFilename = QtGui.QLineEdit(self.splitter)
        self.qt_lineOutputFilename.setObjectName(_fromUtf8("qt_lineOutputFilename"))
        self.splitter_2 = QtGui.QSplitter(self.centralwidget)
        self.splitter_2.setGeometry(QtCore.QRect(770, 240, 261, 26))
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.qt_lblTimeZone = QtGui.QLabel(self.splitter_2)
        self.qt_lblTimeZone.setObjectName(_fromUtf8("qt_lblTimeZone"))
        self.qt_cmbTimeZone = QtGui.QComboBox(self.splitter_2)
        self.qt_cmbTimeZone.setObjectName(_fromUtf8("qt_cmbTimeZone"))
        self.splitter_3 = QtGui.QSplitter(self.centralwidget)
        self.splitter_3.setGeometry(QtCore.QRect(770, 210, 261, 25))
        self.splitter_3.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_3.setObjectName(_fromUtf8("splitter_3"))
        self.qt_lblStartTime = QtGui.QLabel(self.splitter_3)
        self.qt_lblStartTime.setObjectName(_fromUtf8("qt_lblStartTime"))
        self.qt_timeStartTime = QtGui.QTimeEdit(self.splitter_3)
        self.qt_timeStartTime.setObjectName(_fromUtf8("qt_timeStartTime"))
        self.splitter_4 = QtGui.QSplitter(self.centralwidget)
        self.splitter_4.setGeometry(QtCore.QRect(10, 10, 371, 26))
        self.splitter_4.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_4.setObjectName(_fromUtf8("splitter_4"))
        self.qt_lblTelescopeParams = QtGui.QLabel(self.splitter_4)
        self.qt_lblTelescopeParams.setObjectName(_fromUtf8("qt_lblTelescopeParams"))
        self.qt_btnOpenTelescopeParams = QtGui.QPushButton(self.splitter_4)
        self.qt_btnOpenTelescopeParams.setObjectName(_fromUtf8("qt_btnOpenTelescopeParams"))
        self.splitter_5 = QtGui.QSplitter(self.centralwidget)
        self.splitter_5.setGeometry(QtCore.QRect(10, 126, 371, 26))
        self.splitter_5.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_5.setObjectName(_fromUtf8("splitter_5"))
        self.qt_lblSourceCatalog = QtGui.QLabel(self.splitter_5)
        self.qt_lblSourceCatalog.setObjectName(_fromUtf8("qt_lblSourceCatalog"))
        self.qt_btnOpenSourceCatalog = QtGui.QPushButton(self.splitter_5)
        self.qt_btnOpenSourceCatalog.setObjectName(_fromUtf8("qt_btnOpenSourceCatalog"))
        self.splitter_6 = QtGui.QSplitter(self.centralwidget)
        self.splitter_6.setGeometry(QtCore.QRect(10, 800, 371, 26))
        self.splitter_6.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_6.setObjectName(_fromUtf8("splitter_6"))
        self.qt_cmbObsType = QtGui.QComboBox(self.splitter_6)
        self.qt_cmbObsType.setObjectName(_fromUtf8("qt_cmbObsType"))
        self.seesc = QtGui.QPushButton(self.splitter_6)
        self.seesc.setObjectName(_fromUtf8("seesc"))
        self.qt_btnSetToNow = QtGui.QPushButton(self.centralwidget)
        self.qt_btnSetToNow.setGeometry(QtCore.QRect(870, 10, 161, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.qt_btnSetToNow.setFont(font)
        self.qt_btnSetToNow.setObjectName(_fromUtf8("qt_btnSetToNow"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.qt_lblObservationSchedule.setText(_translate("MainWindow", "Observation Schedule", None))
        self.qt_btnGenerateSchedule.setText(_translate("MainWindow", "Generate FS Schedule!", None))
        self.qt_lblStartDate.setText(_translate("MainWindow", "Start date:", None))
        self.qt_txtReservedForPlot.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Noto Sans [monotype]\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">I envision a matplotlib widget sitting in this space.</p></body></html>", None))
        self.qt_lblOutputFilename.setText(_translate("MainWindow", "Output filename", None))
        self.qt_lblTimeZone.setText(_translate("MainWindow", "Time zone:", None))
        self.qt_lblStartTime.setText(_translate("MainWindow", "Start time:", None))
        self.qt_timeStartTime.setDisplayFormat(_translate("MainWindow", "HH:MM", None))
        self.qt_lblTelescopeParams.setText(_translate("MainWindow", "Telescope Parameters", None))
        self.qt_btnOpenTelescopeParams.setText(_translate("MainWindow", "Open", None))
        self.qt_lblSourceCatalog.setText(_translate("MainWindow", "Source catalog:", None))
        self.qt_btnOpenSourceCatalog.setText(_translate("MainWindow", "Open", None))
        self.seesc.setText(_translate("MainWindow", "Insert obs on target", None))
        self.qt_btnSetToNow.setText(_translate("MainWindow", "Set to now", None))

