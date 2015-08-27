import sys
import struct
import socket
import random
import casperfpga
from PyQt4 import QtCore, QtGui
from roachWindow import Ui_MainWindow

class roachWin(QtGui.QMainWindow):

    pollRegisters = False
    fpga = None

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.fftWindowSize = 1024
        self.dataUnitSize = 4*4 # hence 16 bytes per frequency bin
        self.accumulationLength = 3125
        self.samplingFrequency = 800e6

        QtCore.QObject.connect(self.ui._connectToRoachButton, QtCore.SIGNAL('clicked()'), self.connectToRoach)
        QtCore.QObject.connect(self.ui._initRoachButton, QtCore.SIGNAL('clicked()'), self.initialiseRoach)
        QtCore.QObject.connect(self.ui._channelUpdateButton, QtCore.SIGNAL('clicked()'), self.updateChannel)
        QtCore.QObject.connect(self.ui._tenGbeUpdateButton, QtCore.SIGNAL('clicked()'), self.updateTenGbe)
        QtCore.QObject.connect(self.ui._packetsUpdateButton, QtCore.SIGNAL('clicked()'), self.updatePackets)
        QtCore.QObject.connect(self.ui._signalUpdateButton, QtCore.SIGNAL('clicked()'), self.updateSignal)
        QtCore.QObject.connect(self.ui._NDUpdateButton, QtCore.SIGNAL('clicked()'), self.updateNoiseDiode)
        QtCore.QObject.connect(self.ui._NDHighTimeSpinbox, QtCore.SIGNAL('valueChanged(int)'), self.NDHighTimeSeconds)
        QtCore.QObject.connect(self.ui._NDLowTimeSpinbox, QtCore.SIGNAL('valueChanged(int)'), self.NDLowTimeSeconds)

        self.NDHighTimeSeconds()
        self.NDLowTimeSeconds()

        self.runTimer()

    def connectToRoach(self):
        roachIP = self.ui._roachHostIPBox.text()
        katcpPort = self.ui._katcpPortSpinbox.value()
        try:
            self.fpga = casperfpga.katcp_fpga.KatcpFpga(roachIP, katcpPort)
        except casperfpga.katcp_fpga.KatcpRequestError:
            QtGui.QMessageBox.about(self, 'Error', 'Could not connect to ROACH %s'%(roachIP))

    def initialiseRoach(self):
        # An if statement will need to be here to determine which gateware to use.
        gateware = 'wb_spectrometer_11_2015_Aug_24_1502'
        self.fpga.system_info['program_filename'] = '%s.bof'%(gateware)
        try:
            self.fpga.program()
        except casperfpga.katcp_fpga.KatcpRequestError:
            QtGui.QMessageBox.about(self, 'Error', 'Couldn\'t program ROACH with %s.bof'%(gateware))
        else:
            try:
                self.fpga.get_system_information('%s.fpg'%(gateware))
            except IOError:
                QtGui.QMessageBox.about(self, 'Error', 'Couldn\'t find file %s.fpg'%(gateware))
            else:
                self.ui._gatewareSelectCombo.setEnabled(True)
                #self.ui._channelUpdateButton.setEnabled(True)
                self.ui._tenGbeUpdateButton.setEnabled(True)
                self.ui._packetsUpdateButton.setEnabled(True)
                self.ui._signalUpdateButton.setEnabled(True)
                self.ui._NDUpdateButton.setEnabled(True)
                self.ui._initRoachButton.setEnabled(True)

                #self.updateChannel()
                self.updateTenGbe()
                self.updatePackets()
                self.updateSignal()
                self.updateNoiseDiode()

                self.pollRegisters = True # This will actually only come after initialising the ROACH

    def updateChannel(self):
        channel = self.ui._channelSelectSpinbox.text()
        QtGui.QMessageBox.about(self, 'Notice', 'Channel select not implemented yet')

    def updateTenGbe(self):
        strDestinationIP = str(self.ui._destinationIPBox.text()) # because it returns a Qstr, needs to be cast to str
        packedDestinationIP = socket.inet_aton(strDestinationIP)
        destinationIP = struct.unpack('!L', packedDestinationIP)[0]
        destinationPort = self.ui._destinationPortSpinbox.value()
        try:
            self.fpga.registers.tgbe0_dest_ip.write(reg = tGbEDestinationIP)
            self.fpga.registers.tgbe0_dest_port.write(reg = tGbEDestinationPort)
        except casperfpga.katcp_fpga.KatcpRequestError:
            QtGui.QMessageBox.about(self, 'Error', 'Unable to write 10GbE information to ROACH')


    def updatePackets(self):
        dataSizePerPacket_B = self.ui._dataSizePerPacketSpinbox.value()
        interpacketLength_cycles = self.ui._interpacketLengthSpinbox.value()
        packetsPerWindow_n = self.fftWindowSize * self.dataUnitSize / dataSizePerPacket
        self.ui._packetsPerWindowLabel.setText(str(packetsPerWindow))
        try:
            self.fpga.registers.eth_data_size_per_packet.write_int(dataSizePerPacket_B)
            self.fpga.registers.eth_interpacket_length.write_int(interpacketLength_cycles)
            self.fpga.registers.eth_packets_per_accum_window.write_int(packetsPerWindow_n)
        except casperfpga.katcp_fpga.KatcpRequestError:
            QtGui.QMessageBox.about(self, 'Error', 'Unable to write packet information to ROACH')

    def updateSignal(self):
        fftShift = self.ui._fftShiftShiftbox.value()
        accumulationLength = self.ui._accumulationLengthSpinbox.value()
        adcAttenuation = self.ui._adcAttenuationSpinbox.value()
        try:
            self.fpga.registers.fft_shift.write_int(fftShift)
            self.fpga.registers.accumulation_length.write_int(accumulationLength)
        except casperfpga.katcp_fpga.KatcpRequestError:
            QtGui.QMessageBox.about(self, 'Error', 'Unable to write signal information to ROACH')

    def updateNoiseDiode(self):
        NDEnable = self.ui._NDEnableCheckbox.isChecked()
        NDDutyCycleMode = self.ui._NDDutycycleModeCheckbox.isChecked()
        NDHighTime = self.ui._NDHighTimeSpinbox.value()
        NDLowTime = self.ui._NDLowTimeSpinbox.value()
        try:
            fpga.registers.noise_diode_on_length.write_int(NDHighTime)
            fpga.registers.noise_diode_off_length.write_int(NDLowTime)
            fpga.registers.noise_diode_duty_cycle_en.write_int(int(NDDutyCycleMode))
            fpga.registers.noise_diode_en.write_int(int(NDEnable))
        except casperfpga.katcp_fpga.KatcpRequestError:
            QtGui.QMessageBox.about(self, 'Error', 'Unable to write noise diode information to ROACH')

    def NDHighTimeSeconds(self):
        NDHighTimeSeconds = float(self.ui._NDHighTimeSpinbox.value()) * self.accumulationLength * 2*self.fftWindowSize / self.samplingFrequency
        self.ui._NDHighTimeLabel.setText(str(NDHighTimeSeconds) + ' s')

    def NDLowTimeSeconds(self):
        NDLowTimeSeconds = float(self.ui._NDLowTimeSpinbox.value()) * self.accumulationLength * 2*self.fftWindowSize / self.samplingFrequency
        self.ui._NDLowTimeLabel.setText('\t' + str(NDLowTimeSeconds) + ' s') # \t just to space them out a bit more sensibly

    def updateIndicators(self):
        if self.pollRegisters:
            self.ui._tenGbEStatusLabel.setText(str(bool(self.fpga.read_int('tgbe0_linkup'))))
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


