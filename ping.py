import subprocess

def ping(host):
    command = ['ping', '-c', '1', '-t', '1', host]
    return subprocess.call(command)

