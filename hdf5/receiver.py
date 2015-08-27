#!/usr/bin/python
'''
WB.py - multi-processed script for receiving UDP data from the ROACH via 10GbE, plotting some of it, and storing it in an HDF-5 file.
'''

# TODO:
# - Figure out the accumulation length from the difference in timestamps.

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

import h5py


###################### Multiprocessing shared values ######################
script_run = multiprocessing.Value('B', 1) # Boolean to keep track of whether the program shold actually run, initialise to 1

data_mode = multiprocessing.Value('h', -1) # 0 for complex FFT, 1 for Stokes
band_mode = multiprocessing.Value('h', -1) # 0 for wideband, 1 for narrowband

sample_freq = 800e6
fft_size = multiprocessing.Value('H', 0)
data_width = multiprocessing.Value('H', 0)
file_time = 10*60 # This is just a constant, doesn't need to be edited after the fact
file_accums = multiprocessing.Value('H', 0)

pkt_len = multiprocessing.Value('H', 0)
fft_win_len = multiprocessing.Value('H', 0)
pkt_smpl_len = multiprocessing.Value('H', 0)
frame_len = multiprocessing.Value('H', 0)

# Diagnostic information
frame_number_MSB = multiprocessing.Value('L', 0)
frame_number_LSB = multiprocessing.Value('L', 0)
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
    # This can come in release 2.0 perhaps
    print '\n##################### Ctrl+C pressed, exiting sanely...#####################\n'
    script_run.value = 0


###################### UDP functions ######################
def UDP_receiver(output_queue):
    '''
    A life dedicated to grabbing UDP packets and sticking them on a queue
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.

    # This necessary so that the receiver has enough priority to get the packets in.
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
        data, addr = sock.recvfrom(10240) # Sufficiently large that it can handle a big enough packet
        output_queue.put(data)

    output_queue.put(None)
    print 'udp receiver put poison pill on queue'

def UDP_unpacker(input_queue, output_queue):
    '''
    Unpacks the previous process's UDP packets
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    counter = 0 # Packets start with zero (hopefully)

    #logfile = open('logfile.csv', 'w')

    header_length = 16
    data = input_queue.get()
    if data == None:
        output_queue.put(None)
        print 'udp unpacker received poison pill'
        sys.exit()
    packet_length = len(data)
    data_length = packet_length - header_length
    n_samples = data_length / 16
    magic_no, timestamp, subframe_no, frame_size,  mode = struct.unpack('!IqBBH%dx'%(data_length), data)
    logstr = str(magic_no) + ',' + \
             str(timestamp).zfill(20) + ',' + \
             str(subframe_no).zfill(3) + ',' + \
             str(frame_size).zfill(3) + ',' + \
             str(mode).zfill(3) + '\n'
    #logfile.write(logstr)
    packet_data = struct.unpack('!%dx%di'%(header_length, n_samples*4), data)

    if magic_no != 439041101:
        print 'Magic number unexpected value %d'%(magic_no)
        output_queue.put(None)
        sys.exit()

    data_mode.value = mode & 1 # LSB is FFT / Stokes mode.
    band_mode.value = ((mode & 2) >> 1) # Second-to-last bit is wide / narrowband mode
    pkt_len.value = (packet_length)
    pkt_smpl_len.value = (n_samples)
    frame_len.value = (frame_size)
    fft_win_len.value = (frame_size*n_samples)
    interleaved_window_len = (data_length*frame_size) / 4 # /4 to take into account that there are 4 bytes per element

    print

    interleaved_window = []

    if subframe_no == 0:
        counter += 1 # can't forget this, otherwise we miss the first frame (if we happen to catch the first packet, which is usually the case)
        interleaved_window.extend(packet_data)
    else:
        for i in range(subframe_no + 1, frame_size):
            input_queue.get()

    while 1:
        data = input_queue.get()
        if data == None:
            break
        magic_no, timestamp, subframe_no, frame_size,  mode = struct.unpack('!IqBBH%dx'%(data_length), data)
        logstr = str(magic_no) + ',' + \
                 str(timestamp).zfill(20) + ',' + \
                 str(subframe_no).zfill(3) + ',' + \
                 str(frame_size).zfill(3) + ',' + \
                 str(mode).zfill(3) + '\n'
        #logfile.write(logstr)
        noise_diode = (mode & 0b1000000000000000) >> 15 # noise_diode is on MSB
        packet_data = struct.unpack('!%dx%di'%(header_length, n_samples*4), data)

        if subframe_no == counter: # i.e. are the packets coming in synchronously with the incremented counter.
            interleaved_window.extend(packet_data)
            if len(interleaved_window) < interleaved_window_len:
                counter += 1
                #logfile.write('Good packet\n')
            else:
                counter = 0
                output_queue.put((timestamp, noise_diode, interleaved_window))
                interleaved_window = []
                good_frames.value += 1
                frame_number_MSB.value, frame_number_LSB.value = struct.unpack('LL', struct.pack('q', timestamp))
                #logfile.write('Good frame\n')
        else: # If not, just reset everything until you get a 0 again. Start from the beginning of the next frame.
            counter = 0
            interleaved_window = []
            bad_frames.value += 1
            #logfile.write('Bad frame\n')

    print 'poison pill received by udp unpacker'
    output_queue.put(None)
    #logfile.close()

