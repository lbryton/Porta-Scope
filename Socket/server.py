import socket
import threading
import subprocess
import os


tx_lock = threading.Lock()
SERVER_IP = "0.0.0.0"
SERVER_PORT = 5001

def handle_client(conn, addr):
    print(f"New connection from {addr}")
    conn.sendall("Continue".encode())
    total_len = 0

    # TODO: Check if file already exists, if it does, remove it
    # No need to do this, b+w already flushes out file
    base_path = "/home/debian/startup"
    file_path = base_path + "/test/test.raw"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "b+w") as f:
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    print(f"Connection closed by {addr}")
                    break
                f.write(data)
                total_len += len(data)

    # Handle running signal and deleting file
    exec_file = base_path + "/transmit_raw.elf"
    run_file = file_path
    subprocess.run([exec_file, f"--tx-file={run_file}", "--tx-gain=1"])
    subprocess.run(["rm", file_path])

    print("Done")
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

