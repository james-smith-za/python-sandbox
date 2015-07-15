import socket
import struct
import itertools
import numpy as np
import matplotlib.pyplot as plt

localInterface = "10.0.0.3"
localPort = 60000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((localInterface, localPort))

print "Bound to UDP socket ", localInterface, ":", localPort

interleavedWindow = []

#Each FFT window is 4 packets of 4096 bytes each

print "Reading 4 packets of 4096 bytes"

for packetNo in range (0, 4):
    data, addr = sock.recvfrom(4096)
    print "Got packet from ", addr
    interleavedWindow.extend( list(struct.unpack("!1024i", data)) ) #interpret as integer data and append to window list

print "Done."

print "Plotting..."

I = []
Q = []
U = []
V = []

index = 0

for i in range(0, 1024):
    I.append(interleavedWindow[index])
    index += 1
    Q.append(interleavedWindow[index])
    index += 1
    V.append(interleavedWindow[index])
    index += 1
    U.append(interleavedWindow[index])


frequencyTicks_MHz = np.arange(0, 400, 400.0 / 1024.0)

print "Length is ", len(frequencyTicks_MHz)

fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, sharey=True)
ax1.plot(frequencyTicks_MHz, I)
ax2.plot(frequencyTicks_MHz, Q)
ax3.plot(frequencyTicks_MHz, U)
ax4.plot(frequencyTicks_MHz, V)

ax1.set_title("I")
ax2.set_title("Q")
ax3.set_title("U")
ax4.set_title("V")

fig.suptitle("S - Parameters")
ax4.set_xlabel("Frequency [MHz]")

plt.show()