############################### Complex FFT related functions ##############################################

def fft_deinterleaver(input_queue, output_queue):
    '''
    Process for deinterleaving raw fft data.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    while 1:
        queue_input = input_queue.get()

        if queue_input == None:
            break

        timestamp, noise_diode, interleaved_window = queue_input
        interleaved_window = np.array(interleaved_window)

        even1 = (interleaved_window[0::8] + interleaved_window[1::8]*1j)
        odd1  = (interleaved_window[2::8] + interleaved_window[3::8]*1j)
        LCP   = np.reshape(np.dstack((even1, odd1)), (1,-1))[0]

        even2 = (interleaved_window[4::8] + interleaved_window[5::8]*1j)
        odd2  = (interleaved_window[6::8] + interleaved_window[7::8]*1j)
        RCP   = np.reshape(np.dstack((even2, odd2)), (1,-1))[0]

        output_queue.put((timestamp, noise_diode, LCP, RCP))

    print 'deinterleaver found poison pill'
    output_queue.put(None)

def fft_queue_decimator(input_queue, output_queue, output_decimated_queue, decimation_factor = 150):
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
            timestamp, noise_diode, LCP, RCP = input_tuple
            LCP_power = 10*np.log10(np.square(np.abs(LCP)) + 1) # The +1 is to avoid NaN if you log zero.
            RCP_power = 10*np.log10(np.square(np.abs(RCP)) + 1)
            output_decimated_queue.put((LCP_power, RCP_power))

    print 'queue decimator received poison pill'
    output_queue.put(None)
    output_decimated_queue.put(None)

def fft_plotter(input_queue):
    '''
    Plots the decimated spectrum
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    fig = plt.figure(figsize=(10,10))

    ax = plt.subplot(1, 1, 1)
    line_lcp, = ax.plot([], [], 'b', lw=1)
    line_rcp, = ax.plot([], [], 'r', lw=1)
    ax.set_xlim(0,400)
    ax.set_ylim(0,200)
    plt.title('LL is blue, RR is red')
    plt.xlabel('Frequency(MHz)')

    x = []

    if band_mode.value == 0:
        x = np.arange(0, 400, 400.0 / data_width.value)
        ax1.set_xlim(0,400)
        ax2.set_xlim(0,400)
    elif band_mode.value == 1:
        x = np.arange(0, 1.5625, 1.5625 / data_width.value)
        ax1.set_xlim(0,1.5625)
        ax2.set_xlim(0,1.5625)

    line_lcp.set_data(x,y)
    line_rcp.set_data(x,y)

    plt.ion()
    plt.show()

    while 1:
        queue_input = input_queue.get()
        if queue_input == None:
            break
        lcp, rcp = queue_input
        line_lcp.set_ydata(lcp)
        line_rcp.set_ydata(rcp)
        fig.canvas.draw()

    print 'plotter process finished.'

