import socket
import threading
import json

# Socket init
HOST = '127.0.0.1'
PORT = 65432

# Positions for player 1 and player 2
p1Pos = { "xPos": 50, "yPos": 150, "gameOver": 0 }
p2Pos = { "xPos": 750, "yPos": 150, "gameOver": 0 }

"""
This function always runs in its own thread and runs for each client connected to the server. Runs concurrently
for each client.
"""
def thread_client(conn, player):
    print(f"{player} connected to the server.")
    # Send the starting positions of the connected player to that player's client
    if player == 0:
        conn.sendall(bytes(json.dumps(p1Pos, indent=4), encoding="utf-8"))
    else:
        conn.sendall(bytes(json.dumps(p2Pos, indent=4), encoding="utf-8"))
    is_connected = True
    while is_connected:
        # Receive the player positions and game state from the client
        data = conn.recv(1024)
        # decode bytes to a python object that can be accessed
        data_obj = json.loads(data)

        # Update the position of the connected player to the values received from the client (stored in data_obj).
        # Then proceed to send to the client the current position of the other player, as well as the game state
        if player == 0:
            if data_obj["gameOver"] == 1:
                p1Pos["gameOver"] = 1

            p1Pos["xPos"] = data_obj["xPos"]
            p1Pos["yPos"] = data_obj["yPos"]
            conn.sendall(bytes(json.dumps(p2Pos, indent=4), encoding="utf-8"))

        else:
            if data_obj["gameOver"] == 1:
                p2Pos["gameOver"] = 1

            p2Pos["xPos"] = data_obj["xPos"]
            p2Pos["yPos"] = data_obj["yPos"]
            conn.sendall(bytes(json.dumps(p1Pos, indent=4), encoding="utf-8"))

	# If the received data is empty
        if not data:
            is_connected = False

    # If the loop is broken, the connection has been lost and should be closed
    print("Connection lost")
    conn.close()

# Open server side socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(2)
    currentPlayer = 0
    print("Waiting for connection...")
    while True:
        # Wait for new connection to the server, store address for connection when it happens
        conn, address = s.accept()
        thread = threading.Thread(target=thread_client, args=(conn, currentPlayer))
        print("Connected by ", address)
        # Start thread for connected client
        thread.start()
        currentPlayer += 1
