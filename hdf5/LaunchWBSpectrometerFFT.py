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

##### Variable to be set ###########

#Gateware to be loaded.a bof should be on the ROACH and a fpg file in the same directory as this script
gateware = 'wb_spectrometer_09_2015_Jul_30_1734'

#Network:
strDestinationIP = '10.0.0.3'
destinationPort = 60000

#Set frame data length in bytes must be submultiple of 16384 ( 1024 frequencies * 2 for complex * 2 for 2 channels with each value a 4 byte uint32_t. Also excludes 8 bytes header of each frame)
#Set interframe length clock cycles, (note 64 bytes can be transferred per cyle)
dataSizePerPacket_B = 1024
interpacketLength_cycles = 16

#FFT shift (With the number in binary each bit represents whether the corresponding stage should right shift once.There are 2048 stages)
FFTShift = 2047 #shift all stages.

#How many FFT frames to accumulate for. Note: This is inversely proportional to output rate and time resolution and directly proportional to size of output numbers
accumulationLength = 3125 # this makes 8 ms, which divides nice and evenly into a second.

ADC_attenuation = 0

####################################

packedIP = socket.inet_aton(strDestinationIP)
destinationIP = struct.unpack("!L", packedIP)[0]

print '\n---------------------------'
print 'Configuration:'
print '---------------------------'
print ' FPGA gateware:         ', gateware
print ' Destination 10GbE host:', strDestinationIP, '( ', destinationIP, ' )'
print ' Data size per packet:  ', dataSizePerPacket_B, ' bytes'
print ' Interpacket length     ', interpacketLength_cycles, ' cycles'
print ' FFT shift mask         ', FFTShift
print ' Accumulation length    ', accumulationLength, '(', 2048 * accumulationLength / 800e3, ' ms integration per output )'
print '---------------------------'

print '\n---------------------------'
print 'Connecting to FPGA...'
fpga = casperfpga.katcp_fpga.KatcpFpga('catseye', port=7147)

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

fpga.registers.tgbe0_dest_ip.write(reg = destinationIP)
fpga.registers.tgbe0_dest_port.write(reg = destinationPort)
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

print '10 Gb link is up.\n'
sys.stdout.flush()

print '\n---------------------------'
print 'Setting FFT shift and accumulation length'
#Setup values for WB spectrum output
fpga.registers.fft_shift.write_int(FFTShift) #Shift for each FFT stage (2048 points -> 11 stages. Value is a bit mask so decimal of 11111111111. i.e. 2047)
fpga.registers.accumulation_length.write_int(accumulationLength) #Accumulate for this many FFT frames before outputting

print '\n---------------------------'
print 'Enabling ADCs and setting attentuation'
#Enable the ADCs
fpga.registers.adc_ctrl.write(adc0_en=1,adc0_atten=ADC_attenuation, adc1_en=1, adc1_atten=ADC_attenuation)

print '\n---------------------------'
print 'Sending manually triggered sync pulse'
fpga.registers.sync_next_pps.write_int(1)
fpga.registers.sync_next_pps.write_int(0)

print '\n---------------------------'
print 'Resetting Ethernet'
#time.sleep(1) # Wait 1 second and then reset ethernet
#Reset the Packetiser and 10GbE
#fpga.registers.eth_reset.write_int(1)
#fpga.registers.eth_reset.write_int(0)

print '\n---------------------------'
print 'Done'

