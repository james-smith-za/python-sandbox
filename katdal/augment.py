import h5py
import numpy as np
import datetime
import pandas as pd

# Set up option parser
from optparse import OptionParser
option_parser = OptionParser(usage="python %prog [options] filename")

if False: # I've decided not to use these quite yet. Don't want to just delete though.
    option_parser.add_option("-t", "--temperature",
                             action="store",
                             default=None,
                             help="Outside air temperature (deg C)")
    option_parser.add_option("-p","--pressure",
                             action="store",
                             default=None,
                             help="Outside air pressure (mbar)")
    option_parser.add_option("-u","--humidity",
                             action="store",
                             default=None,
                             help="Relative humidity (percent)")
    option_parser.add_option("-s","--speed",
                             action="store",
                             default=None,
                             help="Wind speed (m/s)")
    option_parser.add_option("-d","--direction",
                             action="store",
                             default=None,
                             help="Wind direction (degrees clockwise from N)")

(options, args) = option_parser.parse_args()

if len(args) != 2:
    option_parser.error("Wrong number of arguments - two filename expected, %d arguments received."%(len(args)))

try:
    print "Opening %s for augmenting..."%(args[0])
    h5file = h5py.File(name=args[0], mode='r+')
    print "File successfully opened."
except IOError:
    print "Error opening h5 file! Check spelling and path."
    exit()

try:
    print "Opening %s for antenna position data..."%(args[1])
    csv_file = pd.read_csv(args[1], skipinitialspace=True)
    print "File successfully opened."
except IOError:
    print "Error opening csv file! Check spelling and path."
    exit()
except pd.parser.CParserError:
    # TODO: point to the line number. Figure out how to get exception's text.
    print "Line size problem in csv file. Must fix manually."
    exit()




##### Miscellaneous info about the file printed for the user's convenience. #####
timestamps = h5file["Data/Timestamps"]
begin_time = timestamps[0]
end_time = timestamps[-1]
duration = end_time - begin_time
duration_str = "%dh %dm %.2fs"%( int(duration/3600), int(duration - int(duration/3600)*3600)/60, duration - int(duration/3600)*3600 - (int(duration - int(duration/3600)*3600)/60)*60)
print "Recording start:\t\t%s UTC\nRecording end:\t\t\t%s UTC\nDuration:\t\t\t%s\n"%(datetime.datetime.fromtimestamp(begin_time).isoformat(), datetime.datetime.fromtimestamp(end_time).isoformat(), duration_str)

vis_shape = h5file["Data/VisData"].shape

print "Accumulation length:\t\t%.2f ms"%((timestamps[1] - timestamps[0])*1000)
print "Number of accums:\t\t%d"%(vis_shape[0] - 1)
print "Number of frequency channels:\t%d"%(vis_shape[1])


sensor_group = h5file["MetaData/Sensors"]

##### Weather / Environment information #####
# This section ought only to be here temporarily. At time of writing (Oct 2016), the
# site weather station at Kuntunse isn't available, so we will do some mock weather
# data to satisfy katpoint's requirements.
# This section can later be adapted to read real data once the data becomes available.

while True: # because Python doesn't have do..while loops... :-/
    dummy = raw_input("Add default (dummy) enviroment sensor data? (y/n) ")
    try:
        if (dummy.lower()[0] == 'y') or (dummy.lower() == 'n'):
            break
        else:
            print "Invalid response."
    except IndexError:
        print "Invalid response."
        pass


# TODO: Think about putting some sort of attribute somewhere to test whether or not the file has already been augmented.
#       Then the other try / except blocks shouldn't be necessary.

try:
    enviro_group = sensor_group.create_group("Enviro")
except ValueError:
    print "Warning! Enviro group already exists. File may already have been previously augmented. Carry on regardless."
    enviro_group = sensor_group["Enviro"]

enviro_timestamps = np.arange(begin_time, end_time, 10, dtype=np.float64) # The enviro sensor data needn't be high resolution, 10 seconds for dummy data should be okay.

