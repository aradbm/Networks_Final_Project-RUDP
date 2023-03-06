import subprocess
import os
"""
1. run this file
2. the 3 servers will be started
"""
servers = [
    ("localhost", "30001", "cat1.png"),
    ("localhost", "30002", "cat2.png"),
    ("localhost", "30003", "cat3.png"),
]
if __name__ == "__main__":
    print("starting servers")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    for server in servers:
        command = ["python3", "file_server.py"] + list(server)
        subprocess.Popen(command)
