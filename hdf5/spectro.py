#!/usr/bin/python
'''
TBH too lazy to make the docstring at the moment - JNS
'''
import h5py
import numpy as np
import time
import multiprocessing
import signal
# The following for the plotting. If not for plotting, needn't be in the script.
import collections # Has the most excellent deque object which helps tremendously.

import socket
import struct
import sys
import os

import matplotlib
matplotlib.use('gtkagg')
from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib.widgets import Slider

data_width = 1024

current_data_frame = multiprocessing.Array('f', data_width) # single-precision floating-point for now.
script_run = multiprocessing.Value('B', 1) # Boolean to keep track of whether the program shold actually run, initialise to 1
video_average_length = multiprocessing.Value('B', 10) # This is a bit of a hack, but it seems to work fine...



def ctrl_c(signal, frame):
    '''
    To be called when SIGINT received. Sets the 'script_run' variable to false so
    that the processes stop sanely. Important for not losing HDF5 data.
    '''
    # Though now I'm thinking about it, going to have to figure out some way to tell the script
    # when to stop _other_ than sitting in front of the keyboard to press ctrl+c at the right
    # time...
    print '\n##################### Ctrl+C pressed, exiting sanely...#####################\n'
    script_run.value = 0



def UDP_receiver(output_queue):
    '''
    This process destined to be replaced by an actual socket once I've finished working with Craig
    on the outputs of his FPGA fabric.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.

    localInterface = "10.0.0.3"
    localPort = 60000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((localInterface, localPort))

    print "Bound to UDP socket ", localInterface, ":", localPort


    #Each FFT window is 4 packets of 4096 bytes each

    while script_run.value == 1:

        interleavedWindow = []
        for packetNo in range (0, 4):
            data, addr = sock.recvfrom(4096)
            #print 'Got packet ', packetNo, '  at  ', time.ctime(), ' from ', addr

            interleavedWindow.extend( list(struct.unpack("!IQHH1024i", data)) ) #interpret as integer data and append to window list
        output_queue.put(interleavedWindow)

    print 'poison pill received by data generator'
    output_queue.put(None)

def deinterleaver(input_queue, output_queue):
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    time.sleep(1)
    while 1:
        LCP = []
        RCP = []

        interleavedWindow = input_queue.get()
        if interleavedWindow == None:
            break

        index = 0

        for i in range(0, data_width/2): # data_width/2 because even and odd are interleaved
            even1real = interleavedWindow[index]
            index += 1
            even1imag = interleavedWindow[index]
            index += 1
            LCP.append(even1real + even1imag*1j)
            current_data_frame[2*i] = np.square(np.abs(even1real + even1imag*1j))

            odd1real = interleavedWindow[index]
            index += 1
            odd1imag = interleavedWindow[index]
            index += 1
            LCP.append(odd1real + odd1imag*1j)
            current_data_frame[2*i + 1] = np.square(np.abs(odd1real + odd1imag*1j))

            even2real = interleavedWindow[index]
            index += 1
            even2imag = interleavedWindow[index]
            index += 1
            RCP.append(even2real + even2imag*1j)

            odd2real = interleavedWindow[index]
            index += 1
            odd2imag = interleavedWindow[index]
            index += 1
            RCP.append(odd2real + odd2imag*1j)

        LCP = np.array(LCP)
        RCP = np.array(RCP)
        output_queue.put((LCP,RCP))
    print 'deinterleaver found poison pill'
    output_queue.put(None)

def hdf5_writer(input_queue):
    '''
    Process will read from input queue and (eventually) write out to HDF5 file.
    worthwhile accumulating a bit (32MB?) before you write. To prevent too-frequent disk activity.
    Also, Ludwig mentioned that we should keep the timestamps in memory and write them only at the very end,
    so that they're not peppered throughout the file and eventually take ages to read.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    data = input_queue.get()
    while (data != None):
        # This is where the data needs to be written... before the next one is gotten.
        data = input_queue.get()
    print 'poison pill received by hdf5 writer'


def plotter():
    '''
    This process is supposed to handle the graphs.
    Not pretty at the moment... but then matplotlib never is.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    waterfall_size = 150 # This makes it about 75 seconds in theory. Drawing the graph sometimes takes a bit longer.
    fig = plt.figure(figsize=(20,15))
    plt.subplots_adjust(left = 0.1, bottom = 0.25)
    ax = plt.subplot(2, 1, 2)
    line, = ax.plot([], [], lw=1, marker='o')
    ax.set_xlim(0,400)

    data = collections.deque(maxlen = waterfall_size)

    slider_ax = plt.axes([0.25, 0.1, 0.65, 0.03])

    video_average_length_slider = Slider(slider_ax, 'VAv', 1, waterfall_size, valinit=video_average_length.value)
    def update(val):
        video_average_length.value = int(video_average_length_slider.val)
        fig.canvas.draw_idle()
    video_average_length_slider.on_changed(update)

    def init():
        x = np.zeros(data_width)
        y = np.zeros(data_width)
        line.set_data(x,y)
        return line,

    def animate(*args):
        if script_run.value != 1:
            sys.exit()
        x = np.arange(0, 400, 400.0 / 1024.0)
        data.appendleft(current_data_frame[:])
        y = np.zeros(data_width)
        for i in range(video_average_length.value):
            if i < len(data):
                y += np.array(data[i])
        y /= video_average_length.value
        ax.set_ylim(0,y.max() + 1)
        line.set_data(x,y)
        return line,

    # Set the animation off to a start...
    anim = animation.FuncAnimation(fig, animate, init_func=init, blit=True, interval=500)
    plt.show()
    print 'plotter process finished.'

def diagnostic_info(q1, q2):
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    print 'PID: ', os.getpid()
    diagnose=True
    q1s, q2s = 0, 0
    while diagnose or q1s > 0 or q2s > 0 :
        q1s, q2s = q1.qsize(), q2.qsize()
        sys.stdout.write('\rdata-deint queue length: %d\t\tdeint-hdf5 queue length: %d'%(q1s, q2s))
        sys.stdout.flush()
        if script_run.value == 0:
            diagnose = False
        time.sleep(0.2)

    print 'diagnostic process joining.'

if __name__ == '__main__':
    signal.signal(signal.SIGINT, ctrl_c)

    data_deint_queue = multiprocessing.Queue()
    deint_hdf5_queue = multiprocessing.Queue()

    UDP_receiver_process = multiprocessing.Process(name='UDP receiver', target=UDP_receiver, args=(data_deint_queue,))
    deinterleaver_process = multiprocessing.Process(name='deinterlacer', target=deinterleaver, args=(data_deint_queue, deint_hdf5_queue))
    hdf5_writer_process = multiprocessing.Process(name='HDF5 Writer', target=hdf5_writer, args=(deint_hdf5_queue,))
    plotter_process = multiprocessing.Process(name="Plotter", target=plotter)
    diagnostics_process = multiprocessing.Process(name='diag', target=diagnostic_info, args=(data_deint_queue, deint_hdf5_queue))

    UDP_receiver_process.start()
    deinterleaver_process.start()
    hdf5_writer_process.start()
    plotter_process.start()
    diagnostics_process.start()

    signal.pause()

    UDP_receiver_process.join()
    deinterleaver_process.join()
    hdf5_writer_process.join()
    plotter_process.join()
    diagnostics_process.join()

    print '\n'
