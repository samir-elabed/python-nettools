#! /usr/bin/python3

import getopt
import os
import socket
import sys
import threading
import traceback

debug = False

# TODOs
### rename stuff! use 'client' instead of 'local'
### help text 
### build an http proxy service where receive the destination from the client for each request

def help():
    print("[TODO] HELPFUL HELP TEXT")
    sys.exit(0)


def proxy_handler(client_socket, remote_host, remote_port, receive_first):

    # connect to the target of our proxy
    print("[INFO] Opening connection to target {}:{}".format(remote_host, remote_port))
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:

        target_buffer = receive_from(remote_socket)
        print("[INFO] Received first response:")
        hexdump(target_buffer)

        # apply our middleware to the response we just received
        target_buffer = response_middleware(target_buffer)

        # if we've got something, give it back to our client
        if len(target_buffer):
            print("[INFO] Returning {} bytes to local".format(len(target_buffer)))
            client_socket.send(target_buffer.encode())

    # now we loop!
    # read from local -> send to remote -> receive from remote -> send to local -> REPEAT!
    while True:
        source_buffer = receive_from(client_socket)
        if len(source_buffer):
            print("[INFO] Received {} bytes from local:".format(len(source_buffer)))
            hexdump(source_buffer)

            # apply our middleware and return it to local
            source_buffer = request_middleware(source_buffer)
            remote_socket.send(source_buffer.encode())
            print("[INFO] Sending data to remote target".format(source_buffer))

        # now receive the response from the remote host
        target_buffer = receive_from(remote_socket)
        if len(target_buffer):
            print("[INFO] Received {} bytes from remote host:".format(len(target_buffer)))
            hexdump(target_buffer)

            # apply our middleware and return it to local
            target_buffer = response_middleware(target_buffer)
            print("[INFO] Sending data to client {}".format(target_buffer))
            client_socket.send(target_buffer.encode())
        
        # if we're out of data on both ends then close the connection
        if not len(source_buffer) and not len(target_buffer):
            client_socket.close()
            remote_socket.close()
            print("[INFO] All dried up, closed connections and closing handler thread")
            break


def receive_from(connection):

    global debug

    buffer = ""
    connection.settimeout(2)

    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer = buffer + data.decode()
    except:
        pass
    
    print("[DEBUG] Received data {}".format(buffer))
    return buffer


def hexdump(src, length=16):
    
    #result = []
    #digits = 4 #if isinstance(src, unicode) else 2
    #for i in range(0, len(src), length):
    #    s = src[i:i+length]
    #    hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
    #    text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
    #    result.append(b"%04X %-*s %s" % (i, length*(digits + 1), hexa, text))

    #print(b'\n'.join(result))
    print(src)


def request_middleware(buffer):
    return buffer


def response_middleware(buffer):
    return buffer


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # open a tcp connection with our local ip & port - we'll listen to it for packets and send them on after applying our middleware
    try:
        server.bind((local_host, local_port))
        print("[INFO] TCP connection opened with {}:{}".format(
            local_host, local_port))
    except Exception as e:
        print("[ERROR] Failed to open a TCP connection with TCP connection opened with {}:{}".format(
            local_host, local_port))
        print("[ERROR] Exception type: {}".format(str(e.__class__)))
        traceback.print_exc()
        sys.exit(0)

    # start listening
    queue_size = 10
    server.listen(queue_size)
    print("[INFO] Listening on {}:{} w/ a queue size of {}".format(local_host,
          local_port, queue_size))

    # enter our main server loop
    try:
        while True:
            client_socket, addr = server.accept()

            print("[INFO] Receiving inbound connection from {}:{}".format(
                addr[0], addr[1]))

            proxy_thread = threading.Thread(target=proxy_handler, args=(
                client_socket, remote_host, remote_port, receive_first))

            proxy_thread.start()
    except KeyboardInterrupt as ex:
        print("{}[INFO] Keyboard interrupt received - attempting to gracefully close listener.".format(os.linesep))
        try:
            server.close()
            print("[INFO] Listener connection closed. Peace out!")
        except:
            print(
                "[ERROR] Error occurred when attempting to close listener connection.")


def parse_args():

    global debug

    # if there's no args given then run the usage info command
    if not len(sys.argv[1:]):
        help()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "di:p:j:q:rh:", [
                                   "local-host", "local-port", "remote-host", "remote-port", "receieve-first", "help", "debug"])
    except getopt.GetoptError as err:
        print(str(err))
        help()

    # initialize argument variables w/ defaults
    local_host = '127.0.0.1'
    local_port = 9999
    remote_host = '127.0.0.1'
    remote_port = 21
    receive_first = False

    for o, a in opts:
        if o in ("-h", "--help"):
            help()
        elif o in ("-i", "--local-host"):
            local_host = a
        elif o in ("-p", "--local-port"):
            local_port = int(a)
        elif o in ("-j", "--remote-host"):
            remote_host = a
        elif o in ("-q", "--remote-port"):
            remote_port = int(a)
        elif o in ("-r", "--receive-first"):
            receive_first = True
        elif o in ("-d", "--debug"):
            debug = True
        else:
            help()

    if debug:
        print("[DEBUG] Arguments: {}, {}, {}, {}, {}"
              .format(local_host, local_port, remote_host, remote_port, receive_first))

    return (local_host, local_port, remote_host, remote_port, receive_first)


def main():

    server_loop(*parse_args())


main()
