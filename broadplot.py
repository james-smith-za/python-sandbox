#! /bin/python
'''Python script to get the basics right for plotting fine and several coarse FFT data.
'''
import matplotlib.pyplot as plt
import numpy
import time

coarse_fft_size = 256
fine_fft_size = 4096

coarse_fft_channel = 128

freq_coarse = numpy.linspace(0,coarse_fft_size,coarse_fft_size)
freq_fine = numpy.linspace(0,fine_fft_size,fine_fft_size)

coarse_LCP = numpy.cos(freq_coarse/256 )
coarse_RCP = numpy.sin(freq_coarse/256 )

fine_LCP = numpy.cos(freq_fine/1024)
fine_RCP = numpy.sin(freq_fine/1024)

plt.ion() # This is required to let the script continue after the figure has been shown.

plt.close('all')
fig = plt.figure(figsize=(20,10)) # Fills most of the screen

ax = []

ax.append(plt.subplot2grid((3,5), (0,0), colspan=5))    # 0 - coarse FFT
ax.append(plt.subplot2grid((3,5), (1,0)))               # 1 - fine FFT channel - 2
ax.append(plt.subplot2grid((3,5), (1,1)))               # 2 - fine FFT channel - 1
ax.append(plt.subplot2grid((3,5), (1,2)))               # 3 - fine FFT channel
ax.append(plt.subplot2grid((3,5), (1,3)))               # 4 - fine FFT channel + 1
ax.append(plt.subplot2grid((3,5), (1,4)))               # 5 - fine FFT channel + 2
ax.append(plt.subplot2grid((3,5), (2,0), colspan=5))    # 6 - fine FFT channel zoomed

ax[0].plot(coarse_LCP, 'b-')
ax[0].plot(coarse_RCP, 'r-')
ax[0].set_title('Coarse FFT')
ax[0].set_xlim(0, coarse_fft_size-1)
ax[0].xaxis.set_ticks(numpy.arange(0,coarse_fft_size))

if (coarse_fft_channel - 2) >=  0:
    ax[1].plot(fine_LCP, 'b-')
    ax[1].plot(fine_RCP, 'r-')
    ax[1].set_xlim(0, fine_fft_size-1)
    ax[1].set_title('Fine ch %d'%(coarse_fft_channel - 2))
    ax[1].xaxis.set_ticklabels([])


if (coarse_fft_channel - 1) >= 0:
    ax[2].plot(fine_LCP, 'b-')
    ax[2].plot(fine_RCP, 'r-')
    ax[2].set_xlim(0, fine_fft_size-1)
    ax[2].xaxis.set_ticklabels([])

ax[3].plot(fine_LCP, 'b-')
ax[3].plot(fine_RCP, 'r-')
ax[3].set_xlim(0, fine_fft_size-1)
ax[3].set_title('Fine ch %d'%(coarse_fft_channel))
ax[3].xaxis.set_ticklabels([])


if (coarse_fft_channel + 1) < fine_fft_size:
    ax[4].plot(fine_LCP, 'b-')
    ax[4].plot(fine_RCP, 'r-')
    ax[4].set_xlim(0, fine_fft_size-1)
    ax[4].set_title('Fine ch %d'%(coarse_fft_channel + 1))
    ax[4].xaxis.set_ticklabels([])


if (coarse_fft_channel + 2) < fine_fft_size - 1:
    ax[5].plot(fine_LCP, 'b-')
    ax[5].plot(fine_RCP, 'r-')
    ax[5].set_xlim(0, fine_fft_size-1)
    ax[5].set_title('Fine ch %d'%(coarse_fft_channel + 2))
    ax[5].xaxis.set_ticklabels([])


ax[6].plot(fine_LCP, 'b-')
ax[6].plot(fine_RCP, 'r-')
ax[6].set_xlim(0, fine_fft_size-1)
ax[6].set_title('Fine FFT channel %d'%(coarse_fft_channel))

# plt.tight_layout()
plt.draw() # Use this instead of show(). For some reason.
time.sleep(2)

hello = raw_input('Hello.')
