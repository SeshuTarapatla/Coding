import os
from pathlib import Path
import sys
import subprocess
import signal
import socket
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# Path to store the PID of the background process
PID_FILE = "ftp_server.pid"

def get_ip_address():
    try:
        # Connect to a dummy address to get the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        return f"Error getting IP address: {e}"

def start_server(folder, username, password, ip=None, port=2121):
    """Start the FTP server."""
    # Authorization setup
    authorizer = DummyAuthorizer()
    authorizer.add_user(username, password, folder, perm="elradfmwMT")
    handler = FTPHandler
    handler.authorizer = authorizer

    # FTP server setup
    if not ip: ip = get_ip_address()
    server = FTPServer((ip, port), handler)
    print(f"FTP server running at {ip}:{port}")
    server.serve_forever()

def start_in_background(folder, username, password):
    """Start the FTP server as a background process."""
    if os.path.exists(PID_FILE):
        print("Server is already running.")
        return

    # Spawn the process in the background
    process = subprocess.Popen(
        [sys.executable, __file__, "run-server", folder, username, password],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setpgrp
    )

    # Write the PID to a file
    with open(PID_FILE, "w") as pid_file:
        pid_file.write(str(process.pid))
    print("FTP server started in the background.")

def stop_server():
    """Stop the FTP server."""
    if not os.path.exists(PID_FILE):
        print("No server is running.")
        return

    # Read the PID and kill the process
    with open(PID_FILE, "r") as pid_file:
        pid = int(pid_file.read())
    try:
        os.killpg(pid, signal.SIGTERM)  # Kill the process group
        print("FTP server stopped.")
    except ProcessLookupError:
        print("Server process not found.")
    os.remove(PID_FILE)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  ftpcli.py start-server <folder> <username> <password>")
        print("  ftpcli.py stop-server")
        print("  ftpcli.py run-server <folder> <username> <password>")
        sys.exit(1)

    command = sys.argv[1]

    folder = Path("D:\Movies\mStorage")
    username = "seshu"
    password = "28324630"

    # if command == "start-server":
    #     if len(sys.argv) != 5:
    #         print("Usage: ftpcli.py start-server <folder> <username> <password>")
    #         sys.exit(1)
    #     _, _, folder, username, password = sys.argv
    #     start_in_background(folder, username, password)
    # elif command == "stop-server":
    #     stop_server()
    # elif command == "run-server":
    #     if len(sys.argv) != 5:
    #         print("Usage: ftpcli.py run-server <folder> <username> <password>")
    #         sys.exit(1)
    #     _, _, folder, username, password = sys.argv
    #     start_server(folder, username, password)
    # else:
    #     print(f"Unknown command: {command}")
    #     print("Usage:")
    #     print("  ftpcli.py start-server <folder> <username> <password>")
    #     print("  ftpcli.py stop-server")

    if command == "start-server":
        start_in_background(folder, username, password)
        print(f"Started ftp-server in IP: {get_ip_address()}, Port: {2121}")
    elif command == "stop-server":
        stop_server()
    elif command == "run-server":
        print(f"Starting ftp-server in IP: {get_ip_address()}, Port: {2121}")
        start_server(folder, username, password)
    else:
        print(f"Unknown command: {command}")
        print("Usage:")
        print("  ftpcli.py start-server")
        print("  ftpcli.py stop-server")
        print("  ftpcli.py run-server")
