#!/usr/bin/python
'''
TBH too lazy to make the docstring at the moment - JNS
'''

import socket
import struct
import multiprocessing
import signal
import sys
import time
import os
import numpy as np

import collections

import matplotlib
matplotlib.use('gtkagg') # Necessary on optimus for some reason - older version of matplotlib.
from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib.widgets import Slider

data_width = 1024

###################### Multiprocessing shared values ######################
script_run = multiprocessing.Value('B', 1) # Boolean to keep track of whether the program shold actually run, initialise to 1

data_mode = multiprocessing.Value('h', -1) # Signed short so that I can use a -1 until such time as the right mode comes through
pkt_len = multiprocessing.Value('H', 0)
fft_win_len = multiprocessing.Value('H', 0)
pkt_smpl_len = multiprocessing.Value('H', 0)
frame_len = multiprocessing.Value('H', 0)

frame_number = multiprocessing.Value('L', 0)
good_frames = multiprocessing.Value('L', 0)
bad_frames = multiprocessing.Value('L', 0)


video_average_length = multiprocessing.Value('B', 1) # This is a bit of a hack, but it seems to work fine...


###################### Signal handler functions ######################
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


###################### Process functions ######################
def UDP_receiver(output_queue):
    '''
    A life dedicated to grabbing UDP packets and sticking them on a queue
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.


    udp_process_priority = -19
    time.sleep(0.2) # Just to give the other processes time to print their messages so this doesn't get lost
    command_string = 'sudo renice ' + str(udp_process_priority) + ' ' + str(os.getpid())
    print 'Please enter password to elevate priority of UDP handler process:'
    print command_string
    os.system(command_string)

    local_interface = '10.0.0.3'
    local_port = 60000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((local_interface, local_port))

    print 'Bound to UDP socket', local_interface, ':', local_port

    while script_run.value == 1:
        data, addr = sock.recvfrom(1040) # Sufficiently large that it can handle a big enough packet
        output_queue.put(data)

    output_queue.put(None)
    print 'udp receiver put poison pill on queue'


def UDP_unpacker(input_queue, output_queue):
    '''
    Unpacks the previous process's UDP packets
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    counter = 0 # Packets start with zero (hopefully)

    #log_file = open('udp_logfile', 'w')

    header_length = 16
    data = input_queue.get()
    if data == None:
        output_queue.put(None)
        print 'udp unpacker received poison pill'
        sys.exit()
    packet_length = len(data)
    data_length = packet_length - header_length
    n_samples = data_length / 4
    magic_no, frame_no, subframe_no, frame_size,  mode = struct.unpack('!IQBBH%dx'%(data_length), data)
    packet_data = struct.unpack('!%dx%di'%(header_length, n_samples), data)

    #log_file.write(' frame_no: %d subframe_no: %d frame_size: %d mode: %d '%(frame_no, subframe_no, frame_size, mode ))
    #frame_size = 16 # REMEMBER TO REMOVE ONCE HARDCODED STUFF IS REMOVED!!

    if magic_no != 439041101:
        print 'Magic number unexpected value %d'%(magic_no)
        output_queue.put(None)
        sys.exit()

    data_mode.value = mode
    pkt_len.value = (packet_length)
    pkt_smpl_len.value = (n_samples)
    frame_len.value = (frame_size)
    fft_win_len.value = (frame_size*n_samples)
    interleaved_window_len = (data_length*frame_size) / 4 # /4 to take into account that there are 4 bytes per element
    #interleaved_window_len = 4096

    counter += 1 # can't forget this, otherwise we miss the first frame (if we happen to catch the first packet, which is usually the case)

    interleaved_window = []
    interleaved_window.extend(packet_data)

    while 1:
        data = input_queue.get()
        if data == None:
            break
        magic_no, frame_no, subframe_no, frame_size,  mode = struct.unpack('!IQBBH%dx'%(data_length), data)
        #log_file.write(' frame_no: %d subframe_no: %d frame_size: %d mode: %d '%(frame_no, subframe_no, frame_size, mode ))
        packet_data = struct.unpack('!%dx%di'%(header_length, n_samples), data)

        if subframe_no == counter:
            interleaved_window.extend(packet_data)
            #log_file.write('good pkt - ')
            if len(interleaved_window) < interleaved_window_len:
                counter += 1
                #log_file.write('interleaved window length now %d, counter inc to %d\n'%(len(interleaved_window),counter))
            else:
                counter = 0
                output_queue.put((frame_no, interleaved_window))
                interleaved_window = []
                good_frames.value += 1
                frame_number.value = frame_no
                #log_file.write('fin frame %d\n'%(frame_no))
        else:
            counter = 0
            interleaved_window = []
            bad_frames.value += 1
            #log_file.write('bad pkt\n')

    print 'poison pill received by udp unpacker'
    output_queue.put(None)
    #log_file.close()

