import socket

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

if __name__ == "__main__":
    ip = get_ip_address()
    print(f"Your laptop's IP address is: {ip}")
