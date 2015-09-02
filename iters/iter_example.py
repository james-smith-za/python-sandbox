# -*- coding: utf-8 -*-
"""
Simple code to check how iter(callable, sentinel) works. Seems as though it
works well enough.
"""

tuli = [(1, 2), (4, 5), (6, 7), None]
counter = -1

def returnTuli():
    global counter    
    counter += 1
    return tuli[counter]
    
for a, b in iter(returnTuli, None):
    print a, b
    