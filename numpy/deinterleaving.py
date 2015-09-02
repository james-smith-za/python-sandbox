"""
deinterleaving - trying to get a look at the disassembly code to see what 
I've *actually* been doing, and try to see if it can be made faster
somehow.

Looking at the byte-code for the numpy stuff doesn't help much - 
it's compiled. Would need to look at numpy's source code.
"""

import numpy as np
import dis

def separateSoup():
    alphabetSoup = ['a', 'A', 'b', 'B', 'c', 'C', 'd', 'D', 'e', 'E', 'f', 'F',]
    lowercase = alphabetSoup[0::2]
    uppercase = alphabetSoup[1::2]
    
    alphabetStrict = np.reshape(np.dstack((lowercase, uppercase)), (1, -1))[0]
    
    #print lowercase, uppercase
    
dis.disco(separateSoup.__code__)