import h5py
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import time
import multiprocessing
import signal
import collections

current_data_frame = multiprocessing.Array('f', 1024) # single-precision floating-point for now.
script_run = multiprocessing.Value('B', 1) # Boolean to keep track of whether the program shold actually run, initialise to 1



def ctrl_c(signal, frame):
    '''To be called when SIGINT received. Sets the 'script_run' variable to false so
       that the processes stop sanely.
    '''
    print '\n##################### Ctrl+C pressed, exiting sanely...#####################\n'
    script_run.value = 0 # not False as such because it's a uint8 really...


def random_data_generator(output_queue):
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.

    while script_run.value == 1:
        new_data = np.random.rand(1024)*np.hamming(1024)
        output_queue.put(new_data)
        start_time = time.time()
        for i in range(1024):
            current_data_frame[i] = new_data[i]
        end_time = time.time()
        print end_time - start_time
        time.sleep(0.01)
    print 'poison pill received by data generator'
    output_queue.put(None)
    current_data_frame[0] = 666.0


def hdf5_writer(input_queue):
    '''Process will read from input queue and write out to HDF5 file.
    worthwhile accumulating a bit (32MB?) before you write. To prevent too-frequent disk activity.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    data = input_queue.get()
    while (data != None):
        print 'data saved'
        data = input_queue.get()
    print 'poison pill received by hdf5 writer'


def plotter():
    '''This process is supposed to handle the graphs.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    video_average_length = 1024
    stokes_i_fig = plt.figure()
    stokes_i_ax = plt.axes(xlim=(0,1023), ylim=(0,1))
    stokes_i_line, = stokes_i_ax.plot([], [], lw=1)

    stokes_i_data = collections.deque(maxlen = video_average_length)

    def init():
        x = np.zeros(1024)
        y = np.zeros(1024)
        stokes_i_line.set_data(x,y)
        return stokes_i_line,

    def animate(*args):
        x = range(1024)
        stokes_i_data.appendleft(current_data_frame[:])
        y = np.zeros(1024)
        for i in range(len(stokes_i_data)):
            y += np.array(stokes_i_data[i])
        y /= video_average_length
        print 'some data received'
        #if current_data_frame[0] == 666.0:
        #    plt.close()
        stokes_i_line.set_data(x,y)
        return stokes_i_line,

    # Set the animation off to a start...
    print 'gotten to the anim part'
    anim = animation.FuncAnimation(stokes_i_fig, animate, init_func=init, blit=True, interval=100)
    print 'gotten past the anim part, before the show part'
    try:
        plt.show()
    except:  pass
    print 'gotten past the show part, the process should join now.'



if __name__ == '__main__':
    signal.signal(signal.SIGINT, ctrl_c)

    data_hdf5_queue = multiprocessing.Queue()

    random_data_generator_process = multiprocessing.Process(name='Random Data Generator', target=random_data_generator, args=(data_hdf5_queue,))
    hdf5_writer_process = multiprocessing.Process(name='HDF5 Writer', target=hdf5_writer, args=(data_hdf5_queue,))
    plotter_process = multiprocessing.Process(name="Plotter", target=plotter)

    random_data_generator_process.start()
    hdf5_writer_process.start()
    plotter_process.start()

    signal.pause()

    random_data_generator_process.join()
    hdf5_writer_process.join()
    plotter_process.join()

    print 'Success... all finished'

    if False:
        # Setup.
        # HDF5 file stuff
        #observation_filename = 'observation.hdf5'
        #antenna_data_shape = (100, 1024)
        #antenna_data_dtype = 'complex128'
        #observation_file = h5py.File(observation_filename, mode='w')
        # Creating Data group within HDF5 file
        data_group = observation_file.create_group('Data')
        antenna_data_dataset = data_group.create_dataset('antenna_data', shape=antenna_data_shape, dtype=antenna_data_dtype)
        raw_timestamps_dataset = data_group.create_dataset('raw_timestamps', shape=(antenna_data_shape[0],), dtype='int64')
        timestamps_dataset = data_group.create_dataset('timestamps', shape=(antenna_data_shape[0],), dtype='float64')

        # Global variable (yes, sinful, I know...) to make grabbing an arbitrary frame easier
        current_stokes_i_data = np.hamming(1024)*np.random.rand(1024)

        try:
            while 1:
                current_stokes_i_data = np.hamming(1024)*np.random.rand(1024)
                print "new data generated"
                time.sleep(0.3)


        except KeyboardInterrupt:
            observation_file.close()
