from socket import *
from threading import *

def server_main():
    server_port = 12000
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(("", server_port))
    server_socket.listen(1)
    print("Server is now accepting connections")

    active_connections = {}

    while True:
        # accept incoming connection
        connection, address = server_socket.accept()

        # create new thread to handle this connection
        Thread(target=handle_client_connection, args=(connection, active_connections)).start()

# Receive messages from the given client connection, and forward them to the
#  intended destination
def handle_client_connection(s: socket, active_connections: dict):
    username = request_username(s)
    active_connections[username] = s

    # TODO: send connected message
    print(username + " has connected.")

    while True:
        try:
            data = s.recv(1024)
            # parse the message and forward it to the intended destination
            forward_message(data.decode(), active_connections, username)
        except ConnectionResetError:
            active_connections.pop(username)
            # TODO: send disconnected message
            print(username + " has disconnected.")

# Parse one message and send it to the intended recipient (or to everyone if
#  there is no specific recipient)
def forward_message(message: str, active_connections: dict, sender_username: str):
    # Handle private @username messages
    if message.startswith("@"):
        parts = message.split(" ", 1)
        if len(parts) < 2:
            return
        target = parts[0][1:]  # remove '@'
        text = parts[1]
        if target in active_connections:
            targeted_message = f"{sender_username} > {target}: {text}"
            active_connections[sender_username].send(targeted_message.encode())
            active_connections[target].send(targeted_message.encode())
        else:
            active_connections[sender_username].send(f"Could not send message: User {target} is offline or does not exist.".encode())
    else:
        broadcast_message(f"{sender_username}: {message}", active_connections)


def broadcast_message(message: str, active_connections: dict):
    print(message)
    for user, conn in active_connections.items():
        conn.send(message.encode())

def request_username(s: socket) -> str:
    # send username-request message
    s.send("USERNAME?".encode())

    response = s.recv(1024)

    # validate username-response format
    decoded = response.decode()

    # parse username
    if decoded.startswith("USERNAME:"):
        return decoded.split(":", 1)[1]  # text after USERNAME:
    else:
        return "unknown"  # fallback if client misbehaves

server_main()

