import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import time
import katpoint

def generate_raster(total_extent, x_resolution=0.05, y_resolution=0.05, n_slew_points=5):
    total_extent = float(total_extent)
    n_scans = int(np.ceil(total_extent/y_resolution) + 1)
    n_points_per_scan = int(np.ceil(total_extent/x_resolution) + 1)
    if n_scans % 2 == 0:
        n_scans += 1

    y_space = np.linspace(-total_extent/2, total_extent/2, n_scans, endpoint=True)
    x_space = np.linspace(-total_extent/2, total_extent/2, n_points_per_scan, endpoint=True)

    x_points = np.array([0])
    y_points = np.array([0])

    for i in range(n_scans):
        # Slew to the start of the next scan
        x_points = np.concatenate((x_points, np.linspace(x_points[-1], x_space[0], n_slew_points)))
        y_points = np.concatenate((y_points, np.linspace(y_points[-1], y_space[i], n_slew_points)))
        # Scan
        x_points = np.concatenate((x_points, np.linspace(x_points[-1], x_space[-1], len(x_space) - 1, endpoint=True)))
        y_points = np.concatenate((y_points, np.ones(len(x_space) - 1)*y_space[i]))
        # Slew back to the target
        x_points = np.concatenate((x_points, np.linspace(x_points[-1], 0, n_slew_points)[1:]))
        y_points = np.concatenate((y_points, np.linspace(y_points[-1], 0, n_slew_points)[1:]))

    return x_points, y_points


def update_line(num, data, line):
    line.set_data(data[..., :num])
    return line,


if __name__ == "__main__":
    raster_size = 1
    antenna_str = "Kuntunse, 5:45:2.48, -0:18:17.92, 116, 32.0"
    target_az, target_el = 180, 85

    myTarget = katpoint.construct_azel_target(np.radians(target_az), np.radians(target_el))
    antenna_str = "Kuntunse, 5:45:2.48, -0:18:17.92, 116, 32.0"
    antenna = katpoint.Antenna(antenna_str)
    myTarget.antenna = antenna
    d_az, d_el = generate_raster(raster_size)

    x, y = np.degrees(myTarget.sphere_to_plane(np.radians(target_az + d_az), np.radians(target_el + d_el)))
    data = np.stack((x,y))

    fig = plt.figure()
    plt.xlim(np.min(x) - 0.5, np.max(x) + 0.5)
    plt.ylim(np.min(x) - 0.5, np.max(x) + 0.5)
    my_line, = plt.plot([], [], '.')

    line_ani = anim.FuncAnimation(fig, update_line, len(x), fargs=(data, my_line), interval=50, blit=True, repeat=False)

    plt.show()