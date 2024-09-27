import socket
import threading
import os


class ChatServer:

    def __init__(self):
        self.clients_list = []
        self.lock = threading.Lock()
        self.server_socket = None
        self.create_listening_server()

    def create_listening_server(self):
        try:
            self.server_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            local_ip = socket.gethostbyname(socket.gethostname())
            local_port = 5555
            self.server_socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((local_ip, local_port))
            print("Listening for incoming messages...")
            self.server_socket.listen(5)
            self.receive_connections_in_a_new_thread()
        except socket.error as e:
            print(f"Error creating listening server: {e}")

    def receive_messages(self, client_socket):
        while True:
            try:
                incoming_buffer = client_socket.recv(1024)
                if not incoming_buffer:
                    break
                message = incoming_buffer.decode('utf-8').strip()
                if message.startswith("FILE:"):
                    self.handle_file_transfer(client_socket, message)
                else:
                    print(f"Received: {message}")  # Logging received messages
                    self.broadcast_to_all_clients(client_socket, message)
            except Exception as e:
                print(f"Error receiving message: {e}")
                break
        self.remove_client(client_socket)

    def handle_file_transfer(self, client_socket, message):
        _, filename, filesize = message.split(":")
        filesize = int(filesize)
        with open(f"received_{filename}", "wb") as f:
            bytes_read = client_socket.recv(1024)
            total_bytes_read = len(bytes_read)
            f.write(bytes_read)
            while total_bytes_read < filesize:
                bytes_read = client_socket.recv(1024)
                total_bytes_read += len(bytes_read)
                f.write(bytes_read)
        print(f"File {filename} received successfully")

    def broadcast_to_all_clients(self, sender_socket, message):
        with self.lock:  # Ensuring thread safety
            for client in self.clients_list:
                if client is not sender_socket:
                    try:
                        client.sendall(f"{message}\n".encode('utf-8'))
                    except Exception as e:
                        print(f"Error sending message: {e}")

    def receive_connections_in_a_new_thread(self):
        while True:
            client_socket, (ip, port) = self.server_socket.accept()
            print(f'Connected to {ip}:{port}')
            self.add_to_clients_list(client_socket)
            t = threading.Thread(
                target=self.receive_messages, args=(client_socket,))
            t.start()

    def add_to_clients_list(self, client_socket):
        with self.lock:  # Ensuring thread safety
            if client_socket not in self.clients_list:
                self.clients_list.append(client_socket)

    def remove_client(self, client_socket):
        with self.lock:  # Ensuring thread safety
            if client_socket in self.clients_list:
                self.clients_list.remove(client_socket)
                client_socket.close()
                print("Client disconnected.")
                self.broadcast_to_all_clients(None, "Client disconnected.")


if __name__ == "__main__":
    ChatServer()
