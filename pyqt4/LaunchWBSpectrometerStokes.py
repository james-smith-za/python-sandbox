import casperfpga
import sys
import time
import socket as socket
import struct as struct

def exit_clean():
    try:
        fpga.stop()
    except: pass
    sys.exit()

##### Variables to be set ###########

#Gateware to be loaded.a bof should be on the ROACH and a fpg file in the same directory as this script
gateware = 'wb_spectrometer_11_2015_Aug_27_1506'

#ROACH PowerPC Network:
strRoachIP = 'localhost'
roachKATCPPort = 7147

#TenGbE Network:
strTGbEDestinationIP = '10.0.0.3'
tGbEDestinationPort = 60000

#Set frame data length in bytes must be submultiple of 16384 ( 1024 frequencies * 2 for complex * 2 for 2 channels with each value a 4 byte uint32_t. Also excludes 8 bytes header of each frame)
#Set interframe length clock cycles, (note 64 bytes can be transferred per cyle)
dataSizePerPacket_B = 1024
interpacketLength_cycles = 16

#FFT shift (With the number in binary each bit represents whether the corresponding stage should right shift once.There are 2048 stages)
FFTShift = 2047 #shift all stages.

#How many FFT frames to accumulate for. Note: This is inversely proportional to output rate and time resolution and directly proportional to size of output numbers
accumulationLength = 3125

ADC_attenuation = 0

####################################

packedIP = socket.inet_aton(strTGbEDestinationIP)
tGbEDestinationIP = struct.unpack("!L", packedIP)[0]

print '\n---------------------------'
print 'Configuration:'
print '---------------------------'
print ' FPGA gateware:         ', gateware
print ' Destination 10GbE host:', strTGbEDestinationIP, '( ', tGbEDestinationIP, ' )'
print ' Data size per packet:  ', dataSizePerPacket_B, ' bytes'
print ' Interpacket length     ', interpacketLength_cycles, ' cycles'
print ' FFT shift mask         ', FFTShift
print ' Accumulation length    ', accumulationLength, '(', 2048 * accumulationLength / 800e3, ' ms integration per output )'
print '---------------------------'

print '\n---------------------------'
print 'Connecting to FPGA...'
fpga = casperfpga.katcp_fpga.KatcpFpga(strRoachIP, roachKATCPPort)

if fpga.is_connected():
	print 'Connected.'
else:
        print 'ERROR connecting to KATCP server.'
        exit_clean()

print 'Flashing gateware'

fpga.system_info['program_filename'] = '%s.bof' % gateware #bof needs to be on the roachfs for this to work
fpga.program()
fpga.get_system_information('%s.fpg' % gateware)
sys.stdout.flush()

print '\n---------------------------'
print 'Setting destination network host...'

fpga.registers.tgbe0_dest_ip.write(reg = tGbEDestinationIP)
fpga.registers.tgbe0_dest_port.write(reg = tGbEDestinationPort)
sys.stdout.flush()

print '\n---------------------------'
print 'Checking 10 Gb Ethernet link state...'

time.sleep(2) # Wait 2 seconds for 10GbE link to come up

bTGbELinkUp = bool(fpga.read_int('tgbe0_linkup'))
if not bTGbELinkUp:
	print 'Link not detected on 10 GbE port 0. Make sure that the cable is connected to port 0 on the ROACH and to a computer NIC or switch on the other end. Exiting.\n'
	exit_clean()

fpga.registers.eth_data_size_per_packet.write_int(dataSizePerPacket_B)
fpga.registers.eth_interpacket_length.write_int(interpacketLength_cycles)
fpga.registers.eth_packets_per_accum_window.write_int(16384 / dataSizePerPacket_B)

print '10 Gb link is up.'
sys.stdout.flush()

print '\n---------------------------'
print 'Setting FFT shift and accumulation length.'
#Setup values for WB spectrum output
fpga.registers.fft_shift.write_int(FFTShift) #Shift for each FFT stage (2048 points -> 11 stages. Value is a bit mask so decimal of 11111111111. i.e. 2047)
fpga.registers.accumulation_length.write_int(accumulationLength) #Accumulate for this many FFT frames before outputting

print '\n---------------------------'
print 'Enabling ADCs and setting attentuation.'
#Enable the ADCs
fpga.registers.adc_ctrl.write(adc0_en=1,adc0_atten=ADC_attenuation, adc1_en=1, adc1_atten=ADC_attenuation)

print '\n---------------------------'
print 'Configuring noise diode.'
fpga.registers.noise_diode_on_length.write_int(250) #Set noise diode duty-cycle in accumulation windows (note values can't be 0 will default to 1)
fpga.registers.noise_diode_off_length.write_int(1000)

fpga.registers.noise_diode_duty_cycle_en.write_int(1) #Noise diode mode: always on (0) or duty-cycle (1) as set above.
fpga.registers.noise_diode_en.write_int(1) #Global enabling or disabling of noise diode

print '\n---------------------------'
print 'Setting RTC and signal board to resync on next PPS pulse...'

#Check clock frequency
clkFreq = fpga.registers.clk_frequency.read_uint()
print 'Clock frequency is: ', clkFreq, ' Hz'
if(clkFreq == 200000000):
  print 'Frequency correct.'
else:
  print '!! Error clock frequency is not correct. Check 10 MHz reference and PPS and that Valon is locked to Ext-Ref !!'


#Important note order of commands: first load time then strobe sync_next_pps. Recommend NTP sync before this if a NTP daemon is not running on this computer.
timeNextPPS = int(round((time.time()) + 1) * 1000000) # +1 for next PPS
timeLSB = (timeNextPPS & 0x00000000ffffffff)
timeMSB = int((timeNextPPS & 0xffffffff00000000) / 2**32)

fpga.registers.time_lsb.write_int(timeLSB)
fpga.registers.time_msb.write_int(timeMSB)

fpga.registers.sync_next_pps.write_int(1)
fpga.registers.sync_next_pps.write_int(0)

print 'Setting RTC time to    ', timeNextPPS, ' us'
print 'Waiting 1 s to allow for PPS strobe...'
time.sleep(1)

lastTime = fpga.registers.last_timestamp_msb.read_uint() * 2**32 + fpga.registers.last_timestamp_lsb.read_uint()
print 'Last FPGA timestamp was', lastTime, ' us'

timeDifference = lastTime - timeNextPPS

print 'Difference is', timeDifference, 'us'
if(abs(timeDifference) > 1000000):
  print 'Error time is out by > 1 s. Check PPS and clock reference'
else:
  print 'Offset < 1 s. Time primed correctly.'


print '\n---------------------------'
print 'Done'