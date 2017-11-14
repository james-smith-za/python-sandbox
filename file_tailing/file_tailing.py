'''
The idea here is that you can tail the output of the file periodically to see if new stuff has come in.
This could be useful for whatever purposes.

At the moment, I can't see an easy way to do this asynchronously, only by polling the file for changes
every <sleep_time> seconds, but this should work well enough.
'''
import time

f = open('some_file')

p = 0

while True:
    f.seek(p)
    latest_data = f.read()
    p = f.tell()
    if latest_data:
        print latest_data
        print str(p).center(10).center(80, '=')
    time.sleep(1)

