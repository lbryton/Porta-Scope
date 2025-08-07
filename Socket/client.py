import socket

# Will ask for server ip when actually setup, currently using dummy ip
import os
from dotenv import load_dotenv
load_dotenv()
SERVER_IP = os.getenv("SERVER_IP")
SERVER_PORT = int(os.getenv("SERVER_PORT"))

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client_socket.connect((SERVER_IP, SERVER_PORT))
    data = client_socket.recv(1024).decode()
    if "Continue" == data:
        print("passed")
        with open("./Socket/client.py", "rb") as f:
            bytes_sent = client_socket.sendfile(f)

        # Close the socket, everthing else is dealt with by the server
        client_socket.shutdown(socket.SHUT_WR)
        client_socket.close()
    else:
        print("failed")
        client_socket.close()

except Exception as E:
    print(f"Failed: {E}")