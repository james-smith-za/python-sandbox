import numpy as np
import skimage
import skimage.io as image_io
import pylab

pylab.ion()
image_filename = 'canmaj.jpg'
visibility_filename = 'visibility.jpg'

image = image_io.imread(image_filename, as_grey=True) # as_grey makes it come out as a single float_64

M, N = np.shape(image)
for m in range(0,M):
    for n in range(0,N):
        if (m + n) % 2 == 1:
            image[m,n] = image[m,n]*(-1)

image_FFT = np.fft.fft2(image)
image_FFT_abs = np.abs(image_FFT)

image_io.imshow(image_FFT_abs)

f = raw_input('hello')

visibility = image_io.imread(visibility_filename, as_grey=True)

perceived_sky_FFT = image_FFT * visibility
perceived_sky = np.abs(np.fft.ifft2(perceived_sky_FFT))

image_io.imshow(perceived_sky)

f = raw_input('hello')

