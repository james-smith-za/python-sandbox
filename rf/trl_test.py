import numpy as np
import skrf as rf
import matplotlib.pyplot as plt

freq = rf.Frequency(1,2,101,'GHz')

my_media = rf.media.DefinedGammaZ0(freq)

net1 = my_media.inductor(0.5)
ntwk0 = my_media.match(1)
ntwk1 = net1 ** ntwk0
ntwk2 = my_media.shunt_inductor (6.e-9)
ntwk3 = my_media.capacitor (10e-12)
ntwk4 = ntwk3 ** ntwk2 ** ntwk1
ntwk4.plot_s_smith()
plt.show()
print ntwk3.s