def FFT_deinterleaver(input_queue, output_queue):
    '''
    Process for deinterleaving raw FFT data and plotting.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    while 1:
        LCP = []
        RCP = []

        queue_input = input_queue.get()

        if queue_input == None:
            break

        timestamp, interleaved_window = queue_input
        interleaved_window = np.array(interleaved_window)

        even1 = (interleaved_window[0::8] + interleaved_window[1::8]*1j)
        odd1  = (interleaved_window[2::8] + interleaved_window[3::8]*1j)
        LCP   = np.reshape(np.dstack((even1, odd1)), (1,-1))[0]

        even2 = (interleaved_window[4::8] + interleaved_window[5::8]*1j)
        odd2  = (interleaved_window[6::8] + interleaved_window[7::8]*1j)
        RCP   = np.reshape(np.dstack((even2, odd2)), (1,-1))[0]

        #need to figure out here how to write out to the plotting function.

        output_queue.put((timestamp, LCP, RCP))

    print 'deinterleaver found poison pill'
    output_queue.put(None)

def queue_decimator(input_queue, output_queue, output_decimated_queue, decimation_factor = 150):
    '''
    Decimates the queue by the specified factor. Passes full data rate out to one queue for recording, and decimated data out to plotting queue.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    counter = 0
    while 1:
        input_tuple = input_queue.get()
        if input_tuple == None:
            break
        output_queue.put(input_tuple)
        counter += 1
        if counter == decimation_factor:
            counter = 0
            timestamp, LCP, RCP = input_tuple
            LCP_power = 10*np.log10(np.square(np.abs(LCP)) + 1e-10)
            RCP_power = 10*np.log10(np.square(np.abs(RCP)) + 1e-10)
            output_decimated_queue.put((LCP_power, RCP_power))

    print 'queue decimator received poison pill'
    output_queue.put(None)
    output_decimated_queue.put(None)


def plotter(input_queue):
    '''
    This process is supposed to handle the graphs.
    Not pretty at the moment... but then matplotlib never is.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    waterfall_size = 150 # This makes it about 75 seconds in theory. Drawing the graph sometimes takes a bit longer.
    fig = plt.figure(figsize=(20,14))
    plt.subplots_adjust(left = 0.1, bottom = 0.25)
    ax = plt.subplot(1, 1, 1)
    line_lcp, = ax.plot([], [], 'b', lw=1)
    line_rcp, = ax.plot([], [], 'r', lw=1)
    ax.set_xlim(0,400)
    ax.set_ylim(-100,200)

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
        return line_lcp, line_rcp

    def animate(*args):
        if script_run.value != 1 and input_queue.qsize() == 0:
            sys.exit()
        x = np.arange(0, 400, 400.0 / data_width)
        new_lcp, new_rcp = input_queue.get()
        vav_data_lcp.appendleft(new_lcp)
        vav_data_rcp.appendleft(new_rcp)
        lcp = np.zeros(data_width)
        rcp = np.zeros(data_width)
        for i in range(video_average_length.value):
            if i < len(vav_data_lcp):
                lcp += np.array(vav_data_lcp[i])
                rcp += np.array(vav_data_rcp[i])
        lcp /= video_average_length.value
        rcp /= video_average_length.value
        graph_max = 10
        #if lcp.max() > rcp.max():
        #    graph_max = lcp.max()
        #else:
        #    graph_max = rcp.max()
        #ax.set_ylim(0,graph_max + 1)
        line_lcp.set_data(x,lcp)
        line_rcp.set_data(x,rcp)
        return line_lcp,line_rcp

    # Set the animation off to a start...
    anim = animation.FuncAnimation(fig, animate, init_func=init, blit=True)
    plt.show()
    print 'plotter process finished.'



def dummy_queue_emptyer(input_queue):
    '''
    Dummy process. Just empty the queue so as not to let memory explode.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    input_tuple = input_queue.get()
    while input_tuple != None:
        input_tuple = input_queue.get()
    print 'dummy received poison pill'


