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

import matplotlib
matplotlib.use('gtkagg')
from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib.widgets import Slider

current_data_frame = multiprocessing.Array('f', 2048) # single-precision floating-point for now.
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
        for packetNo in range (0, 8):
            data, addr = sock.recvfrom(4096)
            print 'Got packet at  ', time.ctime(), ' from ', addr
            interleavedWindow.extend( list(struct.unpack("!1024i", data)) ) #interpret as integer data and append to window list
        output_queue.put(interleavedWindow)

    print 'poison pill received by data generator'
    output_queue.put(None)

def deinterleaver(input_queue, output_queue):
    while script_run.value == 1:
        I = []
        Q = []
        U = []
        V = []

        interleavedWindow = input_queue.get()
        index = 0

        for i in range(0, 2048):
            I.append(interleavedWindow[index])
            current_data_frame[i] = interleavedWindow[index]
            index += 1
            Q.append(interleavedWindow[index])
            index += 1
            U.append(interleavedWindow[index])
            index += 1
            V.append(interleavedWindow[index])
            index += 1

        I = np.array(I)
        output_queue.put(I)
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
    ax.set_ylim(0,10000)
    ax.set_xlim(0,2047)

    data = collections.deque(maxlen = waterfall_size)

    slider_ax = plt.axes([0.25, 0.1, 0.65, 0.03])

    video_average_length_slider = Slider(slider_ax, 'VAv', 1, waterfall_size, valinit=video_average_length.value)
    def update(val):
        video_average_length.value = int(video_average_length_slider.val)
        fig.canvas.draw_idle()
    video_average_length_slider.on_changed(update)

    def init():
        x = np.zeros(2048)
        y = np.zeros(2048)
        line.set_data(x,y)
        return line,

    def animate(*args):
        x = range(2048)
        data.appendleft(current_data_frame[:])
        y = np.zeros(2048)
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


if __name__ == '__main__':
    signal.signal(signal.SIGINT, ctrl_c)

    data_deint_queue = multiprocessing.Queue()
    deint_hdf5_queue = multiprocessing.Queue()

    UDP_receiver_process = multiprocessing.Process(name='UDP receiver', target=UDP_receiver, args=(data_deint_queue,))
    deinterleaver_process = multiprocessing.Process(name='deinterlacer', target=deinterleaver, args=(data_deint_queue, deint_hdf5_queue))
    hdf5_writer_process = multiprocessing.Process(name='HDF5 Writer', target=hdf5_writer, args=(deint_hdf5_queue,))
    plotter_process = multiprocessing.Process(name="Plotter", target=plotter)

    UDP_receiver_process.start()
    deinterleaver_process.start()
    hdf5_writer_process.start()
    plotter_process.start()

    signal.pause()

    UDP_receiver_process.join()
    deinterleaver_process.join()
    hdf5_writer_process.join()
    plotter_process.join()

