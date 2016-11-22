import numpy as np
import datetime
import katpoint
import matplotlib.pyplot as plt
import calendar

target_name   = raw_input("Enter target name: ")
file_name     = raw_input("Enter file name: ")
target_RA     = raw_input("Enter target RA (format hh:mm:ss.pp): ")
target_DEC    = raw_input("Enter target DEC (format dd:mm:ss.pp): ")
raster_x_size = float(raw_input("Enter X size (degrees): "))
raster_y_size = float(raw_input("Enter Y size (degrees): "))

x_resolution = 0.06 # degrees - this has to do with the scan speed.
y_resolution = 0.10 # degrees, though this will be flexible. Has to do with the beam width.
no_scans = int(np.ceil(raster_y_size / y_resolution)) + 1
if no_scans % 2 == 0:
    print "Y resolution will be increased slightly to make one in the middle."
    no_scans += 1
    y_resolution = raster_y_size / (no_scans - 1)

year          = int(raw_input("Enter year: "))
month         = int(raw_input("Enter month (number): "))
day           = int(raw_input("Enter day (number): "))
hour          = int(raw_input("Enter start time (hour): "))
minute        = int(raw_input("Enter start time (minute): "))
second        = int(raw_input("Enter start time (second): "))

myTime = datetime.datetime(year, month, day, hour, minute, second)
myDelta = datetime.timedelta(seconds=1)

start_time_tuple = (year, month, day, hour, minute, second)
timestamp  = calendar.timegm(start_time_tuple)

myTarget = katpoint.construct_radec_target(target_RA, target_DEC)
antenna_str = "Kuntunse, 5:45:2.48, -0:18:17.92, 116, 32.0"
antenna = katpoint.Antenna(antenna_str)
myTarget.antenna = antenna

xy_point_list = []
timestamps    = []

output_file   = open("%s.snp"%(file_name), mode="w")
output_file.write('"' + "File automagically generated. X-Y raster script developed 2016-11-17 by James Smith." + '\n')
output_file.write("\"File: %s.snp\n"%(file_name))
output_file.write("\"Target: %s\n"%(target_name))
output_file.write("\"RA: %s\n"%(target_RA))
output_file.write("\"DEC: %s\n"%(target_DEC))
output_file.write("\"Raster size: %f x %f\n"%(raster_x_size, raster_y_size))
output_file.write("\"%d horizontal scans.\n"%(no_scans))
output_file.write("\"%s\n"%(myTime.strftime("%Y.%M.%D-%H:%M:%S"))) # TODO: This needs fixing.

def timestamp_increment():
    #TODO: This needs to be a bit more sophisticated
    return 1

#TODO: At this point, the user needs to be prompted about which sector to start in.
output_file.write("\"%d-slew\n"%(timestamp))
#TODO: add slewing instruction and waiting period to get the antenna to the right place.

for y in range(no_scans):
    output_file.write("\"%d-scan\n"%(timestamp))
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
    output_file.write("\"%d-slew\n"%(timestamp)) #TODO: put a check in to see whether this is the last one, then stop.

xy_points = np.array(xy_point_list)
plt.plot(xy_points[:,0], xy_points[:,1])
plt.show()

timestamps = np.array(timestamps)
azel_points = np.degrees(myTarget.plane_to_sphere(np.radians(xy_points[:,0]), np.radians(xy_points[:,1]), timestamp=timestamps))

for i in range(len(timestamps)):
    output_file.write("!%s\n"%(myTime.strftime("%Y.%j.%H:%M:%S")))
    output_file.write("source=azel,%.6fd,%.6fd\n"%(azel_points[0][i], azel_points[1][i]))
    myTime += myDelta

output_file.write("stop\n")
output_file.close()


plt.plot(azel_points[0], azel_points[1])
plt.show()

