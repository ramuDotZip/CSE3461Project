from socket import *
from threading import *

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


client_main()
