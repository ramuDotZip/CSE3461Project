from socket import *
from threading import *
from encrypts import *

max_packet_length_bytes = 8192
max_username_length = 20
max_message_length = 2000

main_thread_running = True

def server_main():
    global main_thread_running

    server_port = 12000
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.settimeout(1)
    server_socket.bind(("", server_port))
    server_socket.listen(1)
    print("Server is now accepting connections")

    active_connections = {}

    while True:
        try:
            try:  # accept incoming connection
                connection, address = server_socket.accept()
            except timeout:
                continue
        except KeyboardInterrupt:
            print("Received keyboard interrupt, exiting main thread...")
            broadcast_message("[SYSTEM] Server shutting down due to keyboard interrupt.", active_connections)
            main_thread_running = False
            return
        except BaseException as e:
            print("Encountered unknown error, exiting main thread...")
            broadcast_message("[SYSTEM] Server shutting down due to internal error.", active_connections)
            main_thread_running = False
            raise e


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

    # broadcast connection
    broadcast_message(f"[SYSTEM] {username} has connected.", active_connections)

    while True:
        try:
            # try to receive a message.
            data = receive_message(s, max_packet_length_bytes)

        except BaseException as e:  # If something goes wrong
            # try to gracefully disconnect the client before failing
            disconnect_client(username, active_connections)
            raise e

        # If the server is shutting down, close the socket and return immediately
        if not main_thread_running:
            s.close()
            return

        # If the message is empty, attempt to gracefully disconnect the client
        if not data:
            disconnect_client(username, active_connections)
            return

        # Decode, validate, and decrypt
        message = decrypt(data.decode()[:max_message_length])

        # parse the message and forward it to the intended destination
        forward_message(message, active_connections, username)

def disconnect_client(username: str, active_connections: dict):
    active_connections.pop(username)
    broadcast_message(f"[SYSTEM] {username} has disconnected.", active_connections)
    return

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
        target_username = parts[0][1:]  # remove '@'
        message_content = parts[1].strip()
        if message_content == "":
            return
        if target_username in active_connections:
            targeted_message = f"{sender_username} > {target_username}: {message_content}"
            print(targeted_message)
            send_message(active_connections[sender_username], targeted_message, active_connections)
            send_message(active_connections[target_username], targeted_message, active_connections)
        else:
            send_message(active_connections[sender_username],
                         f"Could not send message: User {target_username} is offline or does not exist.",
                         active_connections)
    else:
        broadcast_message(f"{sender_username}: {message}", active_connections)


# Send a message to all connected clients
def broadcast_message(message: str, active_connections: dict):
    print(message)
    for user, conn in active_connections.copy().items():  # Use a copy to avoid issues with the original changing size
        send_message(conn, message, active_connections)

def request_username(s: socket, active_connections: dict) -> str:
    # send username-request message
    send_message(s, "USERNAME?", active_connections)

    response = receive_message(s, max_packet_length_bytes)
    if not response:
        return ""

    # validate username-response format
    decoded = decrypt(response.decode())

    # parse username
    if not decoded.startswith("USERNAME:"):
        return ""
    username = decoded.split(":", 1)[1].strip()  # get text after "USERNAME:"
    username = username[:max_username_length].strip()  # validate username length
    if username in active_connections:
        send_message(s, f"Username {username} already in use.", active_connections)
        return ""
    send_message(s, "USERNAMEOK", active_connections)
    return username

# Wait to receive a message from the specified socket
def receive_message(s: socket, max_length: int):
    while True:
        if not main_thread_running:  # quit the waiting loop if the server's shutting down
            return None
        try:
            return s.recv(max_length)
        except timeout:
            continue
        except (ConnectionError, ConnectionResetError, ConnectionAbortedError, OSError):
            return None

def send_message(s: socket, message: str, active_connections: dict):
    try:
        data = encrypt(message).encode()
        data = data[:max_packet_length_bytes]
        s.send(data)
    except BaseException as e:
        # generic exception handling: look for this socket in the active connections, and
        #  disconnect the corresponding user if it exists
        for username, sock in active_connections.copy().items():
            if sock == s:
                disconnect_client(username, active_connections)
        raise e

server_main()
