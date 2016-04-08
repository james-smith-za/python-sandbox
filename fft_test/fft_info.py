#!/usr/bin/python

import numpy as np

# FFT Information
fft_points = 2**11
fft_magnitude = fft_points / 2
sampling_frequency = 800.0e6 # Hz
sampling_period = 1.0 / sampling_frequency
fpga_frequency = 200e6
fpga_period = 1.0 / fpga_frequency

tone_frequency = np.arange(50, 150, 25, dtype=np.float)*1e6
tone_period = 1.0 / tone_frequency
tone_fpga_period = tone_period / fpga_period


print "FFT Information:"
print "Sampling frequency: \t\t%.2e Hz"%(sampling_frequency)
print "Bandwidth: \t\t\t%.2e Hz"%(sampling_frequency / 2)

spectral_resolution = sampling_frequency / fft_magnitude
print "Spectral resolution: \t\t%.2e Hz"%(spectral_resolution)

frequency_bins = np.arange(0, fft_magnitude - 1, 1.0, np.float)*sampling_frequency / fft_magnitude

print "\n"

fpga_sampling_freq = fpga_frequency / sampling_frequency
print "Sample time: \t\t\t%.2f fpga clocks"%(fpga_sampling_freq)
print "Sample time: \t\t\t%.2e seconds"%(1.0 / sampling_frequency)

print "\n"

for i in range(len(tone_frequency)):
    print "Tone frequency:\t%.2e Hz \t\tTone period:\t%.2e s"%(tone_frequency[i], tone_period[i])
    print "\tTone period in fpga clocks: \t%f"%(tone_fpga_period[i])
    print "\tTone period in samples: \t%f"%(tone_fpga_period[i]*4)
