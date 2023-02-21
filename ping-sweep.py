import platform
import subprocess
import sys

cmd = "ping -c1 127.0.0."

# if we're on windows, count arg is n instead of c
if platform.system() == 'Windows':
    cmd = "ping -n 1 127.0.0."

for x in range (0,255):
    p = subprocess.Popen(cmd+str(x), shell=True, stderr=subprocess.PIPE)

    while True:
        out = p.stderr.read(1)
        if out == b'' and p.poll() != None:
            break
        if out != '':
            sys.stdout.write(out.decode())
            sys.stdout.flush()