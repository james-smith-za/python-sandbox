# Gaussian beamwidth related calculations
import matplotlib.pyplot as plt
import numpy as np

def gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

fig1 = plt.figure(figsize=(10,8))
