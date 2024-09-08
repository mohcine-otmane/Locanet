import tkinter as tk
import socket
import threading


class Server:

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow address reuse
        self.server_running = False  # Flag to track server state

    def startServer(self):
        if not self.server_running:  # Prevent starting the server multiple times
            try:
                self.socket.bind((self.address, self.port))
                self.socket.listen(5)
                print("Server in service")

                self.server_running = True

                # Start a new thread to handle clients
                threading.Thread(target=self.handleClient, daemon=True).start()
            except socket.error as e:
                print(f"Error starting server: {e}")

    def handleClient(self):
        while True:
            try:
                c, addr = self.socket.accept()  # Accept a connection
                print('Connected:', addr)
                c.send(b"Client Connected")  # Send a response
                c.close()  # Close the connection
            except Exception as e:
                print(f"Error handling client: {e}")


# Create server instance
server = Server('127.0.0.1', 53000)

# Set up the GUI
master = tk.Tk()

button = tk.Button(master, text='Start Server', width=25, command=server.startServer)
button.pack()

master.mainloop()
