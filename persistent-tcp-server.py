# a simple tcp server that accepts a connection

import socket
import threading

bind_ip = "0.0.0.0"
bind_port = 5555
address = (bind_ip, bind_port)

server  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(address)

# start listening w/ max connection backlog of 5
server.listen(5)

print("[*] Listening on " + address[0] + ":" + str(address[1]))

def handle_client(client_socket):

    while True:

        request = client_socket.recv(1024)

        print("Received: " + request.decode())
        print("Sending acknowlegement")
        client_socket.send("ACK!".encode())

    #client_socket.close()

# put server into main loop
while True:
    
    client, addr = server.accept()

    print("Accepted connection from " + addr[0] + ":" + str(addr[1]))

    client_handler = threading.Thread(target=handle_client,args=(client,))
    client_handler.start()