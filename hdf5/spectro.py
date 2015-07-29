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

import collections
import matplotlib
matplotlib.use('gtkagg') # Necessary on optimus for some reason - older version of matplotlib.
from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib.widgets import Slider

data_width = multiprocessing.Value('H', 1024)
frame_length = multiprocessing.Value('H', 16)

data_stream_1 = multiprocessing.Array('f', data_width.value) # single-precision floating-point for now.
data_stream_2 = multiprocessing.Array('f', data_width.value)
data_stream_3 = multiprocessing.Array('f', data_width.value)
data_stream_4 = multiprocessing.Array('f', data_width.value)

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

def raw_deinterleaver(input_queue, output_queue, plot_queue):
    '''
    Process for deinterleaving raw FFT data and plotting.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    time.sleep(1)
    while 1:
        LCP = []
        RCP = []

        interleavedWindow = np.array(input_queue.get())
        if interleavedWindow == None:
            break

        index = 0

        even1 = (interleavedWindow[0::8] + interleavedWindow[1::8]*1j)
        odd1  = (interleavedWindow[2::8] + interleavedWindow[3::8]*1j)
        LCP   = np.reshape(np.dstack((even1, odd1)), (1,-1))

        even2 = (interleavedWindow[4::8] + interleavedWindow[5::8]*1j)
        odd2  = (interleavedWindow[6::8] + interleavedWindow[7::8]*1j)
        RCP   = np.reshape(np.dstack((even2, odd2)), (1, -1))

        #need to figure out here how to write out to the plotting function.

        output_queue.put((LCP,RCP))
        plot_queue.put((LCP,RCP))
    print 'raw_deinterleaver found poison pill'
    output_queue.put(None)

def raw_plot_decimator(input_queue, decimation = 10):
    '''
    Processing for decimating the rate at which the data is plotted. This is for the raw FFT data case.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    data = input_queue.get()
    while data != None:
        for i in range(decimation):
            data = input_queue.get()
        LCP, RCP = data
        for i in range(data_width):
            data_stream_1[i] = np.square(np.abs(LCP[i]))
            data_stream_2[i] = np.square(np.abs(RCP[i]))

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
    ax = plt.subplot(1, 1, 1)
    line_lcp, = ax.plot([], [], 'bo', lw=1)
    line_rcp, = ax.plot([], [], 'ro', lw=1)
    ax.set_xlim(0,400)

    vav_data_lcp = collections.deque(maxlen = waterfall_size)
    vav_data_rcp = collections.deque(maxlen = waterfall_size)

    slider_ax = plt.axes([0.25, 0.1, 0.65, 0.03])

    video_average_length_slider = Slider(slider_ax, 'VAv', 1, waterfall_size, valinit=video_average_length.value)
    def update(val):
        video_average_length.value = int(video_average_length_slider.val)
        fig.canvas.draw_idle()
    video_average_length_slider.on_changed(update)

    def init():
        x = np.zeros(data_width)
        y = np.zeros(data_width)
        line_lcp.set_data(x,y)
        line_rcp.set_data(x,y)
        return line,

    def animate(*args):
        if script_run.value != 1:
            sys.exit()
        x = np.arange(0, 400, 400.0 / 1024.0)
        vav_data_lcp.appendleft(data_stream_1[:])
        vav_data_rcp.appendleft(data_stream_2[:])
        lcp = np.zeros(data_width)
        rcp = np.zeros(data_width)
        for i in range(video_average_length.value):
            if i < len(vav_data):
                lcp += np.array(vav_data_lcp[i])
                rcp += np.array(vav_data_rcp[i])
        lcp /= video_average_length.value
        rcp /= video_average_length.value
        graph_max = 0
        if lcp.max() > rcp.max():
            graph_max = lcp.max()
        else:
            graph_max = rcp.max()
        ax.set_ylim(0,graph_max + 1)
        line_lcp.set_data(x,lcp)
        line_rcp.set_data(x.rcp)
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
    deint_plot_queue = multiprocessing.Queue()

    # Initialise shared memory values
    for i in range(data_width):
        data_stream_1[i] = 0.0
        data_stream_2[i] = 0.0
        data_stream_3[i] = 0.0
        data_stream_4[i] = 0.0


    UDP_receiver_process = multiprocessing.Process(name='UDP receiver', target=UDP_receiver, args=(data_deint_queue,))
    raw_deinterleaver_process = multiprocessing.Process(name='raw deinterleaver', target=raw_deinterleaver, args=(data_deint_queue, deint_hdf5_queue))
    hdf5_writer_process = multiprocessing.Process(name='HDF5 Writer', target=hdf5_writer, args=(deint_hdf5_queue,))
    plotter_process = multiprocessing.Process(name="Plotter", target=plotter)
    diagnostics_process = multiprocessing.Process(name='diag', target=diagnostic_info, args=(data_deint_queue, deint_hdf5_queue))

    UDP_receiver_process.start()
    raw_deinterleaver_process.start()
    hdf5_writer_process.start()
    plotter_process.start()
    diagnostics_process.start()

    signal.pause()

    UDP_receiver_process.join()
    raw_deinterleaver_process.join()
    hdf5_writer_process.join()
    plotter_process.join()
    diagnostics_process.join()

    print '\n'
