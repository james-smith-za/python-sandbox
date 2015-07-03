#!/bin/python
'''Test script to see whether casperfpga will work.
'''

import casperfpga
import time

roach = 'localhost'
katcp_port = 7148
filename = 'led_2_2015_Apr_22_1520'

print 'Connecting...'
fpga = casperfpga.katcp_fpga.KatcpFpga(roach,katcp_port)
fpga.program(filename + '.bof')

print 'getting system information'
fpga.get_system_information(filename + '.fpg')
print 'starting on the while loop'

while 1:
    fpga.registers.leds.write(l0=False, l1=True, l2=False, l3=True, l4=False,
            l5=True, l6=False, l7=True)
    time.sleep(0.25)
    fpga.registers.leds.write(l0=True, l1=False, l2=True, l3=False, l4=True,
            l5=False, l6=True, l7=False)
    time.sleep(0.25)

