from socket import *
from threading import *
import string

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
    handle_user_input(client_socket)


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
        data = s.recv(1024)

        # If disconnected, close the socket and return
        if not data:
            s.close()
            return

        # TODO: decode message format
        print(data.decode())  # (placeholder)

# Take keyboard input and send it as messages to the server
def handle_user_input(s: socket):
    while True:
        message = input()

        # TODO: encode message format
        s.send(message.encode())  # (placeholder)


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
    print(text)
    print("\npre encrypt\n")
    for k in key:
        if k.isalpha():
            cea_num = az.index(k.lower())
            text = caesar(text, cea_num)
        elif k.isdigit():
            shift_by = int(k)
            text = rail(text, shift_by)
    print(text)
    print("\npost encrypt\n")
    return text


def decrypt(ciphertext, key):
    text = ciphertext

    # Reverse the key order for decryption
    for k in reversed(key):
        if k.isalpha():
            cea_num = az.index(k.lower())
            text = decaesar(text, cea_num)
        elif k.isdigit():
            shift_by = int(k)
            text = derail(text, shift_by)

    return text
#first 2 must be letters!!!!!
keys="af2r5"
'''test=encrypt("testing 123 idk hello", keys)
print("\npre decrypt\n")
test=decrypt(test, keys)
print("\npost decrypt\n")
print(test)
'''

client_main()
