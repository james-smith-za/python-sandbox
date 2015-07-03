##!/usr/bin/env python
#import signal
#import sys
#def signal_handler(signal, frame):
        #print('You pressed Ctrl+C!')
        #sys.exit(0)
#signal.signal(signal.SIGINT, signal_handler)
#print('Press Ctrl+C')
#signal.pause()

import signal
import time

def handler(signum, frame):
    print 'Here you go'
    f = raw_input('enter something')
    print f
    
signal.signal(signal.SIGINT, handler)

#time.sleep(10) # Press Ctrl+c here
signal.pause()
print 'I thought I\'d carry on doing something'
