"""
Message Protocol Definition
This file defines the structure and format of all messages exchanged between client and server.
"""

import json
from enum import Enum
from datetime import datetime
from shared.utils import get_timestamp, log_error


# ==================== MESSAGE TYPES ====================

class MessageType:
    """Defines all possible message types in the protocol."""
    
    # Authentication
    AUTH = "auth"                    # Client authentication (login)
    AUTH_SUCCESS = "auth_success"    # Authentication successful
    AUTH_FAILED = "auth_failed"      # Authentication failed
    
    # Messaging
    GROUP = "group"                  # Group/broadcast message
    PRIVATE = "private"              # Private message to specific user
    
    # User Management
    USER_JOINED = "user_joined"      # Notification: user joined
    USER_LEFT = "user_left"          # Notification: user left
    GET_USERS = "get_users"          # Request online users list
    USERS_LIST = "users_list"        # Response: list of online users
    
    # History
    GET_HISTORY = "get_history"      # Request chat history
    HISTORY = "history"              # Response: chat history
    
    # Status
    STATUS = "status"                # Status update
    ERROR = "error"                  # Error message
    DISCONNECT = "disconnect"        # Client disconnect notification
    PING = "ping"                    # Keep-alive ping
    PONG = "pong"                    # Keep-alive pong response


# ==================== PROTOCOL CLASS ====================

