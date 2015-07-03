#!/usr/bin/python
import numpy as np
import matplotlib.pyplot as plt
import os

filename = '../' + os.getcwd()[os.getcwd().rfind(u'/') + 1:] + '.png' # Sometimes I am so clever I even amaze myself.

LCP_coarse_accumulator = np.loadtxt('coarse_LCP')
RCP_coarse_accumulator = np.loadtxt('coarse_RCP')
LCP_fine_accumulator = np.loadtxt('fine_LCP')
RCP_fine_accumulator = np.loadtxt('fine_RCP')

coarse_channel = 102
coarse_fft_size = 256
fine_fft_size = 4096

ax = []

ax.append(plt.subplot2grid((3,5), (0,0), colspan=5))    # 0 - coarse FFT
ax.append(plt.subplot2grid((3,5), (1,0)))               # 1 - fine FFT channel - 2
ax.append(plt.subplot2grid((3,5), (1,1)))               # 2 - fine FFT channel - 1
ax.append(plt.subplot2grid((3,5), (1,2)))               # 3 - fine FFT channel
ax.append(plt.subplot2grid((3,5), (1,3)))               # 4 - fine FFT channel + 1
ax.append(plt.subplot2grid((3,5), (1,4)))               # 5 - fine FFT channel + 2
ax.append(plt.subplot2grid((3,5), (2,0), colspan=5))    # 6 - fine FFT channel zoomed

ax[0].plot(LCP_coarse_accumulator, 'b-')
ax[0].plot(RCP_coarse_accumulator, 'r-')
ax[0].set_title('Coarse FFT')
ax[0].set_xlim(0, coarse_fft_size-1)
ax[0].xaxis.set_ticks(np.arange(0,coarse_fft_size), 8)

if (coarse_channel - 2) >=  0 :
    ax[1].plot(LCP_fine_accumulator[0], 'b-')
    ax[1].plot(RCP_fine_accumulator[0], 'r-')
    ax[1].set_xlim(1, fine_fft_size-1) # From 1 because I want to try and remove a potentially big DC bin from the plot.
    ax[1].set_title('Fine ch %d'%(coarse_channel - 2))
    ax[1].xaxis.set_ticklabels([])

if (coarse_channel - 1) >= 0 :
    ax[2].plot(LCP_fine_accumulator[1], 'b-')
    ax[2].plot(RCP_fine_accumulator[1], 'r-')
    ax[2].set_xlim(0, fine_fft_size-1)
    ax[2].set_title('Fine ch %d'%(coarse_channel - 1))
    ax[2].xaxis.set_ticklabels([])

ax[3].plot(LCP_fine_accumulator[2], 'b-')
ax[3].plot(RCP_fine_accumulator[2], 'r-')
ax[3].set_xlim(0, fine_fft_size-1)
ax[3].set_title('Fine ch %d'%(coarse_channel))
ax[3].xaxis.set_ticklabels([])

if (coarse_channel + 1) < fine_fft_size :
    ax[4].plot(LCP_fine_accumulator[3], 'b-')
    ax[4].plot(RCP_fine_accumulator[3], 'r-')
    ax[4].set_xlim(0, fine_fft_size-1)
    ax[4].set_title('Fine ch %d'%(coarse_channel + 1))
    ax[4].xaxis.set_ticklabels([])

if (coarse_channel + 2) < fine_fft_size - 1 :
    ax[5].plot(LCP_fine_accumulator[4], 'b-')
    ax[5].plot(RCP_fine_accumulator[4], 'r-')
    ax[5].set_xlim(0, fine_fft_size-1)
    ax[5].set_title('Fine ch %d'%(coarse_channel + 2))
    ax[5].xaxis.set_ticklabels([])

ax[6].plot(LCP_fine_accumulator[2], 'b-')
ax[6].plot(RCP_fine_accumulator[2], 'r-')
ax[6].set_xlim(0, fine_fft_size-1)
ax[6].set_title('Fine FFT channel %d'%(coarse_channel))

ax[1].set_ylim(ax[3].get_ylim())
ax[2].set_ylim(ax[3].get_ylim())
ax[4].set_ylim(ax[3].get_ylim())
ax[5].set_ylim(ax[3].get_ylim())

plt.savefig(filename)


