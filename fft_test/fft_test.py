'''
Script to demonstrate two-stage FFT-ing and the finer frequency resolution achievable through it.
'''
import numpy as np
import matplotlib.pyplot as plt

# Preliminaries
sine_frequency = 323.0*2*np.pi
cos_frequency = 327.0*2*np.pi # Pretty close to each other, so as to be in the same coarse frequency bin
sine_period = 1.0/sine_frequency
sampling_rate = 1000.0
sampling_period = 1.0/ sampling_rate

coarse_fft_size = 64
coarse_channels = coarse_fft_size / 2
coarse_channel_resolution = sampling_rate / coarse_fft_size
print 'coarse channel resolution: %f Hz'%(coarse_channel_resolution)

# Array representing time space, 30 seconds of signal sampled at sampling_rate
t = np.arange(0,30,step=sampling_period)
# Set up a signal with a big component and a little one, but they must be close to each other so as not to make more than one spike
x = np.sin(sine_frequency*t) + 0.2*np.cos(cos_frequency*t)
X = np.fft.fft(np.hamming(coarse_fft_size)*x[0:coarse_fft_size],n=64)

# Find where the peak of the spike is.
coarse_channel_with_tone = np.argmax(np.abs(X))
coarse_channel_with_tone_freq = (coarse_channel_with_tone - 1)*coarse_channel_resolution
print 'channel with largest value: %d, %f'%(coarse_channel_with_tone, np.abs(X[coarse_channel_with_tone]))
print 'channel\'s frequency: %f'%(coarse_channel_with_tone_freq)

# Set up the fine FFT. Finer resolution than the coarse one.
fine_fft_size = 128
fine_channels = fine_fft_size # not /2 (thanks Griffin) because it's getting a complex input
fine_channel_resolution = coarse_channel_resolution / fine_fft_size
print 'fine channel resoultion: %f Hz'%(fine_channel_resolution)

intermediate_signal = []

# Clunky way of doing it, but for demonstration purposes it seems to work.
for i in range(0,fine_fft_size):
    X = np.fft.fft(np.hamming(coarse_fft_size)*x[i*coarse_fft_size:(i+1)*coarse_fft_size],n=64)
    intermediate_signal.append(X[coarse_channel_with_tone])

x2 = np.array(intermediate_signal)
X2 = np.fft.fft(np.hamming(fine_fft_size)*x2) # Don't need to bother with n=128 this time because there are only 128 elements in the array

fine_channel_with_tone = np.argmax(abs(X2))
fine_channel_with_tone_freq = coarse_channel_with_tone_freq + (fine_channel_with_tone * fine_channel_resolution)

print 'fine channel with largest value: %d, %f'%(fine_channel_with_tone, np.abs(X2[fine_channel_with_tone]))
print 'channel\'s frequency: %f Hz'%(fine_channel_with_tone_freq)

plt.plot(abs(X2))
plt.grid('on')
plt.show()

# Results seem to come out all correct for me...



