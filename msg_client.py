import encrypts
from socket import *
from threading import *
import string
from tkinter import *
import re


def client_main():
    server_host = input("Enter server address: ").strip()
    if server_host == "":
        server_host = "127.0.0.1"
    server_port = 12000
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.settimeout(1)
    print("Connecting...")
    client_socket.connect((server_host, server_port))
    print("Connection established.")

    # Wait for server to request client info
    username = handle_username_request(client_socket)
    if username == "":
        return

    Thread(target=handle_server_connection, args=(client_socket,)).start()
    # handle_user_input(client_socket)

    window = construct_window(client_socket, username)
    window.mainloop()


# Receive a username request from the server, prompt the user for their
#  username, and send a username response back to the server.
def handle_username_request(s: socket) -> str:
    data = receive_message(s, 1024)
    if not data:
        print("Disconnected.")
        return ""
    decoded = data.decode()
    if decoded != "USERNAME?":
        print("Expected username request, received:", data.decode())
        return ""

    username = input("Enter username: ").strip()
    while not re.fullmatch("\\w+", username):
        print("Username must contain only letters, digits, and underscores.")
        username = input("Enter username: ").strip()

    # send username-response message to server
    s.send(f"USERNAME:{username}".encode())

    data = receive_message(s, 1024)
    if not data:
        print("Disconnected.")
        return ""
    decoded = data.decode()
    if decoded != "USERNAMEOK":
        print("Username request error:", decoded)
        return ""

    return username


# Receive messages from the server and display them to the user
def handle_server_connection(s: socket):
    while True:
        data = receive_message(s, 1024)
        if not data:
            print("Disconnected.")
            return

        # TODO: decode message format
        display_message(data.decode())  # (placeholder)


# Wait to receive a message from the server
def receive_message(s: socket, max_length: int):
    while True:
        try:
            return s.recv(max_length)
        except timeout:
            continue
        except (ConnectionError, ConnectionResetError, ConnectionAbortedError, OSError):
            return None


# Send a message to the server
def send_message(message: str, s: socket):
    # TODO: encode message format
    try:
        s.send(message.encode())  # (placeholder)
    except (ConnectionError, ConnectionResetError, ConnectionAbortedError, OSError):
        display_message("Encountered a connection error while trying to send the message.")


# Add a message to the message history box
def display_message(message: str):
    if not history_text:
        return
    history_text.configure(state="normal")
    history_text.insert("end", message + "\n")
    history_text.configure(state="disabled")


# Create a client GUI window
def construct_window(s: socket, username: str):
    global history_text
    window = Tk()
    window.title(f"Message Client ({username})")

    history_frame = Frame(window)
    message_frame = Frame(window)

    history_frame.pack()
    message_frame.pack()

    history_scrollbar = Scrollbar(history_frame)
    history_scrollbar.pack(side=RIGHT, fill=Y)
    history_text = Text(history_frame, width=80, height=24, yscrollcommand=history_scrollbar.set, state="disabled")
    history_text.pack(side=LEFT, fill=BOTH)
    history_scrollbar.config(command=history_text.yview)

    message_scrollbar = Scrollbar(message_frame)
    message_scrollbar.pack(side=RIGHT, fill=Y)
    message_text = Text(message_frame, width=80, height=4, yscrollcommand=message_scrollbar.set)
    message_text.pack(side=LEFT, fill=BOTH)
    message_scrollbar.config(command=message_text.yview)

    def return_callback(event):
        # Get the text from the input box
        message_str = message_text.get("1.0", "end").strip()
        # Clear the input box
        message_text.delete("1.0", "end")

        # If the message is not empty, send it to the server
        if message_str != "":
            send_message(message_str, s)

        # Stop the key press from putting a newline in the (now empty) text box
        return "break"

    message_text.bind("<Return>", return_callback)

    def window_exit_callback():
        s.close()
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", window_exit_callback)

    return window



# first 2 must be letters!!!!!
'''
keys = "af2r5"
test=encrypts.encrypt("testing 123 idk hello", keys)
print("\npre decrypt\n")
print(test)
test=encrypts.decrypt(test, keys)
print("\npost decrypt\n")
print(test)
'''

client_main()
