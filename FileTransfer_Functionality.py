import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import os


class ChatClient:

    def __init__(self, master):
        self.master = master
        self.master.title("Chat Client")

        self.create_widgets()

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.receive_thread = None
        self.connected = False

    def create_widgets(self):
        self.chat_display = scrolledtext.ScrolledText(
            self.master, state='disabled', wrap=tk.WORD)
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.message_entry = tk.Entry(self.master, width=50)
        self.message_entry.pack(padx=10, pady=(
            0, 10), side=tk.LEFT, fill=tk.X, expand=True)
        self.message_entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(
            self.master, text="Send", command=self.send_message)
        self.send_button.pack(padx=10, pady=(0, 10), side=tk.RIGHT)

        self.file_button = tk.Button(
            self.master, text="Send File", command=self.send_file)
        self.file_button.pack(padx=10, pady=(0, 10), side=tk.RIGHT)

    def connect_to_server(self, ip, port):
        try:
            self.client_socket.connect((ip, port))
            self.connected = True
            self.receive_thread = threading.Thread(
                target=self.receive_messages)
            self.receive_thread.start()
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def receive_messages(self):
        while self.connected:
            try:
                message = self.client_socket.recv(1024).decode('utf-8').strip()
                if message:
                    self.display_message(message)
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def send_message(self, event=None):
        if not self.connected:
            messagebox.showerror("Error", "Not connected to the server.")
            return

        message = self.message_entry.get().strip()
        if message:
            try:
                self.client_socket.sendall(message.encode('utf-8'))
                self.message_entry.delete(0, tk.END)
            except Exception as e:
                print(f"Error sending message: {e}")

    def send_file(self):
        if not self.connected:
            messagebox.showerror("Error", "Not connected to the server.")
            return

        filename = filedialog.askopenfilename()
        if filename:
            filesize = os.path.getsize(filename)
            try:
                self.client_socket.sendall(f"FILE:{os.path.basename(filename)}:{
                                           filesize}".encode('utf-8'))
                with open(filename, "rb") as f:
                    bytes_read = f.read(1024)
                    while bytes_read:
                        self.client_socket.sendall(bytes_read)
                        bytes_read = f.read(1024)
            except Exception as e:
                print(f"Error sending file: {e}")

    def display_message(self, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{message}\n")
        self.chat_display.config(state='disabled')
        self.chat_display.yview(tk.END)

    def close_connection(self):
        self.connected = False
        self.client_socket.close()
        self.master.quit()


def main():
    root = tk.Tk()
    client = ChatClient(root)

    server_ip = "127.0.0.1"  # Replace with the server's IP address
    server_port = 5555       # Make sure this matches the server's port

    client.connect_to_server(server_ip, server_port)

    root.protocol("WM_DELETE_WINDOW", client.close_connection)
    root.mainloop()


if __name__ == "__main__":
    main()

