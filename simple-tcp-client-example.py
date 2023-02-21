# the `socket` module is the foundation for all networking client & server tools in python
import socket

target_host = '142.250.217.238'
target_port = 80

# create a socket object - SOCK_STREAM indicates that this will be a TCP client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the client to the target host
client.connect((target_host, target_port))

# send some data
# python3 needs the string to be encoded 
# https://docs.python.org/3/library/stdtypes.html#str.encode
client.send("GET / HTTP/1.1\nHost: google.com\n\n".encode())

# receive some data (the response)
response = client.recv(4096)

# ensure we disconnect
client.close()

print(response)