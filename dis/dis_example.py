# -*- coding: utf-8 -*-
"""
just mucking about with dis module - newly discovered.
"""

import dis

counter = 0
li = [0,1,2,3,4,5,6,7,8,9,None]


def returnValue():
    global counter
    counter += 1
    return li[counter]

def useForLoop():
    for i in iter(returnValue, None):
        print i
        
def useWhileLoop():
    myCounter = 0    
    while 1:
        if li[myCounter] is None:
            break

print "====== with For ====="
dis.disco(useForLoop.__code__)
print "===== with While ====="
dis.disco(useWhileLoop.__code__)