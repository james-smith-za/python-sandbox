import numpy as np

from vectors import vector
from particles import particle, tick_particles

import matplotlib
matplotlib.use("tkagg")

import matplotlib.pyplot as plt
from matplotlib import animation




#Sun   = particle("Sun", 2e30, (0, 0))
#Earth = particle("Earth", 6e24, (1.5e11, 0), (0, 3e4))
#Moon  = particle("Moon", 7.348e22, (1.5e11 + 3.84e9, 0), (0, 3e4 + 1e3))

Earth = particle("Earth", 6e24, (1.5e11, 0), (0, 0))
Moon  = particle("Moon", 7.348e22, (1.5e11 + 3.84e8, 0), (0, 1e3))

one_day = float(24 * 60 * 60)

particle_list = [Earth, Moon]
#for particle in particle_list:
#    print(particle)

fig = plt.figure(figsize=(15,15))
lims = 2e11
ax = fig.add_subplot(111, xlim=(1.4e11, 1.6e11), ylim=(-0.1e11, 0.1e11))
ax.grid()
particles = []
for particle in particle_list:
    line, = ax.plot([particle.position_vector.x], [particle.position_vector.y], 'o')
    particles.append(line)
day_text = ax.text(0.1, 0.90, "", transform=ax.transAxes)

def init():
    for i in range(len(particle_list)):
        particles[i].set_data([], [])
    day_text.set_text("0")
    return tuple([day_text] + particles)

def animate(i):
    tick_particles(particle_list, one_day)
    for j in range(len(particle_list)):
        particles[j].set_data([particle_list[j].position_vector.x], [particle_list[j].position_vector.y])
    day_text.set_text("{:d}".format(i))
    return tuple([day_text] + particles)

anim = animation.FuncAnimation(fig, animate, init_func=init, interval=125, blit=True)

plt.show()