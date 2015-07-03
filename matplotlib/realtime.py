import h5py
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import time
import multiprocessing
import signal
import collections


video_average_length = 10

stokes_i_fig = plt.figure()
stokes_i_ax = plt.axes(xlim=(0,1023), ylim=(0,1))
stokes_i_line, = stokes_i_ax.plot([], [], lw=1)

stokes_i_data = collections.deque(maxlen = video_average_length)

def animate(dummy):
    x = range(1024)
    stokes_i_data.appendleft(np.random.rand(1024)*np.hamming(1024))
    y = np.zeros(1024)
    for i in range(len(stokes_i_data)):
        y += np.array(stokes_i_data[i])
    y /= video_average_length
    stokes_i_line.set_data(x,y)
    return stokes_i_line,

# Set the animation off to a start...
anim = animation.FuncAnimation(stokes_i_fig, animate, blit=True, interval=100)
plt.show()