def diagnostic_info(q1, q2, q3, q4, q5):
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    print 'PID: ', os.getpid()
    print 'Waiting for first packet...'
    while data_mode.value == -1:
        time.sleep(0.01)
    if data_mode.value == 0:
        print 'Complex FFT mode'
    elif data_mode.value == 1:
        print 'Stokes mode'
    else:
        print 'ERROR! Unrecognised data mode!'

    printstr = 'Transmission characteristics:\nPacket size:' + ('%d bytes'%(pkt_len.value)).rjust(10) + \
               '\nFFT window size:' + ('%d channels'%(fft_win_len.value)).rjust(10) + \
               '\nSamples per packet:' + ('%d samples'%(pkt_smpl_len.value)).rjust(10) + \
               '\nPackets per frame:' + ('%d packets'%(frame_len.value)).rjust(10)
    print printstr
    diagnose=True

    while diagnose or q1.qsize() > 0 or q2.qsize() > 0 or q3.qsize() > 0 or q4.qsize() > 0 or q5.qsize() > 0:
        printstr = '\r' + str(diagnose) + \
                   '| Frame number:' + ('%d'%(frame_number.value)).rjust(12) +\
                   '| Good frames:' + ('%d'%(good_frames.value)).rjust(12) +\
                   '| Bad frames:' + ('%d'%(bad_frames.value)).rjust(12) +\
                   '| Q1 length:' + ('%d'%(q1.qsize())).rjust(12) +\
                   '| Q2 length:' + ('%d'%(q2.qsize())).rjust(12) +\
                   '| Q3 length:' + ('%d'%(q3.qsize())).rjust(12) +\
                   '| Q4 length:' + ('%d'%(q4.qsize())).rjust(12) +\
                   '| Q5 length:' + ('%d'%(q5.qsize())).rjust(12) +\
                   '| Frame drop percentage: %f'%(float(bad_frames.value) / (good_frames.value + bad_frames.value + 1) * 100)
        sys.stdout.write(printstr)
        sys.stdout.flush()
        if script_run.value == 0:
            diagnose = False
        time.sleep(0.2)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, ctrl_c)

    receive_unpack_queue = multiprocessing.Queue()
    unpack_deint_queue = multiprocessing.Queue()
    deint_decimate_queue = multiprocessing.Queue()
    storage_queue = multiprocessing.Queue()
    plot_queue = multiprocessing.Queue()

    UDP_receiver_process = multiprocessing.Process(name='UDP receiver', target=UDP_receiver, args=(receive_unpack_queue,))
    UDP_unpacker_process = multiprocessing.Process(name='UDP receiver', target=UDP_unpacker, args=(receive_unpack_queue, unpack_deint_queue,))
    # This is where a decision should be made as to which deinterleaver process to start.
    deinterleaver_process = multiprocessing.Process(name='deinterleaver', target=FFT_deinterleaver, args=(unpack_deint_queue, deint_decimate_queue))
    decimator_process = multiprocessing.Process(name='decimator', target=queue_decimator, args=(deint_decimate_queue, storage_queue, plot_queue))
    plot_process = multiprocessing.Process(name='dummy', target=plotter, args=(plot_queue,))
    dummy_storage_process = multiprocessing.Process(name='dummy', target=dummy_queue_emptyer, args=(storage_queue,))
    diagnostics_process = multiprocessing.Process(name='diagnostics', target=diagnostic_info, args=(receive_unpack_queue, unpack_deint_queue, deint_decimate_queue, storage_queue, plot_queue))

    UDP_receiver_process.start()
    UDP_unpacker_process.start()
    deinterleaver_process.start()
    decimator_process.start()
    plot_process.start()
    dummy_storage_process.start()
    diagnostics_process.start()

    signal.pause()

    UDP_receiver_process.join()
    UDP_unpacker_process.join()
    deinterleaver_process.join()
    decimator_process.join()
    plot_process.join()
    dummy_storage_process.join()
    diagnostics_process.join()


    print '\n'


