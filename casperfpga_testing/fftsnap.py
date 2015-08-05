#!/bin/python
'''snap and plot FFTs from the ROACH
'''

import casperfpga
import time
import matplotlib.pyplot as plt
import numpy as np

#roach = 'catseye'
roach = 'catseye'
katcp_port = 7147
filename = 'wb_spectrometer_sd_real_2_2015_Jul_30_1406'
accumulation_length = 10 # times by 8 to get the actual length

print 'Connecting...'
fpga = casperfpga.katcp_fpga.KatcpFpga(roach,katcp_port)
fpga.system_info['program_filename'] = filename + '.bof' # Not completely sure how this is done on ROACH2 - perhaps someone can clarify?
fpga.program()

print 'getting system information' # This step only necessary on ROACH1
fpga.get_system_information(filename + '.fpg') # fpg file needs to be in current directory, bof file needs to be in the ROACH's bof files
print 'starting on the while loop'

fpga.registers.manual_sync.write_int(1)
fpga.registers.manual_sync.write_int(0)

fpga.registers.fft_shift.write_int(2047)
fpga.registers.adc_ctrl.write(adc0_en=True, adc1_en=True)

fig = plt.figure()
ax1 = plt.subplot(211)
line_lcp, = ax1.plot([], [], 'b', lw=1)
ax2 = plt.subplot(212)
line_rcp, = ax2.plot([], [], 'r', lw=1)
ax1.set_xlim(0,400)
ax2.set_xlim(0,400)
ax1.set_ylim(0,200)
ax2.set_ylim(0,200)
plt.title('FFTs')
plt.xlabel('Frequency(MHz)')
plt.ylabel('Relative power [dB]')

x = np.arange(0, 400, 400.0 / 1024)

plt.ion()
plt.show()

while 1:
    print 'new while loop'

    lcp_acc = np.zeros(1024)
    rcp_acc = np.zeros(1024)

    for i in range(accumulation_length):
        print 'for loop %d'%(i)

        lcp_data = fpga.snapshots.lcp_snap_ss.read()
        rcp_data = fpga.snapshots.rcp_snap_ss.read()

        l_er = np.array(lcp_data['data']['er'])
        l_ei = np.array(lcp_data['data']['ei'])
        l_even = l_er + l_ei*1j
        l_even = l_even[0:512] + l_even[512:1024] + l_even[1024:1536] + l_even[1536:2048] + l_even[2048:2560] + l_even[2560:3072] + l_even[3072:3584] + l_even[3584:4096]
        l_or = np.array(lcp_data['data']['or'])
        l_oi = np.array(lcp_data['data']['oi'])
        l_odd = l_or + l_oi*1j
        l_odd = l_odd[0:512] + l_odd[512:1024] + l_odd[1024:1536] + l_odd[1536:2048] + l_odd[2048:2560] + l_odd[2560:3072] + l_odd[3072:3584] + l_odd[3584:4096]

        r_er = np.array(lcp_data['data']['er'])
        r_ei = np.array(lcp_data['data']['ei'])
        r_even = r_er + r_ei*1j
        r_even = r_even[0:512] + r_even[512:1024] + r_even[1024:1536] + r_even[1536:2048] + r_even[2048:2560] + r_even[2560:3072] + r_even[3072:3584] + r_even[3584:4096]
        r_or = np.array(lcp_data['data']['or'])
        r_oi = np.array(lcp_data['data']['oi'])
        r_odd = r_or + r_oi*1j
        r_odd = r_odd[0:512] + r_odd[512:1024] + r_odd[1024:1536] + r_odd[1536:2048] + r_odd[2048:2560] + r_odd[2560:3072] + r_odd[3072:3584] + r_odd[3584:4096]

        lcp = np.reshape(np.dstack((l_even, l_odd)), (1,-1))
        rcp = np.reshape(np.dstack((r_even, r_odd)), (1,-1))

        lcp_acc += np.square(np.abs(lcp[0]))
        rcp_acc += np.square(np.abs(rcp[0]))

    lcp_acc = 10*np.log10(lcp_acc + 1)
    rcp_acc = 10*np.log10(rcp_acc + 1)

    line_lcp.set_data(x,lcp_acc)
    line_rcp.set_data(x,rcp_acc)

    fig.canvas.draw()

