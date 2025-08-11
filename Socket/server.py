import socket
import threading
import subprocess
import os


tx_lock = threading.Lock()
SERVER_IP = "0.0.0.0"
SERVER_PORT = 5002
MAX_GAIN = 7
MIN_GAIN = 1

def handle_client(conn, addr):
    print(f"New connection from {addr}")
    conn.sendall("Continue".encode())
    total_len = 0

    # TODO: Check if file already exists, if it does, remove it
    # No need to do this, b+w already flushes out file
    base_path = "/home/debian/startup"
    file_path = base_path + "/test/test.raw"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try: 
        with conn:
            header = conn.recv(64).decode().split(";")
            if len(header) != 2:
                tx_lock.release_lock()
                return
            
            data_bytes = header[0]
            gain = header[1]

            if not (data_bytes.isdigit() and gain.isdigit()):
                tx_lock.release_lock()
                return
            
            conn.sendall("Ok".encode())

            # Set gain and data size
            data_bytes = int(data_bytes)
            if (int(gain)) < MIN_GAIN:
                gain = str(MIN_GAIN)
            elif (int(gain) > MAX_GAIN):
                gain = str(MAX_GAIN)

            with open(file_path, "b+w") as f:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        print(f"Connection closed by {addr}")
                        break
                    f.write(data)
                    total_len += len(data)
    except Exception as E:
        print(E)
        tx_lock.release_lock()
        return

    if data_bytes == total_len:

        # Handle running signal and deleting file
        exec_file = base_path + "/transmit_raw.elf"
        run_file = file_path
        subprocess.run([exec_file, f"--tx-file={run_file}", "--tx-gain="+gain])
        subprocess.run(["rm", file_path])

        print("Done")
    else:
        print("Failed, did not recieve whole file")
    tx_lock.release_lock()
def start_server():
    # Set up server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)

    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

    while True:
        print("Waiting for a new connection...")
        conn, addr = server_socket.accept()

        # Only handle one client at a time
        if tx_lock.acquire_lock(blocking=False):
            
            # Punt client onto a new thread
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()

            print("Ready for the next client.")
        else: 
            conn.sendall("Failed to run".encode())
            conn.close()

if __name__ == "__main__":
    start_server()

