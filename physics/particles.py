import numpy as np
from vectors import vector

# All units need to be SI units
G = 6.674e-11

def attraction(particle1, particle2):
    """Calculate the attractive force of particle 2 on particle 1.
    """
    force_numerator   = (G * particle1.mass * particle2.mass) 
    distance_vector   = vector(particle1.position_vector - particle2.position_vector)
    print(distance_vector)
    force_denominator = distance_vector.magnitude * distance_vector.magnitude
    force_magnitude   = force_numerator / force_denominator
    force_direction   = distance_vector.direction
    
    force_x           = force_magnitude * np.cos(force_direction)
    force_y           = force_magnitude * np.sin(force_direction)
    return vector((force_x, force_y))

def tick_particles(particle_list):
    for i in range(len(particle_list)):
        force = vector((0,0))
        for j in range(len(particle_list)):
            if i == j:
                continue
            force += 0
        

class particle(object):
    def __init__(self, mass, position_vector=None, velocity_vector=None, acceleration_vector=None):
        self.mass = float(mass)
        self.position_vector = vector(position_vector if position_vector != None else (0,0))
        self.initial_velocity_vector = vector(velocity_vector if velocity_vector != None else (0,0))
        self.final_velocity_vector = vector(velocity_vector if velocity_vector != None else (0,0))
        self.acceleration_vector = vector(acceleration_vector if acceleration_vector != None else (0,0))
    
    def __repr__(self):
        repr_str =  "Mass:\n\t{:.3f} kg\n".format(self.mass)
        repr_str += "Position:\n\tX: {:.3f} m\n\tY: {:.3f} m\n".format(self.position_vector.x, self.position_vector.y)
        repr_str += "Velocity:\n\tX: {:.3f} m/s\n\tY: {:.3f} m/s\n".format(self.initial_velocity_vector.x, self.initial_velocity_vector.y)
        repr_str += "acceleration:\n\tX: {:.3f} m/s^2\n\tY: {:.3f} m/s^2\n".format(self.acceleration_vector.x, self.acceleration_vector.y)
        return repr_str
        
    def tick(self, force, time_step):
        self.acceleration_vector = vector(force) / self.mass
        self.final_velocity_vector = vector(self.initial_velocity_vector + self.acceleration_vector*time_step)
        self.position_vector = vector(self.position_vector + (self.initial_velocity_vector + self.final_velocity_vector) * time_step / 2.0)
        # finally...
        self.initial_velocity_vector = self.final_velocity_vector
        