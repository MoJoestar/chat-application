"""
PERSON 3: Client Networking

This file handles the client-side networking logic.
"""

import socket
import threading
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.protocol import Protocol, MessageType
from shared.utils import SERVER_HOST, SERVER_PORT, BUFFER_SIZE, log_info, log_error, validate_username


class ChatClient:
    """
    Handles client-side networking operations.
    """
    
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        """
        Initialize the chat client.
        """
        self.host = host
        self.port = port
        self.socket = None
        self.username = None
        self.connected = False
        self.receive_thread = None
        self.message_callback = None  # GUI will set this to handle incoming messages
        
        log_info("Client initialized")
    
    def connect(self, username, host=None, port=None):
        """
        Connect to the chat server.
        
        Args:
            username (str): Username to use for this connection
            host (str): Server host (optional, uses default if not provided)
            port (int): Server port (optional, uses default if not provided)
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Validate username
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                log_error(f"Invalid username: {error_msg}")
                return False, error_msg
            
            # Use custom host/port if provided
            if host:
                self.host = host
            if port:
                self.port = port
            
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)  # 10 second timeout for connection
            
            log_info(f"Attempting to connect to {self.host}:{self.port}")
            
            # Connect to server
            self.socket.connect((self.host, self.port))
            
            # Remove timeout after connection
            self.socket.settimeout(None)
            
            log_info("Connected to server, sending authentication...")
            
            # Send authentication message
            auth_msg = Protocol.create_auth_message(username)
            encoded_msg = Protocol.encode_message(auth_msg)
            self.socket.send(encoded_msg)
            
            # Wait for authentication response
            response_data = self.socket.recv(BUFFER_SIZE)
            response = Protocol.decode_message(response_data)
            
            if not response:
                return False, "No response from server"
            
            if response.get('type') == MessageType.AUTH_SUCCESS:
                self.username = username
                self.connected = True
                
                # Start receive thread
                self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
                self.receive_thread.start()
                
                success_msg = response.get('content', 'Connected successfully!')
                log_info(f"Authentication successful: {success_msg}")
                return True, success_msg
            
            elif response.get('type') == MessageType.ERROR:
                error_msg = response.get('content', 'Authentication failed')
                log_error(f"Authentication failed: {error_msg}")
                self.socket.close()
                return False, error_msg
            
            else:
                log_error("Unexpected response from server")
                self.socket.close()
                return False, "Unexpected response from server"
        
        except socket.timeout:
            log_error("Connection timeout")
            return False, "Connection timeout. Server may be offline."
        
        except ConnectionRefusedError:
            log_error("Connection refused")
            return False, "Connection refused. Server may be offline."
        
        except Exception as e:
            log_error(f"Connection error: {e}")
            return False, f"Connection error: {str(e)}"
    
    def disconnect(self):
        """
        Disconnect from the server.
        """
        try:
            self.connected = False
            
            if self.socket:
                # Send disconnect message
                try:
                    disconnect_msg = Protocol.create_message(
                        message_type=MessageType.DISCONNECT,
                        sender=self.username
                    )
                    self.socket.send(Protocol.encode_message(disconnect_msg))
                except:
                    pass
                
                # Close socket
                self.socket.close()
            
            log_info(f"Disconnected from server")
            
            # Notify GUI
            if self.message_callback:
                self.message_callback({
                    'type': 'notification',
                    'content': 'Disconnected from server'
                })
        
        except Exception as e:
            log_error(f"Error disconnecting: {e}")
    
    def send_message(self, message_text, receiver=None, is_group=True):
        """
        Send a message to the server.
        
        Args:
            message_text (str): The message to send
            receiver (str): Username of receiver (for private messages)
            is_group (bool): Whether this is a group message
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if not self.connected:
                return False, "Not connected to server"
            
            if not message_text or message_text.strip() == "":
                return False, "Message cannot be empty"
            
            # Create appropriate message
            if is_group:
                message_dict = Protocol.create_group_message(self.username, message_text)
            else:
                if not receiver:
                    return False, "Receiver required for private message"
                message_dict = Protocol.create_private_message(self.username, receiver, message_text)
            
            # Send message
            encoded_msg = Protocol.encode_message(message_dict)
            self.socket.send(encoded_msg)
            
            log_info(f"Message sent to {'group' if is_group else receiver}")
            return True, "Message sent"
        
        except Exception as e:
            log_error(f"Error sending message: {e}")
            self.connected = False
            return False, f"Error sending message: {str(e)}"
    
    def receive_messages(self):
        """
        Continuously receive messages from server (runs in separate thread).
        """
        log_info("Receive thread started")
        
        while self.connected:
            try:
                # Receive data from server
                data = self.socket.recv(BUFFER_SIZE)
                
                if not data:
                    # Connection closed by server
                    log_info("Connection closed by server")
                    self.connected = False
                    
                    # Notify GUI
                    if self.message_callback:
                        self.message_callback({
                            'type': 'notification',
                            'content': 'Connection lost'
                        })
                    break
                
                # Decode message
                message_dict = Protocol.decode_message(data)
                
                if message_dict:
                    log_info(f"Received message type: {message_dict.get('type')}")
                    
                    # Pass message to callback (GUI)
                    if self.message_callback:
                        self.message_callback(message_dict)
                
            except ConnectionResetError:
                log_error("Connection reset by server")
                self.connected = False
                if self.message_callback:
                    self.message_callback({
                        'type': 'notification',
                        'content': 'Connection lost'
                    })
                break
            
            except Exception as e:
                if self.connected:
                    log_error(f"Error receiving message: {e}")
                    self.connected = False
                    if self.message_callback:
                        self.message_callback({
                            'type': 'notification',
                            'content': f'Connection error: {str(e)}'
                        })
                break
        
        log_info("Receive thread ended")
    
    def request_online_users(self):
        """
        Request list of online users from server.
        
        Returns:
            bool: True if request sent successfully
        """
        try:
            if not self.connected:
                return False
            
            request_msg = Protocol.create_message(
                message_type=MessageType.GET_USERS,
                sender=self.username
            )
            
            encoded_msg = Protocol.encode_message(request_msg)
            self.socket.send(encoded_msg)
            
            log_info("Requested online users list")
            return True
        
        except Exception as e:
            log_error(f"Error requesting online users: {e}")
            return False
    
    def request_message_history(self):
        """
        Request message history from server.
        
        Returns:
            bool: True if request sent successfully
        """
        try:
            if not self.connected:
                return False
            
            request_msg = Protocol.create_message(
                message_type=MessageType.GET_HISTORY,
                sender=self.username
            )
            
            encoded_msg = Protocol.encode_message(request_msg)
            self.socket.send(encoded_msg)
            
            log_info("Requested message history")
            return True
        
        except Exception as e:
            log_error(f"Error requesting history: {e}")
            return False
    
    def set_message_callback(self, callback):
        """
        Set the callback function for received messages.
        This will be called by GUI to handle incoming messages.
        
        Args:
            callback (function): Function to call when message received
        """
        self.message_callback = callback
        log_info("Message callback set")
    
    def is_connected(self):
        """
        Check if client is connected.
        
        Returns:
            bool: True if connected
        """
        return self.connected
    
    def get_username(self):
        """
        Get current username.
        
        Returns:
            str: Username or None
        """
        return self.username
    
    def auto_reconnect(self, max_attempts=5, delay=5):
        """
        Attempt to reconnect to server automatically (optional feature).
        
        Args:
            max_attempts (int): Maximum reconnection attempts
            delay (int): Seconds to wait between attempts
        
        Returns:
            bool: True if reconnected successfully
        """
        if self.connected:
            return True
        
        log_info(f"Attempting auto-reconnect (max {max_attempts} attempts)")
        
        for attempt in range(1, max_attempts + 1):
            try:
                log_info(f"Reconnection attempt {attempt}/{max_attempts}")
                
                if self.message_callback:
                    self.message_callback({
                        'type': 'notification',
                        'content': f'Reconnecting... (attempt {attempt}/{max_attempts})'
                    })
                
                success, msg = self.connect(self.username)
                
                if success:
                    log_info("Reconnection successful")
                    if self.message_callback:
                        self.message_callback({
                            'type': 'notification',
                            'content': 'Reconnected successfully!'
                        })
                    return True
                
                if attempt < max_attempts:
                    time.sleep(delay)
            
            except Exception as e:
                log_error(f"Reconnection attempt {attempt} failed: {e}")
                if attempt < max_attempts:
                    time.sleep(delay)
        
        log_error("Auto-reconnect failed")
        if self.message_callback:
            self.message_callback({
                'type': 'notification',
                'content': 'Reconnection failed. Please try manually.'
            })
        
        return False


# ==================== TEST CODE ====================

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Chat Client")
    print("=" * 60)
    
    def test_callback(message):
        """Test callback for received messages."""
        print(f"[RECEIVED] Type: {message.get('type')}")
        print(f"           Content: {message.get('content', 'N/A')}")
        print()
    
    # Create client
    client = ChatClient()
    client.set_message_callback(test_callback)
    
    # Test connection
    print("\n1. Testing connection...")
    username = input("Enter username: ")
    success, msg = client.connect(username)
    
    if success:
        print(f"✓ Connected: {msg}")
        
        # Keep alive to receive messages
        print("\nClient running. Press Ctrl+C to disconnect.")
        try:
            while client.is_connected():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nDisconnecting...")
            client.disconnect()
    else:
        print(f"✗ Connection failed: {msg}")
    
    print("\n" + "=" * 60)
    print("Client test complete!")
    print("=" * 60)
