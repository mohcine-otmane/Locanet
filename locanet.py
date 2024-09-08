import tkinter as tk
from tkinter import ttk
import socket
import threading

class ServerGUI:
    def __init__(self, master, server):
        self.master = master
        self.server = server

        # Set up GUI
        self.master.title("Server GUI")

        # Frame for messages
        self.frame_messages = tk.Frame(self.master)
        self.frame_messages.pack(padx=10, pady=10)

        # Text widget for displaying messages
        self.text_messages = tk.Text(self.frame_messages, height=15, width=50)
        self.text_messages.pack(side=tk.LEFT, padx=5)

        # Scrollbar for the messages
        self.scrollbar = tk.Scrollbar(self.frame_messages)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_messages.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text_messages.yview)

        # Frame for client selection and message input
        self.frame_controls = tk.Frame(self.master)
        self.frame_controls.pack(padx=10, pady=10)

        # Dropdown for selecting the client
        self.label_client = tk.Label(self.frame_controls, text="Select Client:")
        self.label_client.grid(row=0, column=0, padx=5)

        self.client_combobox = ttk.Combobox(self.frame_controls, values=[], state="readonly")
        self.client_combobox.grid(row=0, column=1, padx=5)

        # Text entry for typing message
        self.label_message = tk.Label(self.frame_controls, text="Message:")
        self.label_message.grid(row=1, column=0, padx=5)

        self.entry_message = tk.Entry(self.frame_controls, width=40)
        self.entry_message.grid(row=1, column=1, padx=5)

        # Send button to send message to the selected client
        self.button_send = tk.Button(self.frame_controls, text="Send", command=self.send_message_to_client)
        self.button_send.grid(row=1, column=2, padx=5)

        # Start the server in a separate thread
        self.server_thread = threading.Thread(target=self.server.start_server, daemon=True)
        self.server_thread.start()

        # Update client list every second
        self.master.after(1000, self.update_client_list)

    def update_messages(self, message):
        """Add received messages to the text widget."""
        self.text_messages.insert(tk.END, message + "\n")
        self.text_messages.see(tk.END)

    def update_client_list(self):
        """Update the client combobox with the list of connected clients."""
        client_list = [str(client[1]) for client in self.server.clients]
        self.client_combobox['values'] = client_list
        self.master.after(1000, self.update_client_list)  # Continue updating every second

    def send_message_to_client(self):
        """Send the message to the selected client."""
        selected_client = self.client_combobox.get()
        message = self.entry_message.get()

        if selected_client and message:
            # Send the message to the selected client
            for client_socket, client_address in self.server.clients:
                if str(client_address) == selected_client:
                    client_socket.send(message.encode('utf-8'))
                    self.update_messages(f"Sent to {selected_client}: {message}")
                    break
            self.entry_message.delete(0, tk.END)
        else:
            self.update_messages("Select a client and enter a message.")

class Server:
    def __init__(self, address, port, gui):
        self.address = address
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.gui = gui  # Reference to the GUI for updating messages

    def start_server(self):
        try:
            self.server_socket.bind((self.address, self.port))
            self.server_socket.listen(5)
            self.gui.update_messages(f"Server started at {self.address}:{self.port}")
        except socket.error as e:
            self.gui.update_messages(f"Error binding server: {e}")
            return

        while True:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.clients.append((client_socket, client_address))
                self.gui.update_messages(f"Client connected: {client_address}")
                threading.Thread(target=self.handle_client, args=(client_socket, client_address), daemon=True).start()
            except Exception as e:
                self.gui.update_messages(f"Error accepting client: {e}")

    def handle_client(self, client_socket, client_address):
        """Handle communication with a connected client."""
        try:
            while True:
                message = client_socket.recv(1024)
                if not message:
                    break
                decoded_message = message.decode('utf-8')
                self.gui.update_messages(f"Message from {client_address}: {decoded_message}")
        except Exception as e:
            self.gui.update_messages(f"Error handling client {client_address}: {e}")
        finally:
            self.remove_client(client_socket)
            client_socket.close()

    def remove_client(self, client_socket):
        """Remove a client from the list of active clients."""
        for client in self.clients:
            if client[0] == client_socket:
                self.gui.update_messages(f"Client disconnected: {client[1]}")
                self.clients.remove(client)
                break

# Create and run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    server = Server('127.0.0.1', 53000, None)  # Create server without GUI at first
    app = ServerGUI(root, server)  # Pass GUI to server
    server.gui = app  # Link server to GUI
    root.mainloop()