def fft_hdf5_storage(input_queue):
    '''
    Stores FFT data in an hdf5 file directly. This will probably not be used all that much, but will
    be used in the development phase for making sure that everything is working.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    carry_on_regardless = True

    while carry_on_regardless:
        filename = time.strftime('%Y%m%d_%H%M%S.h5', time.gmtime())
        print 'Creating file %s'%(filename)
        h5file = h5py.File( filename, 'w')
        data_group = h5file.create_group('Data')
        fft_dset = data_group.create_dataset('Complex FFT data', shape=(2, file_accums.value, data_width.value), dtype=np.complex64)
        ts_dset = data_group.create_dataset('Timestamps', shape=(file_accums.value, 1), dtype=np.float)
        nd_dset = data_group.create_dataset('Noise Diode', shape=(file_accums.value, 1), dtype=np.uint64)
        average_dset = data_group.create_dataset('Time-averages', shape=(2, file_time), dtype=np.float)
        timestamp_array = []
        noise_diode_array = []
        l_average_array = []
        r_average_array = []

        counter = 0
        l_average = 0.0
        r_average = 0.0

        for i in range(file_accums.value):
            counter += 1
            input_tuple = input_queue.get()
            if input_tuple == None:
                print 'storage process found poison pill'
                # Padding has to be done because the h5 files aren't dynamically sized, so writing an array that's too small into the
                # dataset breaks things and the file doesn't close properly. This we want to avoidi, because it becomes unusable.
                # I'm leaving these lines in - they work in numpy 1.8.2 which is on my laptop (Mint Rebecca), but not on 1.6.2 which is on Optimus (Debian Wheezy).
                # The code below works, but it's much less elegant (IMO).
                #ts_dset[:,0] = np.pad(np.array(timestamp_array), (0, file_accums.value - len(timestamp_array)), 'constant')
                #average_dset[0,:] = np.pad(np.array(l_average_array), (0, file_time - len(l_average_array)), 'constant')
                #average_dset[1,:] = np.pad(np.array(r_average_array), (0, file_time - len(r_average_array)), 'constant')

                for k in range(i, file_accums.value):
                    timestamp_array.append(0)
                    noise_diode_array.append(False)
                for k in range(len(l_average_array), file_time):
                    l_average_array.append(0)
                    r_average_array.append(0)
                print 'Closing file %s'%(filename)
                carry_on_regardless = False
                ts_dset[:,0] = np.array(timestamp_array)
                nd_dset[:,0] = np.array(noise_diode_array)
                average_dset[0,:] = np.array(l_average_array)
                average_dset[1,:] = np.array(r_average_array)
                h5file.close()
                break
            timestamp, noise_diode, l_data, r_data = input_tuple
            timestamp_array.append(timestamp)
            noise_diode_array.append(noise_diode)
            fft_dset[0,i,:] = l_data.astype(np.complex64)
            fft_dset[1,i,:] = r_data.astype(np.complex64)
            l_average += np.average(np.square(np.abs(l_data)))
            r_average += np.average(np.square(np.abs(r_data)))
            if counter == accums_per_sec: # i.e. if we've averaged for a whole second now...
                l_average /= accums_per_sec
                r_average /= accums_per_sec
                l_average_array.append(l_average)
                r_average_array.append(r_average)
                counter = 0
                l_average = 0.0
                r_average = 0.0

        if carry_on_regardless:
            ts_dset[:,0] = np.array(timestamp_array)
            nd_dset[:,0] = np.array(noise_diode_array)
            average_dset[0,:] = np.array(l_average_array)
            average_dset[1,:] = np.array(r_average_array)
            print 'Closing file %s'%(filename)
            h5file.close()



########################################### lrqu functions ########################################################
# This isn't full Stokes - LL, RR, Q and U rather.
# Essentially a repeat of the above functions adapted.

def lrqu_deinterleaver(input_queue, output_queue):
    '''
    Process for deinterleaving raw lrqu data.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    while 1:
        queue_input = input_queue.get()

        if queue_input == None:
            break

        timestamp, noise_diode, interleaved_window = queue_input
        interleaved_window = np.array(interleaved_window)

        ll_even = interleaved_window[0::8]
        rr_even = interleaved_window[1::8]
        Q_even = interleaved_window[2::8]
        U_even = interleaved_window[3::8]

        ll_odd = interleaved_window[4::8]
        rr_odd = interleaved_window[5::8]
        Q_odd = interleaved_window[6::8]
        U_odd = interleaved_window[7::8]

        ll = np.reshape(np.dstack((ll_even, ll_odd)), (1, -1))[0]
        rr = np.reshape(np.dstack((rr_even, rr_odd)), (1, -1))[0]
        Q = np.reshape(np.dstack((Q_even, Q_odd)), (1, -1))[0]
        U = np.reshape(np.dstack((U_even, U_odd)), (1, -1))[0]

        output_queue.put((timestamp, noise_diode, ll, rr, Q, U))

    print 'deinterleaver found poison pill'
    output_queue.put(None)

