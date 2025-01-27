import zmq

# ZMQ Setup
context = zmq.Context()

# Socket to receive messages from clients
receiver = context.socket(zmq.PULL)
receiver.bind("tcp://*:5555")  # Bind to receive messages from clients

# Socket to broadcast messages to clients
publisher = context.socket(zmq.PUB)
publisher.bind("tcp://*:5556")  # Bind to broadcast messages to clients

print("Server is running...")

while True:
    # Receive message from a client
    message = receiver.recv_string()
    print(f"Received: {message}")

    # Broadcast the message to all clients
    publisher.send_string(message)
