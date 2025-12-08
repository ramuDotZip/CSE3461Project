from socket import *
from threading import *

def server_main():
    server_port = 12000
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.settimeout(1)
    server_socket.bind(("", server_port))
    server_socket.listen(1)
    print("Server is now accepting connections")

    active_connections = {}

    while True:
        try:  # accept incoming connection
            connection, address = server_socket.accept()
        except timeout:
            continue

        # create new thread to handle this connection
        Thread(target=handle_client_connection, args=(connection, active_connections)).start()

# Receive messages from the given client connection, and forward them to the
#  intended destination
def handle_client_connection(s: socket, active_connections: dict):
    s.settimeout(1)
    username = request_username(s, active_connections)

    if not username:
        s.close()
        return

    active_connections[username] = s

    # TODO: send connected message
    print(username + " has connected.")

    while True:
        data = receive_message(s, 1024)

        if not data:
            active_connections.pop(username)
            # TODO: send disconnected message
            print(username + " has disconnected.")
            return

        # parse the message and forward it to the intended destination
        forward_message(data.decode(), active_connections, username)


# Parse one message and send it to the intended recipient (or to everyone if
#  there is no specific recipient)
def forward_message(message: str, active_connections: dict, sender_username: str):
    message = message.strip()
    if message == "":
        return

    # Handle private @username messages
    if message.startswith("@"):
        parts = message.split(" ", 1)
        if len(parts) < 2:
            return
        target = parts[0][1:]  # remove '@'
        text = parts[1].strip()
        if text == "":
            return
        if target in active_connections:
            targeted_message = f"{sender_username} > {target}: {text}"
            active_connections[sender_username].send(targeted_message.encode())
            active_connections[target].send(targeted_message.encode())
        else:
            active_connections[sender_username].send(f"Could not send message: User {target} is offline or does not exist.".encode())
    else:
        broadcast_message(f"{sender_username}: {message}", active_connections)


# Send a message to all connected clients
def broadcast_message(message: str, active_connections: dict):
    print(message)
    for user, conn in active_connections.items():
        conn.send(message.encode())

def request_username(s: socket, active_connections: dict) -> str:
    # send username-request message
    s.send("USERNAME?".encode())

    response = receive_message(s, 1024)
    if not response:
        return ""

    # validate username-response format
    decoded = response.decode()

    # parse username
    if not decoded.startswith("USERNAME:"):
        return ""
    username = decoded.split(":", 1)[1].strip()  # text after USERNAME:
    if username in active_connections:
        s.send(f"Username {username} already in use.".encode())
        return ""
    s.send("USERNAMEOK".encode())
    return username

# Wait to receive a message from the specified socket
def receive_message(s: socket, max_length: int):
    while True:
        try:
            return s.recv(max_length)
        except timeout:
            continue
        except (ConnectionError, ConnectionResetError, ConnectionAbortedError, OSError):
            return None

server_main()

