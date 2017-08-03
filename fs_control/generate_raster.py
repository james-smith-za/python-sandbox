import numpy as np
import datetime
import katpoint
import matplotlib.pyplot as plt
import calendar

target_str = raw_input("Enter target str (katpoint format): ")
file_name = raw_input("Enter file name: ")
raster_x_size = float(raw_input("Enter X size (degrees): "))
raster_y_size = float(raw_input("Enter Y size (degrees): "))

x_resolution = 0.05  # degrees
y_resolution = 0.05  # degrees
no_scans = int(np.ceil(raster_y_size / y_resolution)) + 1
if no_scans % 2 == 0:
    print "Y resolution will be increased slightly to make one in the middle."
    no_scans += 1
    y_resolution = raster_y_size / (no_scans - 1)

year = int(raw_input("Enter year: "))
month = int(raw_input("Enter month (number): "))
day = int(raw_input("Enter day (number): "))
hour = int(raw_input("Enter start time (hour): "))
minute = int(raw_input("Enter start time (minute): "))
second = int(raw_input("Enter start time (second): "))

settling_time = 60
integration_time = 60

start_time_tuple = (year, month, day, hour, minute, second)
myTime = datetime.datetime(year, month, day, hour, minute, second)
timestamp = calendar.timegm(start_time_tuple)

myTarget = katpoint.Target(target_str)
antenna_str = "Kuntunse, 5:45:2.48, -0:18:17.92, 116, 32.0"
antenna = katpoint.Antenna(antenna_str)
myTarget.antenna = antenna

xy_point_list = []
timestamps = []

with open("%s.snp"%(file_name), mode="w") as output_file:
    output_file.write('"' + "File automagically generated. X-Y raster script developed 2017-07-17 by James Smith." + '\n')
    output_file.write("\"File: %s.snp\n"%file_name)
    output_file.write("\"Katpoint Target: %s\n"%target_str)

    output_file.write("\"Raster size: %f x %f\n"%(raster_x_size, raster_y_size))
    output_file.write("\"%d horizontal scans.\n"%no_scans)
    output_file.write("\"%s\n"%(myTime.strftime("%Y.%M.%D-%H:%M:%S")))  # TODO: This needs fixing.


    def timestamp_increment():
        # TODO: This needs to be a bit more sophisticated
        return settling_time + integration_time

    # TODO: At this point, the user needs to be prompted about which sector to start in.
    output_file.write("\"%d-slew\n" % timestamp)
    # TODO: add slewing instruction and waiting period to get the antenna to the right place.

    for y in range(no_scans):
        if y % 2 == 0:
           for x in np.arange(-raster_x_size/2, raster_x_size/2 + x_resolution, x_resolution):
               xy_point_list.append((x, raster_y_size/2 - y_resolution*y))
               timestamps.append(timestamp)
               timestamp += timestamp_increment()
        else:
           for x in np.arange(raster_x_size/2, -raster_x_size/2 - x_resolution, -x_resolution):
               xy_point_list.append((x, raster_y_size/2 - y_resolution*y))
               timestamps.append(timestamp)
               timestamp += timestamp_increment()

    xy_points = np.array(xy_point_list)

    timestamps = np.array(timestamps)
    azel_points = np.degrees(myTarget.plane_to_sphere(np.radians(xy_points[:,0]), np.radians(xy_points[:,1]), timestamp=timestamps))
    target_azel_points = np.degrees(myTarget.azel(timestamps))

    if False:  # Change to True if you want a plot of the trajectory of the target and of the scan.
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(target_azel_points[0], target_azel_points[1], 'r')
        ax.plot(azel_points[0], azel_points[1], 'b')
        plt.show()
        plt.close(fig)

    for i in range(len(timestamps)):
        myTime = datetime.datetime.fromtimestamp(timestamps[i])
        output_file.write("\"%d,slew,nominal\n" % timestamps[i])
        output_file.write("!%s\n"%(myTime.strftime("%Y.%j.%H:%M:%S")))
        output_file.write("\"%d,track,nominal\n" % (timestamps[i] + settling_time))
        output_file.write("azeloff=%.6fd,%.6fd\n"%(target_azel_points[0][i] - azel_points[0][i],
                                                  (target_azel_points[1][i] - azel_points[1][i])))

    output_file.write("stop\n")