def lrqu_queue_decimator(input_queue, output_queue, output_decimated_queue):
    '''
    Decimates the queue by the specified factor. Passes full data rate out to one queue for recording, and decimated data out to plotting queue.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.

    decimation_factor = 0

    if band_mode.value == 0:
        decimation_factor = 150
    elif band_mode.value == 1:
        decimation_factor = 1

    counter = 0
    while 1:
        input_tuple = input_queue.get()
        if input_tuple == None:
            break
        output_queue.put(input_tuple)
        counter += 1
        if counter == decimation_factor:
            counter = 0
            timestamp, noise_diode, LL, RR, Q, U = input_tuple
            ll = 10*np.log10(LL + 1)
            rr = 10*np.log10(RR + 1)
            Q = np.divide(Q.astype(np.float), (LL + RR)) # Give Q and U as a fraction of total power.
            U = np.divide(U.astype(np.float), (LL + RR))
            output_decimated_queue.put((ll, rr, Q, U))

    print 'queue decimator received poison pill'
    output_queue.put(None)
    output_decimated_queue.put(None)

def lrqu_plotter(input_queue):
    '''
    Plots decimated Stokes data. Top graph ends up effectively the same as the plot from the FFT (above), but the bottom one shows Q and U.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    fig = plt.figure(figsize=(10,10))

    ax1 = plt.subplot(2, 1, 1)
    line_ll, = ax1.plot([], [], 'b', lw=1)
    line_rr, = ax1.plot([], [], 'r', lw=1)
    ax1.set_ylim(0,100)
    plt.title('LL blue, RR red') # Apologies if there are any colour-bind operators. Perhaps in a future version, circles / squares / triangles can also be used.
    plt.xlabel('Frequency(MHz)')

    ax2 = plt.subplot(2, 1, 2)
    line_Q, = ax2.plot([], [], 'b', lw=1)
    line_U, = ax2.plot([], [], 'g', lw=1)
    ax2.set_ylim(-1, 1)
    plt.title('Q blue, U green')
    plt.xlabel('Frequency(MHz)')

    x = []

    if band_mode.value == 0:
        x = np.arange(0, 400, 400.0 / data_width.value)
        ax1.set_xlim(0,400)
        ax2.set_xlim(0,400)
    elif band_mode.value == 1:
        x = np.arange(0, 1.5625, 1.5625 / data_width.value)
        ax1.set_xlim(0,1.5625)
        ax2.set_xlim(0,1.5625)

    y = np.zeros(data_width.value)
    line_ll.set_data(x,y)
    line_rr.set_data(x,y)
    line_Q.set_data(x,y)
    line_U.set_data(x,y)

    plt.ion()
    plt.show()

    while 1:
        queue_input = input_queue.get()
        if queue_input == None:
            break
        ll,rr,Q,U = queue_input
        line_ll.set_ydata(ll)
        line_rr.set_ydata(rr)
        line_Q.set_ydata(Q)
        line_U.set_ydata(U)

        fig.canvas.draw()

    print 'plotter process finished.'

