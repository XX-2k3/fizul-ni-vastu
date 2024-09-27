from tkinter import Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, messagebox, filedialog
import socket
import threading
import os


class GUI:
    def __init__(self, master):
        self.client_socket = None
        self.root = master
        self.last_received_message = None
        self.chat_transcript_area = None
        self.name_widget = None
        self.enter_text_widget = None
        self.join_button = None
        self.theme = "light"
        self.initialize_socket()
        self.initialize_gui()
        self.listen_for_incoming_messages_in_a_thread()

    def initialize_socket(self):
        try:
            self.client_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            IP_Host = socket.gethostbyname(socket.gethostname())
            IP_Port = 5555
            self.client_socket.connect((IP_Host, IP_Port))
        except ConnectionRefusedError:
            print("Connection refused. Please check that the server is running.")
            self.client_socket = None

    def initialize_gui(self):
        self.root .title("Socket Chat")
        self.root.resizable(True, True)
        self.display_nav_bar()
        self.display_chat_box()
        self.display_chat_entry_box()

    def listen_for_incoming_messages_in_a_thread(self):
        thread = threading.Thread(target=self.receive_message_from_server)
        thread.daemon = True
        thread.start()

    def receive_message_from_server(self):
        if self.client_socket is None:
            return
        while True:
            try:
                buffer = self.client_socket.recv(256)
                if not buffer:
                    break
                message = buffer.decode('utf-8')
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)
            except Exception as e:
                print(f"Error receiving message: {e}")
                break
        if self.client_socket:
            self.client_socket.close()

    def display_nav_bar(self):
        frame = Frame(self.root, bg=self.get_background_color())
        Label(frame, text='Enter Your Name Here!', font=("arial", 13, "bold"), bg=self.get_background_color(
        ), fg=self.get_text_color()).pack(side='left', padx=10, pady=10)
        self.name_widget = Entry(frame, width=30, font=("arial", 13), bg=self.get_entry_background_color(
        ), fg=self.get_text_color())
        self.name_widget.pack(side='left', padx=10, pady=10)
        self.join_button = Button(frame, text="Join", width=10, command=self.on_join,
                                  bg=self.get_button_background_color(), fg=self.get_text_color())
        self.join_button.pack(side='left', padx=10, pady=10)
        Button(frame, text="Switch Theme", command=self.switch_theme, bg=self.get_button_background_color(
        ), fg=self.get_text_color()).pack(side='right', padx=10, pady=10)
        frame.pack(side='top', fill='x')

    def display_chat_box(self):
        frame = Frame(self.root, bg=self.get_background_color())
        self.chat_transcript_area = Text(frame, width=60, height=20, font=("arial", 12), bg=self.get_entry_background_color(
        ), fg=self.get_text_color())
        scrollbar = Scrollbar(
            frame, command=self.chat_transcript_area.yview, orient=VERTICAL)
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')
        self.chat_transcript_area.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        frame.pack(side='top', fill='both', expand=True)

    def display_chat_entry_box(self):
        frame = Frame(self.root, bg=self.get_background_color())
        self.enter_text_widget = Text(frame, width=50, height=5, font=("arial", 12), bg=self.get_entry_background_color(
        ), fg=self.get_text_color())
        self.enter_text_widget.pack(side='left', fill='both', expand=True)
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)
        send_button = Button(frame, text="Send", width=10, command=self.on_send_button_clicked,
                             bg=self.get_button_background_color(), fg=self.get_text_color())
        send_button.pack(side='right', padx=10, pady=10)
        file_button = Button(frame, text="Send File", width=10, command=self.on_send_file_button_clicked,
                             bg=self.get_button_background_color(), fg=self.get_text_color())
        file_button.pack(side='right', padx=10, pady=10)
        frame.pack(side='bottom', fill='x')

    def on_join(self):
        name = self.name_widget.get()
        if not name:
            messagebox.showerror("Error", "Please enter your name")
            return
        self.client_socket.send(name.encode('utf-8'))
        self.name_widget.config(state='disabled')
        self.join_button.config(state='disabled')

    def on_enter_key_pressed(self, event):
        message = self.enter_text_widget.get('1.0', 'end-1c')
        self.client_socket.send(message.encode('utf-8'))
        self.enter_text_widget.delete('0.0', 'end')

    def on_send_button_clicked(self):
        message = self.enter_text_widget.get('1.0', 'end-1c')
        self.client_socket.send(message.encode('utf-8'))
        self.enter_text_widget.delete('0.0', 'end')

    def on_send_file_button_clicked(self):
        filename = filedialog.askopenfilename()
        if filename:
            filesize = os.path.getsize(filename)
            self.client_socket.send(f"FILE:{os.path.basename(filename)}:{
                                    filesize}".encode('utf-8'))
            with open(filename, "rb") as f:
                bytes_read = f.read(1024)
                while bytes_read:
                    self.client_socket.sendall(bytes_read)
                    bytes_read = f.read(1024)

    def switch_theme(self):
        if self.theme == "light":
            self.theme = "dark"
        else:
            self.theme = "light"
        self.root.configure(bg=self.get_background_color())
        self.name_widget.config(
            bg=self.get_entry_background_color(), fg=self.get_text_color())
        self.join_button.config(
            bg=self.get_button_background_color(), fg=self.get_text_color())
        self.chat_transcript_area.config(
            bg=self.get_entry_background_color(), fg=self.get_text_color())
        self.enter_text_widget.config(
            bg=self.get_entry_background_color(), fg=self.get_text_color())

    def get_background_color(self):
        if self.theme == "light":
            return "#f0f0f0"
        else:
            return "#333333"

    def get_text_color(self):
        if self.theme == "light":
            return "#000000"
        else:
            return "#ffffff"

    def get_entry_background_color(self):
        if self.theme == "light":
            return "#ffffff"
        else:
            return "#444444"

    def get_button_background_color(self):
        if self.theme == "light":
            return "#007bff"
        else:
            return "#00698f"


root = Tk()
gui = GUI(root)
root.mainloop()
