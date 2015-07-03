#python function for handling high data rate input from the ROACH 10gbe. It does this using multproc, setting up a UDP server which parses the data packets, and puts them into a heap for handling by the other process. This allows the use of multiple cores.
#CJC

import socket
import struct
import numpy
import multiprocessing as mp
import time
import pylab

##create a queue for handling the requests
dataQueue=mp.Queue()

#define a udp packet server that listens for the ROACH packets. Its job is to take the incoming packets, parse them, create new simple time stamps, put them in a multiproc heap for handling by the other process.
def udpHandler(dataQ):

    #first we set up the UDP socket
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #and bind to the address and ports that we have set up on the roach
    s.bind(("10.0.0.3",60000))

    #create a nice new vector of zeros
    newTimeQ=numpy.zeros(4096)
    newTime=0
    iCount=0
    test="";
    ##dataIn=(); # Creates a tuple. Why?
    dataFrame=numpy.array([]);
    dataPackets=0

    while True:
        #define the length of the data part of the packet. 8 bytes are SPEADlike header information
        list_len=264-8

        #grab/accept the data from the ROACH/ We'll accept up to 1024 bytes
        data,addr=s.recvfrom(1024) # This number could probably change to be 264

        #only bytes 8->264 are actually data. Bytes 0-7 are headers
        #We will only put the data part of the message into the multiproc queue
        test +=data[8:264]
        #and the format of that data is as follows:
        format_str='>'+'BBBBBBBB'+'B'*list_len # I changed this to big-endian in the first instance, and unsigned char in the last, because I suspect that bit-manipulations on signed numbers might end up being a bit odd. # I am now no longer certain of this, perhaps 'b' might be better

        # we will unpack the data we have received so we can look at it directly before it goes ont the multiproc heap. Note that this is the full data packet we are looking at
        dd=struct.unpack(format_str,data)
        #dataIn=dataIn + dd[6:50]
        #numpy.array(dd[6:50])
        #dataFrame=numpy.append(dataFrame,dataIn)
        #for i in range(6,50):
        #    ttimag = dd[i]&0x0f
        #    ttreal = dd[i]>>4&0x0f
        #    tt = ttreal + ttimag*1j
        #    ttPow = tt**2

        #and this is the format of the header part of the packet
        timeStamp = ((dd[3]<<4)+((dd[4]>>4&0x0f)))<<12
        timeStamp2 = ((dd[5]))<<4
        timeStamp3 = dd[4]&0x0f # Note that this just makes the 4 MSBs zero, doesn't remove them, so the signed / unsigned interpretation stays.

        ##the header is defined as follows
        #bits 0-15 antenna base
        #bits 16-27 pcnt
        #bits 29-63 timestamp
        #    print 'antenna base',dd[7],dd[6]
        #    print 'pcnt',dd[5],dd[4]>>4&0x0f
        #    print 'timestamp',dd[4]&0x0f,dd[3],dd[2],dd[1],dd[0]

        #do a little but of decoding of the time part of the header
        oldTime=newTime
        newTime = timeStamp+timeStamp2+timeStamp3
        newTimeQ[iCount]=newTime
        iCount=iCount+1
        #   print oldTime,newTime

        ##now we have 32 packets per 4096 pt fine FFT. When we have received all of those we will put the data in the queue
        #This all tallies up to 8192 bytes, because the two polarisations are interleaved.
        if iCount>=32:
            #first we make ourselves a new simpler header that just has the datapacket number (dataPackets) which will increment up to 32, and the time that we have decoded from the original header
            datamsg=numpy.append(dataPackets, newTimeQ)
            #then we put that on the queue. So the first item is the time.
            dataQ.put(datamsg)
            #then we put the data part of the packet extracted earlier in the queue . This is bytes 8-264 of the packet. So the second item will be the  data.
            dataQ.put(test)
            ##dataIn=()
            #print len(test)
            test=""
            dataPackets=dataPackets+1
            iCount=0
            #print 'iCount=',iCount

        #if the oldTime+1 is not newtime then we have dropped a packet and we print this out as a basic error check.
        if((oldTime+1!=newTime)):
            print 'tt',oldTime,newTime

