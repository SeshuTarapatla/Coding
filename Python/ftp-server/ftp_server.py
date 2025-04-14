from pathlib import Path
from threading import Thread
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import os

from ip_addr import get_ip_address


def start_ftp_server(folder, username, password, ip=None, port=2121):
    # Ensure the folder exists
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Set up user authorization
    authorizer = DummyAuthorizer()
    authorizer.add_user(username, password, folder, perm="elradfmwMT")  # Full permissions

    # Set up the FTP handler
    handler = FTPHandler
    handler.authorizer = authorizer

    # Set up and start the server
    if not ip: ip = get_ip_address()
    server = FTPServer((ip, port), handler)
    print(f"FTP server started at {ip}:{port}")
    print(f"Access files in '{folder}' using username '{username}' and password '{password}'")
    server.serve_forever()

if __name__ == "__main__":
    # Configuration
    folder_path = Path(r"C:\Users\seshu\Videos\Series")
    ftp_username = "seshu"
    ftp_password = "1234"

    ftp_server = Thread(target=start_ftp_server, args=[folder_path, ftp_username, ftp_password])

    # Start the server
    try:
        ftp_server.start()
        while ftp_server.is_alive():
            ftp_server.join(1)
    except KeyboardInterrupt:
        print(f"Received stop signal >>> FTP server stopped")
