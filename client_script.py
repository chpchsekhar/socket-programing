import socket
import sys
import threading

def start_client(client_id, port, server_address):
    """Start a UDP client to communicate with the server."""
    def receive_messages(client_socket):
        """Thread to handle incoming messages."""
        while True:
            try:
                data, addr = client_socket.recvfrom(1024)
                print(f"Client {client_id} received: {data.decode()}")
            except socket.error as e:
                print(f"Client {client_id}: Socket error: {e}")
                break
            except Exception as e:
                print(f"Client {client_id}: Error: {e}")
                break

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        client_socket.bind(("0.0.0.0", port))
        print(f"Client {client_id} started on port {port}")
    except OSError as e:
        print(f"Error binding client {client_id} to port {port}: {e}")
        return

    receiver_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
    receiver_thread.start()

    try:
        while True:
            message = input(f"Client {client_id}: Enter message (or 'exit' to quit): ")
            if message.lower() == "exit":
                print(f"Client {client_id} shutting down.")
                break
            client_socket.sendto(f"{client_id}:{message}".encode(), server_address)
    except KeyboardInterrupt:
        print(f"\nClient {client_id} interrupted and shutting down.")
    finally:
        client_socket.close()
        print(f"Client {client_id} has closed.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python client_script.py <client_id> <port> <server_ip:server_port>")
        sys.exit(1)

    try:
        client_id = sys.argv[1]
        port = int(sys.argv[2])
        server_ip, server_port = sys.argv[3].split(":")
        server_address = (server_ip, int(server_port))
        start_client(client_id, port, server_address)
    except ValueError:
        print("Invalid input. Ensure port and server address are in the correct format.")
