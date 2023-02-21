# the `socket` module is the foundation for all networking client & server tools in python
import socket

target_host = '127.0.0.1'
target_port = 9998

# create a socket object - SOCK_DGRAM indicates that this will be a UDP client
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# send some data to the target
# since UDP is connectionless, there's no call to connect() first
client.sendto("Hellooo?".encode(), (target_host, target_port))

# receive some data (the response)
data, addr = client.recvfrom(4096)

print(data)