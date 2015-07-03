import socket
import struct

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind('10.0.0.3',600000)
data, addr = s.recvfrom(1024)

format_str = '>' + 'B'*264
temp = struct.unpack(format_str,data)

print temp

