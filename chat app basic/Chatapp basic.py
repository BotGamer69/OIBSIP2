import socket
import threading

# Function to continuously receive messages
def handle_receive(sock):
    while True:
        try:
            data = sock.recv(1024).decode()
            if data.lower() == 'exit':
                print("\n[Other] exited the chat.")
                break
            print(f"\n[Other]: {data}")
        except:
            print("\nConnection closed.")
            break

# Function to send messages
def handle_send(sock):
    while True:
        message = input()
        sock.send(message.encode())
        if message.lower() == 'exit':
            break

# Server-side setup
def start_server():
    host = '127.0.0.1'  # localhost
    port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"[Server] Listening on {host}:{port}...")
    conn, addr = server_socket.accept()
    print(f"[Server] Connected to {addr}")

    # Start receiving and sending threads
    threading.Thread(target=handle_receive, args=(conn,), daemon=True).start()
    handle_send(conn)

    # Close connections after chat ends
    conn.close()
    server_socket.close()

# Client-side setup
def start_client():
    host = '127.0.0.1'  # IP of server
    port = 12345
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print(f"[Client] Connected to server at {host}:{port}")

    # Start receiving and sending threads
    threading.Thread(target=handle_receive, args=(client_socket,), daemon=True).start()
    handle_send(client_socket)

    # Close connection after chat ends
    client_socket.close()

if __name__ == "__main__":
    mode = input("Start as (server/client): ").strip().lower()
    if mode == "server":
        start_server()
    elif mode == "client":
        start_client()
    else:
        print("Invalid option. Run the script again and choose 'server' or 'client'.")

# --------------------------------------------
# 💡 How to Use:
# 1. Save this script as 'chat_app.py'.
# 2. Open TWO terminals (on same PC or LAN).
# 3. In the first terminal, run: python chat_app.py
#    - Type: server
# 4. In the second terminal, run: python chat_app.py
#    - Type: client
# 5. Start chatting! Type 'exit' to leave the chat.
# --------------------------------------------
