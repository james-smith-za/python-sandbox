import sys
import struct
import socket
import random
from PyQt4 import QtCore, QtGui
from roachWindow import Ui_MainWindow

class roachWin(QtGui.QMainWindow):

    pollRegisters = False

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.fftWindowSize = 1024
        self.dataUnitSize = 4*4 # hence 16 bytes per frequency bin
        self.accumulationLength = 3125
        self.samplingFrequency = 800e6

        QtCore.QObject.connect(self.ui._connectToRoachButton, QtCore.SIGNAL('clicked()'), self.connectToRoach)
        QtCore.QObject.connect(self.ui._channelUpdateButton, QtCore.SIGNAL('clicked()'), self.updateChannel)
        QtCore.QObject.connect(self.ui._tenGbeUpdateButton, QtCore.SIGNAL('clicked()'), self.updateTenGbe)
        QtCore.QObject.connect(self.ui._packetsUpdateButton, QtCore.SIGNAL('clicked()'), self.updatePackets)
        QtCore.QObject.connect(self.ui._signalUpdateButton, QtCore.SIGNAL('clicked()'), self.updateSignal)
        QtCore.QObject.connect(self.ui._NDUpdateButton, QtCore.SIGNAL('clicked()'), self.updateNoiseDiode)
        QtCore.QObject.connect(self.ui._NDHighTimeSpinbox, QtCore.SIGNAL('valueChanged(int)'), self.NDHighTimeSeconds)
        QtCore.QObject.connect(self.ui._NDLowTimeSpinbox, QtCore.SIGNAL('valueChanged(int)'), self.NDLowTimeSeconds)
        QtCore.QObject.connect(self.ui._initRoachButton, QtCore.SIGNAL('clicked()'), self.initialiseRoach)

        self.NDHighTimeSeconds()
        self.NDLowTimeSeconds()

        self.runTimer()

    def connectToRoach(self):
        self.ui._gatewareSelectCombo.setEnabled(True)
        self.ui._channelUpdateButton.setEnabled(True)
        self.ui._tenGbeUpdateButton.setEnabled(True)
        self.ui._packetsUpdateButton.setEnabled(True)
        self.ui._signalUpdateButton.setEnabled(True)
        self.ui._NDUpdateButton.setEnabled(True)
        self.ui._initRoachButton.setEnabled(True)

        self.pollRegisters = True

    def updateChannel(self):
        channel = self.ui._channelSelectSpinbox.text()
        print channel

    def updateTenGbe(self):
        strDestinationIP = str(self.ui._destinationIPBox.text()) # because it returns a Qstr, needs to be cast to str
        packedDestinationIP = socket.inet_aton(strDestinationIP)
        destinationIP = struct.unpack('!L', packedDestinationIP)[0]
        destinationPort = self.ui._destinationPortSpinbox.value()
        print strDestinationIP + ' ' + str(destinationIP) + ':' + str(destinationPort)

    def updatePackets(self):
        dataSizePerPacket = self.ui._dataSizePerPacketSpinbox.value()
        interpacketLength = self.ui._interpacketLengthSpinbox.value()
        packetsPerWindow = self.fftWindowSize * self.dataUnitSize / dataSizePerPacket
        self.ui._packetsPerWindowLabel.setText(str(packetsPerWindow))
        print 'packets updated'

    def updateSignal(self):
        fftShift = self.ui._fftShiftShiftbox.value()
        self.accumulationLength = self.ui._accumulationLengthSpinbox.value()
        adcAttenuation = self.ui._adcAttenuationSpinbox.value()
        print 'signal updated'

    def updateNoiseDiode(self):
        NDEnable = self.ui._NDEnableCheckbox.isChecked()
        NDDutyCycleMode = self.ui._NDDutycycleModeCheckbox.isChecked()
        NDHighTime = self.ui._NDHighTimeSpinbox.value()
        NDLowTime = self.ui._NDLowTimeSpinbox.value()

    def NDHighTimeSeconds(self):
        NDHighTimeSeconds = float(self.ui._NDHighTimeSpinbox.value()) * self.accumulationLength * 2*self.fftWindowSize / self.samplingFrequency
        self.ui._NDHighTimeLabel.setText(str(NDHighTimeSeconds) + ' s')

    def NDLowTimeSeconds(self):
        NDLowTimeSeconds = float(self.ui._NDLowTimeSpinbox.value()) * self.accumulationLength * 2*self.fftWindowSize / self.samplingFrequency
        self.ui._NDLowTimeLabel.setText('\t' + str(NDLowTimeSeconds) + ' s') # \t just to space them out a bit more sensibly

    def initialiseRoach(self):
        self.updateChannel()
        self.updateTenGbe()
        self.updatePackets()
        self.updateSignal()
        self.updateNoiseDiode()

    def updateIndicators(self):
        if self.pollRegisters:
            self.ui._tenGbEStatusLabel.setText(str(bool(random.randint(0,1))))
            self.ui._adc0OrLabel.setText(str(bool(random.randint(0,1))))
            self.ui._adc1OrLabel.setText(str(bool(random.randint(0,1))))
            self.ui._fft0OfLabel.setText(str(bool(random.randint(0,1))))
            self.ui._fft1OfLabel.setText(str(bool(random.randint(0,1))))
            self.ui._packetiserOfLabel.setText(str(bool(random.randint(0,1))))
            self.ui._fifoOfLabel.setText(str(bool(random.randint(0,1))))
            self.ui._ethTxOfLabel.setText(str(bool(random.randint(0,1))))

    def runTimer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateIndicators)
        self.timer.start(100)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = roachWin()
    myapp.show()
    sys.exit(app.exec_())