temperature_array   = []
pressure_array      = []
humidity_array      = []
windspeed_array     = []
winddirection_array = []


if dummy.lower()[0] == 'y': # Use the default dummy data
    temperature   =   30.0 # degC
    pressure      = 1010.0 # mbar
    humidity      =   80.0 # percent
    windspeed     =    0.0 # m/s
    winddirection =    0.0 # deg (heading)
    enviro_group.attrs["note"] = "Augmented with dummy default data."
else:
    temperature   = float(raw_input("Please enter the temperature (deg C): "))
    pressure      = float(raw_input("Please enter the pressure (mbar): "))
    humidity      = float(raw_input("Please enter the relative humidity (percent): "))
    windspeed     = float(raw_input("Please enter the wind speed (m/s): "))
    winddirection = float(raw_input("Please enter the wind direction (degrees CW from N): "))
    enviro_group.attrs["note"] = "Augmented with user-provided static environment data."

for time in enviro_timestamps:
        temperature_array.append((time, temperature, "nominal"))
        pressure_array.append((time, pressure, "nominal"))
        humidity_array.append((time, humidity, "nominal"))
        windspeed_array.append((time, windspeed, "nominal"))
        winddirection_array.append((time, winddirection, "nominal"))

temperature_dset   = np.array(temperature_array, dtype=[('timestamp','<f8'),('value', '<f8'),('status', 'S7')])
pressure_dset      = np.array(pressure_array, dtype=[('timestamp','<f8'),('value', '<f8'),('status', 'S7')])
humidity_dset      = np.array(humidity_array, dtype=[('timestamp','<f8'),('value', '<f8'),('status', 'S7')])
windspeed_dset     = np.array(windspeed_array, dtype=[('timestamp','<f8'),('value', '<f8'),('status', 'S7')])
winddirection_dset = np.array(winddirection_array, dtype=[('timestamp','<f8'),('value', '<f8'),('status', 'S7')])

try:
    print "\nPopulating air temperature dataset with %.2f degrees..."%(temperature)
    enviro_group.create_dataset("air.temperature", data=temperature_dset)
    enviro_group["air.temperature"].attrs["description"] = "Air temperature"
    enviro_group["air.temperature"].attrs["name"] = "air.temperature"
    enviro_group["air.temperature"].attrs["type"] = "float64"
    enviro_group["air.temperature"].attrs["units"] = "degC"

    print "Populating air pressure dataset with %.2f mbar..."%(pressure)
    enviro_group.create_dataset("air.pressure", data=pressure_dset)
    enviro_group["air.pressure"].attrs["description"] = "Air pressure"
    enviro_group["air.pressure"].attrs["name"] = "air.pressure"
    enviro_group["air.pressure"].attrs["type"] = "float64"
    enviro_group["air.pressure"].attrs["units"] = "mbar"

    print "Populating relative humidity dataset with %.2f percent..."%(humidity)
    enviro_group.create_dataset("relative.humidity", data=humidity_dset)
    enviro_group["relative.humidity"].attrs["description"] = "Relative humidity"
    enviro_group["relative.humidity"].attrs["name"] = "relative.humidity"
    enviro_group["relative.humidity"].attrs["type"] = "float64"
    enviro_group["relative.humidity"].attrs["units"] = "percent"

    print "Populating wind speed dataset with %.2f m/s..."%(windspeed)
    enviro_group.create_dataset("wind.speed", data=windspeed_dset)
    enviro_group["wind.speed"].attrs["description"] = "Wind speed"
    enviro_group["wind.speed"].attrs["name"] = "wind.speed"
    enviro_group["wind.speed"].attrs["type"] = "float64"
    enviro_group["wind.speed"].attrs["units"] = "m/s"

    print "Populating wind direction dataset with %.2f degrees (bearing)..."%(winddirection)
    enviro_group.create_dataset("wind.direction", data=winddirection_dset)
    enviro_group["wind.direction"].attrs["description"] = "Wind direction"
    enviro_group["wind.direction"].attrs["name"] = "wind.direction"
    enviro_group["wind.direction"].attrs["type"] = "float64"
    enviro_group["wind.direction"].attrs["units"] = "degrees (bearing)"
