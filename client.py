import tkinter as tk
import socket
import threading

class Client:

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def connect(self):
        """Connect to the server."""
        try:
            self.socket.connect((self.address, self.port))
            self.connected = True
            print(f"Connected to {self.address}:{self.port}")
            threading.Thread(target=self.receive_messages, daemon=True).start()  # Start receiving messages
        except Exception as e:
            print(f"Error connecting to server: {e}")

    def send_message(self, message):
        """Send message to the server."""
        if self.connected:
            try:
                self.socket.send(message.encode('utf-8'))  # Send message to server
            except Exception as e:
                print(f"Error sending message: {e}")
                self.disconnect()
    
    def receive_messages(self):
        """Continuously listen for messages from the server."""
        while self.connected:
            try:
                message = self.socket.recv(1024).decode('utf-8')  # Receive message
                if message:
                    print(f"Server: {message}")
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.disconnect()

    def disconnect(self):
        """Close the connection to the server."""
        self.connected = False
        try:
            self.socket.close()
            print("Disconnected from the server.")
        except Exception as e:
            print(f"Error disconnecting: {e}")

# Create a Client instance
client = Client('127.0.0.1', 53000)

# GUI for the Client
def send_message():
    """Send message through the client when the button is clicked."""
    message = entry.get()
    client.send_message(message)
    entry.delete(0, tk.END)  # Clear the text entry after sending

def connect_to_server():
    """Connect to the server when the button is clicked."""
    client.connect()

def disconnect_from_server():
    """Disconnect from the server when the button is clicked."""
    client.disconnect()

# Tkinter GUI setup
master = tk.Tk()
master.title("Client Chat")

# Create connection button
connect_button = tk.Button(master, text='Connect to Server', width=25, command=connect_to_server)
connect_button.pack()

# Text entry for sending messages
entry = tk.Entry(master, width=50)
entry.pack()

# Button to send messages
send_button = tk.Button(master, text='Send Message', width=25, command=send_message)
send_button.pack()

# Button to disconnect from the server
disconnect_button = tk.Button(master, text='Disconnect', width=25, command=disconnect_from_server)
disconnect_button.pack()

master.mainloop()
