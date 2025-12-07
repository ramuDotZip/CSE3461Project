from socket import *
from threading import *
from tkinter import *

def client_main():
    server_host = input("Enter server address: ")
    server_port = 12000
    client_socket = socket(AF_INET, SOCK_STREAM)
    print("Connecting...")
    client_socket.connect((server_host, server_port))
    print("Connection established.")

    # Wait for server to request client info
    handle_username_request(client_socket)

    Thread(target=handle_server_connection, args=(client_socket,)).start()
    # handle_user_input(client_socket)

    window = construct_window(client_socket)
    window.mainloop()


# Receive a username request from the server, prompt the user for their
#  username, and send a username response back to the server.
def handle_username_request(s: socket):
    # TODO: add a timeout to abort the connection if the server does
    #  not properly request a username (optional)

    data = s.recv(1024)
    # TODO: ensure username-request format is correct

    username = input("Enter username: ")

    # send username-response message to server
    s.send(f"USERNAME:{username}".encode())  

# Receive messages from the server and display them to the user
def handle_server_connection(s: socket):
    while True:
        try:
            data = s.recv(1024)

            # TODO: decode message format
            display_message(data.decode())  # (placeholder)
        except ConnectionError:
            display_message("you have disconnected.")

# Take keyboard input and send it as messages to the server
def send_message(message: str, s: socket):
    # TODO: encode message format
    try:
        s.send(message.encode())  # (placeholder)
    except ConnectionError:
        display_message("Encountered a connection error while trying to send the message.")

def display_message(message: str):
    if not history_text:
        return
    history_text.configure(state="normal")
    history_text.insert("end", message + "\n")
    history_text.configure(state="disabled")

def construct_window(s: socket):
    global history_text, message_text
    window = Tk()

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

client_main()