except RuntimeError:
    print "Environment sensor dataset(s) already exist. Datafile previously augmented?"
else:
    print "Environment data written."


##### Antenna position information #####

print "\nChecking if sterile datasets were created by the RoachAcquisitionServer."

antenna_pos_dataset_list = ["pos.actual-dec",
                            "pos.actual-ra",
                            "pos.actual-scan-azim",
                            "pos.actual-scan-elev",
                            "pos.request-scan-azim",
                            "pos.request-scan-elev"]

for dset_name in antenna_pos_dataset_list:
    try:
        del sensor_group["Antennas/ant1/%s"%(dset_name)]
    except KeyError:
        print "No sterile %s dataset found."%(dset_name)
    else:
        print "Sterile %s dataset removed."%(dset_name)

print "\nOpening %s for position sensor addition..."%(args[1])
# Check to see that the files line up in at least some way.

csv_begin_time = float(csv_file["Timestamp"][0]) / 1000
csv_end_time   = float(csv_file["Timestamp"][len(csv_file["Timestamp"]) - 1]) / 1000
csv_duration = csv_end_time - csv_begin_time
csv_duration_str = "%dh %dm %.2fs"%( int(csv_duration/3600), int(csv_duration - int(csv_duration/3600)*3600)/60, csv_duration - int(csv_duration/3600)*3600 - (int(csv_duration - int(csv_duration/3600)*3600)/60)*60)
print "Pos data start:\t\t%s UTC\nPos data end:\t\t%s UTC\nDuration:\t\t%s\n"%(datetime.datetime.fromtimestamp(csv_begin_time).isoformat(), datetime.datetime.fromtimestamp(csv_end_time).isoformat(), csv_duration_str)

if (begin_time < csv_begin_time) or (end_time > csv_end_time):
    print "\nError! RF data not completely covered by position data!\nExiting..."
    h5file.close()
    exit()
else:
    print "Overlap detected."

# Now to find where in the csv datafile the overlap is. No sense in putting the whole thing in.
# Explanation about these try/except statements: If there are multiple log .txt files, then I tend to just
# cat them together. The header lines get interleaved as well though, which fact took me quite a while to
# figure out... I need a more unix-y cat command to do it properly.

try:
    csv_lower_index = 0
    while (float(csv_file["Timestamp"][csv_lower_index]) / 1000.0) < begin_time:
        csv_lower_index += 1
        # While loop will break when it gets lower or equal to
    csv_lower_index -= 1 # Set it back to just before the RF data starts.
    print "\nLower bound: %d."%(csv_lower_index)
    print "CSV lower index: %.2f\tH5file lower index: %.2f"%(csv_file["Timestamp"][csv_lower_index]/1000, begin_time)
    print "Difference: %.2f"%(np.abs(csv_file["Timestamp"][csv_lower_index] / 1000 - begin_time))
except ValueError:
    print "There are funny lines in the CSV file. They might be somewhere around line %d."%(csv_lower_index)

try:
    csv_upper_index = len(csv_file["Timestamp"]) - 1
    while (float(csv_file["Timestamp"][csv_upper_index]) / 1000.0) > end_time:
        csv_upper_index -= 1
        # While loop will break when it gets lower or equal to
    csv_upper_index += 1 # Set it back to just after the RF data ends.
    print "\nUpper bound: %d."%(csv_upper_index)
    print "CSV upper index: %.2f\tH5file upper index: %.2f"%(csv_file["Timestamp"][csv_upper_index]/1000, end_time)
    print "Difference: %.2f"%(np.abs(csv_file["Timestamp"][csv_upper_index] / 1000 - end_time))
except ValueError:
    print "There are funny lines in the CSV file. They might be somewhere around line %d."%(csv_upper_index)





h5file.close()

print "\nAugmentation complete."





