'''
Some notes on how to make use of the HDF5 files produced by the current version (2015-08-18) of the
AVN wideband spectrometer.
'''

import numpy as np
import h5py
import pylab
import time

filename = '20010101_120000.h5'

datafile = h5py.File(filename)

# Be aware, these will be large... if you've got enough memory though, go ahead.:w
# Each of these are then a 2D array with 75000 rows (time) and 1024 columns(frequency)
ll = datafile['Data']['lrqu data'][:,:,0]
rr = datafile['Data']['lrqu data'][:,:,1]
q = datafile['Data']['lrqu data'][:,:,2]
u = datafile['Data']['lrqu data'][:,:,3]

time_average_ll = datafile['Data']['Time-averages'][0,:]
time_average_rr = datafile['Data']['Time-averages'][1,:]

pylab.ion()

pylab.plot(time_average_ll)
pylab.plot(time_average_rr)

time.sleep(10)
pylab.close('all')

time_row_to_plot = 0

pylab.plot(ll[time_row_to_plot, :])
pylab.plot(rr[time_row_to_plot, :])
pylab.plot(Q[time_row_to_plot, :])
pylab.plot(U[time_row_to_plot, :])

# To skip the DC bin, throw in a 1 just before the colon. If that doesn't work, the DC "bin" might cover more than one frequency sample, so try up to 10.
#pylab.plot(ll[time_row_to_plot, 10 :]


# Other miscellaneous stuff which may be useful

# To make ipython list the datasets inside the file:
# "group" means folder, basically, and "dataset" means table.
datafile_values = datafile.values()
# This will list the "Data" folder
print datafile_values
# This will list the tables inside the "Data" folder, including timestamps and noise diodes.
print datafile_values[0].values()

timestamps = np.array(datafile['Data']['Timestamps']) # This can be done with any of the desired datasets