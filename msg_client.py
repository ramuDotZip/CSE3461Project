import time
import tkinter

from encrypts import *
from socket import *
from threading import *
from tkinter import *
import re

max_packet_length_bytes = 8192
max_username_length = 20
max_message_length = 2000

def client_main():
    server_host = input("Enter server address: ").strip()
    if server_host == "":
        server_host = "127.0.0.1"
    server_port = 12000
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.settimeout(5)
    print("Connecting...")
    try:
        client_socket.connect((server_host, server_port))
    except TimeoutError:
        print("Error: Timed out. Make sure the server is running and available at the specified address.")
        return
    except ConnectionRefusedError:
        print("Error: The target machine refused the connection.")
        print("Make sure the server is running and available at the specified address.")
        return
    except gaierror:
        print("Encountered a gaierror while connecting. Make sure the address is correct.")
        return
    print("Connection established.")
    client_socket.settimeout(1)

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
    data = receive_message(s, max_packet_length_bytes)
    if not data:
        print("Disconnected.")
        return ""
    decoded = decrypt(data.decode())
    if decoded != "USERNAME?":
        print("Expected username request from server, received:", data.decode())
        return ""

    while True:
        username = input("Enter username: ").strip()
        if len(username) < 1:
            print("Username must be at least 1 character.")
            continue
        if not re.fullmatch("\\w+", username):
            print("Username must contain only letters, digits, and underscores.")
            continue
        if len(username) > max_username_length:
            print("Username must be at most", max_username_length, "characters.")
            continue
        # passed all checks, use this username
        break

    # send username-response message to server
    send_message(s, f"USERNAME:{username}")

    data = receive_message(s, max_packet_length_bytes)
    if not data:
        print("Disconnected.")
        return ""
    decoded = decrypt(data.decode())
    if decoded != "USERNAMEOK":
        print("Username request error:", decoded)
        return ""

    return username


# Receive messages from the server and display them to the user
def handle_server_connection(s: socket):
    while 'history_text' not in globals():  # Don't receive messages if the gui isn't initialized yet
        time.sleep(0.5)
    while True:
        data = receive_message(s, max_packet_length_bytes)
        if not data:
            print("Disconnected.")
            return

        display_message(decrypt(data.decode()))


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
def send_message(s: socket, message: str):
    try:
        message = encrypt(message[:max_message_length])
        s.send(message.encode())
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

    # Send the message when the user presses return
    def return_callback(event):
        # Get the text from the input box
        message_str = message_text.get("1.0", "end-1c").strip()[:max_message_length]
        # Clear the input box
        message_text.delete("1.0", "end")

        # If the message is not empty, send it to the server
        if message_str != "":
            send_message(s, message_str)

        # Stop the key press from putting a newline in the (now empty) text box
        return "break"

    # Prevent the user from entering more than the maximum number of characters
    def keyboard_callback(event: tkinter.Event):
        char_count = len(message_text.get("1.0", "end-1c"))

        # If character count is already over the limit, remove the excess
        if char_count > max_message_length:
            message_text.delete("1." + str(max_message_length), "end-1c")

        # If at the limit, block any keyboard event, except when...
        if (char_count >= max_message_length and
                event.char != "" and  # there is no printing character,
                event.keysym not in {"BackSpace", "Delete", "Return"} and  # it's backspace, delete, or return,
                not (event.keysym == "a" and event.state == 12)):  # or It's Ctrl+A.
            # print("blocked character:", event.__dict__)
            return "break"

    message_text.bind("<Return>", return_callback)
    message_text.bind("<KeyPress>", keyboard_callback, "+")
    message_text.bind("<KeyRelease>", keyboard_callback)

    def window_exit_callback():
        s.close()
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", window_exit_callback)

    return window



# first 2 must be letters!!!!!
'''keys = "af2r5"
test=encrypt("testing 123 idk hello")
print("\npre decrypt\n")
print(test)
test=decrypt(test)
print("\npost decrypt\n")
print(test)'''

client_main()