class Protocol:
    """
    Handles message formatting and parsing according to the protocol.
    All messages are in JSON format.
    """
    
    @staticmethod
    def create_message(message_type, sender=None, receiver=None, content=None, data=None):
        """
        Create a message dictionary according to protocol.
        
        Args:
            message_type (str): Type of message (from MessageType)
            sender (str): Username of sender
            receiver (str): Username of receiver (for private messages)
            content (str): Message content/text
            data (dict): Additional data
        
        Returns:
            dict: Message dictionary
        """
        message = {
            "type": message_type,
            "timestamp": get_timestamp(),
        }
        
        if sender:
            message["sender"] = sender
        
        if receiver:
            message["receiver"] = receiver
        
        if content:
            message["content"] = content
        
        if data:
            message["data"] = data
        
        return message
    
    @staticmethod
    def create_auth_message(username):
        """
        Create authentication message.
        
        Args:
            username (str): Username to authenticate with
        
        Returns:
            dict: Authentication message
        """
        return Protocol.create_message(
            message_type=MessageType.AUTH,
            sender=username,
            content=username
        )
    
    @staticmethod
    def create_group_message(sender, content):
        """
        Create group/broadcast message.
        
        Args:
            sender (str): Username of sender
            content (str): Message content
        
        Returns:
            dict: Group message
        """
        return Protocol.create_message(
            message_type=MessageType.GROUP,
            sender=sender,
            content=content
        )
    
    @staticmethod
    def create_private_message(sender, receiver, content):
        """
        Create private message.
        
        Args:
            sender (str): Username of sender
            receiver (str): Username of receiver
            content (str): Message content
        
        Returns:
            dict: Private message
        """
        return Protocol.create_message(
            message_type=MessageType.PRIVATE,
            sender=sender,
            receiver=receiver,
            content=content
        )
    
    @staticmethod
    def create_user_joined_message(username):
        """
        Create user joined notification.
        
        Args:
            username (str): Username that joined
        
        Returns:
            dict: User joined message
        """
        return Protocol.create_message(
            message_type=MessageType.USER_JOINED,
            content=f"{username} joined the chat"
        )
    
    @staticmethod
    def create_user_left_message(username):
        """
        Create user left notification.
        
        Args:
            username (str): Username that left
        
        Returns:
            dict: User left message
        """
        return Protocol.create_message(
            message_type=MessageType.USER_LEFT,
            content=f"{username} left the chat"
        )
    
    @staticmethod
    def create_users_list_message(users_list):
        """
        Create online users list message.
        
        Args:
            users_list (list): List of online usernames
        
        Returns:
            dict: Users list message
        """
        return Protocol.create_message(
            message_type=MessageType.USERS_LIST,
            data={"users": users_list}
        )
    
    @staticmethod
    def create_history_message(messages):
        """
        Create history response message.
        
        Args:
            messages (list): List of message dictionaries
        
        Returns:
            dict: History message
        """
        return Protocol.create_message(
            message_type=MessageType.HISTORY,
            data={"messages": messages}
        )
    
    @staticmethod
    def create_error_message(error_text):
        """
        Create error message.
        
        Args:
            error_text (str): Error description
        
        Returns:
            dict: Error message
        """
        return Protocol.create_message(
            message_type=MessageType.ERROR,
            content=error_text
        )
    
    @staticmethod
    def create_status_message(status_text):
        """
        Create status message.
        
        Args:
            status_text (str): Status description
        
        Returns:
            dict: Status message
        """
        return Protocol.create_message(
            message_type=MessageType.STATUS,
            content=status_text
        )
    
    @staticmethod
    def serialize(message_dict):
        """
        Convert message dictionary to JSON string for transmission.
        
        Args:
            message_dict (dict): Message dictionary
        
        Returns:
            str: JSON string
        """
        try:
            return json.dumps(message_dict)
        except Exception as e:
            log_error(f"Error serializing message: {e}")
            return None
    
    @staticmethod
    def deserialize(json_string):
        """
        Convert JSON string to message dictionary.
        
        Args:
            json_string (str): JSON string
        
        Returns:
            dict: Message dictionary
        """
        try:
            return json.loads(json_string)
        except Exception as e:
            log_error(f"Error deserializing message: {e}")
            return None
    
    @staticmethod
    def encode_message(message_dict):
        """
        Encode message dictionary to bytes for sending over socket.
        
        Args:
            message_dict (dict): Message dictionary
        
        Returns:
            bytes: Encoded message
        """
        try:
            json_str = Protocol.serialize(message_dict)
            if json_str:
                return json_str.encode('utf-8')
            return None
        except Exception as e:
            log_error(f"Error encoding message: {e}")
            return None
    
    @staticmethod
    def decode_message(message_bytes):
        """
        Decode bytes to message dictionary.
        
        Args:
            message_bytes (bytes): Encoded message
        
        Returns:
            dict: Message dictionary
        """
        try:
            json_str = message_bytes.decode('utf-8')
            return Protocol.deserialize(json_str)
        except Exception as e:
            log_error(f"Error decoding message: {e}")
            return None
    
    @staticmethod
    def validate_message(message_dict):
        """
        Validate if message has required fields.
        
        Args:
            message_dict (dict): Message to validate
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(message_dict, dict):
            return False, "Message must be a dictionary"
        
        if "type" not in message_dict:
            return False, "Message must have a 'type' field"
        
        if "timestamp" not in message_dict:
            return False, "Message must have a 'timestamp' field"
        
        # Additional validation based on message type
        msg_type = message_dict["type"]
        
        if msg_type in [MessageType.GROUP, MessageType.PRIVATE]:
            if "sender" not in message_dict:
                return False, "Message must have a 'sender' field"
            if "content" not in message_dict:
                return False, "Message must have a 'content' field"
        
        if msg_type == MessageType.PRIVATE:
            if "receiver" not in message_dict:
                return False, "Private message must have a 'receiver' field"
        
        return True, ""


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    # Test message creation
    print("Testing Protocol...")
    
    # Create group message
    group_msg = Protocol.create_group_message("Alice", "Hello everyone!")
    print(f"\nGroup Message: {group_msg}")
    
    # Create private message
    private_msg = Protocol.create_private_message("Bob", "Alice", "Hi Alice!")
    print(f"\nPrivate Message: {private_msg}")
    
    # Serialize and deserialize
    json_str = Protocol.serialize(group_msg)
    print(f"\nSerialized: {json_str}")
    
    decoded = Protocol.deserialize(json_str)
    print(f"\nDeserialized: {decoded}")
    
    # Encode and decode
    encoded = Protocol.encode_message(group_msg)
    print(f"\nEncoded bytes: {encoded}")
    
    decoded_msg = Protocol.decode_message(encoded)
    print(f"\nDecoded message: {decoded_msg}")
    
    # Validate
    is_valid, error = Protocol.validate_message(group_msg)
    print(f"\nValidation: {is_valid}, Error: {error}")
    
    print("\nProtocol test complete!")
