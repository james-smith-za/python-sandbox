import multiprocessing
import time

def func1():
    while True:
        print "function 1 is running"
        time.sleep(1)

def func2():
    while True:
        print "function 2 is running"
        time.sleep(1)

def func3():
    while True:
        print "function 3 is running"
        time.sleep(1)

def func4():
    while True:
        print "function 4 is running"
        time.sleep(1)

def func5():
    while True:
        print "function 5 is running"
        time.sleep(1)

def func6():
    while True:
        print "function 6 is running"
        time.sleep(1)

def func7():
    while True:
        print "function 7 is running"
        time.sleep(1)

def func8():
    while True:
        print "function 8 is running"
        time.sleep(1)

def func9():
    while True:
        print "function 9 is running"
        time.sleep(1)

def func10():
    while True:
        print "function 10 is running"
        time.sleep(1)

if __name__ == "__main__":
    func1_proc = multiprocessing.Process(target=func1)
    func2_proc = multiprocessing.Process(target=func2)
    func3_proc = multiprocessing.Process(target=func3)
    func4_proc = multiprocessing.Process(target=func4)
    func5_proc = multiprocessing.Process(target=func5)
    func6_proc = multiprocessing.Process(target=func6)
    func7_proc = multiprocessing.Process(target=func7)
    func8_proc = multiprocessing.Process(target=func8)
    func9_proc = multiprocessing.Process(target=func9)

    func1_proc.start()
    func2_proc.start()
    func3_proc.start()
    func4_proc.start()
    func5_proc.start()
    func6_proc.start()
    func7_proc.start()
    func8_proc.start()
    func9_proc.start()