def lrqu_hdf5_storage(input_queue):
    '''
    Stores lrqu data in an hdf5 file directly. This will probably not be used all that much, but will
    be used in the development phase for making sure that everything is working.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    carry_on_regardless = True

    while carry_on_regardless:
        filename = time.strftime('%Y%m%d_%H%M%S.h5', time.gmtime())
        print 'Creating file %s'%(filename)
        h5file = h5py.File( filename, 'w')
        data_group = h5file.create_group('Data')
        lrqu_dset = data_group.create_dataset('lrqu data', shape=(file_accums.value, data_width.value, 4), dtype=np.int32)
        ts_dset = data_group.create_dataset('Timestamps', shape=(file_accums.value, 1), dtype=np.uint64)
        nd_dset = data_group.create_dataset('Noise Diode', shape=(file_accums.value, 1), dtype=np.uint64)
        average_dset = data_group.create_dataset('Time-averages', shape=(2, file_time), dtype=np.float)
        timestamp_array = []
        noise_diode_array = []
        l_average_array = []
        r_average_array = []

        counter = 0
        l_average = 0.0
        r_average = 0.0

        for i in range(file_accums.value):
            counter += 1
            input_tuple = input_queue.get()
            if input_tuple == None:
                print 'storage process found poison pill'
                # Same here as in the previous storage function, padding arrays to h5 size.
                for k in range(i, file_accums.value):
                    timestamp_array.append(0)
                    noise_diode_array.append(False)
                for k in range(len(l_average_array), file_time):
                    l_average_array.append(0)
                    r_average_array.append(0)
                print 'Closing file %s'%(filename)
                carry_on_regardless = False
                ts_dset[:,0] = np.array(timestamp_array)
                nd_dset[:,0] = np.array(noise_diode_array)
                average_dset[0,:] = np.array(l_average_array)
                average_dset[1,:] = np.array(r_average_array)
                h5file.close()
                break
            timestamp, noise_diode, ll, rr, Q, U = input_tuple
            timestamp_array.append(timestamp)
            noise_diode_array.append(noise_diode)
            lrqu_dset[i,:,0] = ll
            lrqu_dset[i,:,1] = rr
            lrqu_dset[i,:,2] = Q
            lrqu_dset[i,:,3] = U
            l_average += np.average(ll)
            r_average += np.average(rr)
            if counter == accums_per_sec: # i.e. if we've averaged for a whole second now...
                l_average /= accums_per_sec
                r_average /= accums_per_sec
                l_average_array.append(l_average)
                r_average_array.append(r_average)
                counter = 0
                l_average = 0.0
                r_average = 0.0

        if carry_on_regardless:
            ts_dset[:,0] = np.array(timestamp_array)
            nd_dset[:,0] = np.array(noise_diode_array)
            average_dset[0,:] = np.array(l_average_array)
            average_dset[1,:] = np.array(r_average_array)
            print 'Closing file %s'%(filename)
            h5file.close()




############################## Dummy and diagnostics ################################

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
    '''
    Diagnostic information - prints and re-prints a line with queue lengths after initially
    informing the user various relevant details about the data being received.
    '''
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

    printstr = 'Transmission characteristics:\nPacket size: ' + ('%d bytes'%(pkt_len.value)).rjust(10) + \
               '\nFFT window size: ' + ('%d channels'%(fft_win_len.value)).rjust(10) + \
               '\nSamples per packet: ' + ('%d samples'%(pkt_smpl_len.value)).rjust(10) + \
               '\nPackets per frame: ' + ('%d packets'%(frame_len.value)).rjust(10)
    print printstr
    diagnose=True

    while diagnose or q1.qsize() > 0 or q2.qsize() > 0 or q3.qsize() > 0 or q4.qsize() > 0 or q5.qsize() > 0:
        timestamp = struct.unpack('q', struct.pack('LL', frame_number_MSB.value, frame_number_LSB.value))[0]
        printstr = '\r' + str(diagnose) + \
                   '| Frame no:' + ('%d'%(timestamp)).rjust(18) +\
                   '| Good frames:' + ('%d'%(good_frames.value)).rjust(12) +\
                   '| Bad frames:' + ('%d'%(bad_frames.value)).rjust(12) +\
                   '| Q1 length:' + ('%d'%(q1.qsize())).rjust(12) +\
                   '| Q2 length:' + ('%d'%(q2.qsize())).rjust(12) +\
                   '| Q3 length:' + ('%d'%(q3.qsize())).rjust(12) +\
                   '| Q4 length:' + ('%d'%(q4.qsize())).rjust(12) +\
                   '| Q5 length:' + ('%d'%(q5.qsize())).rjust(12) +\
                   '| Frame drop percentage: %.2f'%(float(bad_frames.value) / (good_frames.value + bad_frames.value + 1) * 100)
        sys.stdout.write(printstr)
        sys.stdout.flush()
        if script_run.value == 0:
            diagnose = False
        time.sleep(0.2)

############# main ###################

if __name__ == '__main__':
    signal.signal(signal.SIGINT, ctrl_c)

    receive_unpack_queue = multiprocessing.Queue()
    unpack_deint_queue = multiprocessing.Queue()
    deint_decimate_queue = multiprocessing.Queue()
    storage_queue = multiprocessing.Queue()
    plot_queue = multiprocessing.Queue()

    UDP_receiver_process = multiprocessing.Process(name='UDP receiver', target=UDP_receiver, args=(receive_unpack_queue,))
    UDP_unpacker_process = multiprocessing.Process(name='UDP receiver', target=UDP_unpacker, args=(receive_unpack_queue, unpack_deint_queue,))

    UDP_receiver_process.start()
    UDP_unpacker_process.start()

    while data_mode.value == -1:
        pass

    if data_mode.value == 0:
        deinterleaver = fft_deinterleaver
        queue_decimator = fft_queue_decimator
        plotter = fft_plotter
        storage = fft_hdf5_storage
    elif data_mode.value == 1:
        deinterleaver = lrqu_deinterleaver
        queue_decimator = lrqu_queue_decimator
        plotter = lrqu_plotter
        storage = lrqu_hdf5_storage

    if band_mode.value == 0:
        print 'Wideband mode'
        data_width.value = 1024
        fft_size.value = data_width.value*2
        fft_time = float(fft_size.value) / sample_freq
        accum_len = 3125 # Nice integer number that gives us 8 ms accumulations, and divides evenly into a second.
    elif band_mode.value == 1:
        print 'Narrowband mode'
        data_width.value = 4096
        fft_size = data_width.value # Not *2 because the second stage has a complex input - no symmetry
        fft_time = float(fft_size) / sample_freq * 2048
        accum_len = 128 # TODO: This still needs to be standardised.

    accum_time = accum_len * fft_time
    accums_per_sec = int(1 / accum_time)
    file_accums.value = int(file_time / accum_time) # This will be the number of rows in the file

    deinterleaver_process = multiprocessing.Process(name='deinterleaver', target=deinterleaver, args=(unpack_deint_queue, deint_decimate_queue))
    decimator_process = multiprocessing.Process(name='decimator', target=queue_decimator, args=(deint_decimate_queue, storage_queue, plot_queue))
    plot_process = multiprocessing.Process(name='plotter', target=plotter, args=(plot_queue,))
    storage_process = multiprocessing.Process(name='storage', target=storage, args=(storage_queue,))
    diagnostics_process = multiprocessing.Process(name='diagnostics', target=diagnostic_info, args=(receive_unpack_queue, unpack_deint_queue, deint_decimate_queue, storage_queue, plot_queue))

    deinterleaver_process.start()
    decimator_process.start()
    plot_process.start()
    storage_process.start()
    diagnostics_process.start()

    signal.pause()

    UDP_receiver_process.join()
    UDP_unpacker_process.join()
    deinterleaver_process.join()
    decimator_process.join()
    plot_process.join()
    storage_process.join()
    diagnostics_process.join()


    print '\n'


