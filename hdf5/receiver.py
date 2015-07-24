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
    This process destined to be replaced by an actual socket once I've finished working with Craig
    on the outputs of his FPGA fabric.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.

    udp_process_priority = -11
    time.sleep(0.2) # Just to give the other processes time to print their messages
    command_string = 'sudo renice ' + str(udp_process_priority) + ' ' + str(os.getpid())
    print 'Please enter password to elevate priority of UDP handler process:'
    print command_string
    os.system(command_string)

    local_interface = '10.0.0.3'
    local_port = 60000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((local_interface, local_port))

    print 'Bound to UDP socket', local_interface, ':', local_port

    counter = 0 # Packets start with zero (hopefully)

    header_length = 16
    data, addr = sock.recvfrom(10240) # Sufficiently large that it can handle a big enough packet
    packet_length = len(data)
    data_length = packet_length - header_length
    n_samples = data_length / 4
    magic_no, frame_no, subframe_no, frame_size, mode = struct.unpack('!IQBBH%dx'%(data_length), data)
    packet_data = struct.unpack('!%dx%di'%(header_length, n_samples), data)

    if magic_no != 439041101:
        print 'Magic number unexpected value %d'%(magic_no)
        output_queue.put(None)
        sys.exit()

    data_mode.value = mode
    pkt_len.value = packet_length
    pkt_smpl_len.value = n_samples
    #frame_len.value = frame_size
    frame_len.value = 16
    #fft_win_len.value = frame_size*n_samples
    fft_win_len.value = 1024
    #interleaved_window_len = data_length*frame_size
    interleaved_window_len = 16384

    interleaved_window = []
    interleaved_window.extend(packet_data)

    while (script_run.value == 1):
        data, addr = sock.recvfrom(packet_length)
        magic_no, frame_no, subframe_no, mode, frame_size = struct.unpack('!IQHBB%dx'%(data_length), data)
        packet_data = struct.unpack('!%dx%di'%(header_length, n_samples), data)

        if subframe_no == counter:
            interleaved_window.extend(packet_data)
            if len(interleaved_window) < interleaved_window_len:
                counter += 1
            else:
                output_queue.put((frame_no, interleaved_window))
                good_frames.value += 1
                frame_number.value = frame_no
        else:
            counter = 0
            interleaved_window = []
            bad_frames.value += 1

    print 'poison pill received by data generator'
    output_queue.put(None)

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
        LCP   = np.reshape(np.dstack((even1, odd1)), (1,-1))

        even2 = (interleaved_window[4::8] + interleaved_window[5::8]*1j)
        odd2  = (interleaved_window[6::8] + interleaved_window[7::8]*1j)
        RCP   = np.reshape(np.dstack((even2, odd2)), (1, -1))

        #need to figure out here how to write out to the plotting function.

        output_queue.put((timestamp, LCP, RCP))

    print 'deinterleaver found poison pill'
    output_queue.put(None)


def dummy_queue_emptyer(input_queue):
    '''
    Dummy process. Just empty the queue so as not to let memory explode.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    input_tuple = input_queue.get()
    while input_tuple != None:
        input_tuple = input_queue.get()
    print 'dummy received poison pill'


def diagnostic_info(q1, q2):
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

    while diagnose:
        printstr = '\r' + \
                   ' Frame number:' + ('%d'%(frame_number.value)).rjust(12) +\
                   ' Good frames:' + ('%d'%(good_frames.value)).rjust(12) +\
                   ' Bad frames:' + ('%d'%(bad_frames.value)).rjust(12) +\
                   ' Q1 length:' + ('%d'%(q1.qsize())).rjust(12) +\
                   ' Q2 length:' + ('%d'%(q2.qsize())).rjust(12)
        sys.stdout.write(printstr)
        sys.stdout.flush()
        if script_run.value == 0:
            diagnose = False
        time.sleep(0.2)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, ctrl_c)

    udp_deint_queue = multiprocessing.Queue()
    deint_storage_queue = multiprocessing.Queue()

    UDP_receiver_process = multiprocessing.Process(name='UDP receiver', target=UDP_receiver, args=(udp_deint_queue,))
    # This is where a decision should be made as to which deinterleaver process to start.
    deinterleaver_process = multiprocessing.Process(name='deinterleaver', target=FFT_deinterleaver, args=(udp_deint_queue, deint_storage_queue))
    dummy_process = multiprocessing.Process(name='dummy', target=dummy_queue_emptyer, args=(deint_storage_queue,))
    diagnostics_process = multiprocessing.Process(name='diagnostics', target=diagnostic_info, args=(udp_deint_queue,deint_storage_queue))

    UDP_receiver_process.start()
    deinterleaver_process.start()
    dummy_process.start()
    diagnostics_process.start()

    signal.pause()

    UDP_receiver_process.join()
    deinterleaver_process.join()
    dummy_process.join()
    diagnostics_process.join()


    print '\n'


