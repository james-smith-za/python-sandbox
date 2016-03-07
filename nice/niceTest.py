import multiprocessing
import os
import time

def subProcess():
    myPID = os.getpid()
    myPipe = os.popen("sudo renice -19 %d"%(myPID), 'w')
    myPipe.write("j3rusal3m\n")
    myPipe.close()
    currTime = time.time()
    nextTime = currTime + 20

    x = 0

    while time.time() < nextTime:
        x += 1

    print "subproc: ", x


#print os.getpid()
#commandString = "sudo renice -19 " + str(os.getpid())
#print commandString
#os.system(commandString)

subProc = multiprocessing.Process(target=subProcess)
subProc.start()

currTime = time.time()
nextTime = currTime + 20

x = 0

while time.time() < nextTime:
    x += 1

print "main: ", x
subProc.join()

