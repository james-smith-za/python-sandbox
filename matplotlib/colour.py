"""
Shows how to combine Normalization and Colormap instances to draw
"levels" in pcolor, pcolormesh and imshow type plots in a similar
way to the levels keyword argument to contour/contourf.

"""

import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
import numpy as np


fft_len = 1024
hist_len = 50

z = np.zeros((hist_len,fft_len))
for i in range(hist_len):
    z[i] = np.hamming(fft_len)*np.random.rand(fft_len)


# x and y are bounds, so z should be the value *inside* those bounds.
# Therefore, remove the last value from the z array.
#z = z[:-1, :-1]
levels = MaxNLocator(nbins=50).tick_values(z.min(), z.max())


# pick the desired colormap, sensible levels, and define a normalization
# instance which takes data values and translates those into levels.
cmap = plt.get_cmap('spectral')
norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)

plt.subplot(1, 1, 1)
im = plt.pcolormesh(z, cmap=cmap, norm=norm)
plt.colorbar()
# set the limits of the plot to the limits of the data
plt.axis([0, fft_len - 1, 0, hist_len - 1])
plt.title('Wasserfalldiagramm')


plt.show() 
