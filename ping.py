import subprocess

def ping(host):
    command = ['ping', '-C', '1', host]
    return subprocess.call(command)