##and this is the definition of the processor that gulps up the packets received in the udpHandler process.
def dataProcessor(dataQ):
    i=0
    #number of accumulations
    accumulations=1000
    accCnt=0
    #instantiate a few things
    data=numpy.zeros(4096,dtype=numpy.complex)
    I1total=numpy.zeros(4096,dtype=numpy.complex)
    I2total=numpy.zeros(4096,dtype=numpy.complex)
    Qtotal=numpy.zeros(4096,dtype=numpy.complex)
    Utotal=numpy.zeros(4096,dtype=numpy.complex)

    while(1):
        #get the data from the heap when it is put there. This is a blocking process so it just waits until there is data there. Remember the first item will be the time, while the second item will be the data
        t=dataQ.get()
        #and the second item is the data
        tstring=dataQ.get()
        #print 'gotcha',t[0]
        list_len=264-8
        format_str=('<'+'B'*32*list_len)
        #now we unpack the data from the binary
        dd=struct.unpack(format_str,tstring) #I don't think it's entirely necessary to use struct to unpack this stuff. struct can unpack a numpy array just fine, but why do it when the type that comes out is a numpy array anyway?
        #and create a numpy array with suitably mysterious name.
        tt=numpy.array(dd)

        #now we take out the byte information from the numpy array using bt shifting. There may be a better more elegant way of doing this, but I have yet to discover it.
        ttimag = ((tt&0x0f))
        ttreal = (((tt>>4)&0x0f))
        ttimag[ttimag>=8]=ttimag[ttimag>=8]-16 #I strongly suspect that these lines don't do what you think they do. I don't know of any software package which uses this syntax, I'd use a for loop.
        ttreal[ttreal>=8]=ttreal[ttreal>=8]-16
#       print ttimag,ttreal
        tt = ttreal + ttimag*1j
    #   print t[0]
      # the odd numbers are the Pol 2 FFT channels
        Pol2Complex = tt[1::2]
        #while the even numbers are the Pol 1 FFT channels
        Pol1Complex = tt[0::2]
        #and then we create a proxy of the power by taking absoltue.
        I1 = numpy.abs((Pol1Complex))
        I2 = numpy.abs((Pol2Complex))
    #   I1 = numpy.real(Pol1Complex)
    #   I2 = numpy.real(Pol2Complex)
        Q=numpy.real(Pol1Complex*Pol2Complex)
        U=numpy.imag(Pol1Complex*Pol2Complex)
        I1total+=I1
        I2total+=I2
        Qtotal+=Q
        Utotal+=U

        if i>=accumulations:
            print time.time()
            print I1total
            print I2total
            numpy.savetxt("I1total.csv", numpy.real(I1total), delimiter=",",fmt='%10.5f')
            numpy.savetxt("I2total.csv", numpy.real(I2total), delimiter=",",fmt='%10.5f')
            I1total=numpy.zeros(4096,dtype=numpy.complex)
            I2total=numpy.zeros(4096,dtype=numpy.complex)
            Qtotal=numpy.zeros(4096,dtype=numpy.complex)
            Utotal=numpy.zeros(4096,dtype=numpy.complex)
            #pylab.ion()
            #pylab.plot(I1total)
            i=0
        i=i+1

    #   print(dd[0:1024])
def main():
    ##first we setup the child processes
    udpH=mp.Process(target=udpHandler,args=(dataQueue,))
    dataP=mp.Process(target=dataProcessor,args=(dataQueue,))
    udpH.start()
    dataP.start()

    ##we do this so that the zombie multiprocs will terminate after ctrl-c
    try:
        udpH.join()
        dataP.join()
    except KeyboardInterrupt:
        print 'parent received ctrl-c'
        udpH.terminate()
        udpH.join()
        dataP.terminate()
        dataP.join()
        #tt=numpy.array(dd[6:256])
        #ttcomplex=tt&0x0f
        #ttreal=tt>>4&0x0f
        #ttVals=ttreal+1j*ttcomplex
        #power=numpy.abs(ttVals)
        #Pol1Complex = ttVals[0::2]
        #Pol2Complex = ttVals[1::2]
        #I1 = Pol1Complex*Pol1Complex
        #I2 = Pol2Complex*Pol2Complex
        #Q=numpy.real(Pol1Complex[0:124]*Pol2Complex[0:124])
        #U=numpy.imag(Pol1Complex[0:124]*Pol2Complex[0:124])
        #print dd[0],dd[1],dd[2],dd[3],dd[4]>>4&0x0f,dd[5],dd[4]&0x0f,I1[0:10],I2[0:10],Q[0:10],U[0:10]
        #print dd[0],dd[1],dd[2],dd[3],dd[4]>>4&0x0f,dd[4]&0x0f,dd[5],dd[6],dd[7],dd[8],numpy.size(Pol1Complex)
        #print dd[0],dd[1],dd[2],dd[3],dd[4]>>4&0x0f,dd[4]&0x0f,dd[5],dd[6],dd[7],dd[8]
