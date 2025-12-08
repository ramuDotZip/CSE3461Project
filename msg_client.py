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

az = string.ascii_lowercase
def caesar(str, shifts):
    upper = string.ascii_uppercase
    newstr = ""
    new_char = ''
    for i in range(len(str)):
        char = str[i]
        if char in upper:
            index = upper.index(char.upper())
            shifted = (index + shifts) % 26
            new_char = upper[shifted]
            if char.islower():
                new_char = new_char.lower()
        else:
            new_char = char
        newstr = newstr + new_char
    return newstr


def rail(strings,amount):
    if len(strings)<3:
        return strings
    new_str = ""
    for i in range(0, len(strings), 2):
        new_str = new_str + strings[i]
    for i in range(1, len(strings), 2):
        new_str = new_str + strings[i]
    if (amount > 0):
        rail(strings, amount - 1)
    return new_str


# noinspection SpellCheckingInspection
def decaesar(str, shift):
  upper=string.ascii_uppercase
  newstr=""
  new_char = ''
  for i in range (len(str)):
    char=str[i]
    if char in upper:
      index = upper.index(char)
      shifted = (index - shift)
      new_char = upper[shifted]
    else:
      new_char = char
    newstr=newstr+new_char
  return newstr

def derail(strings,amount):
      result = ""
      if len(strings) < 3:
          return strings
      half = (len(strings) + 1) // 2
      even = strings[:half]
      odd = strings[half:]
      i = 0
      j = 0
      for step in range(len(strings)):
          if step % 2 == 0:
              result=result+even[i]
              i += 1
          else:
              result=result+odd[j]
              j += 1
      if(amount>0):
          derail(strings, amount-1)
      return result

def encrypt(message, key):
    text = message
    offset=0
    #print(text)
    #print("\npre encrypt\n")
    for k in key:
        if k.isalpha():
            cea_num = (az.index(k.lower())+ offset) % 26
            offset = (az.index(k.lower())+ offset) % 26
            text = caesar(text, cea_num)
        elif k.isdigit():
            shift_by = int(k)
            text = rail(text, shift_by)
    #print(text)
    #print("\npost encrypt\n")
    return text


def decrypt(ciphertext, key):
    text = ciphertext
    offset = 0
    for k in key:
        if k.isalpha():
            offset = (az.index(k.lower())+ offset) % 26
    # Reverse the key order for decryption
    for k in reversed(key):
        if k.isalpha():
            cea_num = (az.index(k.lower())+ offset) % 26
            offset =offset -az.index(k.lower())
            if offset <0:
                offset=offset+26
            text = decaesar(text, cea_num)
        elif k.isdigit():
            shift_by = int(k)
            text = derail(text, shift_by)

    return text
#first 2 must be letters!!!!!
keys="af2r5"
'''
test=encrypt("testing 123 idk hello", keys)
print("\npre decrypt\n")
print(test)
test=decrypt(test, keys)
print("\npost decrypt\n")
print(test)
'''

client_main()
