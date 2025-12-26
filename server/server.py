"""
PERSON 1: Server Core & Connection Management

This is the main server file that handles:
- Creating and starting the server
- Accepting client connections
- Managing multiple clients using multithreading
- Broadcasting group messages
- Routing private messages
- Handling disconnections
"""

import socket
import threading
import sys
import os

# Add parent directory to path to import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.utils import SERVER_HOST, SERVER_PORT, BUFFER_SIZE, log_info, log_error, Colors
from shared.protocol import Protocol, MessageType
from server.client_handler import ClientHandler
from server.database import Database


class ChatServer:
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        """
        Initialize the chat server.
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}  # {username: socket}
        self.clients_lock = threading.Lock()
        self.running = False
        self.db = Database()
        
        log_info(f"Server initialized on {host}:{port}")
    
    def start(self):
        """
        Start the server and begin accepting connections.
        """
        try:
            # Create TCP socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Set socket options to reuse address
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind to host and port
            self.server_socket.bind((self.host, self.port))
            
            # Start listening
            self.server_socket.listen(5)
            
            self.running = True
            
            print(f"\n{Colors.OKGREEN}{'=' * 60}{Colors.ENDC}")
            print(f"{Colors.OKGREEN}{Colors.BOLD}Chat Server Started Successfully!{Colors.ENDC}")
            print(f"{Colors.OKGREEN}{'=' * 60}{Colors.ENDC}")
            print(f"{Colors.OKCYAN}Server Address: {Colors.BOLD}{self.host}:{self.port}{Colors.ENDC}")
            print(f"{Colors.OKCYAN}Waiting for connections...{Colors.ENDC}")
            print(f"{Colors.WARNING}Press Ctrl+C to stop the server{Colors.ENDC}\n")
            
            log_info(f"Server listening on {self.host}:{self.port}")
            
            # Start accepting connections
            self.accept_connections()
            
        except Exception as e:
            log_error(f"Error starting server: {e}")
            print(f"{Colors.FAIL}Failed to start server: {e}{Colors.ENDC}")
            self.shutdown()
    
    def accept_connections(self):
        """
        Continuously accept new client connections.
        """
        while self.running:
            try:
                # Accept client connection
                client_socket, client_address = self.server_socket.accept()
                
                print(f"{Colors.OKBLUE}New connection attempt from {client_address}{Colors.ENDC}")
                log_info(f"New connection from {client_address}")
                
                # Create and start client handler thread
                client_handler = ClientHandler(client_socket, client_address, self)
                client_handler.start()
                
            except Exception as e:
                if self.running:
                    log_error(f"Error accepting connection: {e}")
    
    def add_client(self, username, client_socket):
        """
        Add a new client to the connected clients dictionary.
        
        Args:
            username (str): Client's username
            client_socket: Client's socket object
        """
        with self.clients_lock:
            self.clients[username] = client_socket
            print(f"{Colors.OKGREEN}✓ User '{username}' connected. Total users: {len(self.clients)}{Colors.ENDC}")
            log_info(f"Client added: {username}. Total clients: {len(self.clients)}")
    
    def remove_client(self, username):
        """
        Remove a disconnected client.
        
        Args:
            username (str): Client's username
        """
        with self.clients_lock:
            if username in self.clients:
                del self.clients[username]
                print(f"{Colors.WARNING}✗ User '{username}' disconnected. Total users: {len(self.clients)}{Colors.ENDC}")
                log_info(f"Client removed: {username}. Total clients: {len(self.clients)}")
    
    def is_username_taken(self, username):
        """
        Check if username is already taken.
        
        Args:
            username (str): Username to check
        
        Returns:
            bool: True if taken
        """
        with self.clients_lock:
            return username in self.clients
    
    def broadcast_message(self, message_dict, sender_username):
        """
        Send a message to all connected clients (group chat).
        
        Args:
            message_dict (dict): Message dictionary
            sender_username (str): Username of sender
        """
        with self.clients_lock:
            disconnected_clients = []
            
            for username, client_socket in self.clients.items():
                # Don't send back to sender (they already have it)
                if username == sender_username:
                    continue
                
                try:
                    encoded_msg = Protocol.encode_message(message_dict)
                    client_socket.send(encoded_msg)
                except Exception as e:
                    log_error(f"Error sending to {username}: {e}")
                    disconnected_clients.append(username)
            
            # Remove disconnected clients
            for username in disconnected_clients:
                if username in self.clients:
                    del self.clients[username]
                    log_info(f"Removed disconnected client: {username}")
    
    def send_private_message(self, message_dict, sender_username, receiver_username):
        """
        Send a private message to a specific user.
        
        Args:
            message_dict (dict): Message dictionary
            sender_username (str): Username of sender
            receiver_username (str): Username of receiver
        """
        with self.clients_lock:
            if receiver_username in self.clients:
                try:
                    receiver_socket = self.clients[receiver_username]
                    encoded_msg = Protocol.encode_message(message_dict)
                    receiver_socket.send(encoded_msg)
                    
                    # Send confirmation to sender
                    confirmation = Protocol.create_status_message(
                        f"Message sent to {receiver_username}"
                    )
                    sender_socket = self.clients.get(sender_username)
                    if sender_socket:
                        sender_socket.send(Protocol.encode_message(confirmation))
                    
                    log_info(f"Private message sent from {sender_username} to {receiver_username}")
                    
                except Exception as e:
                    log_error(f"Error sending private message: {e}")
                    # Notify sender of failure
                    error_msg = Protocol.create_error_message(
                        f"Failed to send message to {receiver_username}"
                    )
                    sender_socket = self.clients.get(sender_username)
                    if sender_socket:
                        try:
                            sender_socket.send(Protocol.encode_message(error_msg))
                        except:
                            pass
            else:
                # Receiver is offline
                log_info(f"User {receiver_username} is offline")
                error_msg = Protocol.create_error_message(
                    f"User {receiver_username} is offline"
                )
                sender_socket = self.clients.get(sender_username)
                if sender_socket:
                    try:
                        sender_socket.send(Protocol.encode_message(error_msg))
                    except:
                        pass
    
    def broadcast_user_joined(self, username):
        """
        Notify all clients that a user joined.
        
        Args:
            username (str): Username that joined
        """
        join_msg = Protocol.create_user_joined_message(username)
        
        with self.clients_lock:
            for client_username, client_socket in self.clients.items():
                if client_username != username:
                    try:
                        encoded_msg = Protocol.encode_message(join_msg)
                        client_socket.send(encoded_msg)
                    except Exception as e:
                        log_error(f"Error notifying {client_username} of join: {e}")
        
        print(f"{Colors.OKCYAN}→ Broadcasted: {username} joined the chat{Colors.ENDC}")
    
    def broadcast_user_left(self, username):
        """
        Notify all clients that a user left.
        
        Args:
            username (str): Username that left
        """
        left_msg = Protocol.create_user_left_message(username)
        
        with self.clients_lock:
            for client_username, client_socket in self.clients.items():
                try:
                    encoded_msg = Protocol.encode_message(left_msg)
                    client_socket.send(encoded_msg)
                except Exception as e:
                    log_error(f"Error notifying {client_username} of leave: {e}")
        
        print(f"{Colors.OKCYAN}→ Broadcasted: {username} left the chat{Colors.ENDC}")
    
    def get_online_users(self):
        """
        Get list of all currently connected users.
        
        Returns:
            list: List of usernames
        """
        with self.clients_lock:
            return list(self.clients.keys())
    
    def shutdown(self):
        """
        Gracefully shutdown the server.
        """
        print(f"\n{Colors.WARNING}Shutting down server...{Colors.ENDC}")
        log_info("Server shutdown initiated")
        
        self.running = False
        
        # Close all client connections
        with self.clients_lock:
            for username, client_socket in self.clients.items():
                try:
                    disconnect_msg = Protocol.create_message(
                        message_type=MessageType.DISCONNECT,
                        content="Server is shutting down"
                    )
                    client_socket.send(Protocol.encode_message(disconnect_msg))
                    client_socket.close()
                except:
                    pass
            self.clients.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        # Close database
        self.db.close()
        
        print(f"{Colors.OKGREEN}Server shut down successfully{Colors.ENDC}")
        log_info("Server shut down successfully")


def main():
    """
    Main function to start the server.
    """
    print(f"{Colors.BOLD}{Colors.HEADER}")
    print("=" * 60)
    print("     MULTI-CLIENT CHAT SERVER")
    print("     Computer Networks Project")
    print("=" * 60)
    print(f"{Colors.ENDC}")
    
    server = ChatServer()
    
    try:
        server.start()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Keyboard interrupt received{Colors.ENDC}")
        server.shutdown()
    except Exception as e:
        log_error(f"Server error: {e}")
        print(f"{Colors.FAIL}Server error: {e}{Colors.ENDC}")
        server.shutdown()


if __name__ == "__main__":
    main()
