# Script not really working as it is at the moment. Numpy gives overflow and divide "warnings" and the plot produces nothing useful.
import numpy as np
import scipy.integrate as integrate
import matplotlib.pyplot as plt

h = 6.62606957e-34 # J*s - Planck
c = 299792458.0 # m/s - light speed
k = 1.3806488e-23 # J/K - Boltzmann

temp = 1.0e4 # K - this is a variable. Going to make a few runs of this.

def Bv(T):
    # T is temperature in Kelvins
    nu = np.logspace(1e3, 1e9, num=1e4) # nu = frequency to co-operate with these silly astronomers
    B = (2*h*np.power(nu,3))/(np.power(c,2)) * 1/(np.exp(h*nu/(k*T)) - 1)
    return nu, B

plt.plot(Bv(temp))
plt.show()

