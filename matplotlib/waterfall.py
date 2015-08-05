#!/usr/bin/python
'''
renamed this file
it's really a plotting test to see if I can get video averaging and waterfalls right
'''
import h5py
import numpy as np
import time
import multiprocessing
import signal
# The following for the plotting. If not for plotting, needn't be in the script.
import collections # Has the most excellent deque object which helps tremendously.
from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib.colors import BoundaryNorm # For the waterfall
from matplotlib.ticker import MaxNLocator # Also
from matplotlib.widgets import Slider

current_data_frame = multiprocessing.Array('f', 1024) # single-precision floating-point for now.
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



def random_data_generator(output_queue):
    '''
    This process destined to be replaced by an actual socket once I've finished working with Craig
    on the outputs of his FPGA fabric.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Ignore keyboard interrupt signal, parent process will handle.
    rand_section = 0 # Variable for "noise injector" aspect which makes red stripes in the data one second long.

    while script_run.value == 1:
        new_data = np.random.rand(1024)*np.hamming(1024) # Hamming window to sort-of make it look bandpass.

        # Uncomment the following in order to insert the "noise" into a random location in the data stream.
        #if (int(time.time()) % 5) == 3:
        #    rand_section = np.random.randint(1024 - 10)
        # The "5" is for every how many seconds the noise is injected. Adjust as desired.
        if (int(time.time()) % 5) == 0:
            print 'noise_event'
            for i in range(rand_section, rand_section + 9):
                new_data[i] = 0.8
        output_queue.put(new_data)

        # Have to use a for loop because the multiprocessing array doesn't convert easily to a numpy one AFAIK
        for i in range(1024):
            current_data_frame[i] = new_data[i]
        time.sleep(0.01)

    print 'poison pill received by data generator'
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
    line, = ax.plot([], [], lw=1)
    ax.set_ylim(0,1)
    ax.set_xlim(0,1023)

    levels = MaxNLocator(nbins=10).tick_values(0,1)
    cmap = plt.get_cmap('spectral')
    norm = BoundaryNorm(levels,ncolors=cmap.N,clip=True)
    z = np.zeros((waterfall_size, 1024))
    waterfall_ax = plt.subplot(2,1,1)
    waterfall_quad = waterfall_ax.pcolormesh(z, cmap=cmap, norm=norm)
    waterfall_ax.set_ylim(0,waterfall_size)
    waterfall_ax.set_xlim(0,1023)
    waterfall_ax.set_title('Wasserfalldiagramm')

    data = collections.deque(maxlen = waterfall_size)

    slider_ax = plt.axes([0.25, 0.1, 0.65, 0.03])

    video_average_length_slider = Slider(slider_ax, 'VAv', 1, waterfall_size, valinit=video_average_length.value)
    def update(val):
        video_average_length.value = int(video_average_length_slider.val)
        fig.canvas.draw_idle()
    video_average_length_slider.on_changed(update)

    def init():
        x = np.zeros(1024)
        y = np.zeros(1024)
        z = np.zeros((waterfall_size, 1024))
        line.set_data(x,y)
        waterfall_quad.set_array(z.ravel())
        return line,

    def animate(*args):
        x = range(1024)
        data.appendleft(current_data_frame[:])
        y = np.zeros(1024)
        for i in range(video_average_length.value):
            if i < len(data):
                y += np.array(data[i])
        for i in range(waterfall_size):
            if i < len(data):
                z[i] = np.array(data[i])
        waterfall_quad.set_array(z.ravel())
        y /= video_average_length.value
        #if current_data_frame[0] == 666.0:
        #    plt.close()
        line.set_data(x,y)
        return line,waterfall_quad

    # Set the animation off to a start...
    anim = animation.FuncAnimation(fig, animate, init_func=init, blit=True, interval=500)
    plt.show()


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

    # This stuff is leftover from messing around with HDF5.
    # I haven't decided to get rid of it just yet. It's still yet-to-be-integrated into the saving process above.
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
                time.sleep(0.3)


        except KeyboardInterrupt:
            observation_file.close()
