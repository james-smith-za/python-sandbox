'''
Somewhat vain attempt to make a UV map for all the KAT-7 antennas during a several-hour observation of something.
Never quite figured out why I didn't get the same kind of result that CASA gave.
'''

import numpy as np
import matplotlib.pyplot as plt

delta_0 = -57. - 49./60 # Update this to CirX1's
latitude = (-30. - 43./60 - 17.34/3600)/180*np.pi

c = 3e8
frequency = 1.9e9 # This will need to be updated
wavelength = c/frequency

antennas = [[ 25.095, -9.095,  0.045],
            [ 90.284, 26.380, -0.226],
            [  3.985, 26.839,  0.000],
            [-21.605, 25.494,  0.019],
            [-38.272, -2.582,  0.391],
            [-61.595,-79.699,  0.792],
            [-87.988, 75.754,  0.138]]
antennas = np.array(antennas)

baselines = np.zeros((7,7,3))
for i in np.arange(7):
    for j in np.arange(7):
        baselines[i][j] = antennas[j] - antennas[i]

azimuth_angles = np.zeros((7,7))
horizontal_distances = np.zeros((7,7))
elevation_angles = np.zeros((7,7))
distances = np.zeros((7,7))

for i in np.arange(7):
    for j in np.arange(7):
        if i != j:
            azimuth_angles[i][j] = np.arctan(np.abs(baselines[i][j][0]/baselines[i][j][1]))
            if baselines[i][j][0] > 0 and baselines[i][j][1] > 0:
                pass
            if baselines[i][j][0] > 0 and baselines[i][j][1] < 0:
                azimuth_angles[i][j] = np.pi - azimuth_angles[i][j]
            if baselines[i][j][0] < 0 and baselines[i][j][1] < 0:
                azimuth_angles[i][j] = np.pi + azimuth_angles[i][j]
            if baselines[i][j][0] < 0 and baselines[i][j][1] > 0:
                azimuth_angles[i][j] = 2*np.pi - azimuth_angles[i][j]
            horizontal_distances[i][j] = np.sqrt(np.square(baselines[i][j][0]) + np.square(baselines[i][j][1]))
            elevation_angles[i][j] = np.arctan(baselines[i][j][2]/horizontal_distances[i][j])
            distances[i][j] = np.sqrt(np.square(baselines[i][j][0]) + np.square(baselines[i][j][1]) + np.square(baselines[i][j][2]))

XYZ = np.zeros((7,7,3))
for i in np.arange(7):
    for j in np.arange(7):
        if i != j:
            X = distances[i][j]*(np.cos(latitude)*np.sin(elevation_angles[i][j]) - np.sin(latitude)*np.cos(elevation_angles[i][j])*np.cos(azimuth_angles[i][j]))
            Y = distances[i][j]*(elevation_angles[i][j])*np.sin(azimuth_angles[i][j])
            Z = distances[i][j]*(np.sin(latitude)*np.sin(elevation_angles[i][j]) + np.cos(latitude)*np.cos(elevation_angles[i][j])*np.cos(azimuth_angles[i][j]))
            XYZ[i][j][0] = X
            XYZ[i][j][1] = Y
            XYZ[i][j][2] = Z

H = np.linspace(-5,5,100)
H = H*15/180*np.pi

transform_matrix = np.matrix([[np.sin(H),                       np.cos(H),                      0],
                              [-np.sin(delta_0)*np.cos(H),      np.sin(delta_0)*np.sin(H),      np.cos(delta_0)]])

uvs = np.zeros((7,7,3))
plt.ion()

for i in np.arange(7):
    for j in np.arange(7):
        if i != j:
            XYZ_ij = np.matrix(XYZ[i][j]).transpose()
            uv = transform_matrix*XYZ_ij/wavelength
            #uvs[i][j] = np.array(uv.transpose())
            u = np.array(uv[0])[0][0]
            v = np.array(uv[1])[0][0]
            plt.plot(u,v)

plt.grid('on')





