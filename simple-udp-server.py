import socket
import threading

bind_ip = "0.0.0.0"
bind_port = 9998
address = (bind_ip, bind_port)

server  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server.bind(address)

print("[*] Listening on " + address[0] + ":" + str(address[1]))

# put server into main loop
while True:
    
    req, addr = server.recvfrom(4096)

    print("Received data from " + addr[0] + ":" + str(addr[1]))

    print("Data: " + req.decode())
    
    server.sendto("Hi there!".encode(), addr)