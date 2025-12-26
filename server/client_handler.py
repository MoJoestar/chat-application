"""
PERSON 1: Client Handler

This file handles individual client connections in separate threads.
"""

import threading
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.protocol import Protocol, MessageType
from shared.utils import BUFFER_SIZE, log_info, log_error, validate_username


class ClientHandler(threading.Thread):
    """
    Handles individual client connection in a separate thread.
    """
    
    def __init__(self, client_socket, client_address, server):
        """
        Initialize client handler.
        
        Args:
            client_socket: Socket object for this client
            client_address: Tuple of (ip, port)
            server: Reference to main ChatServer instance
        """
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address
        self.server = server
        self.username = None
        self.daemon = True
        self.running = True
        
        log_info(f"New connection from {client_address}")
    
    def run(self):
        """
        Main thread execution - handles client communication.
        """
        try:
            # Authenticate client
            if not self.authenticate():
                log_error(f"Authentication failed for {self.client_address}")
                self.disconnect()
                return
            
            log_info(f"Client {self.username} authenticated successfully")
            
            # Send chat history
            self.send_chat_history()
            
            # Notify other users that this user joined
            self.server.broadcast_user_joined(self.username)
            
            # Send list of online users to the new client
            self.send_online_users()
            
            # Main message receiving loop
            while self.running:
                try:
                    message_dict = self.receive_message()
                    
                    if message_dict is None:
                        # Connection lost
                        break
                    
                    # Process the received message
                    self.process_message(message_dict)
                    
                except Exception as e:
                    log_error(f"Error in message loop for {self.username}: {e}")
                    break
            
        except Exception as e:
            log_error(f"Error handling client {self.username}: {e}")
        finally:
            self.disconnect()
    
    def authenticate(self):
        """
        Authenticate the client and get their username.
        
        Returns:
            bool: True if authentication successful
        """
        try:
            # Receive authentication message
            data = self.client_socket.recv(BUFFER_SIZE)
            
            if not data:
                return False
            
            message_dict = Protocol.decode_message(data)
            
            if not message_dict or message_dict.get('type') != MessageType.AUTH:
                self.send_error("Invalid authentication message")
                return False
            
            username = message_dict.get('content')
            
            # Validate username
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                self.send_error(error_msg)
                return False
            
            # Check if username is already taken
            if self.server.is_username_taken(username):
                self.send_error("Username already taken")
                return False
            
            self.username = username
            
            # Add user to database
            self.server.db.add_user(username)
            
            # Add client to server's connected clients
            self.server.add_client(username, self.client_socket)
            
            # Send success message
            success_msg = Protocol.create_message(
                message_type=MessageType.AUTH_SUCCESS,
                content=f"Welcome {username}!"
            )
            self.send_message(success_msg)
            
            return True
            
        except Exception as e:
            log_error(f"Authentication error: {e}")
            return False
    
    def receive_message(self):
        """
        Receive a message from the client.
        
        Returns:
            dict: Parsed message dictionary or None if error
        """
        try:
            data = self.client_socket.recv(BUFFER_SIZE)
            
            if not data:
                return None
            
            message_dict = Protocol.decode_message(data)
            return message_dict
            
        except Exception as e:
            log_error(f"Error receiving message from {self.username}: {e}")
            return None
    
    def send_message(self, message_dict):
        """
        Send a message to this client.
        
        Args:
            message_dict: Dictionary containing message data
        
        Returns:
            bool: True if successful
        """
        try:
            encoded_msg = Protocol.encode_message(message_dict)
            if encoded_msg:
                self.client_socket.send(encoded_msg)
                return True
            return False
        except Exception as e:
            log_error(f"Error sending message to {self.username}: {e}")
            return False
    
    def process_message(self, message_dict):
        """
        Process received message based on its type.
        
        Args:
            message_dict: Parsed message dictionary
        """
        try:
            msg_type = message_dict.get('type')
            
            if msg_type == MessageType.GROUP:
                # Group message - broadcast to all
                content = message_dict.get('content')
                log_info(f"Group message from {self.username}: {content}")
                
                # Save to database
                self.server.db.save_message(self.username, None, content, is_group=True)
                
                # Broadcast to all clients
                self.server.broadcast_message(message_dict, self.username)
            
            elif msg_type == MessageType.PRIVATE:
                # Private message
                receiver = message_dict.get('receiver')
                content = message_dict.get('content')
                log_info(f"Private message from {self.username} to {receiver}: {content}")
                
                # Save to database
                self.server.db.save_message(self.username, receiver, content, is_group=False)
                
                # Send to specific user
                self.server.send_private_message(message_dict, self.username, receiver)
            
            elif msg_type == MessageType.GET_USERS:
                # Client requesting online users list
                self.send_online_users()
            
            elif msg_type == MessageType.GET_HISTORY:
                # Client requesting chat history
                self.send_chat_history()
            
            elif msg_type == MessageType.DISCONNECT:
                # Client disconnecting
                log_info(f"Client {self.username} requested disconnect")
                self.running = False
            
            else:
                log_error(f"Unknown message type from {self.username}: {msg_type}")
        
        except Exception as e:
            log_error(f"Error processing message from {self.username}: {e}")
    
    def send_chat_history(self):
        """
        Send chat history to the client.
        """
        try:
            # Get group message history
            history = self.server.db.get_group_history(limit=50)
            
            history_msg = Protocol.create_history_message(history)
            self.send_message(history_msg)
            
            log_info(f"Sent chat history to {self.username}")
            
        except Exception as e:
            log_error(f"Error sending chat history: {e}")
    
    def send_online_users(self):
        """
        Send list of online users to the client.
        """
        try:
            users = self.server.get_online_users()
            
            users_msg = Protocol.create_users_list_message(users)
            self.send_message(users_msg)
            
            log_info(f"Sent online users list to {self.username}")
            
        except Exception as e:
            log_error(f"Error sending online users: {e}")
    
    def send_error(self, error_text):
        """
        Send error message to client.
        
        Args:
            error_text (str): Error message
        """
        try:
            error_msg = Protocol.create_error_message(error_text)
            self.send_message(error_msg)
        except Exception as e:
            log_error(f"Error sending error message: {e}")
    
    def disconnect(self):
        """
        Handle client disconnection.
        """
        self.running = False
        
        if self.username:
            # Update last seen in database
            self.server.db.update_user_last_seen(self.username)
            
            # Remove from server's client list
            self.server.remove_client(self.username)
            
            # Notify other users
            self.server.broadcast_user_left(self.username)
            
            log_info(f"Client {self.username} disconnected")
        
        try:
            self.client_socket.close()
        except:
            pass
