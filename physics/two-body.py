from particles import particle, tick_particles

import matplotlib.pyplot as plt
from matplotlib import animation


#Earth = particle("Earth", 5.9721986e24, (0, -4641.0), (0, -12.546163484918269))
#Moon  = particle("Moon", 7.3459e22, (3.844e8, 0), (0, 1020))


Sun   = particle("Sun",   1.988435e30,  (-449,                   0), (0,  -0.08946563005579765))
Earth = particle("Earth", 5.9721986e24, (1.49597887e11 - 4.67e6, 0), (0,  29800 -12.546163484918269))
Moon  = particle("Moon",  7.3459e22,    (-4641.e11 + 3.844e8,    0), (0,  29800 + 1020))

one_hour = float(60 * 60)

particle_list = [Sun, Earth, Moon]
#for particle in particle_list:
#    print(particle)

fig = plt.figure(figsize=(15,15))
lims = 2e11
ax = fig.add_subplot(111, xlim=(-lims, lims), ylim=(-lims, lims))
ax.grid()
particles = []
for particle in particle_list:
    line, = ax.plot([particle.position_vector.x], [particle.position_vector.y], '.')
    particles.append(line)
day_text = ax.text(0.1, 0.90, "", transform=ax.transAxes)

def init():
    for i in range(len(particle_list)):
        particles[i].set_data([], [])
    day_text.set_text("0")
    return tuple([day_text] + particles)

def animate(i):
    tick_particles(particle_list, one_hour)
    for j in range(len(particle_list)):
        particles[j].set_data([particle_list[j].position_vector.x], [particle_list[j].position_vector.y])
    day_text.set_text("{:d}".format(i // (24)))
    return tuple([day_text] + particles)

anim = animation.FuncAnimation(fig, animate, init_func=init, interval=0.2, blit=True)

plt.show()